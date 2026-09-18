"""synthesis/llm.py — Provider abstraction with schema-enforced structured outputs.

Hard constraints:
- Provider abstraction honoring config.llm_provider: anthropic | ollama | vllm.
- Structured output enforced via tool-calling / JSON-schema mode against LLMSynthesisDraft.
  Never "please reply in JSON" in free text.
- temperature = 0.1, explicit max_tokens, timeout, tenacity retry with backoff.
- ONE retry on schema-validation failure, appending the validation error to the message.
  On second failure raise RefusalRequired. Never fall back to free text, never hand-parse
  a malformed response, never regex-repair JSON.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any, Literal

import anthropic
import httpx
import instructor
import openai
import structlog
from instructor.core import InstructorRetryException
from pydantic import Field, ValidationError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from core.config import settings
from core.errors import RefusalRequired
from core.schemas import ChecklistStep, ManualInstruction, _SentryBase

logger = structlog.get_logger(__name__)

# Default model identifiers by provider
_DEFAULT_MODELS: dict[str, str] = {
    "anthropic": "claude-3-5-sonnet-20241022",
    "ollama": "qwen2.5:7b",
    "vllm": "Qwen/Qwen2.5-7B-Instruct",
}

# Default base URLs for local inference servers
_DEFAULT_BASE_URLS: dict[str, str] = {
    "ollama": "http://localhost:11434/v1",
    "vllm": "http://localhost:8000/v1",
}


class LLMHypothesis(_SentryBase):
    """Sub-schema for hypothesis emitted by LLM. Confidence numbers are added in code."""

    rank: int = Field(..., ge=1, description="Ordinal rank; 1 = most probable.")
    cause: str = Field(..., description="Human-readable description of the probable cause.")
    supporting_sensors: list[str] = Field(
        default_factory=list,
        description="Sensor names whose deviations support this hypothesis.",
    )
    supporting_chunks: list[str] = Field(
        default_factory=list,
        description="chunk_ids whose content supports this hypothesis.",
    )
    discriminating_check: str = Field(
        ...,
        description="The single test or observation that would confirm or refute this hypothesis.",
    )


class LLMSynthesisDraft(_SentryBase):
    """Target sub-schema returned by the structured model call."""

    manual_instructions: list[ManualInstruction] = Field(
        default_factory=list,
        description="Cited procedural steps derived from retrieved document chunks.",
    )
    inspection_checklist: list[ChecklistStep] = Field(
        default_factory=list,
        description="Checklist steps with mandatory citations.",
    )
    hypotheses: list[LLMHypothesis] = Field(
        default_factory=list,
        description="Ranked probable causes.",
    )
    refusal_reason: Literal[
        "no_relevant_evidence",
        "unrecognized_code",
        "guardrail_block",
        "schema_failure",
    ] | None = Field(
        default=None,
        description="Populated iff retrieved documents cannot support a procedure.",
    )
    refusal_message: str | None = Field(
        default=None,
        description="Technician-facing explanation if refusing.",
    )
    refusal_suggested_action: str | None = Field(
        default=None,
        description="Escalation guidance if refusing.",
    )


def create_instructor_client(provider: str) -> tuple[Any, str]:
    """Create an instructor-wrapped client and model name matching the requested provider."""
    model = os.environ.get("SENTRY_LLM_MODEL") or _DEFAULT_MODELS.get(provider, "default-model")

    if provider == "anthropic":
        api_key = os.environ.get("ANTHROPIC_API_KEY", "missing_key")
        # Tool-calling mode enforces native tool-based JSON schema validation
        anthropic_client = anthropic.Anthropic(
            api_key=api_key,
            timeout=float(os.environ.get("SENTRY_LLM_TIMEOUT", "30.0")),
        )
        return instructor.from_anthropic(anthropic_client), model

    if provider in ("ollama", "vllm"):
        base_url = os.environ.get("SENTRY_LLM_BASE_URL", _DEFAULT_BASE_URLS[provider])
        api_key = os.environ.get("OPENAI_API_KEY", "dummy_key")
        openai_client = openai.OpenAI(
            base_url=base_url,
            api_key=api_key,
            timeout=float(os.environ.get("SENTRY_LLM_TIMEOUT", "30.0")),
        )
        return instructor.from_openai(openai_client, mode=instructor.Mode.TOOLS), model

    raise ValueError(f"Unsupported llm_provider '{provider}'. Must be anthropic, ollama, or vllm.")


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=0.5, min=0.5, max=4.0),
    retry=retry_if_exception_type((
        httpx.TimeoutException,
        httpx.NetworkError,
        anthropic.APITimeoutError,
        anthropic.APIConnectionError,
        openai.APITimeoutError,
        openai.APIConnectionError,
    )),
    reraise=True,
)
def _call_provider_with_retry(
    client: Any,
    provider: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int,
    temperature: float,
) -> LLMSynthesisDraft:
    """Execute the model call with exponential backoff on transport errors."""
    if provider == "anthropic":
        return client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            response_model=LLMSynthesisDraft,
        )

    return client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_model=LLMSynthesisDraft,
    )


def generate_synthesis_draft(
    system_prompt: str,
    user_prompt: str,
    *,
    client: Any = None,
    provider: str | None = None,
    model: str | None = None,
    max_tokens: int = 2048,
    temperature: float = 0.1,
    custom_invoker: Callable[[str, str], Any] | None = None,
) -> tuple[LLMSynthesisDraft, str]:
    """Generate structured synthesis draft with exactly ONE schema retry.

    Parameters:
      system_prompt: Base system prompt with hard rules.
      user_prompt: Formatted user prompt with read-only facts and context.
      client: Optional pre-configured client (useful for mocks/tests).
      provider: Provider override (defaults to config.llm_provider).
      model: Model name override.
      max_tokens: Strict token ceiling.
      temperature: Strict deterministic temperature (default 0.1).
      custom_invoker: Test hook to directly supply model call results.

    Returns:
      (draft, model_name)

    Raises:
      RefusalRequired: If schema validation fails on both initial and retry attempts.
    """
    active_provider = provider or settings.llm_provider
    if client is None and custom_invoker is None:
        inst_client, default_model = create_instructor_client(active_provider)
    else:
        inst_client = client
        default_model = _DEFAULT_MODELS.get(active_provider, "mock-model")

    active_model = model or default_model

    def _execute(prompt: str) -> LLMSynthesisDraft:
        if custom_invoker is not None:
            raw_output = custom_invoker(system_prompt, prompt)
            if isinstance(raw_output, LLMSynthesisDraft):
                return raw_output
            # If invoker returned dict or JSON string, validate it strictly
            if isinstance(raw_output, dict):
                return LLMSynthesisDraft.model_validate(raw_output)
            if isinstance(raw_output, str):
                return LLMSynthesisDraft.model_validate_json(raw_output)
            raise ValidationError.from_exception_data(
                title="InvalidModelOutput", line_errors=[]
            )

        return _call_provider_with_retry(
            client=inst_client,
            provider=active_provider,
            model=active_model,
            system_prompt=system_prompt,
            user_prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )

    # Attempt 1
    try:
        draft = _execute(user_prompt)
        return draft, active_model
    except (
        ValidationError,
        InstructorRetryException,
        ValueError,
        TypeError,
    ) as err:
        error_message = str(err)
        logger.warning("llm_schema_validation_failed_attempt_1", error=error_message)

    # Attempt 2: Exactly ONE retry appending schema validation error
    retry_prompt = (
        f"{user_prompt}\n\n"
        f"[SCHEMA VALIDATION ERROR]\n"
        f"Your previous response failed schema validation with error:\n{error_message}\n"
        f"You must strictly output structured data adhering to the schema."
    )

    try:
        draft = _execute(retry_prompt)
        logger.info("llm_schema_validation_succeeded_on_retry")
        return draft, active_model
    except (
        ValidationError,
        InstructorRetryException,
        ValueError,
        TypeError,
    ) as second_err:
        logger.error("llm_schema_validation_failed_attempt_2", error=str(second_err))
        # Never fall back to free text, never regex-repair; raise RefusalRequired per brief
        raise RefusalRequired(
            message=f"Schema validation failed after retry: {second_err}",
            reason="schema_failure",
            suggested_action="Escalate to platform engineering or check LLM schema compliance.",
            context={"last_error": str(second_err)},
        ) from second_err
