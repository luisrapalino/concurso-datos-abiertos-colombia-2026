"""Temporal cross-validation for mortality risk models."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error

FEATURE_NAMES = ("observed_mortality_rate", "national_median", "mortality_ratio")


def build_synthetic_panel() -> tuple[np.ndarray, np.ndarray, list[str]]:
    baselines = np.linspace(3.0, 9.0, 12)
    ratios = np.linspace(0.6, 2.4, 16)
    features: list[list[float]] = []
    targets: list[float] = []
    periods: list[str] = []

    for baseline in baselines:
        for ratio in ratios:
            observed = baseline * ratio
            score = max(0.0, min(100.0, 50.0 + (ratio - 1.0) * 50.0))
            features.append([observed, baseline, ratio])
            targets.append(score)
            periods.append(f"synthetic-{baseline:.1f}-{ratio:.2f}")

    return np.array(features, dtype=float), np.array(targets, dtype=float), periods


def evaluate_temporal_holdout() -> dict[str, object]:
    features, targets, _periods = build_synthetic_panel()
    split_index = int(len(features) * 0.8)
    train_x, test_x = features[:split_index], features[split_index:]
    train_y, test_y = targets[:split_index], targets[split_index:]

    model = Ridge(alpha=1.0, random_state=42)
    model.fit(train_x, train_y)
    predictions = model.predict(test_x)
    mae = float(mean_absolute_error(test_y, predictions))

    return {
        "evaluated_at": datetime.now(tz=UTC).isoformat(),
        "strategy": "80/20 holdout on synthetic aligned panel",
        "features": list(FEATURE_NAMES),
        "metrics": {
            "holdout_mae": round(mae, 4),
            "holdout_samples": int(len(test_y)),
        },
        "notes": (
            "Replace synthetic panel with curated PostgreSQL periods for institutional evaluation."
        ),
    }


def main() -> None:
    report = evaluate_temporal_holdout()
    output_dir = Path(__file__).resolve().parent / "artifacts"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "temporal_evaluation.json"
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
