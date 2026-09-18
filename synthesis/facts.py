"""synthesis/facts.py — Build MeasuredFact list in code from EvidenceReport.

Hard constraint: The LLM must NEVER generate measured facts or invent numbers.
All measured facts are constructed deterministically in pure code from the
EvidenceReport and injected into prompts as read-only reference material.
"""

from __future__ import annotations

from core.schemas import Deviation, EvidenceReport, MeasuredFact

# Human-readable labels for well-known industrial sensor identifiers.
_SENSOR_NAME_MAP: dict[str, str] = {
    "bearing_temp_de": "Drive-end bearing temperature",
    "bearing_temp_nde": "Non-drive-end bearing temperature",
    "vibration_rms": "Vibration RMS",
    "motor_current": "Motor current",
    "discharge_pressure": "Discharge pressure",
    "suction_pressure": "Suction pressure",
    "flow_rate": "Flow rate",
    "oil_level_pct": "Oil level percentage",
    "rpm": "Rotational speed (RPM)",
}


def _format_bound(val: float) -> str:
    """Format bounds cleanly, omitting trailing decimals for whole numbers."""
    return f"{int(val)}" if val.is_integer() else f"{val}"


def _human_sensor_name(sensor_key: str) -> str:
    """Resolve a friendly sensor name, falling back to clean title-cased key."""
    if sensor_key in _SENSOR_NAME_MAP:
        return _SENSOR_NAME_MAP[sensor_key]
    return sensor_key.replace("_", " ").capitalize()


def render_deviation_fact(dev: Deviation) -> MeasuredFact:
    """Template-render a single Deviation into a MeasuredFact contract.

    Example sentence:
    'Drive-end bearing temperature is 91.4 C against a normal range of 55-75 C (z = 4.82, alarm band).'
    """
    sensor_name = _human_sensor_name(dev.sensor)
    val_str = _format_bound(dev.value)
    low_str = _format_bound(dev.normal_range[0])
    high_str = _format_bound(dev.normal_range[1])

    statement = (
        f"{sensor_name} is {val_str} {dev.unit} against a normal range of "
        f"{low_str}-{high_str} {dev.unit} (z = {dev.z_score:.2f}, {dev.band} band)."
    )

    # Sensor provenance is set to sensor_engine per PRD contract schema
    return MeasuredFact(
        statement=statement,
        source="sensor_engine",
        sensor=dev.sensor,
    )


def build_measured_facts(evidence: EvidenceReport) -> list[MeasuredFact]:
    """Construct all MeasuredFact objects deterministically from an EvidenceReport.

    Facts are ordered by:
    1. Error code status (if present)
    2. Quantified sensor deviations (already sorted by severity desc in EvidenceReport)
    3. Missing or stale sensor notices
    """
    facts: list[MeasuredFact] = []

    # 1. Error code fact
    if evidence.error_code.code:
        if evidence.error_code.status == "recognized":
            meaning = evidence.error_code.meaning or "unspecified fault"
            facts.append(
                MeasuredFact(
                    statement=f"Error code {evidence.error_code.code}: {meaning}.",
                    source="error_code_lookup",
                    sensor=None,
                )
            )
        elif evidence.error_code.status == "unrecognized":
            facts.append(
                MeasuredFact(
                    statement=f"Error code {evidence.error_code.code} is unrecognized in the asset manual.",
                    source="error_code_lookup",
                    sensor=None,
                )
            )

    # 2. Deviations rendered in order of severity
    for dev in evidence.deviations:
        facts.append(render_deviation_fact(dev))

    # 3. Missing sensor notice to highlight telemetry gaps to technician
    if evidence.missing_sensors:
        facts.append(
            MeasuredFact(
                statement=f"Sensors reported missing or stale: {', '.join(evidence.missing_sensors)}.",
                source="sensor_engine",
                sensor=None,
            )
        )

    return facts


def format_facts_for_prompt(facts: list[MeasuredFact]) -> str:
    """Format facts into a bulleted read-only text block for prompt interpolation."""
    if not facts:
        return "No sensor deviations or active error codes reported."
    return "\n".join(f"- {f.statement}" for f in facts)
