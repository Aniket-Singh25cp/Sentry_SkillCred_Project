"""tests/test_synthesis/test_confidence.py — Unit tests for in-code confidence calibration."""

from __future__ import annotations

from datetime import datetime, timezone

from core.schemas import (
    Chunk,
    Deviation,
    ErrorCodeResult,
    EvidenceReport,
    HistoryFeatures,
    Hypothesis,
    RetrievalResult,
    RetrievedChunk,
    Signature,
)
from synthesis.confidence import (
    calibrate_hypotheses,
    compute_hypothesis_confidence,
    score_to_bucket,
)

_NOW = datetime(2026, 9, 18, 9, 14, 0, tzinfo=timezone.utc)


def _make_evidence() -> EvidenceReport:
    return EvidenceReport(
        asset_id="PUMP-07",
        asset_class="centrifugal_pump",
        captured_at=_NOW,
        error_code=ErrorCodeResult(code="E-204", meaning="Lube fault", status="recognized"),
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
                source="oem_config",
            )
        ],
        normal_sensors=[],
        missing_sensors=[],
        signatures=[
            Signature(
                name="bearing_distress",
                confidence=0.85,
                rule_id="R-014",
                basis=["bearing_temp_de"],
            )
        ],
        history_features=HistoryFeatures(days_since_service=100, same_code_90d=0),
    )


def _make_retrieval() -> RetrievalResult:
    chunk = Chunk(
        chunk_id="chunk_bearing_1",
        doc_id="doc1",
        doc_title="Manual",
        revision="Rev A",
        section_path=["7. Troubleshooting"],
        page_start=10,
        page_end=11,
        text="Check bearing.",
        chunk_type="procedure",
        has_safety=False,
        asset_class="centrifugal_pump",
        token_count=100,
    )
    rc = RetrievedChunk(
        chunk=chunk,
        rerank_score=0.90,
        fused_score=0.85,
    )
    return RetrievalResult(
        status="sufficient",
        chunks=[rc],
        traces=[],
        best_score=0.90,
    )


def test_score_to_bucket() -> None:
    assert score_to_bucket(0.85) == "high"
    assert score_to_bucket(0.70) == "high"
    assert score_to_bucket(0.69) == "medium"
    assert score_to_bucket(0.40) == "medium"
    assert score_to_bucket(0.39) == "low"
    assert score_to_bucket(0.10) == "low"


def test_high_confidence_calculation() -> None:
    evidence = _make_evidence()
    retrieval = _make_retrieval()

    score, bucket = compute_hypothesis_confidence(
        hypothesis_cause="Drive-end bearing distress and lubrication failure",
        supporting_sensors=["bearing_temp_de"],
        supporting_chunks=["chunk_bearing_1"],
        evidence=evidence,
        retrieval=retrieval,
    )

    # 0.45 * 0.90 + 0.35 * 0.95 + 0.20 * 0.85 = 0.405 + 0.3325 + 0.170 = 0.9075 -> 0.91
    assert score >= 0.85
    assert bucket == "high"


def test_calibrate_hypotheses_overrides_llm_values() -> None:
    evidence = _make_evidence()
    retrieval = _make_retrieval()

    raw_h = Hypothesis(
        rank=1,
        cause="Bearing distress",
        confidence="low",  # Raw value from model
        confidence_score=0.05,  # Raw dummy value from model
        supporting_sensors=["bearing_temp_de"],
        supporting_chunks=["chunk_bearing_1"],
        discriminating_check="Inspect test port TP-2.",
    )

    calibrated = calibrate_hypotheses([raw_h], evidence, retrieval)

    assert len(calibrated) == 1
    # Must be calibrated by our in-code logic to high
    assert calibrated[0].confidence == "high"
    assert calibrated[0].confidence_score > 0.70
