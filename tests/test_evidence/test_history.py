"""tests/test_evidence/test_history.py — Tests for maintenance history feature calculations."""

from __future__ import annotations

from datetime import datetime, timezone

from evidence.history import get_history_features


def test_history_features_pump07() -> None:
    """Assert days_since_service, same_code_90d, and recent_parts for PUMP-07."""
    captured_at = datetime(2026, 9, 18, 9, 14, 0, tzinfo=timezone.utc)

    # Synthetic test records for PUMP-07:
    # 1. 2026-02-16 (214 days prior): parts: seal_kit, lube_filter, code: E-204
    # 2. 2026-07-10 (70 days prior): parts: oil_seal, code: E-204
    # 3. 2026-08-25 (24 days prior): parts: gasket, code: E-204
    history_records = [
        {
            "asset_id": "PUMP-07",
            "date": "2026-02-16T00:00:00Z",
            "fault_code": "E-204",
            "parts_replaced": ["seal_kit", "lube_filter"],
        },
        {
            "asset_id": "PUMP-07",
            "date": "2026-07-10T00:00:00Z",
            "fault_code": "E-204",
            "parts_replaced": ["oil_seal"],
        },
        {
            "asset_id": "PUMP-07",
            "date": "2026-08-25T00:00:00Z",
            "fault_code": "E-204",
            "parts_replaced": ["gasket"],
        },
    ]

    features = get_history_features(
        asset_id="PUMP-07",
        error_code="E-204",
        captured_at=captured_at,
        history_records=history_records,
    )

    # 1. Last service event was 2026-08-25 (24 days before 2026-09-18)
    assert features.days_since_service == 24

    # 2. Occurrences of E-204 in last 90 days (since 2026-06-20): 2026-07-10 and 2026-08-25 -> 2 times
    assert features.same_code_90d == 2

    # 3. Parts replaced in last 60 days (since 2026-07-20): 2026-08-25 -> ["gasket"]
    assert features.recent_parts == ["gasket"]


def test_history_features_unknown_asset() -> None:
    """Assert unknown asset returns clean default features."""
    captured_at = datetime(2026, 9, 18, 9, 14, 0, tzinfo=timezone.utc)
    features = get_history_features(
        asset_id="UNKNOWN-99",
        error_code="E-999",
        captured_at=captured_at,
        history_records=[],
    )

    assert features.days_since_service == 365
    assert features.same_code_90d == 0
    assert features.recent_parts == []
