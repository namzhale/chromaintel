from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

from app.adapters.pubchem import PubChemClient
from app.models.baseline import train_baseline_models
from app.schemas.method import CompoundInput, GradientStep, MethodInput, MSSettingsInput
from app.services.data_loader import load_dataset_browser_records, load_training_records
from app.services.descriptors import DescriptorCalculator, InvalidStructureError
from app.services.predictor import ForwardPredictor
from app.services.recommendation import RecommendationEngine


st.set_page_config(
    page_title="AI LC-MS/MS Method MVP",
    layout="wide",
    initial_sidebar_state="expanded",
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MASTER_DATASET_PATH = PROCESSED_DIR / "master_dataset.csv"
MODEL_MATRIX_PATH = PROCESSED_DIR / "model_matrix.csv"
REPORTS_DIR = PROJECT_ROOT / "reports"
FEATURE_IMPORTANCE_PATH = REPORTS_DIR / "feature_importance.csv"
NO_RUNTIME_FEATURE_IMPORTANCE_PATH = REPORTS_DIR / "feature_importance_no_runtime.csv"
TEST_PREDICTIONS_PATH = REPORTS_DIR / "test_predictions.csv"
SOURCE_METRICS_PATH = REPORTS_DIR / "source_metrics.csv"
EVALUATION_MATRIX_PATH = REPORTS_DIR / "evaluation_matrix.csv"
RUNTIME_ABLATION_PATH = REPORTS_DIR / "runtime_ablation_metrics.csv"
RUNTIME_ABLATION_PDF_PATH = REPORTS_DIR / "runtime_leakage_ablation_report.pdf"
TARGET_COVERAGE_PATH = REPORTS_DIR / "target_coverage_matrix.csv"
INVERSE_METRICS_PATH = REPORTS_DIR / "inverse_model_metrics.csv"
INVERSE_TOPK_PATH = REPORTS_DIR / "inverse_topk_evaluation.csv"
TRAINED_MODEL_PATH = PROCESSED_DIR / "models" / "trained_forward_bundle.joblib"
MOCK_TRAINING_RECORDS_PATH = PROJECT_ROOT / "data" / "mock_training_records.csv"
TEMPLATES_DIR = PROJECT_ROOT / "data" / "templates"
INTERNAL_TEMPLATE_PATH = TEMPLATES_DIR / "internal_lab_historical_runs_template.csv"
INTERNAL_DICTIONARY_PATH = TEMPLATES_DIR / "internal_lab_data_dictionary.md"


def _optional_import_training():
    try:
        from app.models.training import train_forward_models
    except Exception as exc:
        return None, exc
    return train_forward_models, None


def _optional_import_assembly():
    try:
        from scripts.assemble_dataset import assemble_dataset
    except Exception as exc:
        return None, exc
    return assemble_dataset, None


def _optional_import_internal_validation():
    try:
        from app.services.internal_validation import (
            preview_internal_lab_import,
            validate_internal_lab_frame,
            write_internal_templates,
        )
    except Exception as exc:
        return None, None, None, exc
    return preview_internal_lab_import, validate_internal_lab_frame, write_internal_templates, None


def _optional_import_public_preview():
    try:
        from app.services.public_import_preview import discover_processed_imports, preview_processed_import
    except Exception as exc:
        return None, None, exc
    return discover_processed_imports, preview_processed_import, None


def _read_csv(path: Path) -> pd.DataFrame | None:
    if not path.exists():
        return None
    try:
        return pd.read_csv(path)
    except Exception as exc:
        st.error(f"Could not read {path}: {exc}")
        return None


def _source_column(records: pd.DataFrame) -> str | None:
    for column in ("source_dataset", "dataset_source", "source"):
        if column in records.columns:
            return column
    return None


def _missingness_frame(records: pd.DataFrame) -> pd.DataFrame:
    missing = records.isna().sum().reset_index()
    missing.columns = ["field", "missing_count"]
    missing["missing_fraction"] = (
        missing["missing_count"] / max(len(records), 1)
    ).round(3)
    return missing.sort_values(["missing_count", "field"], ascending=[False, True])


def _metrics_frame(metrics: dict[str, dict[str, float]]) -> pd.DataFrame:
    if not metrics:
        return pd.DataFrame()
    return pd.DataFrame(metrics).T.reset_index(names="model").round(3)


def _render_training_artifacts() -> None:
    predictions = _read_csv(TEST_PREDICTIONS_PATH)
    source_metrics = _read_csv(SOURCE_METRICS_PATH)
    importance = _read_csv(FEATURE_IMPORTANCE_PATH)
    target_coverage = _read_csv(TARGET_COVERAGE_PATH)
    inverse_metrics = _read_csv(INVERSE_METRICS_PATH)
    inverse_topk = _read_csv(INVERSE_TOPK_PATH)

    if predictions is not None and not predictions.empty:
        st.subheader("Held-out RT validation")
        if "abs_rt_error_min" not in predictions and "rt_error_min" in predictions:
            predictions["abs_rt_error_min"] = predictions["rt_error_min"].abs()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Test rows", len(predictions))
        c2.metric("RT MAE", f"{predictions['abs_rt_error_min'].mean():.2f} min")
        c3.metric("RT RMSE", f"{(predictions['rt_error_min'].pow(2).mean() ** 0.5):.2f} min")
        c4.metric("AD flags", int(predictions["ad_flag"].sum()) if "ad_flag" in predictions else "n/a")
        scatter = px.scatter(
            predictions,
            x="rt_min",
            y="predicted_rt_min",
            color="source_dataset" if "source_dataset" in predictions else None,
            hover_data=[col for col in ["compound_name", "rt_error_min", "ad_reason"] if col in predictions],
            title="Predicted vs actual RT",
        )
        axis_min = float(min(predictions["rt_min"].min(), predictions["predicted_rt_min"].min()))
        axis_max = float(max(predictions["rt_min"].max(), predictions["predicted_rt_min"].max()))
        scatter.add_shape(type="line", x0=axis_min, x1=axis_max, y0=axis_min, y1=axis_max, line={"dash": "dash"})
        st.plotly_chart(scatter, use_container_width=True)
        st.plotly_chart(
            px.histogram(
                predictions,
                x="rt_error_min",
                color="source_dataset" if "source_dataset" in predictions else None,
                title="RT residuals",
            ),
            use_container_width=True,
        )
        worst = predictions.sort_values("abs_rt_error_min", ascending=False)
        st.dataframe(
            worst[[col for col in ["compound_name", "source_dataset", "rt_min", "predicted_rt_min", "rt_error_min", "abs_rt_error_min", "ad_flag", "ad_reason"] if col in worst]],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No held-out prediction artifact yet. Train the forward models to create reports/test_predictions.csv.")

    if source_metrics is not None and not source_metrics.empty:
        st.subheader("Source-wise errors")
        st.plotly_chart(px.bar(source_metrics, x="source_dataset", y="rt_mae", title="RT MAE by source"), use_container_width=True)
        st.dataframe(source_metrics.round(3), use_container_width=True, hide_index=True)

    if importance is not None and not importance.empty:
        st.subheader("Permutation importance / parameter significance")
        top_importance = importance.head(20)
        st.plotly_chart(
            px.bar(
                top_importance,
                x="importance_mean",
                y="feature",
                error_x="importance_std" if "importance_std" in top_importance else None,
                color="significance" if "significance" in top_importance else None,
                orientation="h",
                title="RT permutation importance",
            ),
            use_container_width=True,
        )
        display_cols = [
            col
            for col in ["feature", "feature_group", "importance_mean", "importance_std", "importance_z", "significance"]
            if col in importance
        ]
        st.dataframe(importance[display_cols].round(3), use_container_width=True, hide_index=True)
        st.caption("Permutation importance is computed on the held-out RT split; weak or negative values are unstable diagnostics on tiny test sets.")

    if target_coverage is not None and not target_coverage.empty:
        st.subheader("Peak target readiness")
        plot_frame = target_coverage.copy()
        if "coverage_fraction" in plot_frame:
            plot_frame["coverage_percent"] = plot_frame["coverage_fraction"].astype(float) * 100.0
            st.plotly_chart(
                px.bar(
                    plot_frame,
                    x="coverage_percent",
                    y="target",
                    color="readiness",
                    orientation="h",
                    title="Direct and proxy target coverage",
                    hover_data=[col for col in ["available_rows", "label_source", "recommended_action"] if col in plot_frame],
                ),
                use_container_width=True,
            )
        display_cols = [
            col
            for col in ["target", "available_rows", "coverage_fraction", "label_source", "readiness", "recommended_action"]
            if col in target_coverage
        ]
        st.dataframe(target_coverage[display_cols], use_container_width=True, hide_index=True)

    if inverse_metrics is not None and not inverse_metrics.empty:
        st.subheader("Inverse recommendation ML baselines")
        chart_frame = inverse_metrics.copy()
        metric_col = "pr_auc" if "pr_auc" in chart_frame else "roc_auc" if "roc_auc" in chart_frame else None
        if metric_col:
            st.plotly_chart(
                px.bar(
                    chart_frame.sort_values(metric_col, ascending=False),
                    x=metric_col,
                    y="model",
                    color="label_source" if "label_source" in chart_frame else None,
                    orientation="h",
                    title=f"Inverse model {metric_col.upper()}",
                ),
                use_container_width=True,
            )
        st.dataframe(inverse_metrics.round(4), use_container_width=True, hide_index=True)
        if inverse_topk is not None and not inverse_topk.empty:
            st.dataframe(inverse_topk.round(4), use_container_width=True, hide_index=True)
        st.caption("Inverse recommendation labels are currently synthetic/proxy labels derived from observed method suitability; internal accepted/failed assays are required for production-grade inverse validation.")


def _render_model_evaluation_artifacts() -> None:
    evaluation = _read_csv(EVALUATION_MATRIX_PATH)
    predictions = _read_csv(TEST_PREDICTIONS_PATH)
    source_metrics = _read_csv(SOURCE_METRICS_PATH)
    importance = _read_csv(FEATURE_IMPORTANCE_PATH)
    no_runtime_importance = _read_csv(NO_RUNTIME_FEATURE_IMPORTANCE_PATH)
    runtime_ablation = _read_csv(RUNTIME_ABLATION_PATH)

    if evaluation is not None and not evaluation.empty:
        st.subheader("Validation matrix")
        rt_eval = evaluation[evaluation["target"].eq("rt_min")].copy() if "target" in evaluation else evaluation.copy()
        display_cols = [
            col
            for col in [
                "validation_scope",
                "holdout_key",
                "model",
                "n_rows",
                "mae",
                "rmse",
                "r2",
                "spearman",
                "normalized_mae_runtime_pct",
            ]
            if col in rt_eval
        ]
        st.dataframe(rt_eval[display_cols].round(3), use_container_width=True, hide_index=True)
        if {"validation_scope", "model", "mae"}.issubset(rt_eval.columns):
            st.plotly_chart(
                px.bar(
                    rt_eval.sort_values("mae").head(40),
                    x="mae",
                    y="model",
                    color="validation_scope",
                    orientation="h",
                    title="RT MAE across validation scopes",
                    hover_data=[col for col in ["holdout_key", "rmse", "r2", "spearman"] if col in rt_eval],
                ),
                use_container_width=True,
            )

    if predictions is not None and not predictions.empty:
        st.subheader("Applicability domain flags")
        if "ad_flag" in predictions:
            ad_count = int(predictions["ad_flag"].sum())
            c1, c2, c3 = st.columns(3)
            c1.metric("Held-out rows", len(predictions))
            c2.metric("AD flagged rows", ad_count)
            c3.metric("AD flagged share", f"{ad_count / max(len(predictions), 1) * 100:.1f}%")
            if "ad_reason" in predictions:
                reasons = predictions["ad_reason"].value_counts(dropna=False).reset_index()
                reasons.columns = ["ad_reason", "rows"]
                st.dataframe(reasons.head(20), use_container_width=True, hide_index=True)
        if {"uncertainty_rt_min", "abs_rt_error_min"}.issubset(predictions.columns):
            st.plotly_chart(
                px.scatter(
                    predictions,
                    x="uncertainty_rt_min",
                    y="abs_rt_error_min",
                    color="source_dataset" if "source_dataset" in predictions else None,
                    title="RT error vs uncertainty proxy",
                ),
                use_container_width=True,
            )

    if source_metrics is not None and not source_metrics.empty:
        st.subheader("Source-wise transfer diagnostics")
        st.plotly_chart(
            px.bar(
                source_metrics.sort_values("rt_mae", ascending=False).head(30),
                x="rt_mae",
                y="source_dataset",
                orientation="h",
                title="Worst source-wise RT MAE",
            ),
            use_container_width=True,
        )

    if importance is not None and not importance.empty:
        st.subheader("Feature significance")
        st.dataframe(
            importance[[col for col in ["feature", "feature_group", "importance_mean", "importance_std", "significance"] if col in importance]].head(30).round(4),
            use_container_width=True,
            hide_index=True,
        )

    if no_runtime_importance is not None and not no_runtime_importance.empty:
        st.subheader("No-runtime feature significance")
        st.caption("This excludes `gradient_duration_min` and `total_runtime_min` to reduce runtime-proxy leakage.")
        st.plotly_chart(
            px.bar(
                no_runtime_importance.head(25),
                x="importance_mean",
                y="feature",
                color="feature_group" if "feature_group" in no_runtime_importance else None,
                orientation="h",
                title="RT permutation importance without duration/runtime features",
            ),
            use_container_width=True,
        )

    if runtime_ablation is not None and not runtime_ablation.empty:
        st.subheader("Runtime proxy ablation")
        st.dataframe(runtime_ablation.round(4), use_container_width=True, hide_index=True)
        if RUNTIME_ABLATION_PDF_PATH.exists():
            st.caption(f"PDF report: {RUNTIME_ABLATION_PDF_PATH}")


def _issue_frame(issues: list[Any]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "row": getattr(issue, "row", None),
                "column": getattr(issue, "column", None),
                "severity": getattr(issue, "severity", None),
                "message": getattr(issue, "message", None),
            }
            for issue in issues
        ]
    )


def default_method() -> MethodInput:
    return MethodInput(
        column="BEH C18 50x2.1 mm 1.7um",
        stationary_phase="reversed phase",
        mobile_phase_a="Water + 0.1% formic acid",
        mobile_phase_b="Acetonitrile + 0.1% formic acid",
        ph=3.2,
        temperature_c=40.0,
        flow_rate_ml_min=0.35,
        injection_volume_ul=2.0,
        gradient_steps=[
            GradientStep(time_min=0, percent_b=5),
            GradientStep(time_min=5, percent_b=95),
            GradientStep(time_min=5.8, percent_b=95),
        ],
    )


def method_form(prefix: str = "method") -> MethodInput:
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        column = st.selectbox(
            "Column",
            [
                "BEH C18 50x2.1 mm 1.7um",
                "CSH Phenyl-Hexyl 50x2.1 mm 1.7um",
                "HILIC Amide 100x2.1 mm 2.6um",
            ],
            key=f"{prefix}_column",
        )
        stationary = st.selectbox(
            "Stationary phase", ["reversed phase", "HILIC"], key=f"{prefix}_phase"
        )
        ph = st.number_input("pH", min_value=0.0, max_value=14.0, value=3.2, step=0.1, key=f"{prefix}_ph")
    with col_b:
        mobile_a = st.selectbox(
            "Mobile phase A",
            ["Water + 0.1% formic acid", "10 mM ammonium formate in water", "Water + 2 mM ammonium acetate"],
            key=f"{prefix}_a",
        )
        mobile_b = st.selectbox(
            "Mobile phase B",
            ["Acetonitrile + 0.1% formic acid", "Methanol + 0.1% formic acid", "Acetonitrile"],
            key=f"{prefix}_b",
        )
        temperature = st.number_input(
            "Temperature (C)", min_value=10.0, max_value=90.0, value=40.0, step=1.0, key=f"{prefix}_temp"
        )
    with col_c:
        flow = st.number_input(
            "Flow (mL/min)", min_value=0.05, max_value=2.0, value=0.35, step=0.05, key=f"{prefix}_flow"
        )
        injection = st.number_input(
            "Injection (uL)", min_value=0.0, max_value=50.0, value=2.0, step=0.5, key=f"{prefix}_inj"
        )
        runtime = st.number_input(
            "Gradient end (min)", min_value=1.0, max_value=30.0, value=5.0, step=0.5, key=f"{prefix}_runtime"
        )
    initial_b, final_b = st.slider(
        "%B range", min_value=0, max_value=100, value=(5, 95), step=1, key=f"{prefix}_b_range"
    )
    return MethodInput(
        column=column,
        stationary_phase=stationary,
        mobile_phase_a=mobile_a,
        mobile_phase_b=mobile_b,
        ph=ph,
        temperature_c=temperature,
        flow_rate_ml_min=flow,
        injection_volume_ul=injection,
        gradient_steps=[
            GradientStep(time_min=0, percent_b=float(initial_b)),
            GradientStep(time_min=float(runtime), percent_b=float(final_b)),
            GradientStep(time_min=float(runtime + 0.8), percent_b=float(final_b)),
        ],
    )


def compound_form(prefix: str = "compound") -> CompoundInput:
    col_a, col_b, col_c = st.columns([2, 3, 1])
    with col_a:
        name = st.text_input("Compound name", value="Caffeine", key=f"{prefix}_name")
    with col_b:
        smiles = st.text_input(
            "SMILES", value="Cn1cnc2c1c(=O)n(C)c(=O)n2C", key=f"{prefix}_smiles"
        )
    with col_c:
        cid = st.number_input("PubChem CID", min_value=0, value=2519, step=1, key=f"{prefix}_cid")
    return CompoundInput(name=name, smiles=smiles, pubchem_cid=int(cid) if cid else None)


def dashboard() -> None:
    st.title("AI LC-MS/MS Method Development")
    records = _load_master_or_mock()
    if records.empty:
        st.info("No dataset is available yet. Use Dataset assembly to build from the mock source.")
        return
    cols = st.columns(4)
    cols[0].metric("Records", len(records))
    cols[1].metric("Compounds", records["compound_name"].nunique() if "compound_name" in records.columns else "n/a")
    source_col = _source_column(records)
    rt_col = "rt_min" if "rt_min" in records.columns else "retention_time_min" if "retention_time_min" in records.columns else None
    quality_col = "quality_score" if "quality_score" in records.columns else None
    cols[2].metric("Sources", records[source_col].nunique() if source_col else "n/a")
    cols[3].metric("Median RT", f"{records[rt_col].median():.2f} min" if rt_col else "n/a")
    if rt_col:
        st.plotly_chart(
            px.scatter(
                records,
                x=rt_col,
                y=quality_col or rt_col,
                color=source_col,
                hover_data=[col for col in ["compound_name", "column_name", "column", "matrix"] if col in records.columns],
            ),
            use_container_width=True,
        )
    else:
        st.dataframe(records.head(25), use_container_width=True, hide_index=True)
    st.divider()
    _render_training_artifacts()


def dataset_assembly_page() -> None:
    st.title("Dataset Assembly")
    st.caption("Canonical source merge for METLIN SMRT, RepoRT, PubChem/ChEMBL enrichment, and internal lab templates.")
    st.caption(f"Master dataset path: {MASTER_DATASET_PATH}")

    build_disabled = not MOCK_TRAINING_RECORDS_PATH.exists()
    if st.button("Build from mock source", type="primary", disabled=build_disabled):
        assemble_dataset, import_error = _optional_import_assembly()
        if import_error:
            st.error(f"Dataset assembly function is unavailable: {import_error}")
        else:
            try:
                outputs = assemble_dataset(
                    source_path=MOCK_TRAINING_RECORDS_PATH,
                    output_dir=PROCESSED_DIR,
                    templates_dir=TEMPLATES_DIR,
                )
                st.success(
                    f"Built {outputs.master_rows} master rows and "
                    f"{outputs.model_matrix_rows} model rows."
                )
                st.json(
                    {
                        "source_path": str(outputs.source_path),
                        "master_path": str(outputs.master_path),
                        "model_matrix_path": str(outputs.model_matrix_path),
                        "template_paths": {
                            key: str(path) for key, path in outputs.template_paths.items()
                        },
                    }
                )
            except Exception as exc:
                st.error(f"Dataset assembly failed: {exc}")
    if build_disabled:
        st.warning(f"Mock source is not available at {MOCK_TRAINING_RECORDS_PATH}.")

    master = _read_csv(MASTER_DATASET_PATH)
    if master is not None:
        c1, c2, c3 = st.columns(3)
        c1.metric("Master rows", len(master))
        c2.metric("Compounds", master["compound_name"].nunique() if "compound_name" in master.columns else "n/a")
        source_col = _source_column(master)
        c3.metric("Sources", master[source_col].nunique() if source_col else "n/a")
        if source_col:
            st.subheader("Source distribution")
            source_counts = master[source_col].value_counts(dropna=False).reset_index()
            source_counts.columns = ["source", "rows"]
            st.plotly_chart(px.bar(source_counts, x="source", y="rows"), use_container_width=True)
            st.dataframe(source_counts, use_container_width=True, hide_index=True)
        st.subheader("Missingness")
        st.dataframe(_missingness_frame(master), use_container_width=True, hide_index=True)
        st.subheader("Example rows")
        st.dataframe(master.head(25), use_container_width=True, hide_index=True)
    else:
        st.info(
            "No processed master dataset yet. Build it from the mock source here, "
            "or run scripts/assemble_dataset.py from the project root."
        )

    st.divider()
    st.subheader("Processed public/literature import preview")
    discover_processed_imports, preview_processed_import, preview_error = _optional_import_public_preview()
    if preview_error:
        st.warning(f"Processed import preview is unavailable: {preview_error}")
    else:
        import_files = discover_processed_imports(PROCESSED_DIR)
        if not import_files:
            st.info("No processed external/literature CSVs found yet.")
        else:
            selected = st.selectbox(
                "Processed import file",
                import_files,
                format_func=lambda path: f"{path.name} ({path.stat().st_size / 1024 / 1024:.1f} MB)",
            )
            try:
                preview = preview_processed_import(selected)
            except Exception as exc:
                st.error(f"Could not preview {selected}: {exc}")
            else:
                c1, c2, c3 = st.columns(3)
                c1.metric("Rows", preview.row_count)
                c2.metric("Columns", preview.column_count)
                c3.metric("Sources", len(preview.source_counts) if preview.source_counts else "n/a")
                if preview.source_counts:
                    source_frame = pd.DataFrame(
                        [{"source": source, "rows": rows} for source, rows in preview.source_counts.items()]
                    )
                    st.plotly_chart(
                        px.bar(source_frame.head(25), x="source", y="rows", title="Source distribution"),
                        use_container_width=True,
                    )
                if preview.canonical_coverage:
                    coverage_frame = pd.DataFrame(
                        [
                            {"field": field, "coverage_percent": coverage * 100.0}
                            for field, coverage in preview.canonical_coverage.items()
                        ]
                    ).sort_values("coverage_percent")
                    st.plotly_chart(
                        px.bar(
                            coverage_frame,
                            x="coverage_percent",
                            y="field",
                            orientation="h",
                            title="Canonical field coverage",
                        ),
                        use_container_width=True,
                    )
                st.dataframe(pd.DataFrame(preview.missingness).head(30), use_container_width=True, hide_index=True)
                st.dataframe(preview.example_rows, use_container_width=True, hide_index=True)


def training_page() -> None:
    st.title("Training")
    matrix = _read_csv(MODEL_MATRIX_PATH)
    if matrix is None:
        st.warning("No model matrix found. Build the dataset first.")
        st.caption(f"Expected model matrix path: {MODEL_MATRIX_PATH}")
        return

    st.caption(f"Model matrix: {MODEL_MATRIX_PATH}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", len(matrix))
    c2.metric("Columns", len(matrix.columns))
    c3.metric("Usable RT rows", int(matrix["rt_min"].notna().sum()) if "rt_min" in matrix.columns else "n/a")
    c4.metric("Existing artifact", "yes" if TRAINED_MODEL_PATH.exists() else "no")

    with st.expander("Training configuration", expanded=True):
        st.json(
            {
                "trainer": "app.models.training.train_forward_models",
                "matrix_path": str(MODEL_MATRIX_PATH),
                "artifact_path": str(TRAINED_MODEL_PATH),
                "report_dir": str(REPORTS_DIR),
                "plots_dir": str(PROCESSED_DIR / "plots"),
            }
        )

    if st.button("Train forward models", type="primary"):
        train_forward_models, import_error = _optional_import_training()
        if import_error:
            st.error(f"Training function is unavailable: {import_error}")
        else:
            try:
                summary = train_forward_models(
                    matrix,
                    artifact_path=TRAINED_MODEL_PATH,
                    report_dir=REPORTS_DIR,
                    plots_dir=PROCESSED_DIR / "plots",
                )
            except Exception as exc:
                st.error(f"Training failed: {exc}")
            else:
                payload = asdict(summary)
                st.success("Training complete")
                s1, s2, s3, s4 = st.columns(4)
                s1.metric("Train rows", payload["n_train"])
                s2.metric("Validation rows", payload["n_validation"])
                s3.metric("Test rows", payload["n_test"])
                s4.metric("Feature columns", len(payload["feature_columns"]))
                st.caption(f"Artifact: {payload['artifact_path']}")
                st.caption(f"Report: {payload['report_path']}")
                st.subheader("RT metrics")
                st.dataframe(_metrics_frame(payload["rt_metrics"]), use_container_width=True, hide_index=True)
                st.subheader("Quality metrics")
                st.dataframe(_metrics_frame(payload["quality_metrics"]), use_container_width=True, hide_index=True)

    report_path = REPORTS_DIR / "model_training_summary.md"
    if report_path.exists():
        st.subheader("Training report")
        st.markdown(report_path.read_text(encoding="utf-8"))
    if FEATURE_IMPORTANCE_PATH.exists():
        st.subheader("Feature importance")
        importance = pd.read_csv(FEATURE_IMPORTANCE_PATH).head(20)
        st.plotly_chart(
            px.bar(importance, x="importance_mean", y="feature", orientation="h"),
            use_container_width=True,
        )
        st.dataframe(importance, use_container_width=True, hide_index=True)
    st.divider()
    _render_training_artifacts()


def compound_lookup() -> None:
    st.title("Compound Lookup / Structure Input")
    compound = compound_form("lookup")
    calc = DescriptorCalculator()
    if st.button("Calculate descriptors", type="primary"):
        try:
            descriptors = calc.from_smiles(compound.smiles or "")
            st.dataframe(
                pd.DataFrame(
                    [
                        {k: v for k, v in descriptors.items() if k not in {"morgan_fp"}}
                    ]
                ),
                use_container_width=True,
            )
        except InvalidStructureError as exc:
            st.error(str(exc))
    if st.button("Lookup PubChem"):
        try:
            client = PubChemClient()
            result = client.lookup_by_cid(compound.pubchem_cid) if compound.pubchem_cid else client.lookup_by_name(compound.name or "")
            st.json(result)
        except Exception as exc:
            st.warning(f"PubChem lookup unavailable: {exc}")


def forward_prediction() -> None:
    st.title("Forward Prediction")
    compound = compound_form("predict")
    method = method_form("predict_method")
    ms = MSSettingsInput(
        ionization_mode=st.selectbox("Ionization mode", ["positive", "negative", "both", "unknown"]),
        precursor_mz=st.number_input("Precursor m/z", min_value=0.0, value=195.1, step=0.1),
    )
    if st.button("Predict", type="primary"):
        result = ForwardPredictor().predict(compound.model_dump(exclude_none=True), method, ms)
        cols = st.columns(3)
        cols[0].metric("Predicted RT", f"{result['predicted_rt_min']:.2f} min")
        cols[1].metric("Quality score", f"{result['quality_score']:.2f}")
        cols[2].metric("Confidence", f"{result['confidence']:.2f}")
        if result.get("uncertainty_rt_min"):
            st.caption(f"RT uncertainty proxy: +/- {result['uncertainty_rt_min']:.2f} min")
        if result.get("out_of_domain"):
            st.warning("This condition set is outside the current demo model domain.")
        st.write(result["explanation"])
        risk_frame = pd.DataFrame(
            [{"risk": key, "value": value} for key, value in result["risks"].items()]
        )
        st.plotly_chart(px.bar(risk_frame, x="risk", y="value", range_y=[0, 1]), use_container_width=True)
        st.json(result["feature_summary"])


def method_recommendation() -> None:
    st.title("Method Recommendation")
    compound = compound_form("rec")
    cols = st.columns(3)
    target_rt = cols[0].number_input("Target RT (min)", min_value=0.5, value=4.5, step=0.25)
    target_quality = cols[1].number_input("Target quality", min_value=0.0, max_value=1.0, value=0.82, step=0.01)
    top_n = cols[2].number_input("Top N", min_value=1, max_value=10, value=5, step=1)
    allowed_columns = st.multiselect(
        "Available columns",
        [
            "BEH C18 50x2.1 mm 1.7um",
            "CSH Phenyl-Hexyl 50x2.1 mm 1.7um",
            "HILIC Amide 100x2.1 mm 2.6um",
        ],
        default=["BEH C18 50x2.1 mm 1.7um", "CSH Phenyl-Hexyl 50x2.1 mm 1.7um"],
    )
    ms = MSSettingsInput(ionization_mode=st.selectbox("Recommendation ionization", ["positive", "negative", "unknown"]))
    if st.button("Generate candidates", type="primary"):
        engine = RecommendationEngine(ForwardPredictor())
        if engine.inverse_ranker is not None:
            st.info("Inverse ML reranker enabled. Scores are proxy-trained until internal accepted/failed assay labels are imported.")
        recs = engine.recommend(
            compound.model_dump(exclude_none=True),
            target_rt_min=target_rt,
            top_n=int(top_n),
            allowed_columns=allowed_columns,
            ms_settings=ms,
        )
        for rec in recs:
            if rec.predicted_quality_score < target_quality:
                continue
            with st.container(border=True):
                st.subheader(f"Rank {rec.rank}: {rec.method.column}")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Predicted RT", f"{rec.predicted_rt_min:.2f} min")
                c2.metric("Quality", f"{rec.predicted_quality_score:.2f}")
                c3.metric("Runtime", f"{rec.estimated_runtime_min:.1f} min")
                c4.metric("Confidence", f"{rec.confidence:.2f}")
                if rec.inverse_model_enabled:
                    st.metric("Inverse ML score", f"{rec.inverse_model_score:.2f}" if rec.inverse_model_score is not None else "n/a")
                st.write(f"Score: {rec.score:.3f}. {rec.explanation}")


def dataset_browser() -> None:
    st.title("Dataset Browser")
    records = _load_master_or_mock()
    if records.empty:
        st.info("No dataset is available yet. Use Dataset assembly to build from the mock source.")
        return
    compound_col = "compound_name"
    column_col = "column_name" if "column_name" in records.columns else "column" if "column" in records.columns else None
    ion_col = "ion_mode" if "ion_mode" in records.columns else "ionization_mode" if "ionization_mode" in records.columns else None
    col_a, col_b, col_c, col_d = st.columns(4)
    compound = col_a.multiselect(
        "Compound",
        sorted(records[compound_col].dropna().unique()) if compound_col in records.columns else [],
    )
    column = col_b.multiselect(
        "Column",
        sorted(records[column_col].dropna().unique()) if column_col else [],
    )
    matrix = col_c.multiselect(
        "Matrix",
        sorted(records["matrix"].dropna().unique()) if "matrix" in records.columns else [],
    )
    ion = col_d.multiselect(
        "Ionization",
        sorted(records[ion_col].dropna().unique()) if ion_col else [],
    )
    filtered = records.copy()
    if compound and compound_col in filtered.columns:
        filtered = filtered[filtered[compound_col].isin(compound)]
    if column and column_col:
        filtered = filtered[filtered[column_col].isin(column)]
    if matrix and "matrix" in filtered.columns:
        filtered = filtered[filtered["matrix"].isin(matrix)]
    if ion and ion_col:
        filtered = filtered[filtered[ion_col].isin(ion)]
    st.dataframe(filtered, use_container_width=True, hide_index=True)


def model_evaluation() -> None:
    st.title("Model Evaluation")
    records = load_training_records()
    if st.button("Train / evaluate baseline", type="primary"):
        result = train_baseline_models(records)
        cols = st.columns(4)
        cols[0].metric("RT MAE", f"{result.rt_mae:.2f}")
        cols[1].metric("RT RMSE", f"{result.rt_rmse:.2f}")
        cols[2].metric("Quality MAE", f"{result.quality_mae:.2f}")
        cols[3].metric("Split", f"{result.n_train}/{result.n_validation}")
        st.caption(f"Artifact: {result.artifact_path}")
    st.plotly_chart(
        px.histogram(records, x="retention_time_min", color="dataset_source", nbins=12),
        use_container_width=True,
    )
    st.divider()
    _render_model_evaluation_artifacts()


def admin_import() -> None:
    st.title("Admin / Import")
    (
        preview_internal_lab_import,
        validate_internal_lab_frame,
        write_internal_templates,
        import_error,
    ) = _optional_import_internal_validation()
    uploaded = st.file_uploader("Import normalized CSV", type=["csv"])
    if uploaded:
        try:
            frame = pd.read_csv(uploaded)
        except Exception as exc:
            st.error(f"Could not read uploaded CSV: {exc}")
            return
        st.dataframe(frame.head(50), use_container_width=True)
        if import_error:
            st.error(f"Internal validation is unavailable: {import_error}")
        else:
            preview = preview_internal_lab_import(frame)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Rows", preview.row_count)
            c2.metric("Valid rows", preview.valid_row_count)
            c3.metric("Invalid rows", preview.invalid_row_count)
            c4.metric("Duplicate run IDs", preview.duplicate_run_id_count)
            missingness_rows = [
                {"column": column, "missing_values": count}
                for column, count in preview.missingness_by_column.items()
                if count
            ]
            if missingness_rows:
                missingness = pd.DataFrame(missingness_rows).sort_values("missing_values", ascending=False)
                st.subheader("Missingness summary")
                st.dataframe(missingness, use_container_width=True, hide_index=True)
            result = validate_internal_lab_frame(frame)
            if result.is_valid:
                st.success("Import validation passed.")
            else:
                st.error("Import validation found issues.")
            issues = _issue_frame(result.issues)
            if not issues.empty:
                st.dataframe(issues, use_container_width=True, hide_index=True)
    st.subheader("Expected internal lab template")
    st.caption(f"Template CSV: {INTERNAL_TEMPLATE_PATH}")
    st.caption(f"Data dictionary: {INTERNAL_DICTIONARY_PATH}")
    if st.button("Write internal templates", disabled=write_internal_templates is None):
        try:
            st.json(write_internal_templates(TEMPLATES_DIR))
        except Exception as exc:
            st.error(f"Could not write internal templates: {exc}")
    if import_error:
        st.warning(f"Template writer is unavailable: {import_error}")
    elif INTERNAL_TEMPLATE_PATH.exists() or INTERNAL_DICTIONARY_PATH.exists():
        st.info("Template files are already available at the paths above.")
    st.code(
        "run_id, compound_name, smiles, matrix, sample_prep, column_name, "
        "mobile_phase_a, mobile_phase_b, ph, gradient_profile, total_runtime_min, "
        "flow_ml_min, ion_mode, rt_min, sn_ratio, resolution, success_flag"
    )


def _load_master_or_mock() -> pd.DataFrame:
    master = _read_csv(MASTER_DATASET_PATH)
    if master is not None:
        return master
    try:
        return load_dataset_browser_records()
    except Exception as exc:
        st.warning(f"Could not load mock dataset: {exc}")
        return pd.DataFrame()


PAGES = {
    "Dashboard": dashboard,
    "Dataset assembly": dataset_assembly_page,
    "Training": training_page,
    "Compound lookup / structure input": compound_lookup,
    "Forward prediction": forward_prediction,
    "Method recommendation": method_recommendation,
    "Dataset browser": dataset_browser,
    "Model evaluation": model_evaluation,
    "Admin / import": admin_import,
}


page = st.sidebar.radio("Page", list(PAGES))
PAGES[page]()
