"""tests/test_ingest/test_procedure_integrity.py - Verify procedure integrity."""

import re
from pathlib import Path

from ingest.chunk import chunk_blocks
from ingest.parse import parse_document

CORPUS_DIR = Path(__file__).parent.parent.parent / "data" / "corpus"


def test_no_split_numbered_procedures():
    """Assert zero numbered procedures are split across chunks (no orphaned steps)."""
    md_files = sorted(CORPUS_DIR.glob("*.md"))
    orphaned_chunks = []

    for f in md_files:
        doc = parse_document(f)
        records = chunk_blocks(doc)
        for rec in records:
            text = rec.chunk.text
            sec_names = set(rec.chunk.section_path)
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            # Filter out heading lines which may start with numbers (e.g. '2. Technical Specifications')
            body_lines = [l for l in lines if not l.startswith("#") and l not in sec_names]

            step_numbers = []
            for l in body_lines:
                m = re.match(r"^(\d+)\.\s+", l)
                if m:
                    step_numbers.append(int(m.group(1)))

            if step_numbers:
                # If step numbers are present in procedure body, they must begin at step 1
                if step_numbers[0] > 1:
                    orphaned_chunks.append({
                        "chunk_id": rec.chunk_id,
                        "doc_id": rec.chunk.doc_id,
                        "section_path": rec.chunk.section_path,
                        "steps": step_numbers,
                    })

    assert len(orphaned_chunks) == 0, f"Found {len(orphaned_chunks)} orphaned procedure chunks: {orphaned_chunks}"
