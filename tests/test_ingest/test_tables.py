"""tests/test_ingest/test_tables.py - Verify side-table extraction."""

from pathlib import Path

from core.schemas import ErrorCodeEntry
from ingest.tables import extract_error_codes, extract_specs

CORPUS_DIR = Path(__file__).parent.parent.parent / "data" / "corpus"


def test_extract_error_codes():
    """Assert error code table extraction returns valid ErrorCodeEntry records."""
    cp_text = (CORPUS_DIR / "cp450_pump_manual.md").read_text(encoding="utf-8")
    gb_text = (CORPUS_DIR / "gb200_gearbox_manual.md").read_text(encoding="utf-8")

    cp_codes = extract_error_codes(cp_text, "centrifugal_pump")
    gb_codes = extract_error_codes(gb_text, "industrial_gearbox")

    assert len(cp_codes) >= 12, f"Expected at least 12 CP error codes, got {len(cp_codes)}"
    assert len(gb_codes) >= 12, f"Expected at least 12 GB error codes, got {len(gb_codes)}"

    # All must be valid ErrorCodeEntry models
    for entry in cp_codes + gb_codes:
        assert isinstance(entry, ErrorCodeEntry)
        assert entry.code.startswith(("E-", "G-"))
        assert len(entry.meaning) > 0
        assert len(entry.probable_causes) > 0


def test_extract_specs():
    """Assert torque and specification tables are cleanly extracted."""
    cp_text = (CORPUS_DIR / "cp450_pump_manual.md").read_text(encoding="utf-8")
    cp_specs = extract_specs(cp_text, "centrifugal_pump", "cp450")

    assert len(cp_specs) >= 10, f"Expected at least 10 specs, got {len(cp_specs)}"
    for s in cp_specs:
        assert s.asset_class == "centrifugal_pump"
        assert len(s.item) > 0
        assert len(s.value) > 0
