"""initial LC-MS/MS MVP schema

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-04-24
"""

from alembic import op
import sqlalchemy as sa


revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "compounds",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("pubchem_cid", sa.Integer()),
        sa.Column("chembl_id", sa.String(length=64)),
        sa.Column("formula", sa.String(length=128)),
        sa.Column("monoisotopic_mass", sa.Float()),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_compounds_name", "compounds", ["name"])
    op.create_index("ix_compounds_pubchem_cid", "compounds", ["pubchem_cid"])
    op.create_index("ix_compounds_chembl_id", "compounds", ["chembl_id"])

    op.create_table(
        "compound_structures",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("compound_id", sa.Integer(), sa.ForeignKey("compounds.id"), nullable=False),
        sa.Column("input_smiles", sa.Text(), nullable=False),
        sa.Column("canonical_smiles", sa.Text(), nullable=False),
        sa.Column("inchikey", sa.String(length=64)),
        sa.Column("descriptors_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("compound_id", "canonical_smiles"),
    )
    op.create_index("ix_compound_structures_compound_id", "compound_structures", ["compound_id"])
    op.create_index("ix_compound_structures_inchikey", "compound_structures", ["inchikey"])

    op.create_table(
        "datasets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("source_type", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("license", sa.String(length=255)),
        sa.Column("import_status", sa.String(length=64), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_datasets_source_type", "datasets", ["source_type"])

    op.create_table(
        "methods",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("stationary_phase", sa.String(length=255), nullable=False),
        sa.Column("column", sa.String(length=255), nullable=False),
        sa.Column("mobile_phase_a", sa.String(length=255), nullable=False),
        sa.Column("mobile_phase_b", sa.String(length=255), nullable=False),
        sa.Column("ph", sa.Float()),
        sa.Column("temperature_c", sa.Float()),
        sa.Column("flow_rate_ml_min", sa.Float()),
        sa.Column("injection_volume_ul", sa.Float()),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "method_gradient_steps",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("method_id", sa.Integer(), sa.ForeignKey("methods.id"), nullable=False),
        sa.Column("time_min", sa.Float(), nullable=False),
        sa.Column("percent_b", sa.Float(), nullable=False),
    )
    op.create_index("ix_method_gradient_steps_method_id", "method_gradient_steps", ["method_id"])

    op.create_table(
        "ms_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ionization_mode", sa.String(length=32), nullable=False),
        sa.Column("precursor_mz", sa.Float()),
        sa.Column("transitions_json", sa.JSON(), nullable=False),
        sa.Column("source_parameters_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("dataset_id", sa.Integer(), sa.ForeignKey("datasets.id"), nullable=False),
        sa.Column("method_id", sa.Integer(), sa.ForeignKey("methods.id"), nullable=False),
        sa.Column("ms_settings_id", sa.Integer(), sa.ForeignKey("ms_settings.id")),
        sa.Column("run_identifier", sa.String(length=255), nullable=False),
        sa.Column("matrix", sa.String(length=128)),
        sa.Column("analyst", sa.String(length=128)),
        sa.Column("acquired_at", sa.DateTime(timezone=True)),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_runs_dataset_id", "runs", ["dataset_id"])
    op.create_index("ix_runs_method_id", "runs", ["method_id"])
    op.create_index("ix_runs_ms_settings_id", "runs", ["ms_settings_id"])
    op.create_index("ix_runs_matrix", "runs", ["matrix"])

    op.create_table(
        "peak_metrics",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("run_id", sa.Integer(), sa.ForeignKey("runs.id"), nullable=False),
        sa.Column("compound_id", sa.Integer(), sa.ForeignKey("compounds.id"), nullable=False),
        sa.Column("retention_time_min", sa.Float(), nullable=False),
        sa.Column("peak_area", sa.Float()),
        sa.Column("peak_height", sa.Float()),
        sa.Column("asymmetry", sa.Float()),
        sa.Column("resolution", sa.Float()),
        sa.Column("signal_to_noise", sa.Float()),
        sa.Column("quality_score", sa.Float()),
        sa.Column("is_accepted", sa.Boolean(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_peak_metrics_run_id", "peak_metrics", ["run_id"])
    op.create_index("ix_peak_metrics_compound_id", "peak_metrics", ["compound_id"])

    op.create_table(
        "model_predictions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("model_name", sa.String(length=128), nullable=False),
        sa.Column("model_version", sa.String(length=64), nullable=False),
        sa.Column("compound_id", sa.Integer(), sa.ForeignKey("compounds.id")),
        sa.Column("method_id", sa.Integer(), sa.ForeignKey("methods.id")),
        sa.Column("input_json", sa.JSON(), nullable=False),
        sa.Column("output_json", sa.JSON(), nullable=False),
        sa.Column("confidence", sa.Float()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_model_predictions_compound_id", "model_predictions", ["compound_id"])
    op.create_index("ix_model_predictions_method_id", "model_predictions", ["method_id"])

    op.create_table(
        "recommendations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("compound_id", sa.Integer(), sa.ForeignKey("compounds.id")),
        sa.Column("target_json", sa.JSON(), nullable=False),
        sa.Column("candidate_method_json", sa.JSON(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("model_prediction_id", sa.Integer(), sa.ForeignKey("model_predictions.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_recommendations_compound_id", "recommendations", ["compound_id"])

    op.create_table(
        "audit_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("actor", sa.String(length=128), nullable=False),
        sa.Column("action", sa.String(length=128), nullable=False),
        sa.Column("entity_type", sa.String(length=128), nullable=False),
        sa.Column("entity_id", sa.String(length=128)),
        sa.Column("input_json", sa.JSON(), nullable=False),
        sa.Column("output_json", sa.JSON(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("audit_log")
    op.drop_index("ix_recommendations_compound_id", table_name="recommendations")
    op.drop_table("recommendations")
    op.drop_index("ix_model_predictions_method_id", table_name="model_predictions")
    op.drop_index("ix_model_predictions_compound_id", table_name="model_predictions")
    op.drop_table("model_predictions")
    op.drop_index("ix_peak_metrics_compound_id", table_name="peak_metrics")
    op.drop_index("ix_peak_metrics_run_id", table_name="peak_metrics")
    op.drop_table("peak_metrics")
    op.drop_index("ix_runs_matrix", table_name="runs")
    op.drop_index("ix_runs_ms_settings_id", table_name="runs")
    op.drop_index("ix_runs_method_id", table_name="runs")
    op.drop_index("ix_runs_dataset_id", table_name="runs")
    op.drop_table("runs")
    op.drop_table("ms_settings")
    op.drop_index("ix_method_gradient_steps_method_id", table_name="method_gradient_steps")
    op.drop_table("method_gradient_steps")
    op.drop_table("methods")
    op.drop_index("ix_datasets_source_type", table_name="datasets")
    op.drop_table("datasets")
    op.drop_index("ix_compound_structures_inchikey", table_name="compound_structures")
    op.drop_index("ix_compound_structures_compound_id", table_name="compound_structures")
    op.drop_table("compound_structures")
    op.drop_index("ix_compounds_chembl_id", table_name="compounds")
    op.drop_index("ix_compounds_pubchem_cid", table_name="compounds")
    op.drop_index("ix_compounds_name", table_name="compounds")
    op.drop_table("compounds")
