"""tests/test_evidence/test_property.py — Property tests (Hypothesis) and determinism checks."""

from __future__ import annotations

from datetime import datetime, timezone

from hypothesis import given
from hypothesis import strategies as st

from core.schemas import DiagnoseRequest, SensorReading
from evidence.deviation import compute_severity
from evidence.engine import build_evidence_report

# ---------------------------------------------------------------------------
# Hypothesis Property Tests
# ---------------------------------------------------------------------------


@given(
    z1=st.floats(min_value=0.0, max_value=20.0),
    z2=st.floats(min_value=0.0, max_value=20.0),
    band=st.sampled_from(["normal", "warn", "alarm", "out_of_range"]),
    criticality=st.floats(min_value=0.5, max_value=2.0),
)
def test_property_severity_monotonic_in_abs_z(z1: float, z2: float, band: str, criticality: float) -> None:
    """Hypothesis Property Test: severity is monotonic non-decreasing in |z| for a fixed band."""
    z_low = min(z1, z2)
    z_high = max(z1, z2)

    sev_low = compute_severity(band, z_score=z_low, criticality=criticality)
    sev_high = compute_severity(band, z_score=z_high, criticality=criticality)

    assert sev_high >= sev_low


@given(
    z=st.floats(min_value=0.0, max_value=10.0),
    criticality=st.floats(min_value=0.5, max_value=2.0),
)
def test_property_severity_alarm_greater_than_or_equal_warn(z: float, criticality: float) -> None:
    """Hypothesis Property Test: severity(alarm) >= severity(warn) for the same sensor & z."""
    sev_warn = compute_severity("warn", z_score=z, criticality=criticality)
    sev_alarm = compute_severity("alarm", z_score=z, criticality=criticality)

    assert sev_alarm >= sev_warn


# ---------------------------------------------------------------------------
# Determinism Test
# ---------------------------------------------------------------------------


def test_determinism_same_input_twice_identical_output() -> None:
    """Determinism test: running build_evidence_report twice on identical input produces identical JSON string."""
    req = DiagnoseRequest(
        asset_id="PUMP-07",
        captured_at=datetime(2026, 9, 18, 9, 14, 0, tzinfo=timezone.utc),
        error_code="E-204",
        sensors={
            "bearing_temp_de": SensorReading(name="bearing_temp_de", value=91.4, unit="C"),
            "vibration_rms": SensorReading(name="vibration_rms", value=8.1, unit="mm/s"),
            "discharge_pressure": SensorReading(name="discharge_pressure", value=6.5, unit="bar"),
            "flow_rate": SensorReading(name="flow_rate", value=125.0, unit="m3/h"),
            "oil_level_pct": SensorReading(name="oil_level_pct", value=21.0, unit="%"),
        },
    )

    report1 = build_evidence_report(req)
    report2 = build_evidence_report(req)

    # Exact bit-level JSON string match
    json1 = report1.model_dump_json()
    json2 = report2.model_dump_json()

    assert json1 == json2
