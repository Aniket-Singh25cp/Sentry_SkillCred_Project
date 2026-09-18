"""tests/test_synthesis/test_facts.py — Unit tests for in-code MeasuredFact construction."""

from __future__ import annotations

from datetime import datetime, timezone

from core.schemas import (
    Deviation,
    ErrorCodeResult,
    EvidenceReport,
    HistoryFeatures,
    MeasuredFact,
    Signature,
)
from synthesis.facts import (
    build_measured_facts,
    format_facts_for_prompt,
    render_deviation_fact,
)

_NOW = datetime(2026, 9, 18, 9, 14, 0, tzinfo=timezone.utc)


def _make_sample_deviation() -> Deviation:
    return Deviation(
        sensor="bearing_temp_de",
        value=91.4,
        unit="C",
        nominal=65.0,
        normal_range=(55.0, 75.0),
        delta=26.4,
        pct_dev=0.406,
        z_score=4.82,
        band="alarm",
        severity=92.0,
        trend="rising",
        roc_per_min=0.7,
        source="oem_config",
    )


def test_render_deviation_fact() -> None:
    dev = _make_sample_deviation()
    fact = render_deviation_fact(dev)

    assert isinstance(fact, MeasuredFact)
    assert fact.source == "sensor_engine"
    assert fact.sensor == "bearing_temp_de"
    assert "Drive-end bearing temperature is 91.4 C against a normal range of 55-75 C" in fact.statement
    assert "(z = 4.82, alarm band)." in fact.statement


def test_build_measured_facts_with_recognized_error_code() -> None:
    evidence = EvidenceReport(
        asset_id="PUMP-07",
        asset_class="centrifugal_pump",
        captured_at=_NOW,
        error_code=ErrorCodeResult(
            code="E-204",
            meaning="Lubrication pressure low",
            status="recognized",
        ),
        deviations=[_make_sample_deviation()],
        normal_sensors=["flow_rate"],
        missing_sensors=["suction_pressure"],
        signatures=[
            Signature(
                name="bearing_distress",
                confidence=0.8,
                rule_id="R-014",
                basis=["vibration_rms", "bearing_temp_de"],
            )
        ],
        history_features=HistoryFeatures(
            days_since_service=120,
            same_code_90d=1,
            recent_parts=["filter_cartridge"],
        ),
    )

    facts = build_measured_facts(evidence)

    assert len(facts) == 3
    # 1. Error code fact
    assert facts[0].source == "error_code_lookup"
    assert facts[0].sensor is None
    assert "Error code E-204: Lubrication pressure low." in facts[0].statement

    # 2. Deviation fact
    assert facts[1].source == "sensor_engine"
    assert facts[1].sensor == "bearing_temp_de"

    # 3. Missing sensor notice
    assert facts[2].source == "sensor_engine"
    assert "Sensors reported missing or stale: suction_pressure." in facts[2].statement


def test_build_measured_facts_unrecognized_code() -> None:
    evidence = EvidenceReport(
        asset_id="PUMP-07",
        asset_class="centrifugal_pump",
        captured_at=_NOW,
        error_code=ErrorCodeResult(
            code="E-999",
            meaning=None,
            status="unrecognized",
        ),
        deviations=[],
        normal_sensors=[],
        missing_sensors=[],
        signatures=[],
        history_features=HistoryFeatures(days_since_service=10, same_code_90d=0),
    )

    facts = build_measured_facts(evidence)
    assert len(facts) == 1
    assert "unrecognized in the asset manual" in facts[0].statement


def test_format_facts_for_prompt() -> None:
    facts = [
        MeasuredFact(statement="Bearing temp is 90 C.", source="sensor_engine", sensor="temp"),
        MeasuredFact(statement="Vibration is 7.2 mm/s.", source="sensor_engine", sensor="vib"),
    ]
    prompt_str = format_facts_for_prompt(facts)
    assert "- Bearing temp is 90 C." in prompt_str
    assert "- Vibration is 7.2 mm/s." in prompt_str
