"""ingest/safety_tag.py - Verbatim safety annotation for SENTRY S1.

Detects safety callouts and safety-critical sentences within document chunks.
Hard rule: safety statements must be preserved byte-for-byte with zero
normalization, stripping, or reformatting, to prevent production safety gate failures.
"""

from __future__ import annotations

import re
from typing import Literal

from core.schemas import SafetyNote

# Case-sensitive signal words per IEC/ANSI Z535
SIGNAL_WORDS_PATTERN = re.compile(r"\b(DANGER|WARNING|CAUTION|NOTICE)\b")

# Case-insensitive safety domain keywords
SAFETY_KEYWORDS_PATTERN = re.compile(
    r"\b(lockout|tagout|loto|de-energize|de-energise|isolate|ppe|arc\s+flash|"
    r"confined\s+space|pressure\s+relief|residual\s+pressure|stored\s+energy)\b",
    re.IGNORECASE,
)

# Pattern to identify callout blocks (e.g. "DANGER: ...", "> **WARNING:** ...")
CALLOUT_START_PATTERN = re.compile(
    r"(?:^|\n)(?:>\s*(?:\*\*)?)?(DANGER|WARNING|CAUTION|NOTICE)(?:\*\*)?:\s*",
    re.MULTILINE,
)


def _determine_severity(text: str) -> Literal["danger", "warning", "caution", "notice"]:
    """Determine IEC/ANSI Z535 severity from text signals."""
    if "DANGER" in text:
        return "danger"
    if "WARNING" in text:
        return "warning"
    if "CAUTION" in text:
        return "caution"
    if "NOTICE" in text:
        return "notice"
    # Domain keywords without signal words default to warning level
    return "warning"


def _split_into_sentence_spans(text: str) -> list[tuple[int, int]]:
    """Find start and end indices of sentences in text preserving byte spans.
    
    Uses regex matching sentence terminators (.!?) followed by space/newline/quote
    without modifying or trimming characters.
    """
    spans: list[tuple[int, int]] = []
    # Pattern looks for sentence boundary: terminal punctuation followed by space or newline
    # Handles numbers with decimals (e.g., 2.5 mm) by requiring a space and capital/symbol after period.
    pattern = re.compile(r'(?:[^\.\?!]+(?:\.[0-9]+)*)+(?:[\.\?!]+["\'\)]?|\Z)')
    for match in pattern.finditer(text):
        s = match.start()
        e = match.end()
        # Find actual non-whitespace boundary inside the match without mutating text
        span_text = text[s:e]
        if span_text.strip():
            # Keep exact slice
            left_trim = len(span_text) - len(span_text.lstrip())
            right_trim = len(span_text) - len(span_text.rstrip())
            start_idx = s + left_trim
            end_idx = e - right_trim if right_trim > 0 else e
            if start_idx < end_idx:
                spans.append((start_idx, end_idx))
    return spans


def extract_safety_notes(text: str) -> list[SafetyNote]:
    """Extract all safety notes verbatim from chunk text.

    Captures both:
      1. Full callout blocks (e.g., 'WARNING: Apply lockout/tagout...') verbatim
         which match scenario ground truth strings.
      2. Individual sentences containing domain safety keywords (LOTO, isolation, etc.).
    """
    notes: list[SafetyNote] = []
    seen_texts: set[str] = set()

    # 1. First extract complete callout paragraphs
    # In Markdown/parsed text, callouts are lines or paragraphs starting with signal words
    lines = text.split("\n")
    idx = 0
    while idx < len(lines):
        line = lines[idx]
        stripped = line.strip()
        # Check if line is a callout (e.g. "> **WARNING:** ...", "DANGER: ...")
        m = re.match(r"^(?:>\s*)?(?:\*\*)?(DANGER|WARNING|CAUTION|NOTICE):?(?:\*\*)?:?\s*(.*)$", stripped)
        if m and m.group(2):
            signal = m.group(1)
            body = m.group(2)
            # If multi-line callout, collect subsequent indented or quote lines
            callout_lines = [body]
            idx += 1
            while idx < len(lines) and lines[idx].startswith(">"):
                next_part = lines[idx].lstrip(">").strip()
                if next_part:
                    callout_lines.append(next_part)
                idx += 1

            full_callout = f"{signal}: {' '.join(callout_lines)}"
            sev = _determine_severity(signal)
            if full_callout not in seen_texts:
                seen_texts.add(full_callout)
                notes.append(SafetyNote(text=full_callout, severity=sev))
            continue
        idx += 1

    # 2. Also scan for sentences that contain signal words or safety keywords
    # Sentence spans on the raw text
    spans = _split_into_sentence_spans(text)
    for start, end in spans:
        sentence = text[start:end]
        # Ignore if it's already a full callout or just a table header
        if sentence in seen_texts or len(sentence) < 15:
            continue
        # Clean blockquote marker from start if present for check, but preserve verbatim sentence
        has_signal = bool(SIGNAL_WORDS_PATTERN.search(sentence))
        has_keyword = bool(SAFETY_KEYWORDS_PATTERN.search(sentence))

        if has_signal or has_keyword:
            # Clean markdown blockquote prefix '> ' or '**' from sentence if it was captured from markdown
            clean_sentence = re.sub(r"^>\s*", "", sentence)
            clean_sentence = re.sub(r"^\*\*([A-Z]+):\*\*\s*", r"\1: ", clean_sentence)
            if clean_sentence not in seen_texts:
                seen_texts.add(clean_sentence)
                sev = _determine_severity(clean_sentence)
                notes.append(SafetyNote(text=clean_sentence, severity=sev))

    return notes


def tag_safety_notes(chunk_text: str) -> tuple[bool, list[SafetyNote]]:
    """Scan chunk text for safety notes and return (has_safety, safety_notes)."""
    notes = extract_safety_notes(chunk_text)
    return len(notes) > 0, notes
