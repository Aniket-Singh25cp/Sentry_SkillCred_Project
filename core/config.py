"""core/config.py — SENTRY configuration loader.

Reads settings from environment variables (12-factor) with a config.yaml
overlay.  No secrets or defaults containing credentials live here.

Usage:
    from core.config import settings   # singleton, loaded once at import time

Stages MUST NOT edit this file.  Add new config keys only through a P0
SCHEMA CHANGE REQUEST.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# ---------------------------------------------------------------------------
# Config file path — resolved relative to this file so the project can be
# run from any working directory.
# ---------------------------------------------------------------------------
_CONFIG_YAML_PATH: Path = Path(__file__).parent.parent / "config.yaml"


def _load_yaml_defaults() -> dict[str, object]:
    """Load config.yaml if it exists; return an empty dict otherwise.

    This lets stages that don't need a yaml file skip creating one without
    causing an import error.
    """
    if _CONFIG_YAML_PATH.exists():
        with _CONFIG_YAML_PATH.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        # yaml.safe_load returns None for an empty file
        return data if isinstance(data, dict) else {}
    return {}


class SentrySettings(BaseSettings):
    """SENTRY runtime configuration.

    Precedence (highest to lowest):
      1. Environment variables  (e.g. SENTRY_RETRIEVER=bm25)
      2. config.yaml keys
      3. Field defaults defined here

    All env vars are prefixed with ``SENTRY_`` to avoid collisions.
    URLs that contain credentials MUST be in env vars; no secret defaults here.
    """

    model_config = SettingsConfigDict(
        env_prefix="SENTRY_",
        # Extra keys in the environment are silently ignored so other tools
        # don't break the import.
        extra="ignore",
        # Populate from the loaded YAML dict as initial values.
        # pydantic-settings reads _yaml_defaults via ``model_config`` customise.
    )

    # ------------------------------------------------------------------
    # Feature flags — exact names mandated by the Stage Brief
    # ------------------------------------------------------------------

    retriever: Literal["tfidf", "bm25", "dense", "hybrid"] = Field(
        default="hybrid",
        description="Retrieval strategy.  'hybrid' = BM25 + dense + RRF.",
    )

    use_reranker: bool = Field(
        default=True,
        description="Run a cross-encoder reranker over the top-K hybrid results.",
    )

    use_anomaly_model: bool = Field(
        default=False,
        description="Feature-flag for the optional S4 anomaly detection stage.",
    )

    llm_provider: Literal["anthropic", "ollama", "vllm"] = Field(
        default="anthropic",
        description="Which LLM back-end S5 uses for structured output generation.",
    )

    relevance_floor: float = Field(
        default=0.35,
        ge=0.0,
        le=1.0,
        description=(
            "Minimum fused score for retrieval to be considered 'sufficient'. "
            "Below this threshold the system returns a refusal (R5.6)."
        ),
    )

    max_chunks_to_llm: int = Field(
        default=6,
        ge=1,
        description="Maximum number of retrieved chunks passed into the LLM context window.",
    )

    # ------------------------------------------------------------------
    # Infrastructure URLs — no defaults; must be provided via env.
    # Deliberately typed as str | None so a missing env var surfaces a
    # clear None rather than an obscure connection error.
    # ------------------------------------------------------------------

    database_url: str | None = Field(
        default=None,
        description=(
            "PostgreSQL DSN.  Set via SENTRY_DATABASE_URL env var. "
            "Never hardcode credentials here."
        ),
    )

    redis_url: str | None = Field(
        default=None,
        description="Redis DSN.  Set via SENTRY_REDIS_URL env var.",
    )

    qdrant_url: str | None = Field(
        default=None,
        description="Qdrant HTTP base URL.  Set via SENTRY_QDRANT_URL env var.",
    )


@lru_cache(maxsize=1)
def get_settings() -> SentrySettings:
    """Return the singleton SentrySettings instance.

    ``lru_cache`` ensures the YAML is parsed and env vars are read exactly once
    per process lifetime.  Tests that need to override settings should call
    ``get_settings.cache_clear()`` then patch env vars before re-importing.
    """
    yaml_defaults = _load_yaml_defaults()
    # pydantic-settings does not natively support a dict as a source in its
    # default flow, so we push yaml values as env vars only if they are not
    # already set — this preserves the documented precedence order.
    prefix = "SENTRY_"
    for key, value in yaml_defaults.items():
        env_key = f"{prefix}{key.upper()}"
        if env_key not in os.environ:
            # Store as string; pydantic-settings will coerce back to the
            # declared type (bool, int, float, Literal).
            os.environ[env_key] = str(value)

    return SentrySettings()


# Module-level singleton — ``from core.config import settings`` works naturally.
settings: SentrySettings = get_settings()
