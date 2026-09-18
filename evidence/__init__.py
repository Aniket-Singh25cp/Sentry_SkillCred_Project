"""evidence package — SENTRY Evidence Engine (Stage 2).

Pure deterministic statistical deviation engine. No ML, no LLM.
"""

from evidence.baselines import SensorBaseline, load_baselines
from evidence.deviation import compute_deviation, compute_severity
from evidence.engine import build_evidence_report
from evidence.history import get_history_features
from evidence.signatures import evaluate_signatures

__all__ = [
    "SensorBaseline",
    "build_evidence_report",
    "compute_deviation",
    "compute_severity",
    "evaluate_signatures",
    "get_history_features",
    "load_baselines",
]
