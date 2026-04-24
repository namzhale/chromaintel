from typing import Any, Literal

from pydantic import BaseModel, Field, computed_field, field_validator


class GradientStep(BaseModel):
    time_min: float = Field(ge=0)
    percent_b: float = Field(ge=0, le=100)


class MSSettingsInput(BaseModel):
    ionization_mode: Literal["positive", "negative", "both", "unknown"] = "unknown"
    precursor_mz: float | None = Field(default=None, gt=0)
    transitions: list[dict[str, Any]] = Field(default_factory=list)
    source_parameters: dict[str, Any] = Field(default_factory=dict)


class MethodInput(BaseModel):
    column: str
    stationary_phase: str
    mobile_phase_a: str
    mobile_phase_b: str
    ph: float | None = Field(default=None, ge=0, le=14)
    temperature_c: float | None = Field(default=None, ge=0, le=120)
    flow_rate_ml_min: float | None = Field(default=None, gt=0)
    injection_volume_ul: float | None = Field(default=None, ge=0)
    gradient_steps: list[GradientStep] = Field(default_factory=list)

    @field_validator("gradient_steps")
    @classmethod
    def validate_gradient_order(cls, value: list[GradientStep]) -> list[GradientStep]:
        times = [step.time_min for step in value]
        if times != sorted(times):
            raise ValueError("gradient steps must be sorted by time")
        return value

    @computed_field
    @property
    def runtime_min(self) -> float:
        if not self.gradient_steps:
            return 0.0
        return max(step.time_min for step in self.gradient_steps)


class CompoundInput(BaseModel):
    name: str | None = None
    smiles: str | None = None
    pubchem_cid: int | None = None
    chembl_id: str | None = None

    @field_validator("smiles", "name", "chembl_id")
    @classmethod
    def strip_blank(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None


class PredictionRequest(BaseModel):
    compound: CompoundInput
    method: MethodInput
    ms_settings: MSSettingsInput | None = None


class RecommendationRequest(BaseModel):
    compound: CompoundInput
    target_rt_min: float = Field(gt=0)
    target_quality_score: float = Field(default=0.8, ge=0, le=1)
    top_n: int = Field(default=5, ge=1, le=25)
    allowed_columns: list[str] = Field(default_factory=list)
    allowed_solvents_a: list[str] = Field(default_factory=list)
    allowed_solvents_b: list[str] = Field(default_factory=list)
    ms_settings: MSSettingsInput | None = None
