from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.models.baseline import train_baseline_models
from app.services.data_loader import load_training_records


def main() -> None:
    records = load_training_records()
    result = train_baseline_models(records)
    print(
        "Trained baseline models: "
        f"RT MAE={result.rt_mae:.3f}, RT RMSE={result.rt_rmse:.3f}, "
        f"quality MAE={result.quality_mae:.3f}, "
        f"train={result.n_train}, validation={result.n_validation}, "
        f"artifact={result.artifact_path}"
    )


if __name__ == "__main__":
    main()
