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
    optimization_hooks: dict[str, Any] = field(
        default_factory=lambda: {
            "bayesian_optimization": {
                "enabled": False,
                "status": "roadmap",
                "notes": "Future optional acquisition loop can score candidate batches without adding a hard dependency.",
            },
            "active_learning": {
                "enabled": False,
                "status": "roadmap",
                "notes": "Future hook for selecting high-uncertainty recommendations for lab confirmation.",
            },
        }
    )

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
        known_methods: list[dict[str, Any]] | None = None,
    ):
        settings = get_settings()
        self.predictor = predictor
        self.search_space = search_space or CandidateSearchSpace.default()
        self.known_methods = known_methods or []
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
        constraints = self._applied_constraints(
            allowed_columns=allowed_columns,
            allowed_solvents_a=allowed_solvents_a,
            allowed_solvents_b=allowed_solvents_b,
            allowed_ph_range=allowed_ph_range,
            allowed_flow_range=allowed_flow_range,
            allowed_temperature_range=allowed_temperature_range,
            max_runtime_min=max_runtime_min,
        )
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
            rt_contribution = self.weights["rt_fit"] * rt_fit
            quality_contribution = self.weights["quality"] * pred["quality_score"]
            runtime_contribution = -self.weights["runtime"] * runtime_penalty
            confidence_contribution = self.weights["confidence"] * pred["confidence"]
            ad_contribution = -self.weights.get("ad_penalty", 0.0) * ad_penalty
            components = {
                "rt_fit": round(float(rt_fit), 4),
                "quality": round(float(pred["quality_score"]), 4),
                "runtime_penalty": round(float(runtime_penalty), 4),
                "confidence": round(float(pred["confidence"]), 4),
                "ad_penalty": round(float(ad_penalty), 4),
                "rt_fit_contribution": round(float(rt_contribution), 4),
                "quality_contribution": round(float(quality_contribution), 4),
                "runtime_contribution": round(float(runtime_contribution), 4),
                "confidence_contribution": round(float(confidence_contribution), 4),
                "ad_penalty_contribution": round(float(ad_contribution), 4),
            }
            nearest_known_methods = self._nearest_known_methods(method, compound)
            reason_codes = self._reason_codes(pred, rt_fit, runtime_penalty, ad_penalty, constraints, nearest_known_methods)
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
                    constraints=constraints,
                    reason_codes=reason_codes,
                    forward_prediction=self._forward_prediction_summary(pred),
                    nearest_known_methods=nearest_known_methods,
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

    @staticmethod
    def _applied_constraints(**constraints: Any) -> dict[str, Any]:
        applied: dict[str, Any] = {}
        for key, value in constraints.items():
            if value is None:
                continue
            if isinstance(value, tuple):
                applied[key] = list(value)
            else:
                applied[key] = value
        return applied

    @staticmethod
    def _forward_prediction_summary(pred: dict[str, Any]) -> dict[str, Any]:
        feature_summary = dict(pred.get("feature_summary", {}))
        return {
            "model": feature_summary.get("model"),
            "uncertainty_rt_min": pred.get("uncertainty_rt_min"),
            "out_of_domain_method": pred.get("out_of_domain_method"),
            "feature_summary": feature_summary,
            "risks": dict(pred.get("risks", {})),
        }

    @staticmethod
    def _reason_codes(
        pred: dict[str, Any],
        rt_fit: float,
        runtime_penalty: float,
        ad_penalty: float,
        constraints: dict[str, Any],
        nearest_known_methods: list[dict[str, Any]],
    ) -> list[str]:
        codes: list[str] = []
        model_name = pred.get("feature_summary", {}).get("model")
        if model_name:
            codes.append(f"forward_model:{model_name}")
        if rt_fit >= 0.9:
            codes.append("target_rt_match_high")
        elif rt_fit >= 0.7:
            codes.append("target_rt_match_moderate")
        else:
            codes.append("target_rt_match_low")
        if pred.get("quality_score", 0.0) >= 0.8:
            codes.append("quality_score_high")
        if runtime_penalty <= 0.5:
            codes.append("runtime_compact")
        if ad_penalty:
            codes.append("out_of_domain_penalty")
        else:
            codes.append("within_applicability_domain")
        if constraints:
            codes.append("constraints_applied")
        if nearest_known_methods:
            codes.append("nearest_known_method_available")
        else:
            codes.append("nearest_known_method_unavailable")
        return codes

    def _nearest_known_methods(
        self,
        method: MethodInput,
        compound: dict[str, Any],
        top_k: int = 3,
    ) -> list[dict[str, Any]]:
        if not self.known_methods:
            return []

        scored = []
        for known in self.known_methods:
            similarity, match_reasons = self._known_method_similarity(method, compound, known)
            scored.append((similarity, known, match_reasons))
        scored.sort(key=lambda item: item[0], reverse=True)

        nearest = []
        for similarity, known, match_reasons in scored[:top_k]:
            nearest.append(
                {
                    "method_id": known.get("method_id") or known.get("id"),
                    "source": known.get("source"),
                    "compound_name": known.get("compound_name") or known.get("compound"),
                    "similarity": round(float(similarity), 4),
                    "match_reasons": match_reasons,
                }
            )
        return nearest

    @staticmethod
    def _known_method_similarity(
        method: MethodInput,
        compound: dict[str, Any],
        known: dict[str, Any],
    ) -> tuple[float, list[str]]:
        score = 0.0
        total = 0.0
        reasons: list[str] = []

        exact_fields = [
            ("column", method.column, 0.25),
            ("stationary_phase", method.stationary_phase, 0.1),
            ("mobile_phase_a", method.mobile_phase_a, 0.1),
            ("mobile_phase_b", method.mobile_phase_b, 0.1),
        ]
        for field_name, candidate_value, weight in exact_fields:
            total += weight
            if str(known.get(field_name, "")).lower() == str(candidate_value).lower():
                score += weight
                reasons.append(f"{field_name}_match")

        numeric_fields = [
            ("ph", method.ph, 2.0, 0.15),
            ("flow_rate_ml_min", method.flow_rate_ml_min, 0.5, 0.1),
            ("temperature_c", method.temperature_c, 30.0, 0.1),
            ("runtime_min", method.runtime_min, 12.0, 0.1),
        ]
        for field_name, candidate_value, scale, weight in numeric_fields:
            total += weight
            known_value = known.get(field_name)
            if known_value is None or candidate_value is None:
                continue
            closeness = 1.0 - min(abs(float(candidate_value) - float(known_value)) / scale, 1.0)
            if closeness >= 0.8:
                reasons.append(f"{field_name}_near")
            score += weight * closeness

        compound_name = (compound.get("name") or "").lower()
        known_compound = str(known.get("compound_name") or known.get("compound") or "").lower()
        if compound_name and known_compound:
            total += 0.1
            if compound_name == known_compound:
                score += 0.1
                reasons.append("compound_name_match")

        return (score / total if total else 0.0), reasons
