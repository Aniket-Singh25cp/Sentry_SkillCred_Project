"""evidence/baselines.py — Baseline configuration loader and learned baseline merger.

Handles loading OEM baselines and optionally computing learned baselines from healthy
snapshot data. Enforces the 15% precedence rule between OEM and learned values.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml


@dataclass(frozen=True)
class SensorBaseline:
    """Baseline specification for a single sensor on an asset class."""

    sensor: str
    unit: str
    nominal: float
    normal_range: tuple[float, float]
    warn_low: float | None
    warn_high: float | None
    alarm_low: float | None
    alarm_high: float | None
    criticality: float = 1.0
    mean: float = 0.0
    std: float = 1.0
    median: float = 0.0
    mad: float = 1.0
    source: str = "oem_config"  # "oem_config" or "learned_baseline"
    has_conflict: bool = False
    conflict_pct: float = 0.0


# Default fallback baselines for S0 equipment classes if external YAML is not present
DEFAULT_BASELINES: dict[str, dict[str, dict[str, Any]]] = {
    "centrifugal_pump": {
        "bearing_temp_de": {
            "unit": "C",
            "nominal": 65.0,
            "normal_range": [55.0, 75.0],
            "warn_low": 50.0,
            "warn_high": 80.0,
            "alarm_low": 40.0,
            "alarm_high": 90.0,
            "criticality": 1.2,
            "mean": 65.0,
            "std": 5.5,
            "median": 65.0,
            "mad": 4.5,
        },
        "vibration_rms": {
            "unit": "mm/s",
            "nominal": 2.8,
            "normal_range": [0.0, 4.5],
            "warn_low": None,
            "warn_high": 4.5,
            "alarm_low": None,
            "alarm_high": 7.0,
            "criticality": 1.5,
            "mean": 2.8,
            "std": 0.98,
            "median": 2.7,
            "mad": 0.75,
        },
        "motor_current": {
            "unit": "A",
            "nominal": 32.0,
            "normal_range": [25.0, 38.0],
            "warn_low": 22.0,
            "warn_high": 40.0,
            "alarm_low": 18.0,
            "alarm_high": 45.0,
            "criticality": 1.0,
            "mean": 32.0,
            "std": 3.0,
            "median": 32.0,
            "mad": 2.2,
        },
        "discharge_pressure": {
            "unit": "bar",
            "nominal": 6.5,
            "normal_range": [5.5, 7.5],
            "warn_low": 5.0,
            "warn_high": 8.0,
            "alarm_low": 4.0,
            "alarm_high": 9.0,
            "criticality": 1.1,
            "mean": 6.5,
            "std": 0.5,
            "median": 6.5,
            "mad": 0.4,
        },
        "flow_rate": {
            "unit": "m3/h",
            "nominal": 125.0,
            "normal_range": [110.0, 140.0],
            "warn_low": 100.0,
            "warn_high": 145.0,
            "alarm_low": 90.0,
            "alarm_high": 150.0,
            "criticality": 1.0,
            "mean": 125.0,
            "std": 8.0,
            "median": 125.0,
            "mad": 6.0,
        },
        "oil_level_pct": {
            "unit": "%",
            "nominal": 80.0,
            "normal_range": [60.0, 100.0],
            "warn_low": 50.0,
            "warn_high": None,
            "alarm_low": 30.0,
            "alarm_high": None,
            "criticality": 1.3,
            "mean": 80.0,
            "std": 5.0,
            "median": 80.0,
            "mad": 4.0,
        },
        "differential_pressure": {
            "unit": "bar",
            "nominal": 0.5,
            "normal_range": [0.1, 1.0],
            "warn_low": None,
            "warn_high": 1.2,
            "alarm_low": None,
            "alarm_high": 1.8,
            "criticality": 1.0,
            "mean": 0.5,
            "std": 0.15,
            "median": 0.5,
            "mad": 0.12,
        },
        "rpm": {
            "unit": "RPM",
            "nominal": 1750.0,
            "normal_range": [1700.0, 1800.0],
            "warn_low": 1650.0,
            "warn_high": 1820.0,
            "alarm_low": 1600.0,
            "alarm_high": 1850.0,
            "criticality": 1.0,
            "mean": 1750.0,
            "std": 25.0,
            "median": 1750.0,
            "mad": 20.0,
        },
    }
}


def _parse_sensor_dict(sensor_name: str, data: dict[str, Any], default_source: str = "oem_config") -> SensorBaseline:
    """Construct a SensorBaseline object from a raw dict with fallbacks."""
    nominal = float(data.get("nominal", 0.0))
    norm_range = data.get("normal_range", [nominal * 0.9, nominal * 1.1])
    normal_tuple = (float(norm_range[0]), float(norm_range[1]))

    mean_val = float(data.get("mean", nominal))
    std_val = float(data.get("std", 1.0))
    if std_val <= 0:
        std_val = 1.0

    median_val = float(data.get("median", mean_val))
    mad_val = float(data.get("mad", std_val * 0.7979))  # MAD approx std*sqrt(2/pi) for normal
    if mad_val <= 0:
        mad_val = 1.0

    return SensorBaseline(
        sensor=sensor_name,
        unit=str(data.get("unit", "")),
        nominal=nominal,
        normal_range=normal_tuple,
        warn_low=float(data["warn_low"]) if data.get("warn_low") is not None else None,
        warn_high=float(data["warn_high"]) if data.get("warn_high") is not None else None,
        alarm_low=float(data["alarm_low"]) if data.get("alarm_low") is not None else None,
        alarm_high=float(data["alarm_high"]) if data.get("alarm_high") is not None else None,
        criticality=float(data.get("criticality", 1.0)),
        mean=mean_val,
        std=std_val,
        median=median_val,
        mad=mad_val,
        source=str(data.get("source", default_source)),
        has_conflict=bool(data.get("has_conflict", False)),
        conflict_pct=float(data.get("conflict_pct", 0.0)),
    )


def load_baselines(yaml_path: str | Path | None = None) -> dict[str, dict[str, SensorBaseline]]:
    """Load baseline configurations by equipment class.

    Reads from data/baselines.yaml if present, falling back to embedded defaults.
    Returns: mapping of asset_class -> (mapping of sensor_name -> SensorBaseline).
    """
    raw_dict: dict[str, Any] = {}
    path = Path(yaml_path) if yaml_path else Path("data/baselines.yaml")

    if path.exists() and path.is_file():
        with path.open("r", encoding="utf-8") as fh:
            loaded = yaml.safe_load(fh)
            if isinstance(loaded, dict):
                raw_dict = loaded

    # Merge with default baselines if raw_dict is empty or missing asset classes
    merged_data: dict[str, dict[str, Any]] = {}
    for asset_class, default_sensors in DEFAULT_BASELINES.items():
        merged_data[asset_class] = dict(default_sensors)
        if asset_class in raw_dict and isinstance(raw_dict[asset_class], dict):
            merged_data[asset_class].update(raw_dict[asset_class])

    # Also include any asset classes in raw_dict not in DEFAULT_BASELINES
    for asset_class, sensors in raw_dict.items():
        if asset_class not in merged_data and isinstance(sensors, dict):
            merged_data[asset_class] = sensors

    # Convert to SensorBaseline dataclasses
    res: dict[str, dict[str, SensorBaseline]] = {}
    for asset_class, sensors in merged_data.items():
        res[asset_class] = {}
        for sensor_name, sensor_data in sensors.items():
            if isinstance(sensor_data, dict):
                res[asset_class][sensor_name] = _parse_sensor_dict(sensor_name, sensor_data)

    return res


def compute_learned_baseline(df: pd.DataFrame) -> dict[str, dict[str, float]]:
    """Compute learned baselines from a DataFrame of healthy sensor snapshots.

    Computes mean, std, median, MAD, P05, P95 per sensor column.
    """
    learned: dict[str, dict[str, float]] = {}
    numeric_cols = df.select_dtypes(include=[np.number]).columns

    for col in numeric_cols:
        series = df[col].dropna()
        if len(series) == 0:
            continue

        mean_val = float(series.mean())
        std_val = float(series.std(ddof=1)) if len(series) > 1 else 0.0
        median_val = float(series.median())
        mad_val = float((series - median_val).abs().median())
        p05_val = float(series.quantile(0.05))
        p95_val = float(series.quantile(0.95))

        learned[str(col)] = {
            "nominal": median_val,
            "mean": mean_val,
            "std": std_val if std_val > 0 else 1.0,
            "median": median_val,
            "mad": mad_val if mad_val > 0 else 1.0,
            "p05": p05_val,
            "p95": p95_val,
        }

    return learned


def apply_precedence_rule(
    oem_baseline: SensorBaseline,
    learned_stats: dict[str, float] | None,
) -> SensorBaseline:
    """Apply the 15% precedence rule between OEM config and learned baseline.

    PRECEDENCE RULE: when OEM config and learned baseline disagree by more than 15%
    (|learned - oem| / oem > 0.15), use the OEM value and record the conflict in the output.
    Never silently prefer one.
    """
    if not learned_stats:
        return oem_baseline

    learned_nominal = learned_stats.get("nominal", learned_stats.get("mean", oem_baseline.nominal))
    oem_nominal = oem_baseline.nominal

    if oem_nominal != 0.0:
        diff_fraction = abs(learned_nominal - oem_nominal) / abs(oem_nominal)
    else:
        diff_fraction = abs(learned_nominal)

    disagreement_threshold = 0.15

    if diff_fraction > disagreement_threshold:
        # Conflict detected! Use OEM value and record the conflict.
        # Preserve OEM stats, but record source and conflict details.
        return SensorBaseline(
            sensor=oem_baseline.sensor,
            unit=oem_baseline.unit,
            nominal=oem_baseline.nominal,
            normal_range=oem_baseline.normal_range,
            warn_low=oem_baseline.warn_low,
            warn_high=oem_baseline.warn_high,
            alarm_low=oem_baseline.alarm_low,
            alarm_high=oem_baseline.alarm_high,
            criticality=oem_baseline.criticality,
            mean=oem_baseline.mean,
            std=oem_baseline.std,
            median=oem_baseline.median,
            mad=oem_baseline.mad,
            source="oem_config",
            has_conflict=True,
            conflict_pct=round(diff_fraction * 100.0, 2),
        )

    # No conflict (>15% agreement): incorporate learned statistical parameters
    learned_mean = learned_stats.get("mean", oem_baseline.mean)
    learned_std = learned_stats.get("std", oem_baseline.std)
    learned_median = learned_stats.get("median", oem_baseline.median)
    learned_mad = learned_stats.get("mad", oem_baseline.mad)

    return SensorBaseline(
        sensor=oem_baseline.sensor,
        unit=oem_baseline.unit,
        nominal=learned_nominal,
        normal_range=oem_baseline.normal_range,
        warn_low=oem_baseline.warn_low,
        warn_high=oem_baseline.warn_high,
        alarm_low=oem_baseline.alarm_low,
        alarm_high=oem_baseline.alarm_high,
        criticality=oem_baseline.criticality,
        mean=learned_mean,
        std=learned_std if learned_std > 0 else oem_baseline.std,
        median=learned_median,
        mad=learned_mad if learned_mad > 0 else oem_baseline.mad,
        source="learned_baseline",
        has_conflict=False,
        conflict_pct=round(diff_fraction * 100.0, 2),
    )
