"""tests/test_evidence/test_baselines.py — Tests for baseline configuration and precedence rules."""

from __future__ import annotations

import pandas as pd

from evidence.baselines import (
    SensorBaseline,
    apply_precedence_rule,
    compute_learned_baseline,
    load_baselines,
)


def test_load_baselines_defaults() -> None:
    """Assert default baselines for centrifugal_pump load correctly."""
    baselines = load_baselines()
    assert "centrifugal_pump" in baselines
    pump_base = baselines["centrifugal_pump"]
    assert "bearing_temp_de" in pump_base
    assert "vibration_rms" in pump_base

    temp_base = pump_base["bearing_temp_de"]
    assert temp_base.nominal == 65.0
    assert temp_base.unit == "C"
    assert temp_base.normal_range == (55.0, 75.0)


def test_compute_learned_baseline() -> None:
    """Assert learned baseline computes mean, std, median, MAD, and quantiles."""
    df = pd.DataFrame(
        {
            "temp": [64.0, 65.0, 66.0, 65.5, 64.5, 65.0, 66.5],
            "vibe": [2.5, 2.7, 2.9, 2.8, 2.6, 2.7, 2.8],
        }
    )
    learned = compute_learned_baseline(df)
    assert "temp" in learned
    assert "vibe" in learned

    # Hand-computed expected values for temp
    # values: [64.0, 64.5, 65.0, 65.0, 65.5, 66.0, 66.5]
    # median = 65.0
    assert abs(learned["temp"]["median"] - 65.0) < 1e-4
    assert abs(learned["temp"]["mean"] - 65.2142857) < 1e-4


def test_precedence_rule_disagreement_greater_than_15_percent() -> None:
    """PRECEDENCE RULE: when OEM and learned disagree by > 15%, use OEM value and record conflict."""
    oem = SensorBaseline(
        sensor="bearing_temp_de",
        unit="C",
        nominal=65.0,
        normal_range=(55.0, 75.0),
        warn_low=50.0,
        warn_high=80.0,
        alarm_low=40.0,
        alarm_high=90.0,
        mean=65.0,
        std=5.0,
        median=65.0,
        mad=4.0,
        source="oem_config",
    )
    # Disagreement: learned nominal is 85.0 -> diff = |85 - 65| / 65 = 20.0 / 65 = 30.77% > 15%
    learned_stats = {
        "nominal": 85.0,
        "mean": 85.0,
        "std": 6.0,
        "median": 85.0,
        "mad": 4.5,
    }

    result = apply_precedence_rule(oem, learned_stats)

    # Must prefer OEM values and set conflict flag
    assert result.nominal == 65.0
    assert result.source == "oem_config"
    assert result.has_conflict is True
    assert result.conflict_pct == 30.77


def test_precedence_rule_agreement_within_15_percent() -> None:
    """When OEM and learned agree within 15%, use learned baseline statistics."""
    oem = SensorBaseline(
        sensor="bearing_temp_de",
        unit="C",
        nominal=65.0,
        normal_range=(55.0, 75.0),
        warn_low=50.0,
        warn_high=80.0,
        alarm_low=40.0,
        alarm_high=90.0,
        mean=65.0,
        std=5.0,
        median=65.0,
        mad=4.0,
        source="oem_config",
    )
    # Agreement: learned nominal is 67.0 -> diff = |67 - 65| / 65 = 2 / 65 = 3.08% <= 15%
    learned_stats = {
        "nominal": 67.0,
        "mean": 66.8,
        "std": 4.8,
        "median": 66.9,
        "mad": 3.8,
    }

    result = apply_precedence_rule(oem, learned_stats)

    # Must use learned baseline
    assert result.nominal == 67.0
    assert result.source == "learned_baseline"
    assert result.has_conflict is False
    assert result.conflict_pct == 3.08
