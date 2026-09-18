"""tests/test_evidence/test_engine.py — Tests for main build_evidence_report orchestrator."""

from __future__ import annotations

from datetime import datetime, timezone

from core.schemas import DiagnoseRequest, EvidenceReport, SensorReading
from evidence.engine import build_evidence_report, lookup_error_code


def test_lookup_error_code_recognized() -> None:
    """Exact match for known error code E-204 returns status recognized."""
    res = lookup_error_code("E-204")
    assert res.code == "E-204"
    assert res.status == "recognized"
    assert res.meaning == "Lubrication pressure low"


def test_lookup_error_code_unrecognized() -> None:
    """Unknown code E-999 yields status unrecognized (DO NOT guess or fuzzy-match)."""
    res = lookup_error_code("E-999")
    assert res.code == "E-999"
    assert res.status == "unrecognized"
    assert res.meaning is None


def test_lookup_error_code_absent() -> None:
    """None error_code returns status absent."""
    res_none = lookup_error_code(None)
    assert res_none.code is None
    assert res_none.status == "absent"
    assert res_none.meaning is None

    res_empty = lookup_error_code("   ")
    assert res_empty.code is None
    assert res_empty.status == "absent"


def test_missing_and_stale_sensor_handling() -> None:
    """Explicitly mark missing and stale sensors. NEVER impute missing values."""
    req = DiagnoseRequest(
        asset_id="PUMP-07",
        captured_at=datetime(2026, 9, 18, 9, 14, 0, tzinfo=timezone.utc),
        error_code="E-204",
        sensors={
            "bearing_temp_de": SensorReading(name="bearing_temp_de", value=91.4, unit="C"),
            "vibration_rms": SensorReading(name="vibration_rms", value=8.1, unit="mm/s"),
            "discharge_pressure": SensorReading(name="discharge_pressure", value=6.5, unit="bar"),
            "flow_rate": SensorReading(
                name="flow_rate",
                value=0.0,
                unit="m3/h",
                status="stale",
                last_seen=datetime(2026, 9, 18, 8, 0, 0, tzinfo=timezone.utc),
            ),
        },
    )

    report = build_evidence_report(req)
    assert isinstance(report, EvidenceReport)

    # flow_rate is stale, so it must appear in missing_sensors
    assert "flow_rate" in report.missing_sensors

    # normal sensors must contain discharge_pressure (value 6.5 inside normal range)
    assert "discharge_pressure" in report.normal_sensors

    # deviations must be sorted by severity descending
    assert len(report.deviations) >= 2
    assert report.deviations[0].severity >= report.deviations[1].severity
