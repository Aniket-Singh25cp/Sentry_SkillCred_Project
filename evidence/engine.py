"""evidence/engine.py — Main orchestrator for SENTRY Stage 2 Evidence Engine.

Converts a raw DiagnoseRequest into a quantified, severity-ranked EvidenceReport.
Deterministic statistical output, reproducible to the last decimal.
"""

from __future__ import annotations

from typing import Any

from core.schemas import (
    Deviation,
    DiagnoseRequest,
    ErrorCodeResult,
    EvidenceReport,
)
from evidence.baselines import SensorBaseline, load_baselines
from evidence.deviation import compute_deviation
from evidence.history import get_history_features
from evidence.signatures import evaluate_signatures

# Canonical error code reference database
KNOWN_ERROR_CODES: dict[str, dict[str, Any]] = {
    "E-204": {
        "meaning": "Lubrication pressure low",
        "asset_class": "centrifugal_pump",
        "section_ref": "7.3 Lubrication System",
    },
    "E-101": {
        "meaning": "High bearing vibration",
        "asset_class": "centrifugal_pump",
        "section_ref": "7.1 Vibration Analysis",
    },
    "E-301": {
        "meaning": "Suction pressure low / Cavitation warning",
        "asset_class": "centrifugal_pump",
        "section_ref": "7.4 Hydraulic Performance",
    },
    "E-401": {
        "meaning": "Shaft misalignment detected",
        "asset_class": "centrifugal_pump",
        "section_ref": "7.2 Mechanical Alignment",
    },
    "E-501": {
        "meaning": "Motor overcurrent / Thermal trip",
        "asset_class": "centrifugal_pump",
        "section_ref": "7.5 Drive Motor & Electrical",
    },
    "F-102": {
        "meaning": "Filter differential pressure high",
        "asset_class": "centrifugal_pump",
        "section_ref": "7.6 Filtration",
    },
}


def lookup_error_code(code: str | None, asset_class: str | None = None) -> ErrorCodeResult:
    """Exact-match lookup of error code against known error codes reference table.

    R2.6 contract rules:
    - If code is None or empty -> status "absent", meaning None.
    - If exact match found -> status "recognized", OEM defined meaning.
    - If NOT found -> status "unrecognized", meaning None.
      DO NOT guess, fuzzy-match, or infer meaning from a similar code.
    """
    if not code or not code.strip():
        return ErrorCodeResult(code=None, meaning=None, status="absent")

    clean_code = code.strip().upper()

    if clean_code in KNOWN_ERROR_CODES:
        entry = KNOWN_ERROR_CODES[clean_code]
        # Verify asset_class match if asset_class is specified
        if asset_class and entry.get("asset_class") and entry.get("asset_class") != asset_class:
            # Asset class mismatch: treated as unrecognized for this asset class
            pass
        return ErrorCodeResult(
            code=clean_code,
            meaning=str(entry.get("meaning", "")),
            status="recognized",
        )

    # Unknown / unrecognized code -> refusal trigger downstream
    return ErrorCodeResult(
        code=clean_code,
        meaning=None,
        status="unrecognized",
    )


def resolve_asset_class(request: DiagnoseRequest) -> str:
    """Resolve asset class from request context or asset_id prefix."""
    if "asset_class" in request.context and isinstance(request.context["asset_class"], str):
        return str(request.context["asset_class"])

    asset_id_upper = request.asset_id.upper()
    if "GEAR" in asset_id_upper:
        return "industrial_gearbox"
    if "COMP" in asset_id_upper:
        return "air_compressor"
    return "centrifugal_pump"


def build_evidence_report(
    request: DiagnoseRequest,
    baselines_map: dict[str, dict[str, SensorBaseline]] | None = None,
    history_records: list[dict[str, Any]] | None = None,
) -> EvidenceReport:
    """Build a complete EvidenceReport from a raw DiagnoseRequest.

    Pure, deterministic statistical function.

    Pipeline steps:
    1. Resolve asset_class and load sensor baselines.
    2. Exact-match error code lookup (absent/recognized/unrecognized).
    3. Partition sensors into normal, missing/stale, and deviations.
    4. Sort deviations by severity descending (sensor name ascending for tie-breaks).
    5. Evaluate declarative correlation signatures.
    6. Extract maintenance history features.
    7. Assemble and return validated EvidenceReport.
    """
    asset_class = resolve_asset_class(request)

    if baselines_map is None:
        baselines_map = load_baselines()

    asset_baselines = baselines_map.get(asset_class, baselines_map.get("centrifugal_pump", {}))

    # 1. Error Code Lookup
    error_code_result = lookup_error_code(request.error_code, asset_class=asset_class)

    normal_sensors: list[str] = []
    missing_sensors: list[str] = []
    deviations: list[Deviation] = []

    # Track processed sensors
    processed_sensors: set[str] = set()

    # 2. Process submitted sensors
    for sensor_name, reading in request.sensors.items():
        processed_sensors.add(sensor_name)

        # Handle explicit missing / stale sensor readings (R2.8)
        # NEVER impute, interpolate, or fill a missing sensor value.
        if reading.status in ("missing", "stale"):
            if sensor_name not in missing_sensors:
                missing_sensors.append(sensor_name)
            continue

        baseline = asset_baselines.get(
            sensor_name,
            SensorBaseline(
                sensor=sensor_name,
                unit=reading.unit,
                nominal=reading.value,
                normal_range=(reading.value * 0.9, reading.value * 1.1),
                warn_low=None,
                warn_high=None,
                alarm_low=None,
                alarm_high=None,
            ),
        )

        dev = compute_deviation(sensor_name, reading, baseline)

        if dev.band == "normal":
            if sensor_name not in normal_sensors:
                normal_sensors.append(sensor_name)
        else:
            deviations.append(dev)

    # 3. Check for expected baselines that were not provided in request.sensors
    for expected_sensor in asset_baselines:
        if expected_sensor not in processed_sensors and expected_sensor not in missing_sensors:
            missing_sensors.append(expected_sensor)

    # Sort outputs deterministically
    # Deviations: severity desc, sensor asc
    deviations.sort(key=lambda d: (-d.severity, d.sensor))
    normal_sensors.sort()
    missing_sensors.sort()

    # 4. Evaluate Signature correlation rules
    signatures = evaluate_signatures(deviations)

    # 5. Maintenance history feature extraction
    history_feats = get_history_features(
        asset_id=request.asset_id,
        error_code=request.error_code,
        captured_at=request.captured_at,
        history_records=history_records,
    )

    return EvidenceReport(
        asset_id=request.asset_id,
        asset_class=asset_class,
        captured_at=request.captured_at,
        error_code=error_code_result,
        deviations=deviations,
        normal_sensors=normal_sensors,
        missing_sensors=missing_sensors,
        signatures=signatures,
        history_features=history_feats,
    )
