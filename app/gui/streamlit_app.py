from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from app.adapters.pubchem import PubChemClient
from app.models.baseline import train_baseline_models
from app.models.training import train_forward_models
from app.schemas.method import CompoundInput, GradientStep, MethodInput, MSSettingsInput
from app.services.dataset_assembly import assemble_master_dataset, normalize_source_frame
from app.services.data_loader import load_dataset_browser_records, load_training_records
from app.services.descriptors import DescriptorCalculator, InvalidStructureError
from app.services.feature_engineering import build_model_matrix
from app.services.internal_validation import validate_internal_lab_frame, write_internal_templates
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
    cols = st.columns(4)
    cols[0].metric("Records", len(records))
    cols[1].metric("Compounds", records["compound_name"].nunique())
    source_col = "source_dataset" if "source_dataset" in records.columns else "dataset_source"
    rt_col = "rt_min" if "rt_min" in records.columns else "retention_time_min"
    quality_col = "quality_score" if "quality_score" in records.columns else None
    cols[2].metric("Sources", records[source_col].nunique())
    cols[3].metric("Median RT", f"{records[rt_col].median():.2f} min")
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


def dataset_assembly_page() -> None:
    st.title("Dataset Assembly")
    st.caption("Canonical source merge for METLIN SMRT, RepoRT, PubChem/ChEMBL enrichment, and internal lab templates.")
    if st.button("Build from mock source", type="primary"):
        raw = pd.read_csv(PROJECT_ROOT / "data" / "mock_training_records.csv")
        normalized = normalize_source_frame(raw, "mock_training_records")
        master = assemble_master_dataset([normalized])
        matrix = build_model_matrix(master)
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        master.to_csv(MASTER_DATASET_PATH, index=False)
        matrix.to_csv(MODEL_MATRIX_PATH, index=False)
        outputs = write_internal_templates(PROJECT_ROOT / "data" / "templates")
        st.success(f"Built {len(master)} master rows and {len(matrix)} model rows.")
        st.json(outputs)

    if MASTER_DATASET_PATH.exists():
        master = pd.read_csv(MASTER_DATASET_PATH)
        c1, c2, c3 = st.columns(3)
        c1.metric("Master rows", len(master))
        c2.metric("Compounds", master["compound_name"].nunique())
        c3.metric("Sources", master["source_dataset"].nunique())
        st.subheader("Source distribution")
        st.plotly_chart(px.histogram(master, x="source_dataset"), use_container_width=True)
        st.subheader("Missingness")
        missing = master.isna().mean().sort_values(ascending=False).reset_index()
        missing.columns = ["field", "missing_fraction"]
        st.dataframe(missing, use_container_width=True, hide_index=True)
        st.subheader("Example rows")
        st.dataframe(master.head(25), use_container_width=True, hide_index=True)
    else:
        st.info("No processed master dataset yet. Build it from mock source or run scripts/assemble_dataset.py.")


def training_page() -> None:
    st.title("Training")
    if not MODEL_MATRIX_PATH.exists():
        st.warning("No model matrix found. Build the dataset first.")
        return
    matrix = pd.read_csv(MODEL_MATRIX_PATH)
    st.caption(f"Model matrix: {MODEL_MATRIX_PATH}")
    st.metric("Rows", len(matrix))
    st.metric("Columns", len(matrix.columns))
    if st.button("Train forward models", type="primary"):
        summary = train_forward_models(matrix)
        st.success("Training complete")
        st.json(summary.__dict__)

    report_path = REPORTS_DIR / "model_training_summary.md"
    if report_path.exists():
        st.subheader("Training report")
        st.markdown(report_path.read_text(encoding="utf-8"))
    importance_path = REPORTS_DIR / "feature_importance.csv"
    if importance_path.exists():
        st.subheader("Feature importance")
        importance = pd.read_csv(importance_path).head(20)
        st.plotly_chart(
            px.bar(importance, x="importance_mean", y="feature", orientation="h"),
            use_container_width=True,
        )


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
                st.write(f"Score: {rec.score:.3f}. {rec.explanation}")


def dataset_browser() -> None:
    st.title("Dataset Browser")
    records = _load_master_or_mock()
    compound_col = "compound_name"
    column_col = "column_name" if "column_name" in records.columns else "column"
    source_col = "source_dataset" if "source_dataset" in records.columns else "dataset_source"
    ion_col = "ion_mode" if "ion_mode" in records.columns else "ionization_mode"
    col_a, col_b, col_c, col_d = st.columns(4)
    compound = col_a.multiselect("Compound", sorted(records[compound_col].dropna().unique()))
    column = col_b.multiselect("Column", sorted(records[column_col].dropna().unique()))
    matrix = col_c.multiselect("Matrix", sorted(records["matrix"].dropna().unique()))
    ion = col_d.multiselect("Ionization", sorted(records[ion_col].dropna().unique()))
    filtered = records.copy()
    if compound:
        filtered = filtered[filtered[compound_col].isin(compound)]
    if column:
        filtered = filtered[filtered[column_col].isin(column)]
    if matrix:
        filtered = filtered[filtered["matrix"].isin(matrix)]
    if ion:
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


def admin_import() -> None:
    st.title("Admin / Import")
    uploaded = st.file_uploader("Import normalized CSV", type=["csv"])
    if uploaded:
        frame = pd.read_csv(uploaded)
        st.dataframe(frame.head(50), use_container_width=True)
        result = validate_internal_lab_frame(frame)
        if result.is_valid:
            st.success("Import validation passed.")
        else:
            st.error("Import validation found issues.")
            st.dataframe(pd.DataFrame([issue.__dict__ for issue in result.issues]), use_container_width=True)
    st.subheader("Expected internal lab template")
    if st.button("Write internal templates"):
        st.json(write_internal_templates(PROJECT_ROOT / "data" / "templates"))
    st.code(
        "compound_name, smiles, matrix, column, mobile_phase_a, mobile_phase_b, "
        "ph, temperature_c, flow_rate_ml_min, ionization_mode, retention_time_min, quality_score"
    )


def _load_master_or_mock() -> pd.DataFrame:
    if MASTER_DATASET_PATH.exists():
        return pd.read_csv(MASTER_DATASET_PATH)
    return load_dataset_browser_records()


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
