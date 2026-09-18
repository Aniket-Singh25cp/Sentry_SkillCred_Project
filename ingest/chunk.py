"""ingest/chunk.py - Structure-aware document chunking for SENTRY S1.

Chunking strategy:
  1. Split on document headings first (outermost section boundary).
  2. Within each section, window text at 600-900 tokens with 15% overlap.
  3. HARD RULE: never split a numbered procedure across two chunks.
     If a procedure exceeds the token window, keep it whole in one chunk
     and set `oversized = True` in metadata.
  4. chunk_id = sha1(doc_id + "::" + "/".join(section_path) + "::" + str(chunk_index))[:12]
     Strictly stable across re-ingestion.
  5. Outputs validate strictly against core.schemas.Chunk.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Literal

import tiktoken

from core.schemas import Chunk
from ingest.parse import Block, ParsedDocument
from ingest.safety_tag import tag_safety_notes

_TOKENIZER = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    """Return the exact token count using tiktoken cl100k_base."""
    return len(_TOKENIZER.encode(text))


@dataclass
class ChunkRecord:
    """A Chunk accompanied by extra ingestion metadata stored in DB/Qdrant."""

    chunk: Chunk
    oversized: bool = False
    flagged: bool = False
    content_hash: str = ""

    @property
    def chunk_id(self) -> str:
        return self.chunk.chunk_id


def _compute_chunk_id(doc_id: str, section_path: list[str], chunk_index: int) -> str:
    """Generate stable, deterministic 12-hex-char SHA-1 prefix."""
    raw = f"{doc_id}::{'/'.join(section_path)}::{chunk_index}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]


def _infer_chunk_type(blocks: list[Block], section_path: list[str]) -> Literal["procedure", "description", "table", "warning"]:
    """Determine the chunk_type classification."""
    sec_str = " ".join(section_path).lower()
    has_steps = any(b.block_type == "procedure_step" for b in blocks)
    has_callouts = any(b.block_type == "callout" for b in blocks)
    has_tables = any(b.block_type == "table" for b in blocks)

    # 1. Procedure check
    if has_steps or "procedure" in sec_str or "step" in sec_str:
        return "procedure"

    # 2. Warning / Safety check
    if has_callouts and not has_tables:
        callout_len = sum(len(b.text) for b in blocks if b.block_type == "callout")
        total_len = sum(len(b.text) for b in blocks)
        if callout_len >= 0.4 * total_len:
            return "warning"

    # 3. Table check
    if has_tables:
        table_len = sum(len(b.text) for b in blocks if b.block_type == "table")
        total_len = sum(len(b.text) for b in blocks)
        if table_len >= 0.5 * total_len:
            return "table"

    return "description"


def _is_procedure_block_group(blocks: list[Block]) -> bool:
    """Check if the given block group constitutes a numbered procedure."""
    has_steps = any(b.block_type == "procedure_step" for b in blocks)
    if has_steps:
        return True
    # Also check if blocks have numbered step patterns
    step_count = sum(1 for b in blocks if re.match(r"^\d+\.\s+", b.text.strip()))
    return step_count >= 2


def chunk_blocks(
    parsed_doc: ParsedDocument,
    min_tokens: int = 600,
    max_tokens: int = 900,
    overlap_ratio: float = 0.15,
) -> list[ChunkRecord]:
    """Split a ParsedDocument into structure-aware Chunk records."""
    records: list[ChunkRecord] = []

    # 1. Group blocks by section_path
    sections: dict[tuple[str, ...], list[Block]] = {}
    for block in parsed_doc.blocks:
        key = tuple(block.heading_path)
        if key not in sections:
            sections[key] = []
        sections[key].append(block)

    chunk_counter_per_section: dict[tuple[str, ...], int] = {}

    for sec_key, sec_blocks in sections.items():
        section_path = list(sec_key)
        chunk_counter_per_section[sec_key] = 0

        # Check if the section as a whole represents a procedure with numbered steps
        if _is_procedure_block_group(sec_blocks):
            # HARD RULE: Never split a numbered procedure across chunks.
            # If the entire section is a procedure, keep all procedure steps together.
            full_text = "\n\n".join(b.text for b in sec_blocks)
            token_len = count_tokens(full_text)
            oversized = token_len > max_tokens

            page_start = min(b.page for b in sec_blocks)
            page_end = max(b.page for b in sec_blocks)
            chunk_idx = chunk_counter_per_section[sec_key]
            chunk_counter_per_section[sec_key] += 1

            chunk_id = _compute_chunk_id(parsed_doc.doc_id, section_path, chunk_idx)
            has_safety, safety_notes = tag_safety_notes(full_text)
            chunk_type = _infer_chunk_type(sec_blocks, section_path)

            chunk = Chunk(
                chunk_id=chunk_id,
                doc_id=parsed_doc.doc_id,
                doc_title=parsed_doc.doc_title,
                revision=parsed_doc.revision,
                section_path=section_path,
                page_start=page_start,
                page_end=page_end,
                text=full_text,
                chunk_type=chunk_type,
                has_safety=has_safety,
                safety_notes=safety_notes,
                asset_class=parsed_doc.asset_class,
                applicable_models=parsed_doc.applicable_models,
                token_count=token_len,
            )

            c_hash = hashlib.sha256(full_text.encode("utf-8")).hexdigest()
            records.append(
                ChunkRecord(
                    chunk=chunk,
                    oversized=oversized,
                    flagged=False,
                    content_hash=c_hash,
                )
            )
            continue

        # 2. For non-procedure sections: group into windows of 600-900 tokens with 15% overlap
        current_blocks: list[Block] = []
        current_tokens = 0
        overlap_tokens = int(max_tokens * overlap_ratio)

        b_idx = 0
        while b_idx < len(sec_blocks):
            b = sec_blocks[b_idx]
            b_tokens = count_tokens(b.text)

            if current_tokens + b_tokens <= max_tokens or not current_blocks:
                current_blocks.append(b)
                current_tokens += b_tokens
                b_idx += 1
            else:
                # Flush current chunk
                full_text = "\n\n".join(cb.text for cb in current_blocks)
                token_len = count_tokens(full_text)
                oversized = token_len > max_tokens

                page_start = min(cb.page for cb in current_blocks)
                page_end = max(cb.page for cb in current_blocks)
                chunk_idx = chunk_counter_per_section[sec_key]
                chunk_counter_per_section[sec_key] += 1

                chunk_id = _compute_chunk_id(parsed_doc.doc_id, section_path, chunk_idx)
                has_safety, safety_notes = tag_safety_notes(full_text)
                chunk_type = _infer_chunk_type(current_blocks, section_path)

                chunk = Chunk(
                    chunk_id=chunk_id,
                    doc_id=parsed_doc.doc_id,
                    doc_title=parsed_doc.doc_title,
                    revision=parsed_doc.revision,
                    section_path=section_path,
                    page_start=page_start,
                    page_end=page_end,
                    text=full_text,
                    chunk_type=chunk_type,
                    has_safety=has_safety,
                    safety_notes=safety_notes,
                    asset_class=parsed_doc.asset_class,
                    applicable_models=parsed_doc.applicable_models,
                    token_count=token_len,
                )
                c_hash = hashlib.sha256(full_text.encode("utf-8")).hexdigest()
                records.append(
                    ChunkRecord(
                        chunk=chunk,
                        oversized=oversized,
                        flagged=False,
                        content_hash=c_hash,
                    )
                )

                # Overlap: keep tail blocks that fit within overlap_tokens
                tail_blocks: list[Block] = []
                tail_tokens = 0
                for tb in reversed(current_blocks):
                    t_tok = count_tokens(tb.text)
                    if tail_tokens + t_tok <= overlap_tokens:
                        tail_blocks.insert(0, tb)
                        tail_tokens += t_tok
                    else:
                        break

                current_blocks = list(tail_blocks)
                current_tokens = tail_tokens

        # Flush remaining blocks in section
        if current_blocks:
            full_text = "\n\n".join(cb.text for cb in current_blocks)
            token_len = count_tokens(full_text)
            oversized = token_len > max_tokens

            page_start = min(cb.page for cb in current_blocks)
            page_end = max(cb.page for cb in current_blocks)
            chunk_idx = chunk_counter_per_section[sec_key]
            chunk_counter_per_section[sec_key] += 1

            chunk_id = _compute_chunk_id(parsed_doc.doc_id, section_path, chunk_idx)
            has_safety, safety_notes = tag_safety_notes(full_text)
            chunk_type = _infer_chunk_type(current_blocks, section_path)

            chunk = Chunk(
                chunk_id=chunk_id,
                doc_id=parsed_doc.doc_id,
                doc_title=parsed_doc.doc_title,
                revision=parsed_doc.revision,
                section_path=section_path,
                page_start=page_start,
                page_end=page_end,
                text=full_text,
                chunk_type=chunk_type,
                has_safety=has_safety,
                safety_notes=safety_notes,
                asset_class=parsed_doc.asset_class,
                applicable_models=parsed_doc.applicable_models,
                token_count=token_len,
            )
            c_hash = hashlib.sha256(full_text.encode("utf-8")).hexdigest()
            records.append(
                ChunkRecord(
                    chunk=chunk,
                    oversized=oversized,
                    flagged=False,
                    content_hash=c_hash,
                )
            )

    return records
