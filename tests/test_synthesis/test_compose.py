"""tests/test_synthesis/test_compose.py — Integration tests for S5 synthesize() workflow."""

from __future__ import annotations

from datetime import datetime, timezone

from core.schemas import (
    ChecklistStep,
    Chunk,
    Citation,
    Deviation,
    DiagnosisResponse,
    ErrorCodeResult,
    EvidenceReport,
    HistoryFeatures,
    ManualInstruction,
    RetrievalResult,
    RetrievedChunk,
    SafetyNote,
    Signature,
)
from synthesis.compose import synthesize
from synthesis.llm import LLMHypothesis, LLMSynthesisDraft

_NOW = datetime(2026, 9, 18, 9, 14, 0, tzinfo=timezone.utc)


def _make_citation(chunk_id: str = "chunk_a1f9") -> Citation:
    return Citation(
        chunk_id=chunk_id,
        doc_title="CP-450 Centrifugal Pump Service Manual",
        revision="Rev C, 2023-08",
        section="7. Troubleshooting > 7.3 Excessive Vibration",
        page=61,
    )


def _make_sample_chunk(chunk_id: str = "chunk_a1f9") -> Chunk:
    return Chunk(
        chunk_id=chunk_id,
        doc_id="pump_manual_v3",
        doc_title="CP-450 Centrifugal Pump Service Manual",
        revision="Rev C, 2023-08",
        section_path=["7. Troubleshooting", "7.3 Excessive Vibration"],
        page_start=61,
        page_end=62,
        text="Inspect the drive-end bearing assembly for signs of overheating.",
        chunk_type="procedure",
        has_safety=True,
        safety_notes=[
            SafetyNote(
                text="DANGER: De-energize and lock out the motor before removing the coupling guard.",
                severity="danger",
            )
        ],
        asset_class="centrifugal_pump",
        applicable_models=["CP-450"],
        token_count=150,
    )


def _make_valid_evidence() -> EvidenceReport:
    return EvidenceReport(
        asset_id="PUMP-07",
        asset_class="centrifugal_pump",
        captured_at=_NOW,
        error_code=ErrorCodeResult(
            code="E-204",
            meaning="Lubrication pressure low",
            status="recognized",
        ),
        deviations=[
            Deviation(
                sensor="bearing_temp_de",
                value=91.4,
                unit="C",
                nominal=65.0,
                normal_range=(55.0, 75.0),
                delta=26.4,
                pct_dev=0.406,
                z_score=4.82,
                band="alarm",
                severity=95.0,
                trend="rising",
                roc_per_min=0.7,
                source="oem_config",
            )
        ],
        normal_sensors=["flow_rate"],
        missing_sensors=[],
        signatures=[
            Signature(
                name="bearing_distress",
                confidence=0.85,
                rule_id="R-014",
                basis=["bearing_temp_de"],
            )
        ],
        history_features=HistoryFeatures(
            days_since_service=214,
            same_code_90d=2,
            recent_parts=["seal_kit"],
        ),
    )


def _make_sufficient_retrieval() -> RetrievalResult:
    chunk = _make_sample_chunk("chunk_a1f9")
    rc = RetrievedChunk(
        chunk=chunk,
        rerank_score=0.88,
        fused_score=0.82,
    )
    return RetrievalResult(
        status="sufficient",
        chunks=[rc],
        traces=[],
        best_score=0.88,
    )


def _make_mock_draft() -> LLMSynthesisDraft:
    cit = _make_citation("chunk_a1f9")
    return LLMSynthesisDraft(
        manual_instructions=[
            ManualInstruction(
                step="De-energize the motor and apply lockout/tagout before removing coupling guard.",
                verbatim_safety=True,
                citation=cit,
            )
        ],
        inspection_checklist=[
            ChecklistStep(
                order=1,
                action="Inspect bearing oil sight glass.",
                expected_observation="Normal oil level.",
                if_abnormal_then="Add oil.",
                tools_required=["torch"],
                est_minutes=5,
                is_safety_critical=False,
                citation=cit,
            ),
            ChecklistStep(
                order=2,
                action="Apply LOTO to motor starter.",
                expected_observation="Zero volts across terminals.",
                if_abnormal_then="Escalate to electrical supervisor.",
                tools_required=["LOTO kit", "voltmeter"],
                est_minutes=5,
                is_safety_critical=True,
                citation=cit,
            ),
        ],
        hypotheses=[
            LLMHypothesis(
                rank=1,
                cause="Drive-end bearing lubrication starvation",
                supporting_sensors=["bearing_temp_de"],
                supporting_chunks=["chunk_a1f9"],
                discriminating_check="Check oil pressure at TP-2.",
            )
        ],
    )


# ---------------------------------------------------------------------------
# Acceptance Criterion 1: Scenario 7 (E-999) takes refusal with 0 LLM calls
# ---------------------------------------------------------------------------
def test_scenario_7_unrecognized_code_refusal_zero_llm_calls() -> None:
    evidence_scenario_7 = EvidenceReport(
        asset_id="PUMP-07",
        asset_class="centrifugal_pump",
        captured_at=_NOW,
        error_code=ErrorCodeResult(
            code="E-999",
            meaning=None,
            status="unrecognized",
        ),
        deviations=[],
        normal_sensors=[],
        missing_sensors=[],
        signatures=[],
        history_features=HistoryFeatures(days_since_service=50, same_code_90d=0),
    )

    # Empty chunks or insufficient retrieval
    retrieval_empty = RetrievalResult(
        status="insufficient",
        chunks=[],
        traces=[],
        best_score=0.1,
    )

    call_count = 0

    def mock_invoker(sys: str, usr: str) -> LLMSynthesisDraft:
        nonlocal call_count
        call_count += 1
        return _make_mock_draft()

    response = synthesize(
        evidence_scenario_7,
        retrieval_empty,
        custom_invoker=mock_invoker,
    )

    # ACCEPTANCE CRITERION: ZERO LLM calls
    assert call_count == 0

    # Validate refusal response contract
    assert isinstance(response, DiagnosisResponse)
    assert response.refusal is not None
    assert response.refusal.reason in ("unrecognized_code", "no_relevant_evidence")
    assert response.manual_instructions == []
    assert response.inspection_checklist == []
    assert len(response.measured_facts) > 0
    assert len(response.hypotheses) > 0
    assert "unverified" in response.hypotheses[0].cause
    assert response.hypotheses[0].confidence == "low"


# ---------------------------------------------------------------------------
# Acceptance Criterion: Insufficient retrieval takes refusal with 0 LLM calls
# ---------------------------------------------------------------------------
def test_insufficient_retrieval_refusal_zero_llm_calls() -> None:
    evidence = _make_valid_evidence()
    retrieval_insufficient = RetrievalResult(
        status="insufficient",
        chunks=[],
        traces=[],
        best_score=0.22,
    )

    call_count = 0

    def mock_invoker(sys: str, usr: str) -> LLMSynthesisDraft:
        nonlocal call_count
        call_count += 1
        return _make_mock_draft()

    response = synthesize(
        evidence,
        retrieval_insufficient,
        custom_invoker=mock_invoker,
    )

    assert call_count == 0
    assert response.refusal is not None
    assert response.refusal.reason == "no_relevant_evidence"
    assert response.inspection_checklist == []
    assert response.manual_instructions == []


# ---------------------------------------------------------------------------
# Acceptance Criteria: Happy Path, Citations, Safety Sorting, Meta Version
# ---------------------------------------------------------------------------
def test_happy_path_synthesis() -> None:
    evidence = _make_valid_evidence()
    retrieval = _make_sufficient_retrieval()

    call_count = 0

    def mock_invoker(sys: str, usr: str) -> LLMSynthesisDraft:
        nonlocal call_count
        call_count += 1
        return _make_mock_draft()

    response = synthesize(
        evidence,
        retrieval,
        prompt_version="v1.0.0",
        corpus_revision="Rev_C_2023",
        custom_invoker=mock_invoker,
    )

    assert call_count == 1
    assert response.refusal is None
    assert response.retrieval_status == "sufficient"

    # ACCEPTANCE CRITERION 2: Every ChecklistStep and ManualInstruction carries Citation
    assert len(response.manual_instructions) > 0
    for mi in response.manual_instructions:
        assert isinstance(mi.citation, Citation)
        assert mi.citation.chunk_id == "chunk_a1f9"

    assert len(response.inspection_checklist) == 2
    for step in response.inspection_checklist:
        assert isinstance(step.citation, Citation)
        assert step.citation.chunk_id == "chunk_a1f9"

    # ACCEPTANCE CRITERION 3: Safety-critical step sorts first
    first_step = response.inspection_checklist[0]
    assert first_step.is_safety_critical is True
    assert first_step.order == 1
    assert "Apply LOTO" in first_step.action

    second_step = response.inspection_checklist[1]
    assert second_step.is_safety_critical is False
    assert second_step.order == 2

    # In-code Measured facts
    assert len(response.measured_facts) >= 2
    assert response.measured_facts[0].source == "error_code_lookup"

    # In-code Hypothesis confidence calibration
    assert len(response.hypotheses) == 1
    assert response.hypotheses[0].confidence == "high"
    assert response.hypotheses[0].confidence_score > 0.70

    # ACCEPTANCE CRITERION 4: Prompt version appears in ResponseMeta
    assert response.meta.prompt_version == "v1.0.0"
    assert response.meta.corpus_revision == "Rev_C_2023"
    assert response.meta.chunks_retrieved == 1


# ---------------------------------------------------------------------------
# Acceptance Criterion 5: Determinism across 3 runs
# ---------------------------------------------------------------------------
def test_determinism_across_three_runs() -> None:
    evidence = _make_valid_evidence()
    retrieval = _make_sufficient_retrieval()

    responses: list[DiagnosisResponse] = []

    for _ in range(3):
        res = synthesize(
            evidence,
            retrieval,
            prompt_version="v1.0.0",
            corpus_revision="Rev_C",
            custom_invoker=lambda s, u: _make_mock_draft(),
        )
        responses.append(res)

    # Assert identical checklist structure, order, and citations across runs
    first = responses[0]
    for other in responses[1:]:
        assert [s.order for s in other.inspection_checklist] == [s.order for s in first.inspection_checklist]
        assert [s.is_safety_critical for s in other.inspection_checklist] == [s.is_safety_critical for s in first.inspection_checklist]
        assert [s.citation.chunk_id for s in other.inspection_checklist] == [s.citation.chunk_id for s in first.inspection_checklist]
        assert [h.confidence_score for h in other.hypotheses] == [h.confidence_score for h in first.hypotheses]
        assert [h.confidence for h in other.hypotheses] == [h.confidence for h in first.hypotheses]
        assert [f.statement for f in other.measured_facts] == [f.statement for f in first.measured_facts]


# ---------------------------------------------------------------------------
# Schema Failure Fallback to Refusal
# ---------------------------------------------------------------------------
def test_schema_failure_produces_refusal_response() -> None:
    evidence = _make_valid_evidence()
    retrieval = _make_sufficient_retrieval()

    # Invoker that always fails schema validation
    def bad_invoker(sys: str, usr: str) -> dict:
        return {"broken": "data"}

    response = synthesize(
        evidence,
        retrieval,
        custom_invoker=bad_invoker,
    )

    # Handled via RefusalRequired catch -> Refusal DiagnosisResponse
    assert response.refusal is not None
    assert response.refusal.reason == "schema_failure"
    assert response.inspection_checklist == []
    assert response.manual_instructions == []
