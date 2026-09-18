"""ingest - SENTRY Ingestion Pipeline (Stage 1).

Transforms raw technical documents into structured, retrievable, safety-annotated
Chunk records, extracts side-tables (error codes, specs), generates embeddings
and BM25 indices, and persists them into relational and vector stores.
"""

from ingest.chunk import ChunkRecord, chunk_blocks
from ingest.embed import build_bm25_index, embed_chunks, get_embedding_model
from ingest.parse import Block, ParsedDocument, parse_document
from ingest.safety_tag import extract_safety_notes, tag_safety_notes
from ingest.store import (
    get_engine,
    get_qdrant_client,
    init_db,
    init_qdrant_collection,
    upsert_chunks,
    upsert_error_codes,
    upsert_specs,
    upsert_vectors,
)
from ingest.tables import SpecEntry, extract_error_codes, extract_specs

__all__ = [
    "Block",
    "ParsedDocument",
    "parse_document",
    "ChunkRecord",
    "chunk_blocks",
    "extract_safety_notes",
    "tag_safety_notes",
    "SpecEntry",
    "extract_error_codes",
    "extract_specs",
    "get_embedding_model",
    "embed_chunks",
    "build_bm25_index",
    "get_engine",
    "init_db",
    "upsert_chunks",
    "upsert_error_codes",
    "upsert_specs",
    "get_qdrant_client",
    "init_qdrant_collection",
    "upsert_vectors",
]
