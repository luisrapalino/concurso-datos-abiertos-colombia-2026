"""Offline training and artifact registration for outbreak Random Forest models."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score

from modules.outbreak_prediction.domain.feature_engineering import (
    OUTBREAK_ML_FEATURE_NAMES,
    build_outbreak_feature_vector,
    outbreak_alert_label,
)
from modules.outbreak_prediction.domain.outbreak_prediction import (
    DENGUE_DEFINITION_ID,
    HEALTH_ACCESS_DEFINITION_ID,
    OutbreakFeatureSnapshot,
    PM25_DEFINITION_ID,
    VACCINATION_DEFINITION_ID,
)

DEFAULT_MODEL_VERSION = "randomforest-outbreak-v1.0.0"


def build_synthetic_panel() -> tuple[np.ndarray, np.ndarray, list[str]]:
    snapshots = [
        _snapshot("05001", "2020-W33", 120, 30, 60, 70, 85, 20),
        _snapshot("05001", "2020-W10", 5, 20, 6, 95, 98, 10),
        _snapshot("11001", "2021-W20", 80, 25, 40, 82, 90, 18),
        _snapshot("11001", "2021-W21", 15, 25, 14, 92, 96, 12),
        _snapshot("08001", "2019-W40", 200, 40, 100, 65, 80, 22),
        _snapshot("08001", "2019-W41", 30, 40, 28, 88, 92, 14),
        _snapshot("76001", "2018-W15", 55, 20, 25, 78, 88, 16),
        _snapshot("76001", "2018-W16", 8, 20, 7, 94, 97, 11),
    ]
    features = np.array([build_outbreak_feature_vector(item) for item in snapshots], dtype=float)
    labels = np.array([outbreak_alert_label(item) for item in snapshots], dtype=int)
    periods = [item.period for item in snapshots]
    return features, labels, periods


def build_training_panel_from_db(database_url: str) -> tuple[np.ndarray, np.ndarray, list[str]]:
    from sqlalchemy import func, select
    from sqlalchemy.orm import Session

    from infrastructure.persistence.database import dispose_engine, get_engine, init_engine
    from modules.epidemiological_surveillance.infrastructure.persistence.orm_models import (
        HealthIndicatorObservationRow,
    )
    from modules.outbreak_prediction.infrastructure.outbreak_data_adapter import (
        _previous_epidemiological_week,
    )

    init_engine(database_url)
    features: list[tuple[float, ...]] = []
    labels: list[int] = []
    periods: list[str] = []

    with Session(get_engine()) as session:
        rows = session.execute(
            select(
                HealthIndicatorObservationRow.territorial_code,
                HealthIndicatorObservationRow.period,
                HealthIndicatorObservationRow.value,
            ).where(
                HealthIndicatorObservationRow.definition_id == DENGUE_DEFINITION_ID,
                HealthIndicatorObservationRow.period.like("%-W%"),
            ),
        ).all()

        for territorial_code, period, observed_value in rows:
            baseline = session.scalar(
                select(func.percentile_cont(0.5).within_group(HealthIndicatorObservationRow.value)).where(
                    HealthIndicatorObservationRow.definition_id == DENGUE_DEFINITION_ID,
                    HealthIndicatorObservationRow.period == period,
                ),
            )
            if baseline is None or Decimal(baseline) <= 0:
                continue

            year = int(str(period)[:4])
            annual_period = f"{year:04d}-01"
            previous_period = _previous_epidemiological_week(str(period))
            previous_week = session.scalar(
                select(HealthIndicatorObservationRow.value).where(
                    HealthIndicatorObservationRow.definition_id == DENGUE_DEFINITION_ID,
                    HealthIndicatorObservationRow.territorial_code == territorial_code,
                    HealthIndicatorObservationRow.period == previous_period,
                ),
            )

            def _annual(definition_id: str) -> float | None:
                value = session.scalar(
                    select(HealthIndicatorObservationRow.value).where(
                        HealthIndicatorObservationRow.definition_id == definition_id,
                        HealthIndicatorObservationRow.territorial_code == territorial_code,
                        HealthIndicatorObservationRow.period == annual_period,
                    ),
                )
                return float(value) if value is not None else None

            snapshot = OutbreakFeatureSnapshot(
                territorial_code=str(territorial_code),
                period=str(period),
                event_code="210",
                event_name="DENGUE",
                observed_cases=float(observed_value),
                baseline_cases=float(baseline),
                previous_week_cases=float(previous_week) if previous_week is not None else None,
                vaccination_coverage_pct=_annual(VACCINATION_DEFINITION_ID),
                health_access_pct=_annual(HEALTH_ACCESS_DEFINITION_ID),
                pm25_ug_m3=_annual(PM25_DEFINITION_ID),
            )
            features.append(build_outbreak_feature_vector(snapshot))
            labels.append(outbreak_alert_label(snapshot))
            periods.append(str(period))

    dispose_engine()
    if not features:
        msg = "No dengue weekly observations available to build outbreak training panel."
        raise RuntimeError(msg)
    return np.array(features, dtype=float), np.array(labels, dtype=int), periods


def train_and_register(
    *,
    artifacts_dir: Path,
    model_version: str = DEFAULT_MODEL_VERSION,
    from_db: bool = False,
    database_url: str | None = None,
) -> Path:
    if from_db:
        if database_url is None:
            msg = "DATABASE_URL is required when --from-db is set."
            raise ValueError(msg)
        features, labels, periods = build_training_panel_from_db(database_url)
        notes = "Trained from curated PostgreSQL observations (SIVIGILA dengue panel)."
    else:
        features, labels, periods = build_synthetic_panel()
        notes = "Trained on reproducible synthetic panel aligned with outbreak labels."

    metrics = _evaluate_temporal_split(features, labels, periods)
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42,
    )
    model.fit(features, labels)

    artifacts_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = artifacts_dir / f"{model_version}.joblib"
    metadata_path = artifacts_dir / f"{model_version}.json"
    joblib.dump(
        {
            "model": model,
            "background": features[: min(len(features), 100)],
            "feature_names": list(OUTBREAK_ML_FEATURE_NAMES),
        },
        artifact_path,
    )
    metadata_path.write_text(
        json.dumps(
            {
                "model_version": model_version,
                "algorithm": "RandomForestClassifier",
                "feature_count": len(OUTBREAK_ML_FEATURE_NAMES),
                "features": list(OUTBREAK_ML_FEATURE_NAMES),
                "trained_at": datetime.now(tz=UTC).isoformat(),
                "training_samples": int(len(labels)),
                "positive_rate": round(float(labels.mean()), 4),
                "validation": metrics,
                "notes": notes,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    return artifact_path


def _evaluate_temporal_split(
    features: np.ndarray,
    labels: np.ndarray,
    periods: list[str],
) -> dict[str, object]:
    train_mask = np.array([_period_year(period) <= 2020 for period in periods])
    if train_mask.sum() == 0 or (~train_mask).sum() == 0:
        split_index = max(1, int(len(features) * 0.8))
        train_x, test_x = features[:split_index], features[split_index:]
        train_y, test_y = labels[:split_index], labels[split_index:]
        strategy = "80/20 holdout fallback"
    else:
        train_x, test_x = features[train_mask], features[~train_mask]
        train_y, test_y = labels[train_mask], labels[~train_mask]
        strategy = "temporal split: train <= 2020, test >= 2021"

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42,
    )
    model.fit(train_x, train_y)
    probabilities = model.predict_proba(test_x)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)

    metrics: dict[str, object] = {
        "strategy": strategy,
        "train_samples": int(len(train_y)),
        "test_samples": int(len(test_y)),
        "precision": round(float(precision_score(test_y, predictions, zero_division=0)), 4),
        "recall": round(float(recall_score(test_y, predictions, zero_division=0)), 4),
        "f1": round(float(f1_score(test_y, predictions, zero_division=0)), 4),
    }
    if len(np.unique(test_y)) > 1:
        metrics["roc_auc"] = round(float(roc_auc_score(test_y, probabilities)), 4)
    return metrics


def _period_year(period: str) -> int:
    if period.startswith("synthetic"):
        return 2020
    return int(period[:4])


def _snapshot(
    territorial_code: str,
    period: str,
    observed: float,
    baseline: float,
    previous: float,
    vaccination: float,
    health_access: float,
    pm25: float,
) -> OutbreakFeatureSnapshot:
    return OutbreakFeatureSnapshot(
        territorial_code=territorial_code,
        period=period,
        event_code="210",
        event_name="DENGUE",
        observed_cases=float(observed),
        baseline_cases=float(baseline),
        previous_week_cases=float(previous),
        vaccination_coverage_pct=float(vaccination),
        health_access_pct=float(health_access),
        pm25_ug_m3=float(pm25),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Train outbreak Random Forest experiment")
    parser.add_argument("--from-db", action="store_true")
    parser.add_argument("--database-url", default=None)
    parser.add_argument("--artifacts-dir", default=None)
    parser.add_argument("--model-version", default=DEFAULT_MODEL_VERSION)
    args = parser.parse_args(argv)

    backend_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(backend_root / "src"))

    artifacts_dir = (
        Path(args.artifacts_dir)
        if args.artifacts_dir
        else backend_root / "ml" / "artifacts"
    )
    database_url = args.database_url or __import__("os").environ.get("DATABASE_URL")

    artifact_path = train_and_register(
        artifacts_dir=artifacts_dir,
        model_version=args.model_version,
        from_db=args.from_db,
        database_url=database_url,
    )
    print(f"Registered outbreak model artifact at {artifact_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
