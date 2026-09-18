"""tests/test_evidence/test_deviation.py — Unit and boundary tests for deviation formulas."""

from __future__ import annotations

from datetime import datetime, timezone

from core.schemas import SensorReading
from evidence.baselines import SensorBaseline
from evidence.deviation import (
    compute_deviation,
    compute_robust_z,
    compute_severity,
    compute_standard_z,
    compute_trend_and_roc,
    determine_band,
)


def test_hand_computed_formulas() -> None:
    """Hand-computed verification of delta, pct_dev, z_score, and robust_z.

    Test values:
      value = 91.4, nominal = 65.0, mean = 65.0, std = 5.5, median = 65.0, mad = 4.5

    Expected:
      delta = 91.4 - 65.0 = 26.4
      pct_dev = 26.4 / 65.0 = 0.406153846...
      standard_z = 26.4 / 5.5 = 4.8000
      robust_z = 0.6745 * (91.4 - 65.0) / 4.5 = 0.6745 * 26.4 / 4.5 = 3.9570666...
    """
    value = 91.4
    nominal = 65.0
    mean = 65.0
    std = 5.5
    median = 65.0
    mad = 4.5

    delta = value - nominal
    assert abs(delta - 26.4) < 1e-6

    pct_dev = delta / nominal
    assert abs(pct_dev - 0.406153846) < 1e-6

    z = compute_standard_z(value, mean, std)
    assert abs(z - 4.8) < 1e-6

    robust_z = compute_robust_z(value, median, mad)
    expected_robust_z = 0.6745 * 26.4 / 4.5
    assert abs(robust_z - expected_robust_z) < 1e-6


def test_pct_dev_nominal_zero_guard() -> None:
    """Assert pct_dev calculation handles nominal == 0 cleanly without division by zero."""
    baseline = SensorBaseline(
        sensor="temp",
        unit="C",
        nominal=0.0,
        normal_range=(-5.0, 5.0),
        warn_low=-10.0,
        warn_high=10.0,
        alarm_low=-15.0,
        alarm_high=15.0,
    )
    reading = SensorReading(name="temp", value=5.0, unit="C")
    dev = compute_deviation("temp", reading, baseline)

    assert dev.delta == 5.0
    assert dev.pct_dev == 5.0  # Guarded fallback when nominal is 0


def test_boundary_values() -> None:
    """Boundary tests: exact hits on warn_low, warn_high, alarm_low, alarm_high."""
    warn_low, warn_high = 50.0, 80.0
    alarm_low, alarm_high = 40.0, 90.0

    # Normal band inside boundaries
    assert determine_band(65.0, warn_low, warn_high, alarm_low, alarm_high) == "normal"

    # Exactly on warn_high boundary -> "warn"
    assert determine_band(80.0, warn_low, warn_high, alarm_low, alarm_high) == "warn"

    # Exactly on warn_low boundary -> "warn"
    assert determine_band(50.0, warn_low, warn_high, alarm_low, alarm_high) == "warn"

    # Exactly on alarm_high boundary -> "alarm"
    assert determine_band(90.0, warn_low, warn_high, alarm_low, alarm_high) == "alarm"

    # Exactly on alarm_low boundary -> "alarm"
    assert determine_band(40.0, warn_low, warn_high, alarm_low, alarm_high) == "alarm"

    # Beyond alarm_high -> "alarm"
    assert determine_band(95.0, warn_low, warn_high, alarm_low, alarm_high) == "alarm"


def test_severity_formula_determinism_and_bounds() -> None:
    """Test compute_severity output bounds and determinism."""
    sev_normal = compute_severity("normal", z_score=0.5, criticality=1.0)
    assert 0.0 <= sev_normal <= 35.0

    sev_warn = compute_severity("warn", z_score=2.0, criticality=1.0)
    assert 40.0 <= sev_warn <= 65.0

    sev_alarm = compute_severity("alarm", z_score=4.8, criticality=1.0)
    assert 70.0 <= sev_alarm <= 100.0

    # Severity with high criticality must clamp to 100
    sev_high_crit = compute_severity("alarm", z_score=10.0, criticality=2.0)
    assert sev_high_crit == 100.0


def test_trend_and_roc_per_min() -> None:
    """Assert rate of change per minute and trend direction calculation."""
    t0 = datetime(2026, 9, 18, 9, 0, 0, tzinfo=timezone.utc)
    t1 = datetime(2026, 9, 18, 9, 10, 0, tzinfo=timezone.utc)  # 10 minutes later

    # Rising trend: 65.0 -> 75.0 (10 deg in 10 min = 1.0 C/min)
    ts_rising = [(t0, 65.0), (t1, 75.0)]
    trend, roc = compute_trend_and_roc(ts_rising)
    assert trend == "rising"
    assert roc == 1.0

    # Falling trend: 80.0 -> 70.0 (-1.0 C/min)
    ts_falling = [(t0, 80.0), (t1, 70.0)]
    trend_f, roc_f = compute_trend_and_roc(ts_falling)
    assert trend_f == "falling"
    assert roc_f == -1.0

    # No time series supplied -> unknown / None
    trend_none, roc_none = compute_trend_and_roc(None)
    assert trend_none == "unknown"
    assert roc_none is None
