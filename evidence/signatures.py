"""evidence/signatures.py — Cross-sensor signature correlation rules.

Loads declarative cross-sensor correlation rules from evidence/rules/signatures.yaml
and evaluates them against a list of computed Deviations.

IMPORTANT: Output Signature objects are HEURISTIC HINTS ONLY. They are consumed downstream
by Stage 3 (Retrieval) as search hints and must NEVER be presented as measured fact.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from core.schemas import Deviation, Signature


def _parse_when_condition(condition_str: str) -> tuple[str, str, str, list[str]]:
    """Parse a single rule condition string.

    Supports forms like:
      - "vibration_rms.band in [warn, alarm]"
      - "bearing_temp_de.band == alarm"
      - "motor_current.severity >= 50"

    Returns: (sensor_name, field_name, operator, target_values)
    """
    cond = condition_str.strip()

    # Pattern 1: <sensor>.<field> in [<v1>, <v2>]
    in_match = re.match(r"^([\w_]+)\.([\w_]+)\s+in\s+\[(.*)\]$", cond, re.IGNORECASE)
    if in_match:
        sensor, field, vals_raw = in_match.groups()
        vals = [v.strip().strip("'\"") for v in vals_raw.split(",")]
        return sensor, field, "in", vals

    # Pattern 2: <sensor>.<field> == <value>
    eq_match = re.match(r"^([\w_]+)\.([\w_]+)\s*==\s*(.+)$", cond, re.IGNORECASE)
    if eq_match:
        sensor, field, val_raw = eq_match.groups()
        val = val_raw.strip().strip("'\"")
        return sensor, field, "==", [val]

    # Pattern 3: <sensor>.<field> >= <value>
    gte_match = re.match(r"^([\w_]+)\.([\w_]+)\s*>=\s*(.+)$", cond, re.IGNORECASE)
    if gte_match:
        sensor, field, val_raw = gte_match.groups()
        val = val_raw.strip().strip("'\"")
        return sensor, field, ">=", [val]

    raise ValueError(f"Invalid condition format: '{condition_str}'")


def _evaluate_condition(cond_tuple: tuple[str, str, str, list[str]], deviations_map: dict[str, Deviation]) -> bool:
    """Evaluate a parsed condition tuple against available sensor deviations."""
    sensor, field, op, target_vals = cond_tuple

    if sensor not in deviations_map:
        return False

    dev = deviations_map[sensor]
    field_val = getattr(dev, field, None)
    if field_val is None:
        return False

    if op == "in":
        return str(field_val) in target_vals
    elif op == "==":
        return str(field_val) == target_vals[0]
    elif op == ">=":
        try:
            return float(field_val) >= float(target_vals[0])
        except (ValueError, TypeError):
            return False

    return False


def load_signature_rules(yaml_path: str | Path | None = None) -> list[dict[str, Any]]:
    """Load signature correlation rules from YAML file."""
    path = Path(yaml_path) if yaml_path else Path(__file__).parent / "rules" / "signatures.yaml"

    if not path.exists():
        # Fallback inline rules if file not present
        return [
            {
                "id": "R-014",
                "name": "bearing_distress",
                "when": ["vibration_rms.band in [warn, alarm]", "bearing_temp_de.band in [warn, alarm]"],
                "confidence": 0.8,
            },
            {
                "id": "R-015",
                "name": "cavitation",
                "when": ["discharge_pressure.band in [warn, alarm]", "flow_rate.band in [warn, alarm]"],
                "confidence": 0.85,
            },
        ]

    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
        if isinstance(data, dict) and "rules" in data and isinstance(data["rules"], list):
            return data["rules"]
    return []


def evaluate_signatures(
    deviations: list[Deviation],
    rules: list[dict[str, Any]] | None = None,
) -> list[Signature]:
    """Evaluate cross-sensor rules against computed deviations and emit Signature objects.

    Returns a list of Signature hints sorted deterministically by confidence desc, rule_id asc.
    """
    if rules is None:
        rules = load_signature_rules()

    deviations_map = {dev.sensor: dev for dev in deviations}
    matched_signatures: list[Signature] = []

    for rule in rules:
        rule_id = str(rule.get("id", ""))
        rule_name = str(rule.get("name", ""))
        confidence = float(rule.get("confidence", 0.5))
        when_list = rule.get("when", [])

        if not when_list or not isinstance(when_list, list):
            continue

        all_conditions_met = True
        basis_sensors: list[str] = []

        for cond_str in when_list:
            cond_tuple = _parse_when_condition(str(cond_str))
            sensor_name = cond_tuple[0]
            if sensor_name not in basis_sensors:
                basis_sensors.append(sensor_name)

            if not _evaluate_condition(cond_tuple, deviations_map):
                all_conditions_met = False
                break

        if all_conditions_met:
            matched_signatures.append(
                Signature(
                    name=rule_name,
                    confidence=confidence,
                    rule_id=rule_id,
                    basis=sorted(basis_sensors),
                )
            )

    # Sort deterministically by confidence desc, then rule_id asc
    matched_signatures.sort(key=lambda sig: (-sig.confidence, sig.rule_id))
    return matched_signatures
