"""evidence/deviation.py — Sensor deviation calculations.

Computes delta, percentage deviation, standard z-score / robust MAD z-score,
operating band classification, rate of change, trend, and severity score.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

import numpy as np
from scipy import stats

from core.schemas import Deviation, SensorReading
from evidence.baselines import SensorBaseline


def check_normality(samples: list[float] | np.ndarray, alpha: float = 0.05) -> bool:
    """Perform Shapiro-Wilk test for normality on a sample distribution.

    Returns True if the distribution appears normal (p-value >= alpha), False otherwise.
    Requires at least 3 samples.
    """
    arr = np.asarray(samples, dtype=float)
    if len(arr) < 3:
        return True  # Assume normal for tiny sample size
    try:
        _stat, p_val = stats.shapiro(arr)
        return bool(p_val >= alpha)
    except (ValueError, TypeError, RuntimeError, stats.DegenerateDataError):
        return True


def compute_standard_z(value: float, mean: float, std: float) -> float:
    """Compute standard z-score: (x - μ) / σ."""
    if std <= 0.0 or np.isnan(std):
        return 0.0
    return float((value - mean) / std)


def compute_robust_z(value: float, median: float, mad: float) -> float:
    """Compute modified z-score using Median Absolute Deviation (MAD).

    Formula: 0.6745 * (x - median) / MAD
    The constant 0.6745 makes MAD unbiased for normal distributions.
    """
    if mad <= 0.0 or np.isnan(mad):
        return 0.0
    return float(0.6745 * (value - median) / mad)


def determine_band(
    value: float,
    warn_low: float | None,
    warn_high: float | None,
    alarm_low: float | None,
    alarm_high: float | None,
    min_possible: float | None = None,
    max_possible: float | None = None,
) -> Literal["normal", "warn", "alarm", "out_of_range"]:
    """Determine operating band classification derived from configured thresholds.

    Precedence:
    1. out_of_range: if value exceeds physical/sensor bounds.
    2. alarm: if value >= alarm_high or value <= alarm_low.
    3. warn: if value >= warn_high or value <= warn_low.
    4. normal: otherwise.

    Exact boundary hits (e.g. value == alarm_high) trigger the respective band.
    """
    # 1. Out of range check for physical/sensor boundary violations
    if min_possible is not None and value < min_possible:
        return "out_of_range"
    if max_possible is not None and value > max_possible:
        return "out_of_range"

    # 2. Alarm threshold check
    if alarm_high is not None and value >= alarm_high:
        return "alarm"
    if alarm_low is not None and value <= alarm_low:
        return "alarm"

    # 3. Warning threshold check
    if warn_high is not None and value >= warn_high:
        return "warn"
    if warn_low is not None and value <= warn_low:
        return "warn"

    # 4. Normal operating band
    return "normal"


def compute_severity(band: str, z_score: float, criticality: float = 1.0) -> float:
    """Compute deterministic, monotonic severity score in range [0, 100].

    FORMULA RATIONALE:
    Severity is structured into base bands + continuous z-magnitude scaling:
      - band "normal": base 0.0, scaled up to 35.0 based on z_score.
      - band "warn": base 40.0, scaled up to 65.0 based on z_score.
      - band "alarm": base 70.0, scaled up to 90.0 based on z_score.
      - band "out_of_range": base 90.0, scaled up to 100.0 based on z_score.

    This guarantees:
      1. Monotonic non-decreasing in |z| for any given band.
      2. Monotonic non-decreasing across band rank (alarm >= warn >= normal).
      3. Proportional scaling by sensor criticality factor.
      4. Hard clamping within [0.0, 100.0].
    """
    z_mag = abs(z_score)

    if band == "normal":
        unweighted = min(35.0, z_mag * 10.0)
    elif band == "warn":
        unweighted = 40.0 + min(25.0, z_mag * 5.0)
    elif band == "alarm":
        unweighted = 70.0 + min(20.0, z_mag * 4.0)
    else:  # out_of_range
        unweighted = 90.0 + min(10.0, z_mag * 2.0)

    # Apply sensor criticality factor
    severity_val = unweighted * max(0.1, criticality)

    # Clamp strictly between 0.0 and 100.0 and round to 2 decimal places
    clamped = float(np.clip(severity_val, 0.0, 100.0))
    return round(clamped, 2)


def compute_trend_and_roc(
    time_series: list[tuple[datetime, float]] | None,
) -> tuple[Literal["rising", "falling", "stable", "unknown"], float | None]:
    """Compute rate of change per minute and trend direction if time series is supplied.

    If time series has fewer than 2 points, returns ("unknown", None).
    """
    if not time_series or len(time_series) < 2:
        return "unknown", None

    # Sort time series chronologically
    sorted_ts = sorted(time_series, key=lambda x: x[0])
    t_start, v_start = sorted_ts[0]
    t_end, v_end = sorted_ts[-1]

    dt_minutes = (t_end - t_start).total_seconds() / 60.0
    if dt_minutes <= 0.0:
        return "unknown", None

    roc_per_min = (v_end - v_start) / dt_minutes

    # Classify trend direction based on rate of change threshold
    roc_threshold = 0.01  # units per minute
    trend: Literal["rising", "falling", "stable", "unknown"]
    if roc_per_min > roc_threshold:
        trend = "rising"
    elif roc_per_min < -roc_threshold:
        trend = "falling"
    else:
        trend = "stable"

    return trend, round(float(roc_per_min), 4)


def compute_deviation(
    sensor_name: str,
    reading: SensorReading,
    baseline: SensorBaseline,
    time_series: list[tuple[datetime, float]] | None = None,
    healthy_samples: list[float] | None = None,
) -> Deviation:
    """Compute complete Deviation payload for a single sensor.

    1. Delta & Pct Dev: value - nominal, delta / nominal (guarded against nominal == 0).
    2. Z-Score: chooses robust_z (MAD) if distribution fails normality test or sensor is vibration.
    3. Band: derived from warn/alarm thresholds.
    4. Trend & Rate of Change: computed if time_series is provided.
    5. Severity: deterministic 0-100 monotonic score.
    """
    val = reading.value
    nom = baseline.nominal
    unit = reading.unit or baseline.unit

    # 1. Delta and percentage deviation
    delta = val - nom
    if nom != 0.0:
        pct_dev = delta / nom
    else:
        pct_dev = delta  # Fallback guard when nominal is 0

    # 2. Z-Score selection (Standard z vs Robust MAD z)
    use_robust = False
    if healthy_samples and len(healthy_samples) >= 3:
        is_normal = check_normality(healthy_samples)
        if not is_normal:
            use_robust = True
    elif "vibration" in sensor_name.lower():
        # Vibration distributions are naturally skewed; default to robust z
        use_robust = True

    if use_robust:
        z_val = compute_robust_z(val, baseline.median, baseline.mad)
    else:
        z_val = compute_standard_z(val, baseline.mean, baseline.std)

    # 3. Band classification
    band = determine_band(
        val,
        warn_low=baseline.warn_low,
        warn_high=baseline.warn_high,
        alarm_low=baseline.alarm_low,
        alarm_high=baseline.alarm_high,
    )

    # 4. Trend and Rate of Change
    trend, roc_per_min = compute_trend_and_roc(time_series)

    # 5. Severity score
    sev = compute_severity(band, z_val, criticality=baseline.criticality)

    # Provenance source string
    source_label = baseline.source

    return Deviation(
        sensor=sensor_name,
        value=round(float(val), 4),
        unit=unit,
        nominal=round(float(nom), 4),
        normal_range=(round(float(baseline.normal_range[0]), 4), round(float(baseline.normal_range[1]), 4)),
        delta=round(float(delta), 4),
        pct_dev=round(float(pct_dev), 4),
        z_score=round(float(z_val), 4),
        band=band,
        severity=sev,
        trend=trend,
        roc_per_min=roc_per_min,
        source=source_label,
    )
