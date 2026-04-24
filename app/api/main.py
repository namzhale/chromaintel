from __future__ import annotations

from fastapi import Depends, FastAPI
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.adapters.pubchem import PubChemClient
from app.db.models import AuditLog, PeakMetric, Run
from app.db.session import get_db
from app.schemas.method import PredictionRequest, RecommendationRequest
from app.schemas.prediction import PredictionResponse, RecommendationCandidate
from app.services.predictor import ForwardPredictor
from app.services.recommendation import RecommendationEngine

app = FastAPI(
    title="AI-assisted LC-MS/MS Method Development MVP",
    version="0.1.0",
    description="Bioanalytical LC-MS/MS forward prediction and method recommendation MVP.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/compounds/pubchem")
def pubchem_lookup(name: str | None = None, cid: int | None = None) -> dict:
    client = PubChemClient()
    if cid:
        return client.lookup_by_cid(cid)
    if name:
        return client.lookup_by_name(name)
    return {"error": "Provide name or cid"}


@app.post("/predict", response_model=PredictionResponse)
def predict_rt(request: PredictionRequest, db: Session = Depends(get_db)) -> PredictionResponse:
    predictor = ForwardPredictor()
    compound = request.compound.model_dump(exclude_none=True)
    result = predictor.predict(compound, request.method, request.ms_settings)
    db.add(
        AuditLog(
            actor="api",
            action="predict",
            entity_type="model_prediction",
            input_json=request.model_dump(mode="json"),
            output_json=result,
        )
    )
    db.commit()
    return PredictionResponse(**result)


@app.post("/recommend", response_model=list[RecommendationCandidate])
def recommend_methods(
    request: RecommendationRequest, db: Session = Depends(get_db)
) -> list[RecommendationCandidate]:
    engine = RecommendationEngine(ForwardPredictor())
    recs = engine.recommend(
        compound=request.compound.model_dump(exclude_none=True),
        target_rt_min=request.target_rt_min,
        top_n=request.top_n,
        allowed_columns=request.allowed_columns,
        allowed_solvents_a=request.allowed_solvents_a,
        allowed_solvents_b=request.allowed_solvents_b,
        ms_settings=request.ms_settings,
    )
    db.add(
        AuditLog(
            actor="api",
            action="recommend",
            entity_type="recommendation",
            input_json=request.model_dump(mode="json"),
            output_json=[rec.model_dump(mode="json") for rec in recs],
        )
    )
    db.commit()
    return recs


@app.get("/datasets/browser")
def dataset_browser(
    compound: str | None = None,
    column: str | None = None,
    matrix: str | None = None,
    ionization_mode: str | None = None,
    db: Session = Depends(get_db),
) -> list[dict]:
    stmt = select(PeakMetric, Run).join(Run, PeakMetric.run_id == Run.id).limit(200)
    rows = db.execute(stmt).all()
    results = []
    for peak, run in rows:
        record = {
            "run_identifier": run.run_identifier,
            "compound_id": peak.compound_id,
            "matrix": run.matrix,
            "retention_time_min": peak.retention_time_min,
            "quality_score": peak.quality_score,
        }
        if matrix and record["matrix"] != matrix:
            continue
        results.append(record)
    return results
