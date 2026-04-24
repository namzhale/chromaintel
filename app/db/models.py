from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class Compound(TimestampMixin, Base):
    __tablename__ = "compounds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    pubchem_cid: Mapped[int | None] = mapped_column(Integer, index=True)
    chembl_id: Mapped[str | None] = mapped_column(String(64), index=True)
    formula: Mapped[str | None] = mapped_column(String(128))
    monoisotopic_mass: Mapped[float | None] = mapped_column(Float)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    structures: Mapped[list["CompoundStructure"]] = relationship(
        back_populates="compound", cascade="all, delete-orphan"
    )
    peak_metrics: Mapped[list["PeakMetric"]] = relationship(back_populates="compound")


class CompoundStructure(TimestampMixin, Base):
    __tablename__ = "compound_structures"
    __table_args__ = (UniqueConstraint("compound_id", "canonical_smiles"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    compound_id: Mapped[int] = mapped_column(ForeignKey("compounds.id"), index=True)
    input_smiles: Mapped[str] = mapped_column(Text, nullable=False)
    canonical_smiles: Mapped[str] = mapped_column(Text, nullable=False)
    inchikey: Mapped[str | None] = mapped_column(String(64), index=True)
    descriptors_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    compound: Mapped[Compound] = relationship(back_populates="structures")


class Dataset(TimestampMixin, Base):
    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    license: Mapped[str | None] = mapped_column(String(255))
    import_status: Mapped[str] = mapped_column(String(64), default="loaded")
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    runs: Mapped[list["Run"]] = relationship(back_populates="dataset")


class Method(TimestampMixin, Base):
    __tablename__ = "methods"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    stationary_phase: Mapped[str] = mapped_column(String(255), nullable=False)
    column: Mapped[str] = mapped_column(String(255), nullable=False)
    mobile_phase_a: Mapped[str] = mapped_column(String(255), nullable=False)
    mobile_phase_b: Mapped[str] = mapped_column(String(255), nullable=False)
    ph: Mapped[float | None] = mapped_column(Float)
    temperature_c: Mapped[float | None] = mapped_column(Float)
    flow_rate_ml_min: Mapped[float | None] = mapped_column(Float)
    injection_volume_ul: Mapped[float | None] = mapped_column(Float)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    gradient_steps: Mapped[list["MethodGradientStep"]] = relationship(
        back_populates="method", cascade="all, delete-orphan", order_by="MethodGradientStep.time_min"
    )
    runs: Mapped[list["Run"]] = relationship(back_populates="method")


class MethodGradientStep(Base):
    __tablename__ = "method_gradient_steps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    method_id: Mapped[int] = mapped_column(ForeignKey("methods.id"), index=True)
    time_min: Mapped[float] = mapped_column(Float, nullable=False)
    percent_b: Mapped[float] = mapped_column(Float, nullable=False)

    method: Mapped[Method] = relationship(back_populates="gradient_steps")


class MSSetting(TimestampMixin, Base):
    __tablename__ = "ms_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ionization_mode: Mapped[str] = mapped_column(String(32), nullable=False)
    precursor_mz: Mapped[float | None] = mapped_column(Float)
    transitions_json: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    source_parameters_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    runs: Mapped[list["Run"]] = relationship(back_populates="ms_settings")


class Run(TimestampMixin, Base):
    __tablename__ = "runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"), index=True)
    method_id: Mapped[int] = mapped_column(ForeignKey("methods.id"), index=True)
    ms_settings_id: Mapped[int | None] = mapped_column(ForeignKey("ms_settings.id"), index=True)
    run_identifier: Mapped[str] = mapped_column(String(255), nullable=False)
    matrix: Mapped[str | None] = mapped_column(String(128), index=True)
    analyst: Mapped[str | None] = mapped_column(String(128))
    acquired_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    dataset: Mapped[Dataset] = relationship(back_populates="runs")
    method: Mapped[Method] = relationship(back_populates="runs")
    ms_settings: Mapped[MSSetting | None] = relationship(back_populates="runs")
    peak_metrics: Mapped[list["PeakMetric"]] = relationship(
        back_populates="run", cascade="all, delete-orphan"
    )


class PeakMetric(TimestampMixin, Base):
    __tablename__ = "peak_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id"), index=True)
    compound_id: Mapped[int] = mapped_column(ForeignKey("compounds.id"), index=True)
    retention_time_min: Mapped[float] = mapped_column(Float, nullable=False)
    peak_area: Mapped[float | None] = mapped_column(Float)
    peak_height: Mapped[float | None] = mapped_column(Float)
    asymmetry: Mapped[float | None] = mapped_column(Float)
    resolution: Mapped[float | None] = mapped_column(Float)
    signal_to_noise: Mapped[float | None] = mapped_column(Float)
    quality_score: Mapped[float | None] = mapped_column(Float)
    is_accepted: Mapped[bool] = mapped_column(Boolean, default=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    run: Mapped[Run] = relationship(back_populates="peak_metrics")
    compound: Mapped[Compound] = relationship(back_populates="peak_metrics")


class ModelPrediction(TimestampMixin, Base):
    __tablename__ = "model_predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    model_name: Mapped[str] = mapped_column(String(128), nullable=False)
    model_version: Mapped[str] = mapped_column(String(64), nullable=False)
    compound_id: Mapped[int | None] = mapped_column(ForeignKey("compounds.id"), index=True)
    method_id: Mapped[int | None] = mapped_column(ForeignKey("methods.id"), index=True)
    input_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    output_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float)


class Recommendation(TimestampMixin, Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    compound_id: Mapped[int | None] = mapped_column(ForeignKey("compounds.id"), index=True)
    target_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    candidate_method_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    model_prediction_id: Mapped[int | None] = mapped_column(ForeignKey("model_predictions.id"))


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    actor: Mapped[str] = mapped_column(String(128), default="system")
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(128), nullable=False)
    entity_id: Mapped[str | None] = mapped_column(String(128))
    input_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    output_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
