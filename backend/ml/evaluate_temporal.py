"""Temporal cross-validation for mortality risk models."""

from __future__ import annotations

import argparse
import json
import os
import sys
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


def evaluate_holdout(
    features: np.ndarray,
    targets: np.ndarray,
    *,
    strategy: str,
    notes: str,
) -> dict[str, object]:
    split_index = max(1, int(len(features) * 0.8))
    if split_index >= len(features):
        split_index = len(features) - 1

    train_x, test_x = features[:split_index], features[split_index:]
    train_y, test_y = targets[:split_index], targets[split_index:]

    model = Ridge(alpha=1.0, random_state=42)
    model.fit(train_x, train_y)
    predictions = model.predict(test_x)
    mae = float(mean_absolute_error(test_y, predictions))

    return {
        "evaluated_at": datetime.now(tz=UTC).isoformat(),
        "strategy": strategy,
        "features": list(FEATURE_NAMES),
        "metrics": {
            "holdout_mae": round(mae, 4),
            "holdout_samples": int(len(test_y)),
            "train_samples": int(len(train_y)),
        },
        "notes": notes,
    }


def evaluate_temporal_holdout_synthetic() -> dict[str, object]:
    features, targets, _periods = build_synthetic_panel()
    return evaluate_holdout(
        features,
        targets,
        strategy="80/20 holdout on synthetic aligned panel",
        notes="Baseline reproducible evaluation without database dependency.",
    )


def evaluate_temporal_holdout_from_db(database_url: str) -> dict[str, object]:
    from train_mortality_experiment import build_training_panel_from_db

    features, targets = build_training_panel_from_db(database_url)
    return evaluate_holdout(
        features,
        targets,
        strategy="80/20 holdout on curated PostgreSQL panel",
        notes="Institutional evaluation using ingested mortality observations.",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate territorial risk model temporally")
    parser.add_argument(
        "--from-db",
        action="store_true",
        help="Evaluate using curated PostgreSQL observations",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "artifacts" / "temporal_evaluation.json",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    ml_dir = Path(__file__).resolve().parent
    src_dir = ml_dir.parent / "src"
    for path in (str(src_dir), str(ml_dir)):
        if path not in sys.path:
            sys.path.insert(0, path)

    args = build_parser().parse_args(argv)
    if args.from_db:
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            print("DATABASE_URL is required when using --from-db.", file=sys.stderr)
            return 1
        report = evaluate_temporal_holdout_from_db(database_url)
    else:
        report = evaluate_temporal_holdout_synthetic()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
