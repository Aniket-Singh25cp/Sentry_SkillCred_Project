"""tests/test_schemas.py — Round-trip validation tests for every SENTRY schema.

Design goals
------------
* Every Pydantic model in core/schemas.py has at least one happy-path
  round-trip test: construct → serialise → deserialise → assert equality.
* Each test function constructs the *minimum-viable valid* instance so the
  tests document the required fields clearly.
* One dedicated test asserts that DiagnosisResponse rejects a ChecklistStep
  with a missing citation (i.e. the Citation model is mandatory).
* Tests are pure functions with no I/O; no fixtures or database connections.

Run with:
    pytest tests/test_schemas.py -v
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from core.schemas import (
    AnomalyResult,
    ChecklistStep,
    Chunk,
    Citation,
    DiagnoseRequest,
    DiagnosisResponse,
    Deviation,
    ErrorCodeEntry,
    ErrorCodeResult,
    EvidenceReport,
    FeedbackRequest,
    GuardrailReport,
    HistoryFeatures,
    Hypothesis,
    ManualInstruction,
    MeasuredFact,
    Refusal,
    ResponseMeta,
    RetrievalResult,
    RetrievalTrace,
    RetrievedChunk,
    SafetyNote,
    SensorReading,
    Signature,
)

# ---------------------------------------------------------------------------
# Shared helpers — build minimal valid instances used across multiple tests
# ---------------------------------------------------------------------------

_NOW = datetime(2026, 9, 18, 9, 14, 0, tzinfo=timezone.utc)


def _make_safety_note() -> SafetyNote:
    return SafetyNote(
        text="DANGER: De-energize and lock out the motor before removing the coupling guard.",
        severity="danger",
    )


def _make_chunk() -> Chunk:
    return Chunk(
        chunk_id="a1f9c2d40b77",
        doc_id="pump_manual_v3",
        doc_title="CP-450 Centrifugal Pump Service Manual",
        revision="Rev C, 2023-08",
        section_path=["7. Troubleshooting", "7.3 Excessive Vibration"],
        page_start=61,
        page_end=62,
        text="Inspect the drive-end bearing assembly for signs of overheating.",
        chunk_type="procedure",
        has_safety=True,
        safety_notes=[_make_safety_note()],
        asset_class="centrifugal_pump",
        applicable_models=["CP-450", "CP-460"],
        token_count=742,
    )


def _make_citation() -> Citation:
    return Citation(
        chunk_id="a1f9c2d40b77",
        doc_title="CP-450 Centrifugal Pump Service Manual",
        revision="Rev C, 2023-08",
        section="7.3 Excessive Vibration",
        page=61,
    )


def _make_deviation() -> Deviation:
    return Deviation(
        sensor="bearing_temp_de",
        value=91.4,
        unit="C",
        nominal=65.0,
        normal_range=(55.0, 75.0),
        delta=26.4,
        pct_dev=0.406,
        z_score=4.82,
        band="alarm",
        severity=92.0,
        trend="rising",
        roc_per_min=0.7,
        source="oem_config",
    )


def _make_evidence_report() -> EvidenceReport:
    return EvidenceReport(
        asset_id="PUMP-07",
        asset_class="centrifugal_pump",
        captured_at=_NOW,
        error_code=ErrorCodeResult(
            code="E-204",
            meaning="Lubrication pressure low",
            status="recognized",
        ),
        deviations=[_make_deviation()],
        normal_sensors=["flow_rate", "discharge_pressure"],
        missing_sensors=[],
        signatures=[
            Signature(
                name="bearing_distress",
                confidence=0.8,
                rule_id="R-014",
                basis=["vibration_rms", "bearing_temp_de"],
            )
        ],
        history_features=HistoryFeatures(
            days_since_service=214,
            same_code_90d=2,
            recent_parts=["seal_kit"],
        ),
    )


def _make_checklist_step(order: int = 1) -> ChecklistStep:
    return ChecklistStep(
        order=order,
        action="Apply LOTO to the motor starter.",
        expected_observation="Zero-energy state verified at the terminals.",
        if_abnormal_then="Stop. Escalate to electrical supervisor.",
        tools_required=["LOTO kit", "voltage tester"],
        est_minutes=5,
        is_safety_critical=True,
        citation=_make_citation(),
    )


def _make_diagnosis_response() -> DiagnosisResponse:
    return DiagnosisResponse(
        request_id="req_01J9ABCDE",
        asset_id="PUMP-07",
        measured_facts=[
            MeasuredFact(
                statement=(
                    "Drive-end bearing temperature is 91.4 C against a "
                    "normal range of 55-75 C (z = 4.82, alarm band)."
                ),
                source="sensor_engine",
                sensor="bearing_temp_de",
            )
        ],
        manual_instructions=[
            ManualInstruction(
                step=(
                    "De-energize the motor and apply lockout/tagout "
                    "before removing the coupling guard."
                ),
                verbatim_safety=True,
                citation=_make_citation(),
            )
        ],
        inspection_checklist=[_make_checklist_step(order=1)],
        hypotheses=[
            Hypothesis(
                rank=1,
                cause="Drive-end bearing lubrication starvation",
                confidence="high",
                confidence_score=0.81,
                supporting_sensors=["bearing_temp_de", "vibration_rms"],
                supporting_chunks=["a1f9c2d40b77", "9b3e1c7a55d2"],
                discriminating_check=(
                    "Verify oil level and lube pressure at test port TP-2 (step 4)."
                ),
            )
        ],
        retrieval_status="sufficient",
        refusal=None,
        guardrails=GuardrailReport(
            passed=["citation", "safety", "numeric"],
            failed=[],
            dropped_steps=0,
            notes="All guardrails passed on first attempt.",
        ),
        meta=ResponseMeta(
            prompt_version="v1.4.0",
            model="claude-sonnet-4-5",
            retriever="hybrid+rerank",
            chunks_retrieved=6,
            latency_ms=3410,
            corpus_revision="abc123def456",
        ),
    )


# ===========================================================================
# TESTS — Ingestion / corpus models
# ===========================================================================


class TestSafetyNote:
    def test_round_trip(self) -> None:
        note = _make_safety_note()
        restored = SafetyNote.model_validate_json(note.model_dump_json())
        assert restored == note

    def test_all_severities_accepted(self) -> None:
        for sev in ("danger", "warning", "caution", "notice"):
            n = SafetyNote(text="Test.", severity=sev)  # type: ignore[arg-type]
            assert n.severity == sev

    def test_invalid_severity_rejected(self) -> None:
        with pytest.raises(ValidationError):
            SafetyNote(text="Test.", severity="critical")  # type: ignore[arg-type]


class TestChunk:
    def test_round_trip(self) -> None:
        chunk = _make_chunk()
        restored = Chunk.model_validate_json(chunk.model_dump_json())
        assert restored == chunk

    def test_section_path_is_list(self) -> None:
        chunk = _make_chunk()
        assert isinstance(chunk.section_path, list)
        assert len(chunk.section_path) == 2

    def test_valid_chunk_types(self) -> None:
        for ct in ("procedure", "description", "table", "warning"):
            c = _make_chunk()
            c2 = c.model_copy(update={"chunk_type": ct})
            assert c2.chunk_type == ct

    def test_invalid_chunk_type_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Chunk(
                chunk_id="a1f9c2d40b77",
                doc_id="x",
                doc_title="x",
                revision="x",
                section_path=[],
                page_start=1,
                page_end=1,
                text="x",
                chunk_type="diagram",  # invalid
                has_safety=False,
                asset_class="pump",
                token_count=10,
            )

    def test_page_start_ge1(self) -> None:
        with pytest.raises(ValidationError):
            _make_chunk().model_copy(update={"page_start": 0})


class TestErrorCodeEntry:
    def test_round_trip(self) -> None:
        entry = ErrorCodeEntry(
            code="E-204",
            asset_class="centrifugal_pump",
            meaning="Lubrication pressure low",
            probable_causes=["Low oil level", "Blocked lube line"],
            section_ref="7.5 Lubrication",
        )
        restored = ErrorCodeEntry.model_validate_json(entry.model_dump_json())
        assert restored == entry


# ===========================================================================
# TESTS — Evidence models
# ===========================================================================


class TestSensorReading:
    def test_round_trip(self) -> None:
        sr = SensorReading(
            name="bearing_temp_de",
            value=91.4,
            unit="C",
            status="ok",
            last_seen=_NOW,
        )
        restored = SensorReading.model_validate_json(sr.model_dump_json())
        assert restored == sr

    def test_missing_status_no_last_seen(self) -> None:
        # A missing sensor may legitimately have no last_seen timestamp.
        sr = SensorReading(name="flow_rate", value=0.0, unit="m3/h", status="missing")
        assert sr.last_seen is None

    def test_invalid_status_rejected(self) -> None:
        with pytest.raises(ValidationError):
            SensorReading(name="x", value=0.0, unit="C", status="error")  # type: ignore[arg-type]


class TestDeviation:
    def test_round_trip(self) -> None:
        dev = _make_deviation()
        restored = Deviation.model_validate_json(dev.model_dump_json())
        assert restored == dev

    def test_severity_bounds(self) -> None:
        with pytest.raises(ValidationError):
            _make_deviation().model_copy(update={"severity": 101.0})
        with pytest.raises(ValidationError):
            _make_deviation().model_copy(update={"severity": -1.0})


class TestSignature:
    def test_round_trip(self) -> None:
        sig = Signature(
            name="bearing_distress",
            confidence=0.8,
            rule_id="R-014",
            basis=["vibration_rms", "bearing_temp_de"],
        )
        restored = Signature.model_validate_json(sig.model_dump_json())
        assert restored == sig

    def test_confidence_bounds(self) -> None:
        with pytest.raises(ValidationError):
            Signature(name="x", confidence=1.1, rule_id="R-001", basis=[])
        with pytest.raises(ValidationError):
            Signature(name="x", confidence=-0.1, rule_id="R-001", basis=[])


class TestHistoryFeatures:
    def test_round_trip(self) -> None:
        hf = HistoryFeatures(days_since_service=214, same_code_90d=2, recent_parts=["seal_kit"])
        restored = HistoryFeatures.model_validate_json(hf.model_dump_json())
        assert restored == hf


class TestErrorCodeResult:
    def test_round_trip_recognized(self) -> None:
        ecr = ErrorCodeResult(code="E-204", meaning="Lubrication pressure low", status="recognized")
        restored = ErrorCodeResult.model_validate_json(ecr.model_dump_json())
        assert restored == ecr

    def test_absent_status(self) -> None:
        # When no code is submitted the code and meaning fields are None.
        ecr = ErrorCodeResult(code=None, meaning=None, status="absent")
        assert ecr.code is None

    def test_unrecognized_no_meaning(self) -> None:
        ecr = ErrorCodeResult(code="E-999", meaning=None, status="unrecognized")
        assert ecr.status == "unrecognized"

    def test_invalid_status_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ErrorCodeResult(code="E-204", meaning="x", status="unknown")  # type: ignore[arg-type]


class TestEvidenceReport:
    def test_round_trip(self) -> None:
        report = _make_evidence_report()
        restored = EvidenceReport.model_validate_json(report.model_dump_json())
        assert restored == report

    def test_prd_json_example_validates(self) -> None:
        """Verify the exact JSON example from PRD §S2 validates."""
        prd_json = """{
            "asset_id": "PUMP-07",
            "asset_class": "centrifugal_pump",
            "captured_at": "2026-09-18T09:14:00+05:30",
            "error_code": {"code": "E-204", "meaning": "Lubrication pressure low", "status": "recognized"},
            "deviations": [
                {"sensor":"bearing_temp_de","value":91.4,"unit":"C","nominal":65,"normal_range":[55,75],
                 "delta":26.4,"pct_dev":0.406,"z_score":4.82,"band":"alarm","severity":92,
                 "trend":"rising","roc_per_min":0.7,"source":"oem_config"},
                {"sensor":"vibration_rms","value":8.1,"unit":"mm/s","nominal":2.8,"normal_range":[0,4.5],
                 "delta":5.3,"pct_dev":1.89,"z_score":5.40,"band":"alarm","severity":96,
                 "trend":"rising","source":"learned_baseline"}
            ],
            "normal_sensors": ["flow_rate","discharge_pressure"],
            "missing_sensors": [],
            "signatures": [{"name":"bearing_distress","confidence":0.8,"rule_id":"R-014","basis":["vibration_rms","bearing_temp_de"]}],
            "history_features": {"days_since_service": 214, "same_code_90d": 2, "recent_parts": ["seal_kit"]}
        }"""
        report = EvidenceReport.model_validate_json(prd_json)
        assert report.asset_id == "PUMP-07"
        assert len(report.deviations) == 2
        assert report.deviations[0].z_score == pytest.approx(4.82)


# ===========================================================================
# TESTS — Retrieval models
# ===========================================================================


class TestRetrievedChunk:
    def test_round_trip(self) -> None:
        rc = RetrievedChunk(
            chunk=_make_chunk(),
            sparse_score=0.72,
            dense_score=0.88,
            fused_score=0.83,
            rerank_score=0.91,
            retrieved_by=["sparse", "dense"],
            forced_safety_include=False,
        )
        restored = RetrievedChunk.model_validate_json(rc.model_dump_json())
        assert restored == rc

    def test_all_scores_optional(self) -> None:
        # A chunk retrieved by only one engine may have None scores for others.
        rc = RetrievedChunk(
            chunk=_make_chunk(),
            retrieved_by=["sparse"],
        )
        assert rc.dense_score is None
        assert rc.rerank_score is None


class TestRetrievalTrace:
    def test_round_trip(self) -> None:
        trace = RetrievalTrace(
            query_text="bearing overheating vibration",
            engine="bm25",
            top_k=20,
            raw_results=[("a1f9c2d40b77", 0.91), ("9b3e1c7a55d2", 0.74)],
        )
        restored = RetrievalTrace.model_validate_json(trace.model_dump_json())
        assert restored == trace


class TestRetrievalResult:
    def test_round_trip_sufficient(self) -> None:
        rr = RetrievalResult(
            status="sufficient",
            chunks=[
                RetrievedChunk(
                    chunk=_make_chunk(),
                    fused_score=0.83,
                    retrieved_by=["sparse", "dense"],
                )
            ],
            traces=[],
            best_score=0.83,
        )
        restored = RetrievalResult.model_validate_json(rr.model_dump_json())
        assert restored == rr

    def test_insufficient_status(self) -> None:
        rr = RetrievalResult(status="insufficient", chunks=[], traces=[], best_score=0.12)
        assert rr.status == "insufficient"

    def test_invalid_status_rejected(self) -> None:
        with pytest.raises(ValidationError):
            RetrievalResult(status="partial", chunks=[], traces=[], best_score=0.5)  # type: ignore[arg-type]


# ===========================================================================
# TESTS — Anomaly model
# ===========================================================================


class TestAnomalyResult:
    def test_round_trip(self) -> None:
        ar = AnomalyResult(
            model_version="1.2.0",
            anomaly_score=0.91,
            is_anomalous=True,
            feature_attributions={"bearing_temp_de": 0.61, "vibration_rms": 0.29},
        )
        restored = AnomalyResult.model_validate_json(ar.model_dump_json())
        assert restored == ar

    def test_score_bounds(self) -> None:
        with pytest.raises(ValidationError):
            AnomalyResult(model_version="x", anomaly_score=1.1, is_anomalous=True)
        with pytest.raises(ValidationError):
            AnomalyResult(model_version="x", anomaly_score=-0.01, is_anomalous=False)


# ===========================================================================
# TESTS — Synthesis / output models
# ===========================================================================


class TestCitation:
    def test_round_trip(self) -> None:
        citation = _make_citation()
        restored = Citation.model_validate_json(citation.model_dump_json())
        assert restored == citation


class TestMeasuredFact:
    def test_round_trip(self) -> None:
        mf = MeasuredFact(
            statement="Bearing temp 91.4 C, z=4.82, alarm band.",
            source="sensor_engine",
            sensor="bearing_temp_de",
        )
        restored = MeasuredFact.model_validate_json(mf.model_dump_json())
        assert restored == mf

    def test_no_sensor_field(self) -> None:
        # MeasuredFact from error-code lookup has no associated sensor.
        mf = MeasuredFact(
            statement="Error code E-204: Lubrication pressure low.",
            source="error_code_lookup",
        )
        assert mf.sensor is None


class TestManualInstruction:
    def test_round_trip(self) -> None:
        mi = ManualInstruction(
            step="De-energize the motor and apply LOTO.",
            verbatim_safety=True,
            citation=_make_citation(),
        )
        restored = ManualInstruction.model_validate_json(mi.model_dump_json())
        assert restored == mi


class TestChecklistStep:
    def test_round_trip(self) -> None:
        step = _make_checklist_step()
        restored = ChecklistStep.model_validate_json(step.model_dump_json())
        assert restored == step

    def test_citation_required(self) -> None:
        """A ChecklistStep without a citation must be rejected by the schema."""
        with pytest.raises((ValidationError, TypeError)):
            # citation field is required; omitting it must fail validation.
            ChecklistStep(
                order=1,
                action="Inspect bearing.",
                expected_observation="No discolouration.",
                if_abnormal_then="Escalate.",
                tools_required=["torch"],
                est_minutes=10,
                is_safety_critical=False,
                # citation intentionally omitted
            )

    def test_order_ge1(self) -> None:
        with pytest.raises(ValidationError):
            _make_checklist_step().model_copy(update={"order": 0})


class TestHypothesis:
    def test_round_trip(self) -> None:
        h = Hypothesis(
            rank=1,
            cause="Drive-end bearing lubrication starvation",
            confidence="high",
            confidence_score=0.81,
            supporting_sensors=["bearing_temp_de", "vibration_rms"],
            supporting_chunks=["a1f9c2d40b77"],
            discriminating_check="Check oil level at TP-2.",
        )
        restored = Hypothesis.model_validate_json(h.model_dump_json())
        assert restored == h

    def test_invalid_confidence_literal(self) -> None:
        with pytest.raises(ValidationError):
            Hypothesis(
                rank=1,
                cause="x",
                confidence="very_high",  # type: ignore[arg-type]
                confidence_score=0.9,
                discriminating_check="x",
            )


class TestRefusal:
    def test_round_trip(self) -> None:
        r = Refusal(
            reason="unrecognized_code",
            message="Error code E-999 is not in the corpus.",
            suggested_action="Contact OEM technical support or consult a reliability engineer.",
        )
        restored = Refusal.model_validate_json(r.model_dump_json())
        assert restored == r

    def test_all_refusal_reasons(self) -> None:
        for reason in ("no_relevant_evidence", "unrecognized_code", "guardrail_block", "schema_failure"):
            r = Refusal(reason=reason, message="x", suggested_action="y")  # type: ignore[arg-type]
            assert r.reason == reason

    def test_invalid_reason_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Refusal(reason="hallucination", message="x", suggested_action="y")  # type: ignore[arg-type]


class TestGuardrailReport:
    def test_round_trip(self) -> None:
        gr = GuardrailReport(
            passed=["citation", "safety"],
            failed=["numeric"],
            dropped_steps=2,
            notes="Numeric check failed on step 3.",
        )
        restored = GuardrailReport.model_validate_json(gr.model_dump_json())
        assert restored == gr


class TestResponseMeta:
    def test_round_trip(self) -> None:
        meta = ResponseMeta(
            prompt_version="v1.4.0",
            model="claude-sonnet-4-5",
            retriever="hybrid+rerank",
            chunks_retrieved=6,
            latency_ms=3410,
            corpus_revision="abc123def456",
        )
        restored = ResponseMeta.model_validate_json(meta.model_dump_json())
        assert restored == meta


class TestDiagnosisResponse:
    def test_round_trip_full(self) -> None:
        response = _make_diagnosis_response()
        restored = DiagnosisResponse.model_validate_json(response.model_dump_json())
        assert restored == response

    def test_refusal_none_by_default(self) -> None:
        response = _make_diagnosis_response()
        assert response.refusal is None

    def test_refusal_populated(self) -> None:
        response = _make_diagnosis_response()
        response_with_refusal = response.model_copy(
            update={
                "refusal": Refusal(
                    reason="unrecognized_code",
                    message="E-999 not found.",
                    suggested_action="Contact OEM.",
                ),
                "inspection_checklist": [],
                "retrieval_status": "insufficient",
            }
        )
        assert response_with_refusal.refusal is not None
        assert response_with_refusal.refusal.reason == "unrecognized_code"

    def test_checklist_step_missing_citation_is_rejected(self) -> None:
        """DiagnosisResponse must reject a ChecklistStep that has no citation.

        This is the specific acceptance-criteria test mandated by the Stage Brief.
        Citation is a required field on ChecklistStep; Pydantic must raise
        ValidationError when it is absent.
        """
        with pytest.raises((ValidationError, TypeError)):
            # Construct a response where a step has no citation by directly
            # attempting to instantiate a ChecklistStep without citation.
            bad_step = ChecklistStep(
                order=1,
                action="Inspect bearing race for spalling.",
                expected_observation="Smooth raceway surface.",
                if_abnormal_then="Replace bearing assembly.",
                tools_required=["bearing puller", "inspection mirror"],
                est_minutes=20,
                is_safety_critical=False,
                # citation is intentionally omitted — must raise ValidationError
            )
            # If somehow the step is created (should not happen), wrapping it in
            # a DiagnosisResponse should also fail.
            _make_diagnosis_response().model_copy(
                update={"inspection_checklist": [bad_step]}
            )

    def test_prd_json_example_validates(self) -> None:
        """Verify the abbreviated DiagnosisResponse JSON from PRD §S5 validates."""
        prd_json = """{
            "request_id": "req_01JABCDE",
            "asset_id": "PUMP-07",
            "measured_facts": [
                {"statement": "Drive-end bearing temperature is 91.4 C against a normal range of 55-75 C (z = 4.82, alarm band).",
                 "source": "sensor_engine", "sensor": "bearing_temp_de"}
            ],
            "manual_instructions": [
                {"step": "De-energize the motor and apply lockout/tagout before removing the coupling guard.",
                 "verbatim_safety": true,
                 "citation": {"chunk_id": "a1f9c2d40b77", "doc_title": "CP-450 Service Manual",
                              "revision": "Rev C", "section": "7.3 Excessive Vibration", "page": 61}}
            ],
            "inspection_checklist": [
                {"order": 1, "action": "Apply LOTO to the motor starter.",
                 "is_safety_critical": true,
                 "expected_observation": "Zero-energy state verified at the terminals.",
                 "if_abnormal_then": "Stop. Escalate to electrical supervisor.",
                 "tools_required": ["LOTO kit", "voltage tester"], "est_minutes": 5,
                 "citation": {"chunk_id": "a1f9c2d40b77", "doc_title": "CP-450 Service Manual",
                              "revision": "Rev C", "section": "7.3 Excessive Vibration", "page": 61}}
            ],
            "hypotheses": [
                {"rank": 1, "cause": "Drive-end bearing lubrication starvation",
                 "confidence": "high", "confidence_score": 0.81,
                 "supporting_sensors": ["bearing_temp_de", "vibration_rms"],
                 "supporting_chunks": ["a1f9c2d40b77", "9b3e1c7a55d2"],
                 "discriminating_check": "Verify oil level and lube pressure at test port TP-2 (step 4)."}
            ],
            "retrieval_status": "sufficient",
            "refusal": null,
            "guardrails": {"passed": ["citation", "safety", "numeric"], "failed": [],
                           "dropped_steps": 0, "notes": ""},
            "meta": {"prompt_version": "v1.4.0", "model": "claude-sonnet-4-5",
                     "retriever": "hybrid+rerank", "chunks_retrieved": 6,
                     "latency_ms": 3410, "corpus_revision": "abc123def456"}
        }"""
        dr = DiagnosisResponse.model_validate_json(prd_json)
        assert dr.request_id == "req_01JABCDE"
        assert dr.inspection_checklist[0].is_safety_critical is True
        assert dr.hypotheses[0].confidence == "high"


# ===========================================================================
# TESTS — API I/O models
# ===========================================================================


class TestDiagnoseRequest:
    def test_round_trip(self) -> None:
        req = DiagnoseRequest(
            asset_id="PUMP-07",
            captured_at=_NOW,
            error_code="E-204",
            sensors={
                "bearing_temp_de": SensorReading(
                    name="bearing_temp_de", value=91.4, unit="C", status="ok", last_seen=_NOW
                ),
                "vibration_rms": SensorReading(
                    name="vibration_rms", value=8.1, unit="mm/s", status="ok", last_seen=_NOW
                ),
            },
            context={"operating_hours": 8412, "notes": "Rising noise since morning shift"},
        )
        restored = DiagnoseRequest.model_validate_json(req.model_dump_json())
        assert restored == req

    def test_prd_appendix_b_validates(self) -> None:
        """Verify the exact request payload from PRD Appendix B validates."""
        prd_json = """{
            "asset_id": "PUMP-07",
            "captured_at": "2026-09-18T09:14:00+05:30",
            "error_code": "E-204",
            "sensors": {
                "bearing_temp_de": {"name": "bearing_temp_de", "value": 91.4, "unit": "C"},
                "vibration_rms":   {"name": "vibration_rms",   "value": 8.1,  "unit": "mm/s"},
                "motor_current":   {"name": "motor_current",   "value": 41.2, "unit": "A"},
                "discharge_pressure": {"name": "discharge_pressure", "value": 5.9, "unit": "bar"},
                "flow_rate":       {"name": "flow_rate",       "value": 118.0,"unit": "m3/h"},
                "oil_level_pct":   {"name": "oil_level_pct",   "value": 21.0, "unit": "%"}
            },
            "context": {"operating_hours": 8412, "notes": "Rising noise since morning shift"}
        }"""
        req = DiagnoseRequest.model_validate_json(prd_json)
        assert req.asset_id == "PUMP-07"
        assert req.error_code == "E-204"
        assert len(req.sensors) == 6

    def test_no_error_code(self) -> None:
        req = DiagnoseRequest(asset_id="PUMP-07", captured_at=_NOW)
        assert req.error_code is None
        assert req.sensors == {}

    def test_extra_fields_rejected(self) -> None:
        with pytest.raises(ValidationError):
            DiagnoseRequest(  # type: ignore[call-arg]
                asset_id="PUMP-07",
                captured_at=_NOW,
                unknown_field="should_fail",
            )


class TestFeedbackRequest:
    def test_round_trip(self) -> None:
        fb = FeedbackRequest(
            request_id="req_01J9ABCDE",
            resolved_at_step=3,
            was_resolved=True,
            comments="Replacing seal kit fixed the leak.",
        )
        restored = FeedbackRequest.model_validate_json(fb.model_dump_json())
        assert restored == fb

    def test_unresolved_feedback(self) -> None:
        fb = FeedbackRequest(
            request_id="req_01J9ABCDE",
            resolved_at_step=None,
            was_resolved=False,
            comments="Could not reproduce in field.",
        )
        assert fb.resolved_at_step is None

    def test_resolved_at_step_ge1(self) -> None:
        with pytest.raises(ValidationError):
            FeedbackRequest(
                request_id="req_01J9ABCDE",
                resolved_at_step=0,  # must be >= 1
                was_resolved=True,
            )
