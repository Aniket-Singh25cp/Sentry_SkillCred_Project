"""synthesis/confidence.py — Calibrate hypothesis confidence in code.

Hard constraint: The model NEVER computes or sets the numeric confidence score.
Confidence is computed deterministically in code from:
  1. Rerank / fused scores of cited supporting chunks (weight 0.45)
  2. Normalized severity of matching sensor deviations (weight 0.35)
  3. Pattern confidence of matching cross-sensor signatures (weight 0.20)

Thresholds:
  - "high":   confidence_score >= 0.70
  - "medium": 0.40 <= confidence_score < 0.70
  - "low":    confidence_score < 0.40
"""

from __future__ import annotations

from typing import Literal

from core.schemas import EvidenceReport, Hypothesis, RetrievalResult

HIGH_CONFIDENCE_THRESHOLD: float = 0.70
MEDIUM_CONFIDENCE_THRESHOLD: float = 0.40


def score_to_bucket(score: float) -> Literal["high", "medium", "low"]:
    """Map numeric confidence score [0.0, 1.0] to discrete bucket."""
    if score >= HIGH_CONFIDENCE_THRESHOLD:
        return "high"
    if score >= MEDIUM_CONFIDENCE_THRESHOLD:
        return "medium"
    return "low"


def compute_hypothesis_confidence(
    hypothesis_cause: str,
    supporting_sensors: list[str],
    supporting_chunks: list[str],
    evidence: EvidenceReport,
    retrieval: RetrievalResult,
) -> tuple[float, Literal["high", "medium", "low"]]:
    """Compute calibrated confidence score and bucket deterministically.

    Formula:
      score = 0.45 * chunk_score + 0.35 * dev_score + 0.20 * sig_score
    Clamped to [0.0, 1.0] and rounded to 2 decimal places.
    """
    # 1. Chunk score component
    chunk_score = 0.0
    if supporting_chunks and retrieval.chunks:
        matching_chunks = [
            rc for rc in retrieval.chunks if rc.chunk.chunk_id in supporting_chunks
        ]
        if matching_chunks:
            # Prefer rerank score if present, else fused_score
            scores: list[float] = []
            for mc in matching_chunks:
                if mc.rerank_score is not None:
                    scores.append(mc.rerank_score)
                elif mc.fused_score is not None:
                    scores.append(mc.fused_score)
                else:
                    scores.append(0.5)
            chunk_score = max(scores) if scores else 0.5
        else:
            chunk_score = min(1.0, max(0.0, retrieval.best_score * 0.5))
    elif retrieval.chunks:
        chunk_score = min(1.0, max(0.0, retrieval.best_score * 0.4))

    # 2. Deviation severity component (scale 0-100 down to 0.0-1.0)
    dev_score = 0.0
    if evidence.deviations:
        dev_map = {d.sensor: (d.severity / 100.0) for d in evidence.deviations}
        matched_dev_scores = [
            dev_map[s] for s in supporting_sensors if s in dev_map
        ]
        if matched_dev_scores:
            dev_score = max(matched_dev_scores)
        else:
            dev_score = max(dev_map.values()) * 0.5

    # 3. Correlation signature component
    sig_score = 0.0
    if evidence.signatures:
        cause_lower = hypothesis_cause.lower()
        matched_sig_scores: list[float] = []
        for sig in evidence.signatures:
            # Match on sensor basis overlap or signature name in cause text
            has_sensor_overlap = any(s in supporting_sensors for s in sig.basis)
            has_name_in_cause = sig.name.lower().replace("_", " ") in cause_lower
            if has_sensor_overlap or has_name_in_cause:
                matched_sig_scores.append(sig.confidence)
        if matched_sig_scores:
            sig_score = max(matched_sig_scores)
        else:
            sig_score = max(s.confidence for s in evidence.signatures) * 0.5

    # Weighted blend ensuring calibrated bounds
    raw_score = 0.45 * chunk_score + 0.35 * dev_score + 0.20 * sig_score
    clamped_score = round(max(0.0, min(1.0, raw_score)), 2)
    bucket = score_to_bucket(clamped_score)

    return clamped_score, bucket


def calibrate_hypotheses(
    hypotheses_input: list[Hypothesis],
    evidence: EvidenceReport,
    retrieval: RetrievalResult,
) -> list[Hypothesis]:
    """Recalculate confidence scores and buckets for all hypotheses in pure code."""
    calibrated: list[Hypothesis] = []
    for h in hypotheses_input:
        score, bucket = compute_hypothesis_confidence(
            hypothesis_cause=h.cause,
            supporting_sensors=h.supporting_sensors,
            supporting_chunks=h.supporting_chunks,
            evidence=evidence,
            retrieval=retrieval,
        )
        calibrated.append(
            h.model_copy(
                update={
                    "confidence": bucket,
                    "confidence_score": score,
                }
            )
        )
    return calibrated
