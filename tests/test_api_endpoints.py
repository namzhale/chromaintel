from __future__ import annotations

from types import SimpleNamespace

from app.api.main import dataset_browser, health, predict_rt, recommend_methods
from app.schemas.method import PredictionRequest, RecommendationRequest


class FakeDB:
    def __init__(self) -> None:
        self.added = []
        self.commits = 0

    def add(self, item) -> None:
        self.added.append(item)

    def commit(self) -> None:
        self.commits += 1

    def execute(self, statement):
        peak = SimpleNamespace(
            compound_id=101,
            retention_time_min=2.35,
            quality_score=0.82,
        )
        run = SimpleNamespace(
            run_identifier="run-api-001",
            matrix="plasma",
        )
        return SimpleNamespace(all=lambda: [(peak, run)])


def _prediction_payload() -> dict:
    return {
        "compound": {
            "name": "Caffeine",
            "smiles": "Cn1cnc2c1c(=O)n(C)c(=O)n2C",
        },
        "method": {
            "column": "BEH C18 50x2.1 mm 1.7um",
            "stationary_phase": "C18",
            "mobile_phase_a": "Water + 0.1% formic acid",
            "mobile_phase_b": "Acetonitrile + 0.1% formic acid",
            "ph": 3.2,
            "temperature_c": 40.0,
            "flow_rate_ml_min": 0.35,
            "injection_volume_ul": 2.0,
            "gradient_steps": [
                {"time_min": 0.0, "percent_b": 5.0},
                {"time_min": 5.0, "percent_b": 95.0},
            ],
        },
        "ms_settings": {"ionization_mode": "positive", "precursor_mz": 195.1},
    }


def test_health_endpoint():
    assert health() == {"status": "ok"}


def test_predict_endpoint_returns_forward_prediction_and_audits():
    db = FakeDB()
    response = predict_rt(PredictionRequest(**_prediction_payload()), db=db)

    payload = response.model_dump()
    assert payload["predicted_rt_min"] > 0
    assert 0 <= payload["quality_score"] <= 1
    assert 0 <= payload["confidence"] <= 1
    assert "feature_summary" in payload
    assert "explanation" in payload
    assert len(db.added) == 1
    assert db.commits == 1


def test_recommend_endpoint_returns_ranked_candidates():
    db = FakeDB()
    request = {
        "compound": _prediction_payload()["compound"],
        "target_rt_min": 4.0,
        "target_quality_score": 0.75,
        "top_n": 3,
        "allowed_columns": ["BEH C18 50x2.1 mm 1.7um"],
        "ms_settings": {"ionization_mode": "positive"},
    }

    response = recommend_methods(RecommendationRequest(**request), db=db)

    payload = [item.model_dump() for item in response]
    assert len(payload) == 3
    assert payload[0]["rank"] == 1
    assert payload[0]["score_components"]
    assert payload[0]["method"]["column"] == "BEH C18 50x2.1 mm 1.7um"
    assert len(db.added) == 1
    assert db.commits == 1


def test_dataset_browser_endpoint_uses_filters_and_serializes_rows():
    response = dataset_browser(matrix="plasma", db=FakeDB())

    assert response == [
        {
            "run_identifier": "run-api-001",
            "compound_id": 101,
            "matrix": "plasma",
            "retention_time_min": 2.35,
            "quality_score": 0.82,
        }
    ]
