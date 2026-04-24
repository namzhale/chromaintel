from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from app.core.config import get_settings
from app.models.baseline import BaselineModelBundle
from app.schemas.method import MethodInput, MSSettingsInput
from app.services.features import build_feature_row


class ForwardPredictor:
    """Forward RT and peak-quality predictor with trained-model and fallback paths."""

    def __init__(self, artifact_path: str | Path | None = None):
        settings = get_settings()
        self.artifact_path = Path(artifact_path or settings.model_artifact_dir) / "baseline_bundle.joblib"
        self._bundle: BaselineModelBundle | None = None
        if self.artifact_path.exists():
            self._bundle = BaselineModelBundle.load(self.artifact_path)

    def predict(
        self,
        compound: dict[str, Any],
        method: MethodInput,
        ms_settings: MSSettingsInput | None = None,
    ) -> dict[str, Any]:
        features = build_feature_row(compound, method, ms_settings)
        if self._bundle:
            pred = self._bundle.predict(features)
            confidence = 0.72
            model_note = "trained RandomForest baseline"
        else:
            pred = self._heuristic_predict(features)
            confidence = 0.42
            model_note = "descriptor/condition heuristic fallback"

        risks = self._risk_components(pred["quality_score"], features, ms_settings)
        return {
            "predicted_rt_min": round(pred["predicted_rt_min"], 2),
            "quality_score": round(pred["quality_score"], 3),
            "confidence": confidence,
            "risks": risks,
            "feature_summary": {
                "model": model_note,
                "logp": round(features.get("logp", 0.0), 2),
                "tpsa": round(features.get("tpsa", 0.0), 2),
                "runtime_min": round(features.get("runtime_min", 0.0), 2),
                "gradient_slope_percent_b_min": round(
                    features.get("gradient_slope_percent_b_min", 0.0), 2
                ),
            },
            "explanation": self._explain(pred, features, model_note),
        }

    @staticmethod
    def _heuristic_predict(features: dict[str, Any]) -> dict[str, float]:
        logp = features.get("logp", 1.0)
        tpsa = features.get("tpsa", 50.0)
        runtime = max(features.get("runtime_min", 6.0), 1.0)
        final_b = features.get("final_percent_b", 95.0)
        ph = features.get("ph", 7.0)
        column_bonus = 0.7 if "C18" in str(features.get("column", "")).upper() else 0.2
        hydrophobicity = np.clip((logp + 1.5) / 6.0, 0.05, 1.2)
        polarity_penalty = np.clip(tpsa / 180.0, 0.0, 0.8)
        organic_strength = np.clip(final_b / 100.0, 0.2, 1.0)
        rt = runtime * np.clip(0.25 + hydrophobicity + column_bonus - 0.35 * organic_strength - polarity_penalty, 0.1, 0.95)
        quality = 0.62 + 0.12 * (3.0 <= ph <= 5.5) + 0.08 * (30 <= features.get("temperature_c", 35) <= 50)
        quality -= 0.08 * (features.get("gradient_slope_percent_b_min", 12) > 25)
        return {"predicted_rt_min": float(rt), "quality_score": float(np.clip(quality, 0.2, 0.95))}

    @staticmethod
    def _risk_components(
        quality_score: float,
        features: dict[str, Any],
        ms_settings: MSSettingsInput | None,
    ) -> dict[str, float]:
        slope = features.get("gradient_slope_percent_b_min", 0)
        flow = features.get("flow_rate_ml_min", 0.3)
        ion_mode_known = bool(ms_settings and ms_settings.ionization_mode != "unknown")
        return {
            "asymmetry": round(float(np.clip(0.55 - quality_score * 0.35 + max(flow - 0.6, 0), 0, 1)), 3),
            "low_intensity": round(float(np.clip(0.45 - quality_score * 0.25 + (0 if ion_mode_known else 0.12), 0, 1)), 3),
            "poor_resolution": round(float(np.clip(0.5 - quality_score * 0.3 + max(slope - 20, 0) / 50, 0, 1)), 3),
        }

    @staticmethod
    def _explain(pred: dict[str, float], features: dict[str, Any], model_note: str) -> str:
        return (
            f"Using the {model_note}, the compound is expected near "
            f"{pred['predicted_rt_min']:.2f} min. Retention is driven mainly by logP "
            f"({features.get('logp', 0):.2f}), TPSA ({features.get('tpsa', 0):.1f}), "
            f"column chemistry, and the gradient ending at {features.get('final_percent_b', 0):.0f}% B."
        )
