#!/usr/bin/env python3
"""scripts/generate_history.py — Synthetic maintenance work-order generator for SENTRY S0.

Generates:
  data/history/work_orders.parquet
  data/history/work_orders.csv

Design decisions:
  - Fixed seed (SEED = 42) for full determinism.
  - 8 assets across two classes; 210 work orders.
  - Date range: 2023-01-01 to 2026-09-17 (day before data cut-off).
  - Fault codes drawn from the corpus error-code tables (E-xxx for pumps, G-xxx for gearboxes).
  - Realistic maintenance vocabulary for actions, parts, and technician notes.

Usage:
    python scripts/generate_history.py

Approved dependencies: numpy, pandas, pyarrow.
"""

from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SEED: int = 42
TARGET_ROWS: int = 210

ASSETS: list[dict[str, str]] = [
    {"asset_id": "PUMP-01", "asset_class": "centrifugal_pump"},
    {"asset_id": "PUMP-02", "asset_class": "centrifugal_pump"},
    {"asset_id": "PUMP-03", "asset_class": "centrifugal_pump"},
    {"asset_id": "PUMP-04", "asset_class": "centrifugal_pump"},
    {"asset_id": "PUMP-05", "asset_class": "centrifugal_pump"},
    {"asset_id": "GEAR-01", "asset_class": "industrial_gearbox"},
    {"asset_id": "GEAR-02", "asset_class": "industrial_gearbox"},
    {"asset_id": "GEAR-03", "asset_class": "industrial_gearbox"},
]

# Error codes drawn from the corpus (recognised codes only — no E-999)
PUMP_FAULT_CODES: list[str] = [
    "E-101", "E-102", "E-103", "E-104", "E-105", "E-107", "E-108",
    "E-109", "E-111", "E-112", "E-201", "E-202", "E-203", "E-204",
    "E-205", "E-301", "E-302", "E-303", "E-304",
]
GEAR_FAULT_CODES: list[str] = [
    "G-101", "G-102", "G-103", "G-104", "G-105", "G-106", "G-107",
    "G-108", "G-109", "G-110", "G-111", "G-112", "G-114", "G-115",
    "G-201", "G-202", "G-203", "G-205", "G-207",
]

PUMP_ACTIONS: list[str] = [
    "Replaced drive-end bearing; refilled oil to mid-level",
    "Serviced suction strainer; cleaned basket; restored DP to normal",
    "Realigned shaft coupling using laser system; verified < 0.05 mm TIR",
    "Changed bearing housing oil (ISO VG 46); flushed sump",
    "Replaced mechanical seal cartridge SFT-CS100; tested zero leakage",
    "Investigated motor overload; confirmed phase imbalance corrected at MCC",
    "Replaced non-drive-end bearing; re-torqued cover plate to 45 Nm",
    "Re-primed pump after air-lock; vented casing; confirmed suction pressure normal",
    "Inspected coupling insert; replaced worn rubber spider",
    "Performed insulation resistance test on motor; IR > 200 MΩ — passed",
    "Cleared blocked discharge check valve; valve seat re-ground",
    "Adjusted impeller clearance; measured wear ring gap at 0.4 mm — within tolerance",
    "Oil change and filter replacement; oil sample sent to laboratory",
    "Inspected and re-torqued all suction and discharge flange bolts to 95 Nm",
    "Reset motor overload relay after confirming shaft turns freely",
    "Replaced drain plug with new PTFE tape; confirmed no leakage after restart",
    "Performed full vibration baseline measurement; results logged to CMMS",
    "Completed quarterly PM inspection; all checks normal — no defects found",
]

GEAR_ACTIONS: list[str] = [
    "Changed gearbox oil (ISO VG 150); drained 3.2 L, refilled to mid-level",
    "Realigned input shaft using laser alignment system; offset < 0.05 mm",
    "Replaced input shaft seal (65×90×10 NBR); confirmed zero leakage",
    "Inspected gear mesh through top cover; no pitting; cover refitted and torqued",
    "Replaced oil filter element (25 µm); ΔP reduced to < 0.2 bar after change",
    "Investigated G-108 alarm; found drain plug loose; re-torqued and added 0.6 L oil",
    "Replaced input coupling insert (polyurethane); re-aligned after fitting",
    "Checked and tightened all foot mounting bolts; soft-foot corrected with 0.3 mm shim",
    "Performed bearing condition assessment; axial play 0.18 mm — within tolerance",
    "Oil sampling submitted to laboratory; results showed elevated iron (12 ppm) — monitoring",
    "Cleaned and replaced breather/vent element; blocked element causing pressure build-up",
    "Investigated overload alarm G-207; confirmed downstream jam cleared; restarted",
    "Full PM inspection: oil level, coupling guard, vibration baseline — all normal",
    "Replaced output shaft seal (75×100×12 NBR); no further oil loss",
]

PUMP_PARTS: list[list[str]] = [
    ["Bearing SKF 6209-2RS (DE)"],
    ["Strainer basket (316 SS)"],
    ["Coupling insert (rubber spider)"],
    ["ISO VG 46 oil 1 L"],
    ["Mechanical seal SFT-CS100"],
    [],
    ["Bearing SKF 6207-2RS (NDE)"],
    [],
    ["Coupling insert (rubber spider)"],
    [],
    [],
    ["Wear ring (impeller, bronze)"],
    ["ISO VG 46 oil 1 L", "Oil filter element"],
    [],
    [],
    ["Drain plug (1/2 NPT SS)", "PTFE tape"],
    [],
    [],
]

GEAR_PARTS: list[list[str]] = [
    ["ISO VG 150 gear oil 4 L"],
    [],
    ["Input shaft seal (65x90x10 NBR)"],
    ["Inspection cover gasket"],
    ["Oil filter element (25 µm)"],
    ["Drain plug (1 BSP SS)", "PTFE tape", "ISO VG 150 gear oil 0.6 L"],
    ["Input coupling insert (polyurethane)"],
    ["Stainless shims 0.3 mm"],
    [],
    [],
    ["Breather element"],
    [],
    [],
    ["Output shaft seal (75x100x12 NBR)"],
]

PUMP_NOTES_TEMPLATES: list[str] = [
    "Vibration {vib:.1f} mm/s before job, {vib2:.1f} mm/s after. Bearing temp normalised within 30 min.",
    "Strainer DP was {dp:.2f} bar; after clean DP reduced to 0.04 bar. Debris mainly scale.",
    "Pre-alignment offset {pre:.3f} mm TIR; post-alignment {post:.3f} mm TIR.",
    "Oil drained: amber colour, slight dark sludge, no water contamination.",
    "Seal showing zero leakage at 6.5 bar discharge. Run test 30 min.",
    "Phase imbalance was {imb:.1f}% — corrected at MCC distribution board.",
    "Bearing removed; raceway showed early spalling. Replaced as precaution.",
    "Air-lock in suction line traced to open vent valve upstream. Valve closed.",
    "Coupling insert crumbling; replaced. Re-aligned to 0.03 mm TIR.",
    "IR measured 210 MΩ at 500 V DC. PI = 2.4. Insulation in good condition.",
    "Check valve seat worn; re-ground in situ. Valve seats correctly after work.",
    "Wear ring gap measured at {gap:.2f} mm (limit 0.80 mm). Acceptable.",
    "Oil sample sent to EOS Lubricants ref {ref}. Iron 8 ppm, no water.",
    "All bolts torqued to 95 Nm (suction) and 65 Nm (discharge). No leaks.",
    "Relay reset. Motor restarted without re-trip. Current balanced at {curr:.1f} A.",
    "Drain plug re-torqued 38 Nm with PTFE tape. No further leakage after 24 h check.",
    "Vibration baseline recorded: 2.4 mm/s DE, 2.2 mm/s NDE. Within normal.",
    "All items on PM checklist completed and signed. No defects identified.",
]

GEAR_NOTES_TEMPLATES: list[str] = [
    "Oil drained {vol:.1f} L; mild metallic sheen in drained oil — normal for service interval. Refilled 3.2 L.",
    "Pre-alignment radial offset {pre:.3f} mm; corrected to {post:.3f} mm. Foot bolts torqued 285 Nm.",
    "Seal lip worn on shaft contact face; shaft surface smooth — no re-grinding required.",
    "Gear flanks: uniform contact pattern >75% face width. No pitting. Backlash 0.12 mm.",
    "Filter ΔP was 1.8 bar before; 0.15 bar after element replacement.",
    "Oil level was 20 mm below low mark. Drain plug loose by 1.5 turns. Cause: vibration loosening.",
    "Coupling insert cracked; replaced. Post-coupling alignment 0.04 mm TIR.",
    "Soft-foot measured 0.08 mm at rear-left foot; corrected with 0.3 mm shim. Bolt torque 290 Nm.",
    "Axial play input shaft: 0.18 mm (limit 0.25 mm). NDE play 0.14 mm. Both acceptable.",
    "Oil sample result: Fe {fe} ppm, Cu {cu} ppm, particle count ISO 4406 18/16/13. Monitoring.",
    "Breather element collapsed inward; internal pressure 0.08 bar above ambient before cleaning.",
    "Downstream conveyor jam cleared. Gearbox sustained G-207 for approx. 4 s. No damage found.",
    "PM: oil level mid-glass, coupling guard secure, vibration 1.7 mm/s OA — normal.",
    "Seal replaced; post-repair run: zero leakage at all operating speeds.",
]

TECHNICIANS: list[str] = [
    "R. Mehta", "S. Okafor", "J. Hartley", "P. Gupta", "A. Kowalski",
    "T. Williams", "F. Nkosi", "L. Andersen", "V. Krishnamurthy", "B. Santos",
]

START_DATE: date = date(2023, 1, 1)
END_DATE:   date = date(2026, 9, 17)


def _random_date(rng: np.random.Generator, start: date, end: date) -> date:
    """Return a uniformly random date in [start, end]."""
    delta = (end - start).days
    offset = int(rng.integers(0, delta + 1))
    return start + timedelta(days=offset)


def _generate_note(
    py_rng: random.Random,
    notes_templates: list[str],
    asset_class: str,
) -> str:
    """Fill a random notes template with plausible numeric values."""
    template = py_rng.choice(notes_templates)
    try:
        return template.format(
            vib=py_rng.uniform(4.5, 9.0),
            vib2=py_rng.uniform(1.8, 2.8),
            dp=py_rng.uniform(0.35, 0.65),
            pre=py_rng.uniform(0.10, 0.30),
            post=py_rng.uniform(0.02, 0.05),
            imb=py_rng.uniform(6.0, 14.0),
            gap=py_rng.uniform(0.30, 0.60),
            ref=f"EOS-{py_rng.randint(10000, 99999)}",
            curr=py_rng.uniform(40.0, 45.0),
            vol=py_rng.uniform(3.0, 3.3),
            fe=py_rng.randint(5, 25),
            cu=py_rng.randint(1, 8),
        )
    except KeyError:
        # Template has no format placeholders — return as-is
        return template


def generate_history(out_dir: Path, rng: np.random.Generator) -> pd.DataFrame:
    """Generate work-order history rows."""
    # Use a Python stdlib RNG seeded from numpy so both are deterministic
    py_seed = int(rng.integers(0, 2**31))
    py_rng = random.Random(py_seed)

    rows: list[dict[str, object]] = []
    wo_counter: int = 10001

    for i in range(TARGET_ROWS):
        # Cycle through assets so each asset gets roughly equal coverage
        asset = ASSETS[i % len(ASSETS)]
        asset_class = asset["asset_class"]

        is_pump = asset_class == "centrifugal_pump"
        fault_codes = PUMP_FAULT_CODES if is_pump else GEAR_FAULT_CODES
        actions     = PUMP_ACTIONS     if is_pump else GEAR_ACTIONS
        parts_opts  = PUMP_PARTS       if is_pump else GEAR_PARTS
        notes_tmpl  = PUMP_NOTES_TEMPLATES if is_pump else GEAR_NOTES_TEMPLATES

        fault_code  = py_rng.choice(fault_codes)
        action_idx  = py_rng.randrange(len(actions))
        action      = actions[action_idx]
        parts_raw   = parts_opts[action_idx % len(parts_opts)]
        parts_str   = "; ".join(parts_raw) if parts_raw else "None"
        note        = _generate_note(py_rng, notes_tmpl, asset_class)
        wo_date     = _random_date(rng, START_DATE, END_DATE)
        downtime    = int(rng.integers(15, 480))  # 15 min to 8 h

        rows.append({
            "wo_id":             f"WO-{wo_counter}",
            "asset_id":          asset["asset_id"],
            "asset_class":       asset_class,
            "date":              wo_date.isoformat(),
            "fault_code":        fault_code,
            "action_taken":      action,
            "parts_replaced":    parts_str,
            "technician_notes":  note,
            "downtime_min":      downtime,
            "technician":        py_rng.choice(TECHNICIANS),
        })
        wo_counter += 1

    df = pd.DataFrame(rows)
    # Sort by date for readability
    df = df.sort_values("date").reset_index(drop=True)
    return df


def main() -> None:
    print("generate_history.py - fixed seed:", SEED)
    rng = np.random.default_rng(SEED)

    project_root = Path(__file__).parent.parent
    out_dir = project_root / "data" / "history"
    out_dir.mkdir(parents=True, exist_ok=True)

    df = generate_history(out_dir, rng)

    parquet_path = out_dir / "work_orders.parquet"
    csv_path     = out_dir / "work_orders.csv"

    table = pa.Table.from_pandas(df, preserve_index=False)
    pq.write_table(table, parquet_path, row_group_size=50, compression="snappy")
    df.to_csv(csv_path, index=False)

    print(f"  Wrote {len(df)} work orders -> {parquet_path}")
    print(f"  Wrote CSV copy          -> {csv_path}")
    print(f"  Assets covered: {df['asset_id'].nunique()} ({', '.join(sorted(df['asset_id'].unique()))})")
    print("Done.")


if __name__ == "__main__":
    main()
