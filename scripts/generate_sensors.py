#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scripts/generate_sensors.py - Synthetic sensor snapshot generator for SENTRY S0.

Generates:
  data/snapshots/healthy.parquet   - 600 healthy snapshots per asset class (1 200 total)
  data/snapshots/faults/<id>.json  - One faulted snapshot per scenario

Design decisions:
  - Single fixed seed (SEED = 42) propagated through numpy.random.default_rng for full
    determinism. Re-running twice must produce byte-identical Parquet output.
  - Healthy snapshots use a multivariate Gaussian model with realistic inter-sensor
    correlations (current <-> flow <-> pressure, etc.).
  - The correlation matrix is projected to the nearest positive-semidefinite matrix
    via eigenvalue clipping so numpy never raises a RuntimeWarning.
  - Each fault scenario applies a documented fault-signature function to the healthy
    nominal vector. Signature parameters are stored in module-level dicts so the
    derivation is auditable without running the code.
  - pyarrow.parquet.write_table is used with fixed row-group size so the binary layout
    is stable across PyArrow patch versions.
  - All print() calls use ASCII only to avoid cp1252 encoding errors on Windows.

Usage:
    python scripts/generate_sensors.py

Approved dependencies: numpy, pandas, pyarrow, pyyaml.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SEED: int = 42
HEALTHY_PER_CLASS: int = 600  # >= 500 as required

SENSORS: list[str] = [
    "vibration_rms",
    "bearing_temp_de",
    "bearing_temp_nde",
    "motor_current",
    "discharge_pressure",
    "flow_rate",
    "oil_level_pct",
    "rpm",
    "suction_pressure",
]

# Nominal values for healthy state — aligned with data/baselines.yaml
NOMINALS: dict[str, dict[str, float]] = {
    "centrifugal_pump": {
        "vibration_rms":      2.5,
        "bearing_temp_de":   65.0,
        "bearing_temp_nde":  60.0,
        "motor_current":     42.0,
        "discharge_pressure": 6.5,
        "flow_rate":        185.0,
        "oil_level_pct":     75.0,
        "rpm":             2950.0,
        "suction_pressure":   0.8,
    },
    "industrial_gearbox": {
        "vibration_rms":      1.8,
        "bearing_temp_de":   55.0,
        "bearing_temp_nde":  50.0,
        "motor_current":     38.0,
        "discharge_pressure": 4.2,
        "flow_rate":        120.0,
        "oil_level_pct":     70.0,
        "rpm":             1475.0,
        "suction_pressure":   0.5,
    },
}

# Standard deviations for healthy Gaussian noise (realistic operational spread)
STDEVS: dict[str, dict[str, float]] = {
    "centrifugal_pump": {
        "vibration_rms":      0.3,
        "bearing_temp_de":    2.0,
        "bearing_temp_nde":   1.8,
        "motor_current":      0.8,
        "discharge_pressure": 0.15,
        "flow_rate":          5.0,
        "oil_level_pct":      2.0,
        "rpm":               12.0,
        "suction_pressure":   0.04,
    },
    "industrial_gearbox": {
        "vibration_rms":      0.2,
        "bearing_temp_de":    1.5,
        "bearing_temp_nde":   1.4,
        "motor_current":      0.7,
        "discharge_pressure": 0.12,
        "flow_rate":          4.0,
        "oil_level_pct":      2.0,
        "rpm":                8.0,
        "suction_pressure":   0.03,
    },
}

# Asset IDs to embed in the healthy snapshot metadata
ASSET_IDS: dict[str, list[str]] = {
    "centrifugal_pump":   ["PUMP-01", "PUMP-02", "PUMP-03", "PUMP-04", "PUMP-05"],
    "industrial_gearbox": ["GEAR-01", "GEAR-02", "GEAR-03"],
}

# ---------------------------------------------------------------------------
# Fault-signature definitions
# Each entry maps scenario_id → {sensor: multiplier or additive delta, mode: "mult"|"add"}
# Fault signature rationale is documented per scenario below.
# ---------------------------------------------------------------------------

FAULT_SIGNATURES: dict[str, dict[str, Any]] = {
    # Bearing degradation: spalling raises vibration 3.1× nominal; bearing temp +24 °C
    # NDE temp slightly elevated; motor current marginally up (+3 A) due to mechanical drag.
    "bearing_degradation": {
        "asset_id":    "PUMP-02",
        "asset_class": "centrifugal_pump",
        "error_code":  "E-107",
        "deltas": {
            "vibration_rms":     ("mult", 3.12),   # 2.5 × 3.12 = 7.80 mm/s (alarm)
            "bearing_temp_de":   ("add",  24.0),   # 65 + 24 = 89 °C (alarm)
            "bearing_temp_nde":  ("add",   8.5),   # 60 + 8.5 = 68.5 °C (warn)
            "motor_current":     ("add",   3.2),   # 42 + 3.2 = 45.2 A (warn)
            "discharge_pressure":("add",  -0.2),
            "flow_rate":         ("add",  -4.0),
        },
    },
    # Cavitation: NPSHa collapse. Suction pressure critically low; discharge and flow drop;
    # vibration erratic (2.04× due to impeller erosion and vapour collapse).
    "cavitation": {
        "asset_id":    "PUMP-03",
        "asset_class": "centrifugal_pump",
        "error_code":  "E-102",
        "deltas": {
            "suction_pressure":   ("mult", 0.20),  # 0.8 × 0.20 = 0.16 bar (alarm)
            "discharge_pressure": ("mult", 0.554), # 6.5 × 0.554 = 3.60 bar (alarm)
            "flow_rate":          ("mult", 0.524), # 185 × 0.524 = 97.0 m3/h (alarm)
            "vibration_rms":      ("mult", 2.04),  # 2.5 × 2.04 = 5.1 mm/s (warn)
            "motor_current":      ("add",  -6.0),  # 42 − 6 = 36 A (reduced, less work done)
        },
    },
    # Misalignment on gearbox: dominant 1×/2× vibration; temps mildly elevated.
    "misalignment": {
        "asset_id":    "GEAR-01",
        "asset_class": "industrial_gearbox",
        "error_code":  "G-114",
        "deltas": {
            "vibration_rms":    ("mult", 2.61),  # 1.8 × 2.61 = 4.7 mm/s (alarm)
            "bearing_temp_de":  ("add",   6.0),  # 55 + 6 = 61 °C (warn)
            "bearing_temp_nde": ("add",   6.5),  # 50 + 6.5 = 56.5 °C (warn)
            "motor_current":    ("add",   2.1),  # slight increase due to misaligned coupling drag
        },
    },
    # Lubrication failure: oil level critically low; both bearing temps in alarm band.
    "lubrication_failure": {
        "asset_id":    "PUMP-04",
        "asset_class": "centrifugal_pump",
        "error_code":  "E-204",
        "deltas": {
            "oil_level_pct":    ("mult", 0.293), # 75 × 0.293 = 22.0% (alarm)
            "bearing_temp_de":  ("add",  26.4),  # 65 + 26.4 = 91.4 °C (alarm)
            "bearing_temp_nde": ("add",  23.5),  # 60 + 23.5 = 83.5 °C (alarm)
            "vibration_rms":    ("mult", 2.32),  # 2.5 × 2.32 = 5.8 mm/s (warn)
            "motor_current":    ("add",   1.8),
        },
    },
    # Motor overload: current 39% above rated; rpm below warn-low (motor struggling).
    "motor_overload_phase_imbalance": {
        "asset_id":    "PUMP-05",
        "asset_class": "centrifugal_pump",
        "error_code":  "E-301",
        "deltas": {
            "motor_current":    ("mult", 1.393), # 42 × 1.393 = 58.5 A (alarm)
            "rpm":              ("add",  -135.0),# 2950 − 135 = 2815 rpm (warn)
            "vibration_rms":    ("mult", 1.92),  # 2.5 × 1.92 = 4.8 mm/s (warn)
            "bearing_temp_de":  ("add",  11.5),  # 65 + 11.5 = 76.5 °C (warn)
            "discharge_pressure":("add", -0.6),
            "flow_rate":        ("add",  -17.0),
        },
    },
    # Clogged filter: strainer blind; suction pressure drops; flow/discharge reduced.
    "clogged_filter": {
        "asset_id":    "PUMP-01",
        "asset_class": "centrifugal_pump",
        "error_code":  "E-111",
        "deltas": {
            "suction_pressure":   ("mult", 0.275), # 0.8 × 0.275 = 0.22 bar (alarm)
            "discharge_pressure": ("mult", 0.631), # 6.5 × 0.631 = 4.1 bar (warn)
            "flow_rate":          ("mult", 0.546), # 185 × 0.546 = 101 m3/h (alarm)
            "vibration_rms":      ("mult", 1.24),  # 2.5 × 1.24 = 3.1 mm/s (warn)
            "motor_current":      ("add",  -4.5),  # less hydraulic work done
        },
    },
    # Unknown code: all sensors near nominal — the code E-999 is what triggers refusal.
    "unknown_code_E999": {
        "asset_id":    "GEAR-02",
        "asset_class": "industrial_gearbox",
        "error_code":  "E-999",
        "deltas": {
            "vibration_rms":    ("add",  0.2),   # very slight noise, within normal
            "bearing_temp_de":  ("add",  1.0),
            "bearing_temp_nde": ("add",  1.5),
            "motor_current":    ("add",  0.8),
        },
    },
}

# ---------------------------------------------------------------------------
# Correlation matrix (lower triangular, sensors in SENSORS order)
# Reflects real-world coupling: current ~ flow ~ pressure; temps ~ each other.
# ---------------------------------------------------------------------------

# Correlation coefficient matrix for centrifugal_pump sensors (order = SENSORS list)
# Off-diagonal entries encode physics-based relationships:
#   motor_current <-> flow_rate:        0.70  (more flow = more motor load)
#   motor_current <-> discharge_pressure: 0.55  (higher back-pressure = higher current)
#   flow_rate <-> suction_pressure:     0.50  (better suction → more flow)
#   bearing_temp_de <-> bearing_temp_nde: 0.75 (same oil supply, similar environment)
_PUMP_CORR: list[list[float]] = [
    # vib    bde   bnde  curr  pdis   flow   oil   rpm   psuc
    [1.00,  0.20,  0.15,  0.10,  0.00,  0.00,  0.00,  0.05,  0.00],
    [0.20,  1.00,  0.75,  0.10,  0.00, -0.10, -0.25,  0.05, -0.10],
    [0.15,  0.75,  1.00,  0.08,  0.00, -0.08, -0.20,  0.05, -0.08],
    [0.10,  0.10,  0.08,  1.00,  0.55,  0.70,  0.00,  0.40,  0.35],
    [0.00,  0.00,  0.00,  0.55,  1.00,  0.60,  0.00,  0.35,  0.45],
    [0.00, -0.10, -0.08,  0.70,  0.60,  1.00,  0.00,  0.30,  0.50],
    [0.00, -0.25, -0.20,  0.00,  0.00,  0.00,  1.00,  0.00,  0.00],
    [0.05,  0.05,  0.05,  0.40,  0.35,  0.30,  0.00,  1.00,  0.15],
    [0.00, -0.10, -0.08,  0.35,  0.45,  0.50,  0.00,  0.15,  1.00],
]

# Same structure for gearbox (slightly different correlations)
_GEAR_CORR: list[list[float]] = [
    [1.00,  0.25,  0.20,  0.12,  0.00,  0.00,  0.00,  0.05,  0.00],
    [0.25,  1.00,  0.72,  0.10,  0.00, -0.08, -0.22,  0.05, -0.08],
    [0.20,  0.72,  1.00,  0.08,  0.00, -0.06, -0.18,  0.04, -0.06],
    [0.12,  0.10,  0.08,  1.00,  0.50,  0.65,  0.00,  0.38,  0.30],
    [0.00,  0.00,  0.00,  0.50,  1.00,  0.55,  0.00,  0.30,  0.40],
    [0.00, -0.08, -0.06,  0.65,  0.55,  1.00,  0.00,  0.28,  0.45],
    [0.00, -0.22, -0.18,  0.00,  0.00,  0.00,  1.00,  0.00,  0.00],
    [0.05,  0.05,  0.04,  0.38,  0.30,  0.28,  0.00,  1.00,  0.12],
    [0.00, -0.08, -0.06,  0.30,  0.40,  0.45,  0.00,  0.12,  1.00],
]


def _make_corr_matrix(raw: list[list[float]]) -> np.ndarray:
    """Symmetrise and project to the nearest positive-semidefinite correlation matrix.

    Why: hand-crafted correlation matrices can violate PSD constraints due to
    floating-point inconsistencies. We clip negative eigenvalues to a small epsilon
    and rescale to restore unit diagonal, guaranteeing numpy accepts the matrix.
    """
    m = np.array(raw)
    # Symmetrise
    corr = m + m.T - np.diag(np.diag(m))
    # Project to nearest PSD: clip eigenvalues to >= epsilon
    eigvals, eigvecs = np.linalg.eigh(corr)
    epsilon = 1e-8
    eigvals_clipped = np.maximum(eigvals, epsilon)
    corr_psd = eigvecs @ np.diag(eigvals_clipped) @ eigvecs.T
    # Restore unit diagonal (rescale so correlation interpretation is preserved)
    d = np.sqrt(np.diag(corr_psd))
    corr_normalised = corr_psd / np.outer(d, d)
    return corr_normalised


def _corr_to_cov(
    corr: np.ndarray, stdevs: dict[str, float]
) -> np.ndarray:
    """Convert a correlation matrix + per-sensor std devs to a covariance matrix."""
    sd = np.array([stdevs[s] for s in SENSORS])
    return corr * np.outer(sd, sd)


def _generate_healthy_class(
    asset_class: str,
    n: int,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """Generate `n` healthy sensor snapshots for the given asset class.

    Uses multivariate Gaussian with realistic inter-sensor correlations.
    Clips values to physically plausible minima (e.g. vibration > 0).
    """
    nominals = NOMINALS[asset_class]
    stdevs = STDEVS[asset_class]
    corr_raw = _PUMP_CORR if asset_class == "centrifugal_pump" else _GEAR_CORR
    corr = _make_corr_matrix(corr_raw)
    cov = _corr_to_cov(corr, stdevs)
    mean = np.array([nominals[s] for s in SENSORS])

    # Draw correlated samples
    samples = rng.multivariate_normal(mean, cov, size=n)

    # Clip physical bounds (no negative vibration, temperature, pressure, flow)
    mins = [0.1, 20.0, 20.0, 0.0, 0.05, 30.0, 0.0, 500.0, 0.05]
    maxs = [15.0, 120.0, 115.0, 70.0, 10.0, 280.0, 100.0, 3200.0, 3.0]
    for i, (lo, hi) in enumerate(zip(mins, maxs)):
        samples[:, i] = np.clip(samples[:, i], lo, hi)

    df = pd.DataFrame(samples, columns=SENSORS)
    df.insert(0, "asset_class", asset_class)

    # Round per-sensor to meaningful decimal places
    df["vibration_rms"]      = df["vibration_rms"].round(2)
    df["bearing_temp_de"]    = df["bearing_temp_de"].round(1)
    df["bearing_temp_nde"]   = df["bearing_temp_nde"].round(1)
    df["motor_current"]      = df["motor_current"].round(1)
    df["discharge_pressure"] = df["discharge_pressure"].round(2)
    df["flow_rate"]          = df["flow_rate"].round(1)
    df["oil_level_pct"]      = df["oil_level_pct"].round(1)
    df["rpm"]                = df["rpm"].round(0)
    df["suction_pressure"]   = df["suction_pressure"].round(3)

    return df


def _apply_fault_signature(
    asset_class: str,
    sig: dict[str, Any],
    rng: np.random.Generator,
) -> dict[str, float]:
    """Apply a fault signature to the healthy nominal vector.

    Returns a dict of sensor → faulted value (rounded to same precision as healthy data).
    Small Gaussian noise is added to avoid perfectly deterministic integers in the output.
    """
    nominals = NOMINALS[asset_class]
    noise_scale = {s: STDEVS[asset_class][s] * 0.1 for s in SENSORS}
    result: dict[str, float] = {}
    for sensor in SENSORS:
        base = nominals[sensor]
        noise = float(rng.normal(0.0, noise_scale[sensor]))
        if sensor in sig["deltas"]:
            mode, param = sig["deltas"][sensor]
            if mode == "mult":
                faulted = base * param + noise
            else:  # "add"
                faulted = base + param + noise
        else:
            faulted = base + noise
        result[sensor] = round(faulted, 3)

    # Clip to physical minima
    result["vibration_rms"]      = max(0.1, result["vibration_rms"])
    result["bearing_temp_de"]    = max(20.0, result["bearing_temp_de"])
    result["bearing_temp_nde"]   = max(20.0, result["bearing_temp_nde"])
    result["motor_current"]      = max(0.0, result["motor_current"])
    result["discharge_pressure"] = max(0.05, result["discharge_pressure"])
    result["flow_rate"]          = max(10.0, result["flow_rate"])
    result["oil_level_pct"]      = max(0.0, min(100.0, result["oil_level_pct"]))
    result["rpm"]                = max(100.0, result["rpm"])
    result["suction_pressure"]   = max(0.01, result["suction_pressure"])
    return result


def generate_healthy(out_path: Path, rng: np.random.Generator) -> None:
    """Generate healthy baseline snapshots for both asset classes."""
    frames: list[pd.DataFrame] = []
    for asset_class in ["centrifugal_pump", "industrial_gearbox"]:
        df = _generate_healthy_class(asset_class, HEALTHY_PER_CLASS, rng)
        frames.append(df)
    healthy = pd.concat(frames, ignore_index=True)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    table = pa.Table.from_pandas(healthy, preserve_index=False)
    # Fixed row_group_size for byte-stable output across re-runs
    pq.write_table(table, out_path, row_group_size=200, compression="snappy")
    # Use ASCII arrow to avoid cp1252 encoding errors on Windows
    print("  Wrote %d healthy snapshots -> %s" % (len(healthy), out_path))


def generate_fault_snapshots(out_dir: Path, rng: np.random.Generator) -> None:
    """Generate one faulted snapshot per scenario."""
    out_dir.mkdir(parents=True, exist_ok=True)
    for scenario_id, sig in FAULT_SIGNATURES.items():
        asset_class: str = sig["asset_class"]
        sensors = _apply_fault_signature(asset_class, sig, rng)
        payload: dict[str, Any] = {
            "scenario_id": scenario_id,
            "asset_id":    sig["asset_id"],
            "asset_class": asset_class,
            "error_code":  sig["error_code"],
            "seed":        SEED,
            "sensors":     sensors,
            "fault_signature_params": {
                k: list(v) for k, v in sig["deltas"].items()
            },
        }
        out_file = out_dir / f"{scenario_id}.json"
        with open(out_file, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
        print("  Wrote fault snapshot -> %s" % out_file)


def main() -> None:
    print("generate_sensors.py - fixed seed: %d" % SEED)
    # Single RNG instance; order of calls is deterministic by construction.
    rng = np.random.default_rng(SEED)

    project_root = Path(__file__).parent.parent
    healthy_path = project_root / "data" / "snapshots" / "healthy.parquet"
    faults_dir   = project_root / "data" / "snapshots" / "faults"

    print("Generating healthy snapshots ...")
    generate_healthy(healthy_path, rng)

    print("Generating fault snapshots ...")
    generate_fault_snapshots(faults_dir, rng)

    print("Done.")


if __name__ == "__main__":
    main()
