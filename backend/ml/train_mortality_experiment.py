"""Offline training and artifact registration for territorial risk models."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import joblib
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error

DEFAULT_MODEL_VERSION = "ridge-mortality-risk-v1.0.0"
FEATURE_NAMES = ("observed_mortality_rate", "national_median", "mortality_ratio")


def build_training_panel() -> tuple[np.ndarray, np.ndarray]:
    """Build a reproducible synthetic panel aligned with rule-based scoring."""
    baselines = np.linspace(3.0, 9.0, 12)
    ratios = np.linspace(0.6, 2.4, 16)
    features: list[list[float]] = []
    targets: list[float] = []

    for baseline in baselines:
        for ratio in ratios:
            observed = baseline * ratio
            score = max(0.0, min(100.0, 50.0 + (ratio - 1.0) * 50.0))
            features.append([observed, baseline, ratio])
            targets.append(score)

    return np.array(features, dtype=float), np.array(targets, dtype=float)


def build_training_panel_from_db(database_url: str) -> tuple[np.ndarray, np.ndarray]:
    from sqlalchemy import func, select
    from sqlalchemy.orm import Session

    from infrastructure.persistence.database import dispose_engine, init_engine
    from modules.epidemiological_surveillance.infrastructure.persistence.orm_models import (
        HealthIndicatorObservationRow,
    )
    from modules.territorial_risk.domain.risk_score import GENERAL_MORTALITY_DEFINITION_ID

    init_engine(database_url)
    features: list[list[float]] = []
    targets: list[float] = []

    from infrastructure.persistence.database import get_engine

    with Session(get_engine()) as session:
        periods = list(
            session.scalars(
                select(HealthIndicatorObservationRow.period)
                .where(HealthIndicatorObservationRow.definition_id == GENERAL_MORTALITY_DEFINITION_ID)
                .distinct(),
            ).all(),
        )
        for period in periods:
            median = session.scalar(
                select(
                    func.percentile_cont(0.5).within_group(HealthIndicatorObservationRow.value),
                ).where(
                    HealthIndicatorObservationRow.definition_id == GENERAL_MORTALITY_DEFINITION_ID,
                    HealthIndicatorObservationRow.period == period,
                ),
            )
            if median is None or Decimal(median) <= 0:
                continue
            baseline = float(median)
            rows = session.scalars(
                select(HealthIndicatorObservationRow.value).where(
                    HealthIndicatorObservationRow.definition_id == GENERAL_MORTALITY_DEFINITION_ID,
                    HealthIndicatorObservationRow.period == period,
                ),
            ).all()
            for value in rows:
                observed = float(value)
                ratio = observed / baseline
                score = max(0.0, min(100.0, 50.0 + (ratio - 1.0) * 50.0))
                features.append([observed, baseline, ratio])
                targets.append(score)

    dispose_engine()
    if not features:
        msg = "No curated observations available to train from database."
        raise RuntimeError(msg)
    return np.array(features, dtype=float), np.array(targets, dtype=float)


def train_and_register(
    *,
    artifacts_dir: Path,
    model_version: str = DEFAULT_MODEL_VERSION,
    from_db: bool = False,
    database_url: str | None = None,
) -> Path:
    if from_db:
        if not database_url:
            msg = "DATABASE_URL is required when using --from-db."
            raise ValueError(msg)
        features, targets = build_training_panel_from_db(database_url)
        dataset_note = "curated PostgreSQL observations"
    else:
        features, targets = build_training_panel()
        dataset_note = "reproducible synthetic panel aligned with rule-based scoring"

    model = Ridge(alpha=1.0, random_state=42)
    model.fit(features, targets)
    predictions = model.predict(features)
    mae = float(mean_absolute_error(targets, predictions))

    artifacts_dir.mkdir(parents=True, exist_ok=True)
    joblib_path = artifacts_dir / f"{model_version}.joblib"
    metadata_path = artifacts_dir / f"{model_version}.json"

    joblib.dump(
        {
            "model": model,
            "background": features[: min(len(features), 100)],
            "feature_names": list(FEATURE_NAMES),
        },
        joblib_path,
    )

    metadata = {
        "model_version": model_version,
        "model_name": model_version,
        "trained_at": datetime.now(tz=UTC).isoformat(),
        "metrics": {"train_mae": round(mae, 4)},
        "features": list(FEATURE_NAMES),
        "dataset_note": dataset_note,
        "explainer": "shap.LinearExplainer",
        "notes": (
            "Promote with `python -m modules.territorial_risk.interfaces.ml_cli promote "
            f"{model_version}` to enable SHAP-backed serving."
        ),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return metadata_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train territorial mortality risk model")
    parser.add_argument(
        "--artifacts-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "artifacts",
    )
    parser.add_argument("--model-version", default=DEFAULT_MODEL_VERSION)
    parser.add_argument(
        "--from-db",
        action="store_true",
        help="Train from curated PostgreSQL observations instead of synthetic panel",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    import os

    args = build_parser().parse_args(argv)
    metadata_path = train_and_register(
        artifacts_dir=args.artifacts_dir,
        model_version=args.model_version,
        from_db=args.from_db,
        database_url=os.environ.get("DATABASE_URL"),
    )
    print(f"Wrote model artifacts for {args.model_version} ({metadata_path})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
