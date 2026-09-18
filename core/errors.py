"""core/errors.py — SENTRY typed exception hierarchy.

Stages raise these exceptions to communicate failure modes across boundaries.
The API layer (S6) maps each exception type to an appropriate HTTP status code
and structured error response.

Hierarchy
---------
SentryError (base)
├── IngestionError     — S1: document parsing / indexing failure
├── EvidenceError      — S2: sensor data or baseline config failure
├── RetrievalError     — S3: retrieval engine failure
├── SynthesisError     — S5: LLM call or schema validation failure
├── GuardrailBlocked   — S5: a hard guardrail check failed (citation / safety / numeric)
└── RefusalRequired    — S5: evidence is too thin to produce a grounded response
"""

from __future__ import annotations


class SentryError(Exception):
    """Base class for all SENTRY domain exceptions.

    Always pass a human-readable message as the first positional argument;
    downstream layers log this message verbatim in the audit trail.
    """

    def __init__(self, message: str, *, context: dict[str, object] | None = None) -> None:
        super().__init__(message)
        # Extra structured context for log enrichment without polluting the
        # exception message string itself.
        self.context: dict[str, object] = context or {}


class IngestionError(SentryError):
    """Raised by S1 when a document cannot be parsed, chunked, or indexed.

    Examples: corrupt PDF, missing section structure, failed embedding call.
    """


class EvidenceError(SentryError):
    """Raised by S2 when the sensor snapshot or baseline config is unusable.

    Examples: all sensors missing, baseline config absent for the asset_class,
    NaN propagation detected in deviation math.
    """


class RetrievalError(SentryError):
    """Raised by S3 when the retrieval engine returns an unexpected failure.

    Distinguished from 'insufficient' retrieval, which is a normal outcome
    modelled by RetrievalResult.status == 'insufficient'.
    """


class SynthesisError(SentryError):
    """Raised by S5 when the LLM call fails or its output cannot be parsed.

    After one retry with the schema-validation error appended, a second failure
    raises this exception and the pipeline falls through to the refusal path.
    """


class GuardrailBlocked(SentryError):
    """Raised by the S5 guardrail layer when a hard check cannot be satisfied.

    Hard checks: citation validity (R5.4), safety-substring preservation (R5.5),
    numeric grounding (R5.9).  Unlike RefusalRequired, this indicates that a
    response was generated but must not be served.

    Attributes
    ----------
    failed_guardrails : list[str]
        Names of the guardrail checks that failed.
    """

    def __init__(
        self,
        message: str,
        *,
        failed_guardrails: list[str],
        context: dict[str, object] | None = None,
    ) -> None:
        super().__init__(message, context=context)
        self.failed_guardrails: list[str] = failed_guardrails


class RefusalRequired(SentryError):
    """Raised when SENTRY cannot produce a grounded response and must refuse.

    Callers should catch this and convert it to a DiagnosisResponse with a
    non-None Refusal payload and an empty inspection_checklist (R5.6).

    Attributes
    ----------
    reason : str
        Machine-readable reason matching Refusal.reason literals.
    suggested_action : str
        Escalation guidance for the technician.
    """

    def __init__(
        self,
        message: str,
        *,
        reason: str,
        suggested_action: str,
        context: dict[str, object] | None = None,
    ) -> None:
        super().__init__(message, context=context)
        self.reason: str = reason
        self.suggested_action: str = suggested_action
