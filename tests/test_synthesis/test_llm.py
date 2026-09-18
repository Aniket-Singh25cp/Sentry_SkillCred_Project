"""tests/test_synthesis/test_llm.py — Unit tests for LLM abstraction and schema validation retry."""

from __future__ import annotations

from typing import Any

import pytest

from core.errors import RefusalRequired
from core.schemas import ChecklistStep, Citation, ManualInstruction
from synthesis.llm import (
    LLMHypothesis,
    LLMSynthesisDraft,
    create_instructor_client,
    generate_synthesis_draft,
)


def _make_citation() -> Citation:
    return Citation(
        chunk_id="chunk_abc123",
        doc_title="CP-450 Manual",
        revision="Rev C",
        section="7.3 Excessive Vibration",
        page=61,
    )


def _make_valid_draft() -> LLMSynthesisDraft:
    return LLMSynthesisDraft(
        manual_instructions=[
            ManualInstruction(
                step="De-energize motor and apply lockout/tagout.",
                verbatim_safety=True,
                citation=_make_citation(),
            )
        ],
        inspection_checklist=[
            ChecklistStep(
                order=1,
                action="Apply LOTO to motor starter.",
                expected_observation="Zero volts across terminals.",
                if_abnormal_then="Stop and report.",
                tools_required=["LOTO kit"],
                est_minutes=5,
                is_safety_critical=True,
                citation=_make_citation(),
            )
        ],
        hypotheses=[
            LLMHypothesis(
                rank=1,
                cause="Bearing lubrication starvation",
                supporting_sensors=["bearing_temp_de"],
                supporting_chunks=["chunk_abc123"],
                discriminating_check="Check oil pressure at TP-2.",
            )
        ],
    )


def test_generate_synthesis_draft_happy_path() -> None:
    expected_draft = _make_valid_draft()
    call_count = 0

    def mock_invoker(sys_prompt: str, user_prompt: str) -> LLMSynthesisDraft:
        nonlocal call_count
        call_count += 1
        return expected_draft

    draft, _model_name = generate_synthesis_draft(
        system_prompt="sys",
        user_prompt="usr",
        custom_invoker=mock_invoker,
    )

    assert call_count == 1
    assert draft == expected_draft
    assert len(draft.manual_instructions) == 1
    assert len(draft.inspection_checklist) == 1
    assert len(draft.hypotheses) == 1


def test_generate_synthesis_draft_retries_once_on_schema_error() -> None:
    expected_draft = _make_valid_draft()
    calls: list[str] = []

    def failing_first_invoker(sys_prompt: str, user_prompt: str) -> Any:
        calls.append(user_prompt)
        if len(calls) == 1:
            # First attempt returns malformed data (missing required citation in step)
            return {
                "manual_instructions": [],
                "inspection_checklist": [{"order": 1, "action": "inspect"}],  # invalid: missing citation
                "hypotheses": [],
            }
        # Second attempt returns valid draft
        return expected_draft

    draft, _model_name = generate_synthesis_draft(
        system_prompt="sys",
        user_prompt="original_user_prompt",
        custom_invoker=failing_first_invoker,
    )

    # Must have attempted exactly twice
    assert len(calls) == 2
    assert "original_user_prompt" in calls[0]
    # Second attempt must include schema validation error feedback
    assert "[SCHEMA VALIDATION ERROR]" in calls[1]
    assert draft == expected_draft


def test_generate_synthesis_draft_raises_refusal_required_on_second_failure() -> None:
    calls: list[str] = []

    def always_failing_invoker(sys_prompt: str, user_prompt: str) -> Any:
        calls.append(user_prompt)
        # Returns missing citation consistently
        return {
            "manual_instructions": [],
            "inspection_checklist": [{"order": 1, "action": "inspect"}],
            "hypotheses": [],
        }

    with pytest.raises(RefusalRequired) as exc_info:
        generate_synthesis_draft(
            system_prompt="sys",
            user_prompt="original_user_prompt",
            custom_invoker=always_failing_invoker,
        )

    # Confirmed: Exactly ONE retry (total 2 calls) before raising RefusalRequired
    assert len(calls) == 2
    assert exc_info.value.reason == "schema_failure"
    assert "Schema validation failed after retry" in str(exc_info.value)


def test_create_instructor_client_supported_providers() -> None:
    # Test client instantiation without live API calls
    client_ant, model_ant = create_instructor_client("anthropic")
    assert client_ant is not None
    assert "claude" in model_ant.lower() or "default" in model_ant

    client_oll, model_oll = create_instructor_client("ollama")
    assert client_oll is not None
    assert "qwen" in model_oll.lower() or "default" in model_oll

    client_vll, model_vll = create_instructor_client("vllm")
    assert client_vll is not None
    assert "qwen" in model_vll.lower() or "default" in model_vll


def test_create_instructor_client_unsupported_provider_raises() -> None:
    with pytest.raises(ValueError, match="Unsupported llm_provider"):
        create_instructor_client("unsupported_engine")
