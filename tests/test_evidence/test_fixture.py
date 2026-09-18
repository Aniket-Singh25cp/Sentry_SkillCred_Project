"""tests/test_evidence/test_fixture.py — Validates evidence_report.sample.json fixture."""

from __future__ import annotations

from pathlib import Path

from core.schemas import EvidenceReport


def test_evidence_report_fixture_validates() -> None:
    """Assert fixtures/evidence_report.sample.json parses cleanly into EvidenceReport model."""
    fixture_path = Path(__file__).parent.parent.parent / "fixtures" / "evidence_report.sample.json"
    assert fixture_path.exists(), f"Fixture missing at {fixture_path}"

    content = fixture_path.read_text(encoding="utf-8")
    report = EvidenceReport.model_validate_json(content)

    assert report.asset_id == "PUMP-07"
    assert report.error_code.code == "E-204"
    assert report.error_code.status == "recognized"
    assert len(report.deviations) > 0
    assert len(report.signatures) > 0
