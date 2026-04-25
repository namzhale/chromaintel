from typing import Any

from pydantic import BaseModel, Field

from app.schemas.method import MethodInput


class PredictionResponse(BaseModel):
    predicted_rt_min: float
    quality_score: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    risks: dict[str, float]
    feature_summary: dict[str, Any]
    explanation: str


class RecommendationCandidate(BaseModel):
    rank: int
    method: MethodInput
    predicted_rt_min: float
    predicted_quality_score: float
    estimated_runtime_min: float
    confidence: float
    score: float
    score_components: dict[str, float] = Field(default_factory=dict)
    out_of_domain: bool = False
    out_of_domain_reasons: list[str] = Field(default_factory=list)
    explanation: str
