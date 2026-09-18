"""synthesis — SENTRY Stage 5 Synthesis and Structured Generation Layer.

Composes EvidenceReport + RetrievalResult into a schema-grounded DiagnosisResponse.
"""

from synthesis.compose import synthesize
from synthesis.confidence import calibrate_hypotheses, compute_hypothesis_confidence
from synthesis.facts import build_measured_facts, render_deviation_fact
from synthesis.llm import LLMSynthesisDraft, generate_synthesis_draft
from synthesis.ordering import classify_step_tier, order_checklist_steps

__all__ = [
    "LLMSynthesisDraft",
    "build_measured_facts",
    "calibrate_hypotheses",
    "classify_step_tier",
    "compute_hypothesis_confidence",
    "generate_synthesis_draft",
    "order_checklist_steps",
    "render_deviation_fact",
    "synthesize",
]
