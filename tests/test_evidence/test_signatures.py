"""tests/test_evidence/test_signatures.py — Tests for cross-sensor correlation signatures."""

from __future__ import annotations

from core.schemas import Deviation
from evidence.signatures import evaluate_signatures


def _make_dev(sensor: str, band: str, severity: float = 80.0) -> Deviation:
    return Deviation(
        sensor=sensor,
        value=8.1 if sensor == "vibration_rms" else 91.4,
        unit="mm/s" if sensor == "vibration_rms" else "C",
        nominal=2.8 if sensor == "vibration_rms" else 65.0,
        normal_range=(0.0, 4.5) if sensor == "vibration_rms" else (55.0, 75.0),
        delta=5.3 if sensor == "vibration_rms" else 26.4,
        pct_dev=1.89 if sensor == "vibration_rms" else 0.40,
        z_score=5.4 if sensor == "vibration_rms" else 4.8,
        band=band,  # type: ignore[arg-type]
        severity=severity,
        trend="rising",
        roc_per_min=None,
        source="oem_config",
    )


def test_bearing_distress_signature_matches() -> None:
    """R-014 bearing_distress triggers when vibration_rms and bearing_temp_de are both in warn/alarm."""
    dev_vibe = _make_dev("vibration_rms", "alarm")
    dev_temp = _make_dev("bearing_temp_de", "warn")

    signatures = evaluate_signatures([dev_vibe, dev_temp])
    assert len(signatures) >= 1

    sig_names = [s.name for s in signatures]
    assert "bearing_distress" in sig_names

    bearing_sig = next(s for s in signatures if s.name == "bearing_distress")
    assert bearing_sig.rule_id == "R-014"
    assert bearing_sig.confidence == 0.8
    assert sorted(bearing_sig.basis) == ["bearing_temp_de", "vibration_rms"]


def test_signature_does_not_match_if_condition_unmet() -> None:
    """R-014 bearing_distress does NOT trigger if bearing_temp_de is normal."""
    dev_vibe = _make_dev("vibration_rms", "alarm")
    # Only vibration is alarm, temp is not present in deviations (meaning it's normal)

    signatures = evaluate_signatures([dev_vibe])
    sig_names = [s.name for s in signatures]
    assert "bearing_distress" not in sig_names


def test_signature_rule_ordering() -> None:
    """Matched signatures are ordered deterministically by confidence desc."""
    dev_vibe = _make_dev("vibration_rms", "alarm")
    dev_temp = _make_dev("bearing_temp_de", "alarm")
    dev_oil = _make_dev("oil_level_pct", "alarm")

    signatures = evaluate_signatures([dev_vibe, dev_temp, dev_oil])

    # Signatures returned should be sorted by confidence descending
    confidences = [s.confidence for s in signatures]
    assert confidences == sorted(confidences, reverse=True)
