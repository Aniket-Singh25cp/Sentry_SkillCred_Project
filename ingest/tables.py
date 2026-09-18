"""ingest/tables.py - Structured side-table extraction for SENTRY S1.

Extracts structured tables from the corpus:
  1. Error code reference tables -> ErrorCodeEntry records (for exact match lookup)
  2. Equipment specification and torque tables -> SpecEntry records
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from core.schemas import ErrorCodeEntry


@dataclass(frozen=True)
class SpecEntry:
    """A structured equipment specification or torque setting row."""

    asset_class: str
    item: str
    value: str
    unit: str
    section_ref: str
    doc_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_class": self.asset_class,
            "item": self.item,
            "value": self.value,
            "unit": self.unit,
            "section_ref": self.section_ref,
            "doc_id": self.doc_id,
        }


def parse_markdown_table_rows(table_text: str) -> tuple[list[str], list[list[str]]]:
    """Parse a Markdown table string into (headers, rows)."""
    lines = [line.strip() for line in table_text.strip().split("\n") if line.strip()]
    if len(lines) < 3:
        return [], []

    # First line: headers
    headers = [col.strip() for col in lines[0].strip("|").split("|")]

    # Second line: separator (|---|---|...)
    if not all(set(c.strip()) <= {"-", ":", "|"} for c in lines[1].split("|")):
        return [], []

    # Subsequent lines: data rows
    rows: list[list[str]] = []
    for line in lines[2:]:
        if not line.startswith("|") and not line.endswith("|"):
            continue
        cols = [col.strip() for col in line.strip("|").split("|")]
        # Pad or trim to header length
        if len(cols) < len(headers):
            cols.extend([""] * (len(headers) - len(cols)))
        rows.append(cols[:len(headers)])

    return headers, rows


def extract_error_codes(
    text: str,
    asset_class: str,
    default_section_ref: str = "Section 8",
) -> list[ErrorCodeEntry]:
    """Extract error code rows from markdown text into ErrorCodeEntry models."""
    entries: list[ErrorCodeEntry] = []
    # Find table blocks following Error Code headings
    sections = re.split(r"(?:^|\n)(?=#{1,4}\s+)", text)

    for section in sections:
        header_match = re.match(r"^#{1,4}\s+(.*)", section.strip())
        section_title = header_match.group(1).strip() if header_match else default_section_ref
        if "error code" not in section_title.lower() and "fault code" not in section_title.lower():
            continue

        # Extract table from this section
        table_match = re.search(r"(\|.*\|(?:\n\|.*\|)+)", section)
        if not table_match:
            continue

        headers, rows = parse_markdown_table_rows(table_match.group(1))
        if not headers:
            continue

        # Map column positions by header names
        header_lower = [h.lower() for h in headers]
        code_col = next((i for i, h in enumerate(header_lower) if "code" in h), 0)
        meaning_col = next((i for i, h in enumerate(header_lower) if "meaning" in h or "description" in h), 1)
        causes_col = next((i for i, h in enumerate(header_lower) if "cause" in h), 2)
        ref_col = next((i for i, h in enumerate(header_lower) if "ref" in h or "section" in h), 3)

        for row in rows:
            if not row or len(row) <= max(code_col, meaning_col):
                continue
            code = row[code_col].strip()
            # Validate code format (e.g. E-101, G-201)
            if not re.match(r"^[A-Z]-[0-9]{3}$", code):
                continue

            meaning = row[meaning_col].strip()
            # Probable causes: comma- or semicolon-separated list
            causes_raw = row[causes_col].strip() if len(row) > causes_col else ""
            if causes_raw:
                causes = [c.strip() for c in re.split(r"[,;]\s*", causes_raw) if c.strip()]
            else:
                causes = []

            ref = row[ref_col].strip() if len(row) > ref_col and row[ref_col].strip() else section_title

            entries.append(
                ErrorCodeEntry(
                    code=code,
                    asset_class=asset_class,
                    meaning=meaning,
                    probable_causes=causes,
                    section_ref=ref,
                )
            )

    return entries


def extract_specs(
    text: str,
    asset_class: str,
    doc_id: str = "",
) -> list[SpecEntry]:
    """Extract equipment specifications and torque values into SpecEntry records."""
    specs: list[SpecEntry] = []
    sections = re.split(r"(?:^|\n)(?=#{1,4}\s+)", text)

    for section in sections:
        header_match = re.match(r"^#{1,4}\s+(.*)", section.strip())
        section_title = header_match.group(1).strip() if header_match else "Specifications"
        title_lower = section_title.lower()

        is_torque = "torque" in title_lower or "bolt" in title_lower or "fastener" in title_lower
        is_perf = "performance" in title_lower or "specification" in title_lower or "data" in title_lower
        if not (is_torque or is_perf):
            continue

        # Find tables in this section
        for table_match in re.finditer(r"(\|.*\|(?:\n\|.*\|)+)", section):
            headers, rows = parse_markdown_table_rows(table_match.group(1))
            if not headers:
                continue

            header_lower = [h.lower() for h in headers]

            # Case A: Torque table (| Location | Fastener Size | Torque (Nm) | ... |)
            if any("torque" in h for h in header_lower):
                loc_col = 0
                torque_col = next((i for i, h in enumerate(header_lower) if "torque" in h), 2)
                fastener_col = next((i for i, h in enumerate(header_lower) if "fastener" in h or "size" in h), 1)

                unit = "Nm"
                for row in rows:
                    if not row or len(row) <= loc_col:
                        continue
                    item_name = row[loc_col].strip()
                    if not item_name:
                        continue
                    fastener_info = row[fastener_col].strip() if len(row) > fastener_col else ""
                    torque_val = row[torque_col].strip() if len(row) > torque_col else ""
                    val_str = f"{fastener_info}: {torque_val}".strip(": ") if fastener_info else torque_val

                    specs.append(
                        SpecEntry(
                            asset_class=asset_class,
                            item=item_name,
                            value=val_str,
                            unit=unit,
                            section_ref=section_title,
                            doc_id=doc_id,
                        )
                    )

            # Case B: General Parameter/Value/Unit table (| Parameter | Value | Unit |)
            elif any("parameter" in h for h in header_lower) and any("value" in h for h in header_lower):
                param_col = next(i for i, h in enumerate(header_lower) if "parameter" in h)
                val_col = next(i for i, h in enumerate(header_lower) if "value" in h)
                unit_col = next((i for i, h in enumerate(header_lower) if "unit" in h), -1)

                for row in rows:
                    if not row or len(row) <= max(param_col, val_col):
                        continue
                    param_name = row[param_col].strip()
                    param_val = row[val_col].strip()
                    param_unit = row[unit_col].strip() if unit_col >= 0 and len(row) > unit_col else ""
                    if not param_name or not param_val:
                        continue

                    specs.append(
                        SpecEntry(
                            asset_class=asset_class,
                            item=param_name,
                            value=param_val,
                            unit=param_unit,
                            section_ref=section_title,
                            doc_id=doc_id,
                        )
                    )

    return specs
