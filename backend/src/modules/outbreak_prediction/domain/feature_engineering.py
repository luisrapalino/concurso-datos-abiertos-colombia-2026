"""Feature engineering for intermediate-level outbreak ML models."""

from __future__ import annotations

import math
import re

from modules.outbreak_prediction.domain.outbreak_prediction import OutbreakFeatureSnapshot

OUTBREAK_ML_FEATURE_NAMES: tuple[str, ...] = (
    "log_observed_cases",
    "log_baseline_cases",
    "cases_vs_median",
    "log_previous_week_cases",
    "week_over_week_ratio",
    "vaccination_coverage_pct",
    "vaccination_gap",
    "health_access_pct",
    "health_access_gap",
    "pm25_ug_m3",
    "epidemiological_week_sin",
    "epidemiological_week_cos",
    "cases_above_baseline",
    "accelerated_growth",
    "territorial_risk_proxy",
)

_DEFAULT_VACCINATION = 85.0
_DEFAULT_HEALTH_ACCESS = 90.0
_DEFAULT_PM25 = 15.0


def build_outbreak_feature_vector(
    snapshot: OutbreakFeatureSnapshot,
) -> tuple[float, ...]:
    """Transform a curated snapshot into a fixed-length ML feature vector."""
    baseline = max(snapshot.baseline_cases, 1e-6)
    observed = max(snapshot.observed_cases, 0.0)
    ratio = observed / baseline

    previous = snapshot.previous_week_cases
    if previous is not None and previous > 0:
        wow_ratio = observed / previous
    else:
        wow_ratio = 1.0

    vaccination = snapshot.vaccination_coverage_pct if snapshot.vaccination_coverage_pct is not None else _DEFAULT_VACCINATION
    health_access = snapshot.health_access_pct if snapshot.health_access_pct is not None else _DEFAULT_HEALTH_ACCESS
    pm25 = snapshot.pm25_ug_m3 if snapshot.pm25_ug_m3 is not None else _DEFAULT_PM25

    vaccination_gap = max(0.0, 100.0 - vaccination)
    health_access_gap = max(0.0, 100.0 - health_access)
    week = _parse_epidemiological_week(snapshot.period)
    season_angle = (2.0 * math.pi * week) / 52.0

    return (
        _log1p(observed),
        _log1p(baseline),
        ratio,
        _log1p(previous or 0.0),
        wow_ratio,
        vaccination,
        vaccination_gap,
        health_access,
        health_access_gap,
        pm25,
        math.sin(season_angle),
        math.cos(season_angle),
        1.0 if ratio >= 1.0 else 0.0,
        1.0 if wow_ratio >= 1.5 else 0.0,
        ratio * (vaccination_gap / 100.0) * (pm25 / 25.0),
    )


def outbreak_alert_label(snapshot: OutbreakFeatureSnapshot) -> int:
    """Binary label aligned with territorial anomaly thresholds (ratio >= 1.5)."""
    if snapshot.baseline_cases <= 0:
        return 0
    ratio = snapshot.observed_cases / snapshot.baseline_cases
    if ratio >= 1.5:
        return 1
    if snapshot.previous_week_cases is not None and snapshot.previous_week_cases > 0:
        wow = snapshot.observed_cases / snapshot.previous_week_cases
        if wow >= 1.5:
            return 1
    return 0


def _log1p(value: float) -> float:
    return math.log1p(max(value, 0.0))


def _parse_epidemiological_week(period: str) -> int:
    match = re.search(r"-W(\d+)", period)
    if match is None:
        return 1
    return max(1, min(52, int(match.group(1))))
