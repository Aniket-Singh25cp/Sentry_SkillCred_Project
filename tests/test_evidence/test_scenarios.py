"""tests/test_evidence/test_scenarios.py — Tests for all 7 S0 fault scenarios."""

from __future__ import annotations

from datetime import datetime, timezone

from core.schemas import DiagnoseRequest, SensorReading
from evidence.engine import build_evidence_report

_CAPTURED_AT = datetime(2026, 9, 18, 9, 14, 0, tzinfo=timezone.utc)


def test_scenario_1_bearing_degradation() -> None:
    """Scenario 1: Bearing degradation.

    Expected deviations: vibration_rms (alarm), bearing_temp_de (alarm/warn).
    """
    req = DiagnoseRequest(
        asset_id="PUMP-01",
        captured_at=_CAPTURED_AT,
        error_code="E-101",
        sensors={
            "vibration_rms": SensorReading(name="vibration_rms", value=8.5, unit="mm/s"),
            "bearing_temp_de": SensorReading(name="bearing_temp_de", value=82.0, unit="C"),
            "motor_current": SensorReading(name="motor_current", value=32.0, unit="A"),
            "discharge_pressure": SensorReading(name="discharge_pressure", value=6.5, unit="bar"),
            "flow_rate": SensorReading(name="flow_rate", value=125.0, unit="m3/h"),
        },
    )

    report = build_evidence_report(req)
    dev_map = {d.sensor: d.band for d in report.deviations}

    assert "vibration_rms" in dev_map
    assert dev_map["vibration_rms"] == "alarm"
    assert "bearing_temp_de" in dev_map
    assert dev_map["bearing_temp_de"] in ("warn", "alarm")
    assert report.error_code.status == "recognized"
    assert report.error_code.meaning == "High bearing vibration"


def test_scenario_2_cavitation() -> None:
    """Scenario 2: Cavitation.

    Expected deviations: discharge_pressure (warn/alarm low), flow_rate (warn/alarm low).
    Signature: cavitation.
    """
    req = DiagnoseRequest(
        asset_id="PUMP-02",
        captured_at=_CAPTURED_AT,
        error_code="E-301",
        sensors={
            "discharge_pressure": SensorReading(name="discharge_pressure", value=4.2, unit="bar"),
            "flow_rate": SensorReading(name="flow_rate", value=95.0, unit="m3/h"),
            "vibration_rms": SensorReading(name="vibration_rms", value=2.8, unit="mm/s"),
            "bearing_temp_de": SensorReading(name="bearing_temp_de", value=65.0, unit="C"),
        },
    )

    report = build_evidence_report(req)
    dev_map = {d.sensor: d.band for d in report.deviations}

    assert "discharge_pressure" in dev_map
    assert dev_map["discharge_pressure"] in ("warn", "alarm")
    assert "flow_rate" in dev_map
    assert dev_map["flow_rate"] in ("warn", "alarm")

    sig_names = [s.name for s in report.signatures]
    assert "cavitation" in sig_names


def test_scenario_3_misalignment() -> None:
    """Scenario 3: Misalignment / imbalance.

    Expected deviations: vibration_rms (alarm), temp normal.
    """
    req = DiagnoseRequest(
        asset_id="PUMP-03",
        captured_at=_CAPTURED_AT,
        error_code="E-401",
        sensors={
            "vibration_rms": SensorReading(name="vibration_rms", value=7.2, unit="mm/s"),
            "bearing_temp_de": SensorReading(name="bearing_temp_de", value=66.0, unit="C"),
            "motor_current": SensorReading(name="motor_current", value=32.5, unit="A"),
        },
    )

    report = build_evidence_report(req)
    dev_map = {d.sensor: d.band for d in report.deviations}

    assert "vibration_rms" in dev_map
    assert dev_map["vibration_rms"] == "alarm"
    assert "bearing_temp_de" in report.normal_sensors


def test_scenario_4_lubrication_failure() -> None:
    """Scenario 4: Lubrication failure.

    Expected deviations: oil_level_pct (alarm low), bearing_temp_de (alarm high), code E-204.
    Signature: lubrication_failure.
    """
    req = DiagnoseRequest(
        asset_id="PUMP-07",
        captured_at=_CAPTURED_AT,
        error_code="E-204",
        sensors={
            "oil_level_pct": SensorReading(name="oil_level_pct", value=21.0, unit="%"),
            "bearing_temp_de": SensorReading(name="bearing_temp_de", value=91.4, unit="C"),
            "vibration_rms": SensorReading(name="vibration_rms", value=8.1, unit="mm/s"),
            "discharge_pressure": SensorReading(name="discharge_pressure", value=6.5, unit="bar"),
            "flow_rate": SensorReading(name="flow_rate", value=125.0, unit="m3/h"),
        },
    )

    report = build_evidence_report(req)
    dev_map = {d.sensor: d.band for d in report.deviations}

    assert "oil_level_pct" in dev_map
    assert dev_map["oil_level_pct"] == "alarm"
    assert "bearing_temp_de" in dev_map
    assert dev_map["bearing_temp_de"] == "alarm"
    assert report.error_code.status == "recognized"
    assert report.error_code.meaning == "Lubrication pressure low"

    sig_names = [s.name for s in report.signatures]
    assert "lubrication_failure" in sig_names


def test_scenario_5_motor_overload() -> None:
    """Scenario 5: Motor overload / phase imbalance.

    Expected deviations: motor_current (alarm high), rpm (warn/alarm low), code E-501.
    """
    req = DiagnoseRequest(
        asset_id="PUMP-05",
        captured_at=_CAPTURED_AT,
        error_code="E-501",
        sensors={
            "motor_current": SensorReading(name="motor_current", value=48.0, unit="A"),
            "rpm": SensorReading(name="rpm", value=1610.0, unit="RPM"),
            "bearing_temp_de": SensorReading(name="bearing_temp_de", value=65.0, unit="C"),
        },
    )

    report = build_evidence_report(req)
    dev_map = {d.sensor: d.band for d in report.deviations}

    assert "motor_current" in dev_map
    assert dev_map["motor_current"] == "alarm"
    assert "rpm" in dev_map
    assert dev_map["rpm"] in ("warn", "alarm")
    assert report.error_code.status == "recognized"
    assert report.error_code.meaning == "Motor overcurrent / Thermal trip"


def test_scenario_6_clogged_filter() -> None:
    """Scenario 6: Clogged filter.

    Expected deviations: differential_pressure (alarm high), flow_rate (warn/alarm low), code F-102.
    """
    req = DiagnoseRequest(
        asset_id="PUMP-06",
        captured_at=_CAPTURED_AT,
        error_code="F-102",
        sensors={
            "differential_pressure": SensorReading(name="differential_pressure", value=2.1, unit="bar"),
            "flow_rate": SensorReading(name="flow_rate", value=92.0, unit="m3/h"),
            "discharge_pressure": SensorReading(name="discharge_pressure", value=6.5, unit="bar"),
        },
    )

    report = build_evidence_report(req)
    dev_map = {d.sensor: d.band for d in report.deviations}

    assert "differential_pressure" in dev_map
    assert dev_map["differential_pressure"] == "alarm"
    assert "flow_rate" in dev_map
    assert dev_map["flow_rate"] in ("warn", "alarm")
    assert report.error_code.status == "recognized"
    assert report.error_code.meaning == "Filter differential pressure high"


def test_scenario_7_unknown_code_e999() -> None:
    """Scenario 7: Unknown code E-999 yields error_code.status == 'unrecognized'."""
    req = DiagnoseRequest(
        asset_id="PUMP-07",
        captured_at=_CAPTURED_AT,
        error_code="E-999",
        sensors={
            "bearing_temp_de": SensorReading(name="bearing_temp_de", value=65.0, unit="C"),
            "vibration_rms": SensorReading(name="vibration_rms", value=2.8, unit="mm/s"),
        },
    )

    report = build_evidence_report(req)

    assert report.error_code.code == "E-999"
    assert report.error_code.status == "unrecognized"
    assert report.error_code.meaning is None
