"""tests/test_evidence/test_coverage_boost.py — Additional test cases for 90%+ line coverage."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from core.schemas import SensorReading
from evidence.baselines import (
    SensorBaseline,
    _parse_sensor_dict,
    compute_learned_baseline,
    load_baselines,
)
from evidence.deviation import (
    check_normality,
    compute_deviation,
    compute_robust_z,
    compute_standard_z,
    determine_band,
)
from evidence.history import _normalize_dt, get_history_features
from evidence.signatures import (
    _parse_when_condition,
    load_signature_rules,
)


def test_baselines_extra_coverage(tmp_path: Path) -> None:
    """Cover _parse_sensor_dict edge cases and custom YAML file loading."""
    data = {
        "unit": "bar",
        "nominal": 0.0,
        "std": 0.0,
        "mad": 0.0,
        "warn_low": 2.0,
        "warn_high": 8.0,
        "alarm_low": 1.0,
        "alarm_high": 9.0,
    }
    base = _parse_sensor_dict("press", data)
    assert base.std == 1.0
    assert base.mad == 1.0
    assert base.warn_low == 2.0

    # Custom YAML file loading
    yaml_file = tmp_path / "custom_baselines.yaml"
    yaml_file.write_text(
        """
custom_asset:
  temp:
    unit: "C"
    nominal: 50.0
    normal_range: [40.0, 60.0]
""",
        encoding="utf-8",
    )
    loaded = load_baselines(yaml_file)
    assert "custom_asset" in loaded

    # Empty df / non-numeric in compute_learned_baseline
    df = pd.DataFrame({"empty_col": [None, None], "str_col": ["a", "b"], "val": [10.0, 10.0]})
    learned = compute_learned_baseline(df)
    assert "val" in learned
    assert learned["val"]["std"] == 1.0
    assert learned["val"]["mad"] == 1.0


def test_deviation_extra_coverage() -> None:
    """Cover check_normality edge cases, zero std/mad z-scores, out_of_range bounds."""
    # Normality with < 3 samples
    assert check_normality([1.0, 2.0]) is True

    # Normality with non-normal skewed distribution
    skewed = [1.0, 1.1, 1.2, 1.05, 100.0, 200.0, 500.0]
    assert check_normality(skewed) is False

    # Zero std/mad guards
    assert compute_standard_z(10.0, 10.0, std=0.0) == 0.0
    assert compute_robust_z(10.0, 10.0, mad=0.0) == 0.0

    # determine_band out_of_range min/max bounds
    assert determine_band(5.0, warn_low=10.0, warn_high=20.0, alarm_low=5.0, alarm_high=25.0, min_possible=10.0) == "out_of_range"
    assert determine_band(30.0, warn_low=10.0, warn_high=20.0, alarm_low=5.0, alarm_high=25.0, max_possible=25.0) == "out_of_range"

    # compute_deviation with healthy_samples and time_series
    baseline = SensorBaseline(
        sensor="vibration_rms",
        unit="mm/s",
        nominal=2.8,
        normal_range=(0.0, 4.5),
        warn_low=None,
        warn_high=4.5,
        alarm_low=None,
        alarm_high=7.0,
        mean=2.8,
        std=0.98,
        median=2.7,
        mad=0.75,
    )
    t0 = datetime(2026, 9, 18, 9, 0, 0, tzinfo=timezone.utc)
    t1 = datetime(2026, 9, 18, 9, 10, 0, tzinfo=timezone.utc)
    ts = [(t0, 2.8), (t1, 8.1)]
    reading = SensorReading(name="vibration_rms", value=8.1, unit="mm/s")

    dev = compute_deviation(
        sensor_name="vibration_rms",
        reading=reading,
        baseline=baseline,
        time_series=ts,
        healthy_samples=skewed,
    )
    assert dev.band == "alarm"
    assert dev.trend == "rising"
    assert dev.roc_per_min is not None


def test_signatures_extra_coverage(tmp_path: Path) -> None:
    """Cover == and >= condition parsers and evaluations."""
    c_eq = _parse_when_condition("sensor.band == alarm")
    assert c_eq == ("sensor", "band", "==", ["alarm"])

    c_gte = _parse_when_condition("sensor.severity >= 80")
    assert c_gte == ("sensor", "severity", ">=", ["80"])

    # Test load_signature_rules with custom file
    rule_file = tmp_path / "custom_rules.yaml"
    rule_file.write_text(
        """
rules:
  - id: R-999
    name: test_rule
    when:
      - sensor.band == alarm
    confidence: 0.95
""",
        encoding="utf-8",
    )
    rules = load_signature_rules(rule_file)
    assert len(rules) == 1
    assert rules[0]["id"] == "R-999"

    # Non-existent file falls back gracefully
    fallback_rules = load_signature_rules(tmp_path / "non_existent.yaml")
    assert len(fallback_rules) >= 1


def test_history_extra_coverage() -> None:
    """Cover datetime string parsing in history."""
    dt_str = "2026-09-18T09:14:00Z"
    norm = _normalize_dt(dt_str)
    assert norm.year == 2026

    # history with DataFrame input
    df = pd.DataFrame(
        [
            {
                "asset_id": "PUMP-07",
                "date": "2026-08-01T00:00:00Z",
                "fault_code": "E-204",
                "parts_replaced": ["bearing"],
            }
        ]
    )
    features = get_history_features("PUMP-07", "E-204", datetime(2026, 9, 18, 9, 14, 0, tzinfo=timezone.utc), history_records=df)
    assert features.days_since_service == 48
    assert features.recent_parts == ["bearing"]
