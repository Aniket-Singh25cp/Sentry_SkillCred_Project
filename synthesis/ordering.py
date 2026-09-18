"""synthesis/ordering.py — Enforce checklist tier ordering in code.

Hard constraint: Checklist step ordering is never left to the model.
Ordering tiers:
  1. is_safety_critical steps (energy isolation / LOTO / PPE) — ALWAYS FIRST
  2. non-invasive observation and measurement
  3. low-cost / low-time checks
  4. invasive disassembly

Within each tier, the model's relative ordering is strictly preserved.
Any re-sorting is logged for traceability.
"""

from __future__ import annotations

import re

import structlog

from core.schemas import ChecklistStep

logger = structlog.get_logger(__name__)

# Action and tool regex patterns with word boundaries
_SAFETY_PATTERN = re.compile(
    r"\b(lockout|tagout|loto|isolate|isolation|de-energize|de-energise|zero-energy|ppe|arc flash)\b",
    re.IGNORECASE,
)

_INVASIVE_PATTERN = re.compile(
    r"\b(disassemble|disassembly|remove|removal|replace|replacement|tear down|overhaul|pull|unbolt|strip|extract|dismantle|rebuild)\b",
    re.IGNORECASE,
)

_OBSERVATION_PATTERN = re.compile(
    r"\b(inspect|observe|check|measure|verify|read|listen|visual|monitor|gauge|examine|record|test port)\b",
    re.IGNORECASE,
)


def classify_step_tier(step: ChecklistStep) -> int:
    """Classify a checklist step into one of four strictly ordered execution tiers.

    Returns:
      1: Safety critical (LOTO, PPE, energy isolation)
      2: Non-invasive observation and measurement
      3: Low-cost / low-time checks
      4: Invasive disassembly
    """
    action_text = step.action
    tools_text = " ".join(step.tools_required)
    combined_text = f"{action_text} {tools_text}"

    # Tier 1: Explicit flag or regex-matched safety isolation
    if step.is_safety_critical or _SAFETY_PATTERN.search(combined_text):
        return 1

    # Tier 4: Invasive mechanical actions
    if _INVASIVE_PATTERN.search(action_text):
        return 4

    # Tier 2: Non-invasive sensory check or measurement
    if _OBSERVATION_PATTERN.search(action_text):
        return 2

    # Tier 3: Default bucket for routine low-cost checks
    return 3


def order_checklist_steps(steps: list[ChecklistStep]) -> list[ChecklistStep]:
    """Sort checklist steps strictly by tier while preserving relative intra-tier ordering.

    Re-indexes the final list 1-based (order = 1, 2, 3...) per ChecklistStep contract.
    Logs an audit event if re-ordering changes the sequence.
    """
    if not steps:
        return []

    # Preserve initial order via enumeration index for stable sorting
    indexed_tiers: list[tuple[int, int, ChecklistStep]] = []
    for idx, step in enumerate(steps):
        tier = classify_step_tier(step)
        # Force is_safety_critical=True if tier 1 was triggered via safety keywords
        is_safety = step.is_safety_critical or (tier == 1)
        if is_safety != step.is_safety_critical:
            step = step.model_copy(update={"is_safety_critical": True})
        indexed_tiers.append((tier, idx, step))

    # Python sort on tuples (tier, idx) guarantees stable ordering within the same tier
    indexed_tiers.sort(key=lambda item: (item[0], item[1]))

    resorted: list[ChecklistStep] = []
    was_reordered = False

    for new_order, (tier, old_idx, step) in enumerate(indexed_tiers, start=1):
        if (new_order - 1) != old_idx:
            was_reordered = True
        # Re-assign 1-based order index per schema requirement
        resorted.append(step.model_copy(update={"order": new_order}))

    if was_reordered:
        logger.info(
            "checklist_resorted_by_safety_tier",
            step_count=len(steps),
            safety_steps_count=sum(1 for s in resorted if s.is_safety_critical),
        )

    return resorted
