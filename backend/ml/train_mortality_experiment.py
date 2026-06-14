"""Offline experiment registry for mortality risk models (train/serving separation)."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error


def main() -> None:
    artifacts_dir = Path(__file__).resolve().parent / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # Synthetic annual panel for reproducible offline evaluation.
    years = np.array([2016, 2017, 2018, 2019, 2020], dtype=float)
    features = np.column_stack([years, years**2])
    targets = np.array([6.2, 6.8, 7.1, 7.8, 8.4])

    model = Ridge(alpha=1.0, random_state=42)
    model.fit(features[:-1], targets[:-1])
    holdout_prediction = float(model.predict(features[-1:])[0])
    mae = float(mean_absolute_error([targets[-1]], [holdout_prediction]))

    metadata = {
        "model_name": "ridge-mortality-panel-v1.0.0",
        "trained_at": datetime.now(tz=UTC).isoformat(),
        "metrics": {"holdout_mae": mae},
        "features": ["year", "year_squared"],
        "notes": (
            "Offline scaffold for CRISP-ML promotion workflow. "
            "Serving continues to use rule-based mortality-relative scoring."
        ),
    }
    metadata_path = artifacts_dir / "ridge-mortality-panel-v1.0.0.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Wrote experiment metadata to {metadata_path}")


if __name__ == "__main__":
    main()
