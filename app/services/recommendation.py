from __future__ import annotations

import json
from dataclasses import dataclass, field
from itertools import product
from pathlib import Path
from typing import Any

import numpy as np

from app.core.config import get_settings
from app.schemas.method import GradientStep, MethodInput, MSSettingsInput
from app.schemas.prediction import RecommendationCandidate
from app.services.predictor import ForwardPredictor


DEFAULT_SEARCH_SPACE_PATH = Path(__file__).resolve().parents[2] / "config" / "recommendation_search_space.json"


@dataclass
class CandidateSearchSpace:
    columns: list[str] = field(
        default_factory=lambda: [
            "BEH C18 50x2.1 mm 1.7um",
            "CSH Phenyl-Hexyl 50x2.1 mm 1.7um",
            "HILIC Amide 100x2.1 mm 2.6um",
        ]
    )
    ph_values: list[float] = field(default_factory=lambda: [3.2, 4.8, 7.0])
    flow_rates_ml_min: list[float] = field(default_factory=lambda: [0.25, 0.35, 0.5])
    temperatures_c: list[float] = field(default_factory=lambda: [30.0, 40.0, 50.0])
    solvents_a: list[str] = field(
        default_factory=lambda: ["Water + 0.1% formic acid", "10 mM ammonium formate in water"]
    )
    solvents_b: list[str] = field(
        default_factory=lambda: ["Acetonitrile + 0.1% formic acid", "Methanol + 0.1% formic acid"]
    )
    gradient_end_times: list[float] = field(default_factory=lambda: [3.5, 5.0, 8.0])
    max_runtime_min: float = 12.0

    @classmethod
    def from_config(cls, path: str | Path = DEFAULT_SEARCH_SPACE_PATH) -> "CandidateSearchSpace":
        """Load a checked-in constrained LC method search space from JSON."""

        config_path = Path(path)
        payload = json.loads(config_path.read_text(encoding="utf-8"))
        allowed_fields = cls.__dataclass_fields__
        values = {key: value for key, value in payload.items() if key in allowed_fields}
        return cls(**values)

    @classmethod
    def default(cls) -> "CandidateSearchSpace":
        """Use checked-in config when present, otherwise fall back to in-code defaults."""

        return cls.from_config(DEFAULT_SEARCH_SPACE_PATH) if DEFAULT_SEARCH_SPACE_PATH.exists() else cls()


class RecommendationEngine:
    """Constrained optimizer that ranks generated methods with forward models."""

    def __init__(
        self,
        predictor: ForwardPredictor,
        search_space: CandidateSearchSpace | None = None,
        weights: dict[str, float] | None = None,
    ):
        settings = get_settings()
        self.predictor = predictor
        self.search_space = search_space or CandidateSearchSpace.default()
        self.weights = weights or {
            "quality": settings.recommendation_quality_weight,
            "rt_fit": settings.recommendation_rt_weight,
            "runtime": settings.recommendation_runtime_weight,
            "confidence": settings.recommendation_confidence_weight,
            "ad_penalty": 0.2,
        }

    def recommend(
        self,
        compound: dict[str, Any],
        target_rt_min: float,
        top_n: int = 5,
        allowed_columns: list[str] | None = None,
        allowed_solvents_a: list[str] | None = None,
        allowed_solvents_b: list[str] | None = None,
        allowed_ph_range: tuple[float, float] | None = None,
        allowed_flow_range: tuple[float, float] | None = None,
        allowed_temperature_range: tuple[float, float] | None = None,
        max_runtime_min: float | None = None,
        ms_settings: MSSettingsInput | None = None,
    ) -> list[RecommendationCandidate]:
        candidates: list[RecommendationCandidate] = []
        for method in self._candidate_methods(
            allowed_columns,
            allowed_solvents_a,
            allowed_solvents_b,
            allowed_ph_range,
            allowed_flow_range,
            allowed_temperature_range,
            max_runtime_min,
        ):
            pred = self.predictor.predict(compound, method, ms_settings)
            rt_fit = 1.0 - min(abs(pred["predicted_rt_min"] - target_rt_min) / max(target_rt_min, 0.1), 1.0)
            runtime_penalty = min(method.runtime_min / max(self.search_space.max_runtime_min, 0.1), 1.0)
            ad_penalty = 1.0 if pred.get("out_of_domain") else 0.0
            score = (
                + self.weights["rt_fit"] * rt_fit
                + self.weights["quality"] * pred["quality_score"]
                - self.weights["runtime"] * runtime_penalty
                + self.weights["confidence"] * pred["confidence"]
                - self.weights.get("ad_penalty", 0.0) * ad_penalty
            )
            components = {
                "rt_fit": round(float(rt_fit), 4),
                "quality": round(float(pred["quality_score"]), 4),
                "runtime_penalty": round(float(runtime_penalty), 4),
                "confidence": round(float(pred["confidence"]), 4),
                "ad_penalty": round(float(ad_penalty), 4),
            }
            candidates.append(
                RecommendationCandidate(
                    rank=0,
                    method=method,
                    predicted_rt_min=pred["predicted_rt_min"],
                    predicted_quality_score=pred["quality_score"],
                    estimated_runtime_min=method.runtime_min,
                    confidence=pred["confidence"],
                    score=round(float(score), 4),
                    score_components=components,
                    out_of_domain=bool(pred.get("out_of_domain", False)),
                    out_of_domain_reasons=list(pred.get("out_of_domain_reasons", [])),
                    explanation=(
                        f"Predicted RT is {pred['predicted_rt_min']:.2f} min versus target RT "
                        f"{target_rt_min:.2f} min; quality is {pred['quality_score']:.2f}. "
                        f"The method balances runtime ({method.runtime_min:.1f} min), pH {method.ph}, "
                        f"and {method.column} selectivity."
                        + (" Applicability-domain support is low for this candidate." if ad_penalty else "")
                    ),
                )
            )

        ranked = sorted(
            candidates,
            key=lambda item: (item.score, item.predicted_quality_score, -abs(item.predicted_rt_min - target_rt_min)),
            reverse=True,
        )[:top_n]
        return [candidate.model_copy(update={"rank": idx + 1}) for idx, candidate in enumerate(ranked)]

    def _candidate_methods(
        self,
        allowed_columns: list[str] | None,
        allowed_solvents_a: list[str] | None,
        allowed_solvents_b: list[str] | None,
        allowed_ph_range: tuple[float, float] | None = None,
        allowed_flow_range: tuple[float, float] | None = None,
        allowed_temperature_range: tuple[float, float] | None = None,
        max_runtime_min: float | None = None,
    ) -> list[MethodInput]:
        columns = self._constrain(self.search_space.columns, allowed_columns)
        solvents_a = self._constrain(self.search_space.solvents_a, allowed_solvents_a)
        solvents_b = self._constrain(self.search_space.solvents_b, allowed_solvents_b)
        ph_values = self._range_constrain(self.search_space.ph_values, allowed_ph_range)
        flow_rates = self._range_constrain(self.search_space.flow_rates_ml_min, allowed_flow_range)
        temperatures = self._range_constrain(self.search_space.temperatures_c, allowed_temperature_range)
        runtime_limit = max_runtime_min or self.search_space.max_runtime_min
        methods = []
        for column, ph, flow, temp, solvent_a, solvent_b, end_time in product(
            columns,
            ph_values,
            flow_rates,
            temperatures,
            solvents_a,
            solvents_b,
            self.search_space.gradient_end_times,
        ):
            if float(end_time + 0.8) > float(runtime_limit):
                continue
            stationary_phase = "HILIC" if "HILIC" in column.upper() else "reversed phase"
            initial_b = 85.0 if stationary_phase == "HILIC" else 5.0
            final_b = 95.0
            if stationary_phase == "HILIC":
                final_b = 45.0
            methods.append(
                MethodInput(
                    column=column,
                    stationary_phase=stationary_phase,
                    mobile_phase_a=solvent_a,
                    mobile_phase_b=solvent_b,
                    ph=ph,
                    temperature_c=temp,
                    flow_rate_ml_min=flow,
                    injection_volume_ul=2.0,
                    gradient_steps=[
                        GradientStep(time_min=0.0, percent_b=initial_b),
                        GradientStep(time_min=float(end_time), percent_b=final_b),
                        GradientStep(time_min=float(end_time + 0.8), percent_b=final_b),
                    ],
                )
            )
        return methods

    @staticmethod
    def _constrain(defaults: list[str], allowed: list[str] | None) -> list[str]:
        allowed = [item for item in (allowed or []) if item]
        return [item for item in defaults if item in allowed] if allowed else defaults

    @staticmethod
    def _range_constrain(defaults: list[float], allowed_range: tuple[float, float] | None) -> list[float]:
        if not allowed_range:
            return defaults
        low, high = allowed_range
        return [value for value in defaults if float(low) <= float(value) <= float(high)]
