"""ingest/store.py - Idempotent storage layer for SENTRY S1.

Handles persistence across:
  1. Relational DB (SQLAlchemy with SQLite in dev or PostgreSQL in production)
     Stores chunks, error_codes, and specs tables.
  2. Vector DB (Qdrant)
     Stores dense 384-d vectors with rich search payloads.
Running ingestion multiple times is strictly idempotent.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    Text,
    create_engine,
    delete,
    select,
)
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from core.config import settings
from core.schemas import ErrorCodeEntry
from ingest.chunk import ChunkRecord
from ingest.tables import SpecEntry

DEFAULT_SQLITE_PATH = Path(__file__).parent.parent / "data" / "sentry.db"
DEFAULT_QDRANT_STORAGE = Path(__file__).parent.parent / "data" / "qdrant_storage"
QDRANT_COLLECTION = "sentry_chunks"


class Base(DeclarativeBase):
    pass


class ChunkModel(Base):
    __tablename__ = "chunks"

    chunk_id = Column(String(32), primary_key=True)
    doc_id = Column(String(128), index=True, nullable=False)
    doc_title = Column(String(256), nullable=False)
    revision = Column(String(64), nullable=False)
    section_path = Column(Text, nullable=False)  # JSON-encoded list[str]
    page_start = Column(Integer, nullable=False)
    page_end = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    chunk_type = Column(String(32), nullable=False)
    has_safety = Column(Boolean, index=True, nullable=False)
    safety_notes = Column(Text, nullable=False)  # JSON-encoded list[dict]
    asset_class = Column(String(64), index=True, nullable=False)
    applicable_models = Column(Text, nullable=False)  # JSON-encoded list[str]
    token_count = Column(Integer, nullable=False)
    oversized = Column(Boolean, default=False, nullable=False)
    flagged = Column(Boolean, default=False, nullable=False)
    content_hash = Column(String(64), nullable=False)


class ErrorCodeModel(Base):
    __tablename__ = "error_codes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(32), index=True, nullable=False)
    asset_class = Column(String(64), index=True, nullable=False)
    meaning = Column(Text, nullable=False)
    probable_causes = Column(Text, nullable=False)  # JSON-encoded list[str]
    section_ref = Column(String(128), nullable=False)


class SpecModel(Base):
    __tablename__ = "specs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_class = Column(String(64), index=True, nullable=False)
    item = Column(String(256), index=True, nullable=False)
    value = Column(String(256), nullable=False)
    unit = Column(String(64), nullable=False)
    section_ref = Column(String(128), nullable=False)
    doc_id = Column(String(128), index=True, default="")


def get_engine(database_url: str | None = None) -> Engine:
    """Create SQLAlchemy engine using settings or SQLite default."""
    url = database_url or settings.database_url
    if not url:
        DEFAULT_SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)
        url = f"sqlite:///{DEFAULT_SQLITE_PATH.resolve()}"
    return create_engine(url, echo=False)


def init_db(engine: Engine) -> None:
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def upsert_chunks(session: Session, records: list[ChunkRecord]) -> int:
    """Idempotently upsert chunk records into the relational database."""
    if not records:
        return 0

    chunk_ids = [r.chunk_id for r in records]
    # Delete existing to guarantee clean idempotent state
    session.execute(delete(ChunkModel).where(ChunkModel.chunk_id.in_(chunk_ids)))

    for rec in records:
        c = rec.chunk
        model = ChunkModel(
            chunk_id=c.chunk_id,
            doc_id=c.doc_id,
            doc_title=c.doc_title,
            revision=c.revision,
            section_path=json.dumps(c.section_path),
            page_start=c.page_start,
            page_end=c.page_end,
            text=c.text,
            chunk_type=c.chunk_type,
            has_safety=c.has_safety,
            safety_notes=json.dumps([n.model_dump() for n in c.safety_notes]),
            asset_class=c.asset_class,
            applicable_models=json.dumps(c.applicable_models),
            token_count=c.token_count,
            oversized=rec.oversized,
            flagged=rec.flagged,
            content_hash=rec.content_hash,
        )
        session.add(model)

    session.commit()
    return len(records)


def upsert_error_codes(session: Session, error_entries: list[ErrorCodeEntry]) -> int:
    """Idempotently upsert error code records into the database."""
    if not error_entries:
        return 0

    codes = [e.code for e in error_entries]
    session.execute(delete(ErrorCodeModel).where(ErrorCodeModel.code.in_(codes)))

    for entry in error_entries:
        model = ErrorCodeModel(
            code=entry.code,
            asset_class=entry.asset_class,
            meaning=entry.meaning,
            probable_causes=json.dumps(entry.probable_causes),
            section_ref=entry.section_ref,
        )
        session.add(model)

    session.commit()
    return len(error_entries)


def upsert_specs(session: Session, spec_entries: list[SpecEntry]) -> int:
    """Idempotently upsert equipment specs into the database."""
    if not spec_entries:
        return 0

    # Delete existing by doc_id or asset_class/item
    doc_ids = list(set(s.doc_id for s in spec_entries if s.doc_id))
    if doc_ids:
        session.execute(delete(SpecModel).where(SpecModel.doc_id.in_(doc_ids)))

    for s in spec_entries:
        model = SpecModel(
            asset_class=s.asset_class,
            item=s.item,
            value=s.value,
            unit=s.unit,
            section_ref=s.section_ref,
            doc_id=s.doc_id,
        )
        session.add(model)

    session.commit()
    return len(spec_entries)


def get_qdrant_client(url: str | None = None, local_path: Path | None = None) -> QdrantClient:
    """Instantiate a Qdrant client based on configuration."""
    target_url = url or settings.qdrant_url
    if target_url:
        return QdrantClient(url=target_url)

    storage_path = local_path or DEFAULT_QDRANT_STORAGE
    storage_path.mkdir(parents=True, exist_ok=True)
    return QdrantClient(path=str(storage_path))


def init_qdrant_collection(client: QdrantClient, collection_name: str = QDRANT_COLLECTION) -> None:
    """Ensure the Qdrant vector collection exists with 384-d Cosine config."""
    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )


def _chunk_id_to_uuid(chunk_id: str) -> str:
    """Convert 12-char hex chunk_id to a deterministic RFC 4122 UUID for Qdrant."""
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk_id))


def upsert_vectors(
    client: QdrantClient,
    records: list[ChunkRecord],
    embeddings: list[list[float]],
    collection_name: str = QDRANT_COLLECTION,
    batch_size: int = 64,
) -> int:
    """Upsert chunk embeddings and payload into Qdrant idempotently."""
    if not records or not embeddings:
        return 0

    init_qdrant_collection(client, collection_name)

    points: list[PointStruct] = []
    for rec, emb in zip(records, embeddings):
        c = rec.chunk
        point_id = _chunk_id_to_uuid(c.chunk_id)
        payload: dict[str, Any] = {
            "chunk_id": c.chunk_id,
            "doc_id": c.doc_id,
            "doc_title": c.doc_title,
            "revision": c.revision,
            "section_path": c.section_path,
            "page_start": c.page_start,
            "page_end": c.page_end,
            "chunk_type": c.chunk_type,
            "has_safety": c.has_safety,
            "asset_class": c.asset_class,
            "applicable_models": c.applicable_models,
            "token_count": c.token_count,
            "oversized": rec.oversized,
            "flagged": rec.flagged,
            "text": c.text,
        }
        points.append(PointStruct(id=point_id, vector=emb, payload=payload))

    # Batch upsert
    for i in range(0, len(points), batch_size):
        client.upsert(
            collection_name=collection_name,
            points=points[i:i + batch_size],
        )

    return len(points)
