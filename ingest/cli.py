"""ingest/cli.py - Ingestion CLI for SENTRY S1.

Usage:
    python -m ingest.cli --corpus data/corpus --rebuild
    python -m ingest.cli --corpus data/corpus --incremental

Features:
  1. Parses Markdown/PDF corpus files.
  2. Structure-aware chunking preserving procedures.
  3. Verbatim safety note extraction.
  4. Structured side-table extraction (error codes and specs).
  5. Dense (bge-small-en-v1.5) and sparse (BM25) embedding generation.
  6. Idempotent persistence to SQL DB and Qdrant.
  7. Security injection scan with quarantine reporting.
  8. Ingestion manifest creation.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import typer
from sqlalchemy.orm import Session

from ingest.chunk import ChunkRecord, chunk_blocks
from ingest.embed import DEFAULT_MODEL_NAME, build_bm25_index, embed_chunks
from ingest.parse import parse_document
from ingest.store import (
    QDRANT_COLLECTION,
    get_engine,
    get_qdrant_client,
    init_db,
    init_qdrant_collection,
    upsert_chunks,
    upsert_error_codes,
    upsert_specs,
    upsert_vectors,
)
from ingest.tables import extract_error_codes, extract_specs

app = typer.Typer(help="SENTRY S1 Ingestion Pipeline CLI")

# Security prompt-injection patterns mandated by PRD
INJECTION_PATTERNS = [
    re.compile(r"ignore\s+previous", re.IGNORECASE),
    re.compile(r"ignore\s+all", re.IGNORECASE),
    re.compile(r"system:", re.IGNORECASE),
    re.compile(r"you\s+are\s+now", re.IGNORECASE),
    re.compile(r"disregard\s+the\s+above", re.IGNORECASE),
    re.compile(r"new\s+instructions", re.IGNORECASE),
]


def scan_prompt_injections(records: list[ChunkRecord]) -> list[dict[str, Any]]:
    """Scan chunks for prompt injection patterns.

    Flag matches in record.flagged and produce quarantine report entries.
    Do NOT drop chunks or alter text.
    """
    quarantine: list[dict[str, Any]] = []

    for rec in records:
        text = rec.chunk.text
        for pattern in INJECTION_PATTERNS:
            match = pattern.search(text)
            if match:
                rec.flagged = True
                # Extract surrounding snippet
                start = max(0, match.start() - 30)
                end = min(len(text), match.end() + 30)
                snippet = text[start:end].replace("\n", " ")
                quarantine.append({
                    "chunk_id": rec.chunk.chunk_id,
                    "doc_id": rec.chunk.doc_id,
                    "section_path": rec.chunk.section_path,
                    "pattern": pattern.pattern,
                    "matched_text": match.group(0),
                    "snippet": snippet,
                })
                break  # Flag once per chunk

    return quarantine


def compute_file_hash(path: Path) -> str:
    """Return SHA-256 hash of file contents."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


@app.command()
def run(
    corpus: Path = typer.Option(
        Path("data/corpus"),
        "--corpus",
        "-c",
        help="Path to corpus directory containing Markdown/PDF files",
    ),
    rebuild: bool = typer.Option(
        False,
        "--rebuild",
        help="Rebuild all indices and database tables from scratch",
    ),
    incremental: bool = typer.Option(
        False,
        "--incremental",
        help="Run incremental ingestion (skip re-embedding unchanged chunks)",
    ),
    model_name: str = typer.Option(
        DEFAULT_MODEL_NAME,
        "--model",
        "-m",
        help="HuggingFace model identifier for dense embeddings",
    ),
) -> None:
    """Run SENTRY Ingestion Pipeline over the corpus."""
    if not corpus.exists():
        typer.secho(f"Corpus directory not found: {corpus}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"

    typer.echo(f"Starting SENTRY Ingestion Pipeline (rebuild={rebuild}, incremental={incremental})")
    typer.echo(f"  Corpus: {corpus.resolve()}")
    typer.echo(f"  Embedding model: {model_name}")

    # 1. Gather documents
    # Prioritize .md sources; fallback to .pdf if .md not present
    md_files = sorted(corpus.glob("*.md"))
    pdf_files = sorted(corpus.glob("*.pdf"))

    target_files: list[Path] = []
    if md_files:
        target_files = md_files
    elif pdf_files:
        target_files = pdf_files
    else:
        typer.secho("No .md or .pdf files found in corpus directory.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    typer.echo(f"  Found {len(target_files)} corpus files to process.")

    # 2. Database & Qdrant setup
    engine = get_engine()
    init_db(engine)

    qdrant = get_qdrant_client()
    if rebuild:
        # Clear Qdrant collection
        if qdrant.collection_exists(QDRANT_COLLECTION):
            qdrant.delete_collection(QDRANT_COLLECTION)
        init_qdrant_collection(qdrant, QDRANT_COLLECTION)
    else:
        init_qdrant_collection(qdrant, QDRANT_COLLECTION)

    all_records: list[ChunkRecord] = []
    all_error_codes = []
    all_specs = []
    doc_manifest: dict[str, dict[str, Any]] = {}
    corpus_hasher = hashlib.sha256()

    # 3. Process each document
    for doc_file in target_files:
        f_hash = compute_file_hash(doc_file)
        corpus_hasher.update(f_hash.encode("utf-8"))

        parsed_doc = parse_document(doc_file)
        records = chunk_blocks(parsed_doc)
        all_records.extend(records)

        # Extract tables
        doc_raw_text = doc_file.read_text(encoding="utf-8") if doc_file.suffix == ".md" else "\n".join(b.text for b in parsed_doc.blocks)
        error_codes = extract_error_codes(doc_raw_text, parsed_doc.asset_class)
        specs = extract_specs(doc_raw_text, parsed_doc.asset_class, doc_id=parsed_doc.doc_id)

        all_error_codes.extend(error_codes)
        all_specs.extend(specs)

        doc_manifest[doc_file.name] = {
            "doc_id": parsed_doc.doc_id,
            "hash": f_hash,
            "chunks": len(records),
            "safety_chunks": sum(1 for r in records if r.chunk.has_safety),
            "error_codes": len(error_codes),
            "specs": len(specs),
        }

        typer.echo(
            f"  Parsed {doc_file.name}: {len(records)} chunks, "
            f"{len(error_codes)} error codes, {len(specs)} specs"
        )

    # 4. Prompt Injection Security Scan
    quarantine_report = scan_prompt_injections(all_records)
    quarantine_file = data_dir / "quarantine_report.json"
    quarantine_file.write_text(json.dumps(quarantine_report, indent=2), encoding="utf-8")
    if quarantine_report:
        typer.secho(
            f"  SECURITY WARNING: {len(quarantine_report)} chunks flagged for prompt-injection patterns!",
            fg=typer.colors.YELLOW,
        )
    else:
        typer.echo("  Security injection scan: 0 threats detected.")

    # 5. Embeddings (Dense & Sparse)
    typer.echo("  Generating / caching dense embeddings (BAAI/bge-small-en-v1.5) ...")
    embeddings = embed_chunks(
        all_records,
        model_name=model_name,
    )
    typer.echo(f"  Dense embeddings ready: {len(embeddings)} vectors (dim={len(embeddings[0]) if embeddings else 0}).")

    typer.echo("  Building BM25 sparse index ...")
    bm25_path = data_dir / "indices" / "bm25_index.pkl"
    build_bm25_index(all_records, out_path=bm25_path)
    typer.echo(f"  BM25 index saved -> {bm25_path}")

    # 6. Idempotent Storage
    typer.echo("  Persisting chunks and side-tables to database ...")
    with Session(engine) as session:
        upsert_chunks(session, all_records)
        upsert_error_codes(session, all_error_codes)
        upsert_specs(session, all_specs)

    typer.echo("  Upserting vectors into Qdrant ...")
    upsert_vectors(qdrant, all_records, embeddings)

    # 7. Write Manifest
    manifest = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "corpus_path": str(corpus.resolve()),
        "corpus_revision": corpus_hasher.hexdigest()[:16],
        "embedding_model": model_name,
        "embedding_dim": 384,
        "total_chunks": len(all_records),
        "safety_chunks": sum(1 for r in all_records if r.chunk.has_safety),
        "oversized_chunks": sum(1 for r in all_records if r.oversized),
        "flagged_chunks": len(quarantine_report),
        "error_codes_count": len(all_error_codes),
        "specs_count": len(all_specs),
        "documents": doc_manifest,
    }
    manifest_file = data_dir / "manifest.json"
    manifest_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    typer.echo(f"  Manifest written -> {manifest_file}")

    typer.secho("\nIngestion completed successfully!", fg=typer.colors.GREEN)
    typer.echo(f"  Total Chunks:     {len(all_records)}")
    typer.echo(f"  Safety Chunks:    {manifest['safety_chunks']}")
    typer.echo(f"  Error Codes:      {len(all_error_codes)}")
    typer.echo(f"  Specs Extracted:  {len(all_specs)}")
    typer.echo(f"  Flagged Chunks:   {manifest['flagged_chunks']}")


if __name__ == "__main__":
    app()
