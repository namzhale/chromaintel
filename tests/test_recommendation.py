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


class DomainAwareStubForwardModel:
    def predict(self, compound, method, ms_settings=None):
        out_of_domain = "HILIC" in method.column
        return {
            "predicted_rt_min": 4.0,
            "quality_score": 0.8,
            "confidence": 0.7,
            "out_of_domain": out_of_domain,
            "out_of_domain_reasons": ["unseen category"] if out_of_domain else [],
            "risks": {},
            "feature_summary": {},
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
    assert {"rt_fit", "quality", "runtime_penalty", "confidence", "ad_penalty"}.issubset(
        recs[0].score_components
    )


def test_recommendations_penalize_out_of_domain_candidates():
    search_space = CandidateSearchSpace(
        columns=["BEH C18 50x2.1 mm 1.7um", "HILIC 100x2.1 mm 2.6um"],
        ph_values=[3.2],
        flow_rates_ml_min=[0.35],
        temperatures_c=[40.0],
        solvents_a=["Water + 0.1% formic acid"],
        solvents_b=["Acetonitrile + 0.1% formic acid"],
        gradient_end_times=[5.0],
    )
    engine = RecommendationEngine(DomainAwareStubForwardModel(), search_space=search_space)

    recs = engine.recommend(
        compound={"smiles": "CCO", "name": "ethanol"},
        target_rt_min=4.0,
        top_n=2,
        ms_settings=MSSettingsInput(ionization_mode="positive"),
    )

    assert recs[0].method.column == "BEH C18 50x2.1 mm 1.7um"
    assert recs[0].score_components["ad_penalty"] == 0.0
    assert recs[1].out_of_domain is True
    assert recs[1].score_components["ad_penalty"] == 1.0


def test_search_space_loads_from_checked_in_config_and_applies_bounds():
    search_space = CandidateSearchSpace.from_config()
    engine = RecommendationEngine(StubForwardModel(), search_space=search_space)

    methods = engine._candidate_methods(
        allowed_columns=["BEH C18 50x2.1 mm 1.7um"],
        allowed_solvents_a=["Water + 0.1% formic acid"],
        allowed_solvents_b=["Acetonitrile + 0.1% formic acid"],
        allowed_ph_range=(3.0, 3.5),
        allowed_flow_range=(0.3, 0.4),
        allowed_temperature_range=(39.0, 41.0),
        max_runtime_min=6.0,
    )

    assert methods
    assert {method.ph for method in methods} == {3.2}
    assert {method.flow_rate_ml_min for method in methods} == {0.35}
    assert {method.temperature_c for method in methods} == {40.0}
    assert all(method.runtime_min <= 6.0 for method in methods)


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
