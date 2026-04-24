from app.schemas.method import GradientStep, MethodInput, MSSettingsInput
from app.services.recommendation import CandidateSearchSpace, RecommendationEngine


class StubForwardModel:
    def predict(self, compound, method, ms_settings=None):
        rt = 0.55 * method.gradient_steps[-1].time_min
        if "BEH C18" in method.column:
            rt += 0.4
        quality = 0.75
        if method.ph and 3.0 <= method.ph <= 4.0:
            quality += 0.15
        return {
            "predicted_rt_min": rt,
            "quality_score": min(quality, 0.98),
            "confidence": 0.72,
            "risks": {
                "asymmetry": 0.2,
                "low_intensity": 0.15,
                "poor_resolution": 0.2,
            },
            "feature_summary": {"model": "stub"},
        }


def test_recommendations_rank_rt_fit_quality_and_runtime():
    search_space = CandidateSearchSpace(
        columns=["BEH C18 50x2.1 mm 1.7um", "HILIC 100x2.1 mm 2.6um"],
        ph_values=[3.2, 7.0],
        flow_rates_ml_min=[0.35],
        temperatures_c=[40.0],
        solvents_a=["Water + 0.1% formic acid"],
        solvents_b=["Acetonitrile + 0.1% formic acid"],
        gradient_end_times=[4.0, 8.0],
    )
    engine = RecommendationEngine(StubForwardModel(), search_space=search_space)

    recs = engine.recommend(
        compound={"smiles": "CC(=O)Oc1ccccc1C(=O)O", "name": "aspirin"},
        target_rt_min=4.5,
        top_n=3,
        allowed_columns=["BEH C18 50x2.1 mm 1.7um"],
        ms_settings=MSSettingsInput(ionization_mode="positive"),
    )

    assert len(recs) == 3
    assert recs[0].method.column == "BEH C18 50x2.1 mm 1.7um"
    assert recs[0].score >= recs[1].score >= recs[2].score
    assert "target RT" in recs[0].explanation


def test_method_input_estimates_runtime_from_gradient_steps():
    method = MethodInput(
        column="BEH C18",
        stationary_phase="C18",
        mobile_phase_a="Water",
        mobile_phase_b="Acetonitrile",
        ph=3.2,
        temperature_c=40,
        flow_rate_ml_min=0.35,
        injection_volume_ul=2,
        gradient_steps=[
            GradientStep(time_min=0, percent_b=5),
            GradientStep(time_min=5, percent_b=95),
            GradientStep(time_min=6, percent_b=95),
        ],
    )

    assert method.runtime_min == 6
