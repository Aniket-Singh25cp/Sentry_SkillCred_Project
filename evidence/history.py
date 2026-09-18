"""evidence/history.py — Maintenance history feature extraction.

Computes days_since_service, same_code_90d, and recent_parts from maintenance history data.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import pandas as pd

from core.schemas import HistoryFeatures

# Default synthetic maintenance history table for test assets
DEFAULT_HISTORY_TABLE: list[dict[str, Any]] = [
    {
        "asset_id": "PUMP-07",
        "date": "2026-02-16T00:00:00Z",  # 214 days before 2026-09-18
        "fault_code": "E-204",
        "action_taken": "Replaced mechanical seal and lubricated bearings.",
        "parts_replaced": ["seal_kit", "lube_filter"],
    },
    {
        "asset_id": "PUMP-07",
        "date": "2026-07-10T00:00:00Z",  # 70 days before 2026-09-18
        "fault_code": "E-204",
        "action_taken": "Topped up oil reservoir and checked alignment.",
        "parts_replaced": ["oil_seal"],
    },
    {
        "asset_id": "PUMP-07",
        "date": "2026-08-25T00:00:00Z",  # 24 days before 2026-09-18
        "fault_code": "E-204",
        "action_taken": "Inspected bearing housing.",
        "parts_replaced": ["gasket"],
    },
    {
        "asset_id": "COMP-01",
        "date": "2026-05-01T00:00:00Z",
        "fault_code": "E-101",
        "action_taken": "General overhaul.",
        "parts_replaced": ["valves"],
    },
    {
        "asset_id": "GEAR-02",
        "date": "2026-03-15T00:00:00Z",
        "fault_code": "E-301",
        "action_taken": "Oil flush and replacement.",
        "parts_replaced": ["gear_oil"],
    },
]


def _normalize_dt(dt: datetime | str) -> datetime:
    """Parse string or normalize datetime to UTC timezone-aware or naive comparison."""
    if isinstance(dt, str):
        parsed = pd.to_datetime(dt)
        if parsed.tzinfo is not None:
            return parsed.tz_convert("UTC").to_pydatetime()
        return parsed.to_pydatetime().replace(tzinfo=timezone.utc)
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc)
    return dt.replace(tzinfo=timezone.utc)


def get_history_features(
    asset_id: str,
    error_code: str | None,
    captured_at: datetime,
    history_records: list[dict[str, Any]] | pd.DataFrame | None = None,
) -> HistoryFeatures:
    """Extract maintenance history features for an asset.

    Calculates:
      - days_since_service: days since last recorded service event prior to captured_at.
      - same_code_90d: count of occurrences of the same error_code on this asset in the 90 days before captured_at.
      - recent_parts: list of unique parts replaced on this asset in the 60 days before captured_at.
    """
    target_dt = _normalize_dt(captured_at)

    records: list[dict[str, Any]] = []
    if history_records is not None:
        if isinstance(history_records, pd.DataFrame):
            records = history_records.to_dict(orient="records")
        elif isinstance(history_records, list):
            records = history_records
    else:
        records = DEFAULT_HISTORY_TABLE

    # Filter to asset records occurring on or before captured_at
    asset_records: list[tuple[datetime, dict[str, Any]]] = []
    for rec in records:
        if str(rec.get("asset_id", "")) == asset_id:
            rec_dt = _normalize_dt(rec.get("date", target_dt))
            if rec_dt <= target_dt:
                asset_records.append((rec_dt, rec))

    if not asset_records:
        return HistoryFeatures(
            days_since_service=365,
            same_code_90d=0,
            recent_parts=[],
        )

    # Sort records descending by date
    asset_records.sort(key=lambda x: x[0], reverse=True)

    # 1. days_since_service
    last_service_dt = asset_records[0][0]
    days_since_service = max(0, (target_dt - last_service_dt).days)

    # 2. same_code_90d
    cutoff_90d = target_dt - timedelta(days=90)
    same_code_count = 0
    if error_code:
        for rec_dt, rec in asset_records:
            if rec_dt >= cutoff_90d and str(rec.get("fault_code", "")) == error_code:
                same_code_count += 1

    # 3. recent_parts (parts replaced in last 60 days)
    cutoff_60d = target_dt - timedelta(days=60)
    recent_parts_set: set[str] = set()

    for rec_dt, rec in asset_records:
        if rec_dt >= cutoff_60d:
            parts = rec.get("parts_replaced", [])
            if isinstance(parts, list):
                for p in parts:
                    recent_parts_set.add(str(p))

    return HistoryFeatures(
        days_since_service=days_since_service,
        same_code_90d=same_code_count,
        recent_parts=sorted(recent_parts_set),
    )
