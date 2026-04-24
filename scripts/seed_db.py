from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.db.init_db import init_db
from app.db.models import (
    Compound,
    CompoundStructure,
    Dataset,
    MSSetting,
    Method,
    MethodGradientStep,
    PeakMetric,
    Run,
)
from app.db.session import SessionLocal
from app.services.descriptors import DescriptorCalculator


def main() -> None:
    init_db()
    compounds = pd.read_csv("data/mock_compounds.csv")
    methods = pd.read_csv("data/mock_methods.csv")
    runs = pd.read_csv("data/mock_runs.csv")
    peaks = pd.read_csv("data/mock_peak_metrics.csv")
    calc = DescriptorCalculator()

    with SessionLocal() as db:
        dataset_by_source = {}
        for source in sorted(runs["dataset_source"].unique()):
            dataset = Dataset(
                name=f"{source} mock import",
                source_type=source,
                description="MVP mock seed data",
                license="Internal/mock data for development",
            )
            db.add(dataset)
            db.flush()
            dataset_by_source[source] = dataset

        compound_by_name = {}
        for row in compounds.to_dict("records"):
            compound = Compound(
                name=row["compound_name"],
                pubchem_cid=int(row["pubchem_cid"]),
                chembl_id=row.get("chembl_id"),
                metadata_json={"matrix": row.get("matrix")},
            )
            db.add(compound)
            db.flush()
            descriptors = calc.from_smiles(row["smiles"])
            canonical, inchikey = calc.canonicalize(row["smiles"])
            db.add(
                CompoundStructure(
                    compound_id=compound.id,
                    input_smiles=row["smiles"],
                    canonical_smiles=canonical,
                    inchikey=inchikey,
                    descriptors_json=descriptors,
                )
            )
            compound_by_name[row["compound_name"]] = compound

        method_by_name = {}
        for row in methods.to_dict("records"):
            method = Method(
                name=row["method_name"],
                column=row["column"],
                stationary_phase=row["stationary_phase"],
                mobile_phase_a=row["mobile_phase_a"],
                mobile_phase_b=row["mobile_phase_b"],
                ph=float(row["ph"]),
                temperature_c=float(row["temperature_c"]),
                flow_rate_ml_min=float(row["flow_rate_ml_min"]),
                injection_volume_ul=float(row["injection_volume_ul"]),
            )
            db.add(method)
            db.flush()
            db.add_all(
                [
                    MethodGradientStep(method_id=method.id, time_min=0, percent_b=float(row["initial_percent_b"])),
                    MethodGradientStep(
                        method_id=method.id,
                        time_min=float(row["runtime_min"]),
                        percent_b=float(row["final_percent_b"]),
                    ),
                ]
            )
            method_by_name[row["method_name"]] = method

        run_by_identifier = {}
        for row in runs.to_dict("records"):
            ms = MSSetting(
                ionization_mode=row["ionization_mode"],
                precursor_mz=float(row["precursor_mz"]),
            )
            db.add(ms)
            db.flush()
            run = Run(
                dataset_id=dataset_by_source[row["dataset_source"]].id,
                method_id=method_by_name[row["method_name"]].id,
                ms_settings_id=ms.id,
                run_identifier=row["run_identifier"],
                matrix=row["matrix"],
            )
            db.add(run)
            db.flush()
            run_by_identifier[row["run_identifier"]] = run

        for row in peaks.to_dict("records"):
            db.add(
                PeakMetric(
                    run_id=run_by_identifier[row["run_identifier"]].id,
                    compound_id=compound_by_name[row["compound_name"]].id,
                    retention_time_min=float(row["retention_time_min"]),
                    peak_area=float(row["peak_area"]),
                    asymmetry=float(row["asymmetry"]),
                    resolution=float(row["resolution"]),
                    signal_to_noise=float(row["signal_to_noise"]),
                    quality_score=float(row["quality_score"]),
                )
            )
        db.commit()
    print("Seeded mock LC-MS/MS database records.")


if __name__ == "__main__":
    main()
