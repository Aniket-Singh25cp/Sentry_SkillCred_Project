"""ingest/embed.py - Dense and sparse embedding generation for SENTRY S1.

Generates dense embeddings using sentence-transformers (BAAI/bge-small-en-v1.5)
with content-hash disk caching to avoid re-embedding unchanged chunks.
Builds and persists a BM25Okapi index artifact for sparse retrieval (S3).
"""

from __future__ import annotations

import os
import pickle
import re
from pathlib import Path
from typing import Any

from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

from ingest.chunk import ChunkRecord

DEFAULT_MODEL_NAME = "BAAI/bge-small-en-v1.5"
DEFAULT_CACHE_DIR = Path(__file__).parent.parent / "data" / "cache"
DEFAULT_INDICES_DIR = Path(__file__).parent.parent / "data" / "indices"

_MODEL_INSTANCE: SentenceTransformer | None = None


def get_embedding_model(model_name: str = DEFAULT_MODEL_NAME) -> SentenceTransformer:
    """Singleton loader for the embedding model."""
    global _MODEL_INSTANCE
    if _MODEL_INSTANCE is None:
        _MODEL_INSTANCE = SentenceTransformer(model_name)
    return _MODEL_INSTANCE


def _load_cache(cache_path: Path) -> dict[str, list[float]]:
    """Load cached embeddings from disk."""
    if cache_path.exists():
        try:
            with cache_path.open("rb") as fh:
                data = pickle.load(fh)
                if isinstance(data, dict):
                    return data
        except Exception:
            return {}
    return {}


def _save_cache(cache_data: dict[str, list[float]], cache_path: Path) -> None:
    """Save embeddings cache to disk."""
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = cache_path.with_suffix(".tmp")
    with temp_path.open("wb") as fh:
        pickle.dump(cache_data, fh, protocol=pickle.HIGHEST_PROTOCOL)
    temp_path.replace(cache_path)


def embed_chunks(
    records: list[ChunkRecord],
    model_name: str = DEFAULT_MODEL_NAME,
    cache_path: Path | None = None,
    batch_size: int = 32,
) -> list[list[float]]:
    """Embed chunks using BAAI/bge-small-en-v1.5 with content-hash disk cache.

    Returns a list of 384-dimensional float vectors corresponding 1-to-1 with records.
    """
    if cache_path is None:
        cache_path = DEFAULT_CACHE_DIR / "embeddings_cache.pkl"

    cache = _load_cache(cache_path)
    model = get_embedding_model(model_name)

    results: list[list[float] | None] = [None] * len(records)
    missing_indices: list[int] = []
    missing_texts: list[str] = []

    for idx, rec in enumerate(records):
        h = rec.content_hash
        if h in cache:
            results[idx] = cache[h]
        else:
            missing_indices.append(idx)
            missing_texts.append(rec.chunk.text)

    if missing_texts:
        # Compute embeddings for uncached texts
        embeddings = model.encode(
            missing_texts,
            batch_size=batch_size,
            show_progress_bar=False,
            normalize_embeddings=True,
        )

        for orig_idx, emb in zip(missing_indices, embeddings):
            vec = [float(v) for v in emb]
            results[orig_idx] = vec
            cache[records[orig_idx].content_hash] = vec

        # Update cache on disk
        _save_cache(cache, cache_path)

    # All results are now populated
    final_embeddings: list[list[float]] = [res for res in results if res is not None]
    return final_embeddings


def tokenize_for_bm25(text: str) -> list[str]:
    """Tokenize text into lowercase alphanumeric terms for BM25."""
    return [term.lower() for term in re.findall(r"\b[A-Za-z0-9_-]+\b", text)]


def build_bm25_index(
    records: list[ChunkRecord],
    out_path: Path | None = None,
) -> BM25Okapi:
    """Build BM25Okapi sparse index and persist it to disk."""
    if out_path is None:
        out_path = DEFAULT_INDICES_DIR / "bm25_index.pkl"

    out_path.parent.mkdir(parents=True, exist_ok=True)

    corpus_tokens = [tokenize_for_bm25(r.chunk.text) for r in records]
    bm25 = BM25Okapi(corpus_tokens)

    payload = {
        "bm25": bm25,
        "chunk_ids": [r.chunk_id for r in records],
        "corpus_tokens": corpus_tokens,
    }

    temp_path = out_path.with_suffix(".tmp")
    with temp_path.open("wb") as fh:
        pickle.dump(payload, fh, protocol=pickle.HIGHEST_PROTOCOL)
    temp_path.replace(out_path)

    return bm25
