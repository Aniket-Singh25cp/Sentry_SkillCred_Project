"""tests/test_ingest/test_chunk_stability.py - Verify chunk_id stability."""

from pathlib import Path

from ingest.chunk import chunk_blocks
from ingest.parse import parse_document

CORPUS_DIR = Path(__file__).parent.parent.parent / "data" / "corpus"


def test_chunk_id_stability():
    """Assert re-ingesting documents produces identical chunk_ids."""
    md_files = sorted(CORPUS_DIR.glob("*.md"))
    assert len(md_files) >= 4, f"Expected at least 4 corpus documents, found {len(md_files)}"

    def run_chunking():
        ids = []
        for f in md_files:
            doc = parse_document(f)
            records = chunk_blocks(doc)
            ids.extend([r.chunk_id for r in records])
        return ids

    run1 = run_chunking()
    run2 = run_chunking()

    assert len(run1) > 0
    assert run1 == run2, "Chunk IDs must be strictly stable and identical across runs"
