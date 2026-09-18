"""tests/test_ingest/test_store_idempotency.py - Verify idempotent storage."""

from pathlib import Path

from qdrant_client import QdrantClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from ingest.chunk import chunk_blocks
from ingest.parse import parse_document
from ingest.store import (
    Base,
    ChunkModel,
    ErrorCodeModel,
    init_db,
    init_qdrant_collection,
    upsert_chunks,
    upsert_error_codes,
    upsert_vectors,
)
from ingest.tables import extract_error_codes

CORPUS_DIR = Path(__file__).parent.parent.parent / "data" / "corpus"


def test_sqlite_idempotency(tmp_path):
    """Assert database upsert is strictly idempotent across multiple runs."""
    db_file = tmp_path / "test_sentry.db"
    engine = create_engine(f"sqlite:///{db_file}")
    init_db(engine)

    doc = parse_document(CORPUS_DIR / "sop_loto_01.md")
    records = chunk_blocks(doc)

    with Session(engine) as session:
        # First run
        n1 = upsert_chunks(session, records)
        assert n1 == len(records)
        count1 = session.scalar(select(func.count()).select_from(ChunkModel))
        assert count1 == len(records)

        # Second run with same records
        n2 = upsert_chunks(session, records)
        assert n2 == len(records)
        count2 = session.scalar(select(func.count()).select_from(ChunkModel))
        # Row count must remain identical
        assert count2 == count1


def test_qdrant_idempotency():
    """Assert Qdrant vector upsert is strictly idempotent."""
    client = QdrantClient(":memory:")
    col = "test_col"
    init_qdrant_collection(client, collection_name=col)

    doc = parse_document(CORPUS_DIR / "sop_lub_01.md")
    records = chunk_blocks(doc)
    dummy_embs = [[0.1] * 384 for _ in records]

    # First upsert
    upsert_vectors(client, records, dummy_embs, collection_name=col)
    info1 = client.get_collection(col)
    assert info1.points_count == len(records)

    # Second upsert (same records and IDs)
    upsert_vectors(client, records, dummy_embs, collection_name=col)
    info2 = client.get_collection(col)
    assert info2.points_count == len(records)
