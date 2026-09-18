"""ingest/parse.py - Document parsing for Markdown and PDF in SENTRY S1.

Parses Markdown sources and PyMuPDF PDFs into a stream of structured Block objects:
  (text, page, heading_path, block_type)
Preserves list/step numbering (e.g. '1.', '2.', '3.') without loss.
Extracts document metadata (doc_id, doc_title, revision, asset_class, applicable_models).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

try:
    import pymupdf as fitz  # type: ignore[import-untyped]
except ImportError:
    import fitz  # type: ignore[import-untyped]


BlockType = Literal["heading", "procedure_step", "paragraph", "table", "callout"]


@dataclass
class Block:
    """An intermediate block of parsed document content."""

    text: str
    page: int
    heading_path: list[str] = field(default_factory=list)
    block_type: BlockType = "paragraph"


@dataclass
class ParsedDocument:
    """A fully parsed document with extracted metadata and block stream."""

    doc_id: str
    doc_title: str
    revision: str
    asset_class: str
    applicable_models: list[str]
    blocks: list[Block]
    file_path: Path


def _slugify(name: str) -> str:
    """Convert filename or title to a clean slug doc_id."""
    base = Path(name).stem
    return re.sub(r"[^a-zA-Z0-9_-]", "_", base).lower()


def _extract_markdown_metadata(text: str, default_doc_id: str) -> dict[str, str | list[str]]:
    """Extract document-level metadata from the markdown front matter / top lines."""
    meta: dict[str, str | list[str]] = {
        "doc_id": default_doc_id,
        "doc_title": "",
        "revision": "Rev A",
        "asset_class": "centrifugal_pump",
        "applicable_models": [],
    }

    lines = text.split("\n")
    for line in lines[:30]:
        stripped = line.strip()
        if stripped.startswith("# ") and not meta["doc_title"]:
            meta["doc_title"] = stripped[2:].strip()
        elif "**Document Number:**" in stripped:
            val = stripped.split("**Document Number:**")[1].strip()
            meta["doc_number"] = val
        elif "**Revision:**" in stripped:
            meta["revision"] = stripped.split("**Revision:**")[1].strip()
        elif "**Asset Class:**" in stripped or "**Asset Classes:**" in stripped:
            val = re.split(r"\*\*Asset Class(?:es)?:\*\*", stripped)[1].strip()
            # If multiple comma-separated, pick first matching or default
            classes = [c.strip() for c in val.split(",")]
            meta["asset_class"] = classes[0] if classes else "centrifugal_pump"
        elif "**Applicable Models:**" in stripped:
            models = stripped.split("**Applicable Models:**")[1].strip()
            meta["applicable_models"] = [m.strip() for m in models.split(",") if m.strip()]

    if not meta["doc_title"]:
        meta["doc_title"] = default_doc_id.replace("_", " ").title()

    return meta


def parse_markdown(file_path: Path) -> ParsedDocument:
    """Parse a Markdown document into metadata and an ordered Block stream."""
    text = file_path.read_text(encoding="utf-8")
    doc_id = _slugify(file_path.stem)
    meta = _extract_markdown_metadata(text, default_doc_id=doc_id)

    blocks: list[Block] = []
    current_headings: list[str] = []
    current_page = 1
    lines_per_page = 35  # Approximate page length for markdown pagination

    lines = text.split("\n")
    i = 0
    total_lines = len(lines)

    while i < total_lines:
        line = lines[i]
        stripped = line.strip()

        # Update page number estimation
        current_page = max(1, (i // lines_per_page) + 1)

        # Skip empty lines and horizontal rules
        if not stripped or stripped in ("---", "***", "___"):
            i += 1
            continue

        # 1. Headings
        heading_match = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if heading_match:
            level = len(heading_match.group(1))
            heading_text = heading_match.group(2).strip()

            if level == 1:
                # Top level document title
                current_headings = []
            elif level == 2:
                current_headings = [heading_text]
            elif level >= 3:
                # Keep up to level - 2 parent headings, then append
                parent_depth = level - 2
                current_headings = current_headings[:parent_depth] + [heading_text]

            blocks.append(
                Block(
                    text=heading_text,
                    page=current_page,
                    heading_path=list(current_headings),
                    block_type="heading",
                )
            )
            i += 1
            continue

        # 2. Callouts (e.g. "> **WARNING:** ...")
        if stripped.startswith(">"):
            callout_lines = [stripped]
            i += 1
            while i < total_lines and lines[i].strip().startswith(">"):
                callout_lines.append(lines[i].strip())
                i += 1
            full_callout = "\n".join(callout_lines)
            blocks.append(
                Block(
                    text=full_callout,
                    page=current_page,
                    heading_path=list(current_headings),
                    block_type="callout",
                )
            )
            continue

        # 3. Tables (starts with |)
        if stripped.startswith("|") and stripped.endswith("|"):
            table_lines = [stripped]
            i += 1
            while i < total_lines and lines[i].strip().startswith("|") and lines[i].strip().endswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            full_table = "\n".join(table_lines)
            blocks.append(
                Block(
                    text=full_table,
                    page=current_page,
                    heading_path=list(current_headings),
                    block_type="table",
                )
            )
            continue

        # 4. Procedure steps (starts with 1., 2., 3., etc.)
        step_match = re.match(r"^(\d+\.)\s+(.*)$", stripped)
        if step_match:
            step_num = step_match.group(1)
            step_body = [stripped]
            i += 1
            # Collect continuation lines indented or belonging to this step
            while i < total_lines:
                next_line = lines[i]
                next_stripped = next_line.strip()
                if not next_stripped:
                    # Look ahead: if next non-empty is another step or heading, stop
                    break
                if re.match(r"^\d+\.\s+", next_stripped) or next_stripped.startswith(("#", ">", "|")):
                    break
                step_body.append(next_stripped)
                i += 1
            full_step = " ".join(step_body)
            blocks.append(
                Block(
                    text=full_step,
                    page=current_page,
                    heading_path=list(current_headings),
                    block_type="procedure_step",
                )
            )
            continue

        # 5. Regular paragraph
        para_lines = [stripped]
        i += 1
        while i < total_lines:
            next_line = lines[i]
            next_stripped = next_line.strip()
            if not next_stripped:
                break
            if next_stripped.startswith(("#", ">", "|")) or re.match(r"^\d+\.\s+", next_stripped):
                break
            para_lines.append(next_stripped)
            i += 1
        full_para = " ".join(para_lines)
        blocks.append(
            Block(
                text=full_para,
                page=current_page,
                heading_path=list(current_headings),
                block_type="paragraph",
            )
        )

    return ParsedDocument(
        doc_id=doc_id,
        doc_title=str(meta["doc_title"]),
        revision=str(meta["revision"]),
        asset_class=str(meta["asset_class"]),
        applicable_models=list(meta["applicable_models"]),
        blocks=blocks,
        file_path=file_path,
    )


def parse_pdf(file_path: Path) -> ParsedDocument:
    """Parse a PDF document via PyMuPDF into metadata and an ordered Block stream."""
    doc = fitz.open(str(file_path))
    doc_id = _slugify(file_path.stem)

    # Check for corresponding markdown file to read canonical metadata
    md_companion = file_path.with_suffix(".md")
    if md_companion.exists():
        md_parsed = parse_markdown(md_companion)
        meta = {
            "doc_title": md_parsed.doc_title,
            "revision": md_parsed.revision,
            "asset_class": md_parsed.asset_class,
            "applicable_models": md_parsed.applicable_models,
        }
    else:
        meta = {
            "doc_title": doc_id.replace("_", " ").title(),
            "revision": "Rev A",
            "asset_class": "centrifugal_pump" if "pump" in doc_id else "industrial_gearbox",
            "applicable_models": [],
        }

    blocks: list[Block] = []
    current_headings: list[str] = []

    for page_idx in range(len(doc)):
        page = doc[page_idx]
        page_num = page_idx + 1

        # Use page.get_text("blocks") -> (x0, y0, x1, y1, text, block_no, block_type)
        page_blocks = page.get_text("blocks")
        for b in page_blocks:
            raw_text = b[4].strip()
            if not raw_text or raw_text.startswith("Page ") and " of " in raw_text:
                continue

            # Detect heading lines (e.g. "1. Introduction", "7.3 Excessive Vibration")
            heading_m = re.match(r"^(\d+(?:\.\d+)*\.?\s+[A-Za-z].*)$", raw_text)
            if heading_m and len(raw_text.split("\n")) == 1 and len(raw_text) < 80:
                h_text = heading_m.group(1).strip()
                # Determine level by dot count
                dots = h_text.split()[0].count(".")
                if dots <= 1:
                    current_headings = [h_text]
                else:
                    current_headings = current_headings[:dots - 1] + [h_text]

                blocks.append(
                    Block(
                        text=h_text,
                        page=page_num,
                        heading_path=list(current_headings),
                        block_type="heading",
                    )
                )
                continue

            # Detect callouts
            if any(raw_text.startswith(sw) for sw in ("DANGER:", "WARNING:", "CAUTION:", "NOTICE:")):
                blocks.append(
                    Block(
                        text=raw_text,
                        page=page_num,
                        heading_path=list(current_headings),
                        block_type="callout",
                    )
                )
                continue

            # Detect numbered procedure steps
            if re.match(r"^\d+\.\s+", raw_text):
                blocks.append(
                    Block(
                        text=raw_text,
                        page=page_num,
                        heading_path=list(current_headings),
                        block_type="procedure_step",
                    )
                )
                continue

            # Detect tables (contains multiple pipe characters or tabular spacing)
            if "|" in raw_text:
                blocks.append(
                    Block(
                        text=raw_text,
                        page=page_num,
                        heading_path=list(current_headings),
                        block_type="table",
                    )
                )
                continue

            # General paragraph
            blocks.append(
                Block(
                    text=raw_text,
                    page=page_num,
                    heading_path=list(current_headings),
                    block_type="paragraph",
                )
            )

    doc.close()

    return ParsedDocument(
        doc_id=doc_id,
        doc_title=str(meta["doc_title"]),
        revision=str(meta["revision"]),
        asset_class=str(meta["asset_class"]),
        applicable_models=list(meta["applicable_models"]),
        blocks=blocks,
        file_path=file_path,
    )


def parse_document(file_path: Path) -> ParsedDocument:
    """Parse document according to its file extension (.md or .pdf)."""
    ext = file_path.suffix.lower()
    if ext == ".md":
        return parse_markdown(file_path)
    elif ext == ".pdf":
        return parse_pdf(file_path)
    else:
        raise ValueError(f"Unsupported document format: {ext} (expected .md or .pdf)")
