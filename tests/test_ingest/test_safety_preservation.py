"""tests/test_ingest/test_safety_preservation.py - Verify verbatim safety extraction."""

from pathlib import Path
import yaml

from ingest.chunk import chunk_blocks
from ingest.parse import parse_document

CORPUS_DIR = Path(__file__).parent.parent.parent / "data" / "corpus"
SCENARIOS_DIR = Path(__file__).parent.parent.parent / "data" / "scenarios"


def test_scenario_safety_strings_appear_verbatim():
    """Assert every required safety string in scenario files appears verbatim in some chunk.safety_notes."""
    all_chunks = []
    for f in sorted(CORPUS_DIR.glob("*.md")):
        doc = parse_document(f)
        all_chunks.extend(chunk_blocks(doc))

    all_safety_note_texts = set()
    for rec in all_chunks:
        for note in rec.chunk.safety_notes:
            all_safety_note_texts.add(note.text)

    # Validate against all scenario required safety strings
    scenario_files = sorted(SCENARIOS_DIR.glob("*.yaml"))
    checked_count = 0

    for s_file in scenario_files:
        scenario_data = yaml.safe_load(s_file.read_text(encoding="utf-8"))
        for req in scenario_data.get("required_safety_strings", []):
            checked_count += 1
            assert req in all_safety_note_texts, (
                f"Safety string from {s_file.name} not found verbatim in any chunk.safety_notes:\n  '{req}'"
            )

    assert checked_count >= 5, f"Expected to verify multiple safety strings across scenarios, checked {checked_count}"
