# fixtures/ — SENTRY Stage Output Fixture Discipline

## Purpose

Every stage commits **at least one canonical sample of its output** to this
directory.  Downstream stages build and test against these fixtures rather
than against the upstream service directly.  This enforces contract fidelity
and enables all stages to be developed in parallel without live dependencies.

## Naming Convention

```
fixtures/
  s1_ingestion/
    sample_chunk.json            ← one Chunk model instance
    sample_error_code_entry.json ← one ErrorCodeEntry instance
  s2_evidence/
    pump07_bearing_fault.json    ← EvidenceReport for scenario 4
    pump07_unknown_code.json     ← EvidenceReport for adversarial scenario 7
  s3_retrieval/
    retrieval_result_sufficient.json
    retrieval_result_insufficient.json
  s4_anomaly/
    anomaly_result_positive.json
  s5_synthesis/
    diagnosis_response_bearing_fault.json
    diagnosis_response_refusal.json
```

## Rules

1. **Every fixture is a valid JSON-serialised Pydantic model.**
   Running `python -c "from core.schemas import X; X.model_validate_json(open('fixtures/...').read())"` must succeed.

2. **Fixtures are committed at the same time as the stage code** that produces
   them.  A stage PR without a fixture is incomplete.

3. **Fixture data is synthetic, never real plant data.**
   Sensor values, asset IDs, and technician names are all invented.

4. **Safety notes are preserved verbatim** in fixtures — they serve as the
   reference strings for the safety-preservation gate tests (G-3).

5. **Fixtures are read-only for downstream stages.**
   If a downstream stage discovers that a fixture is incorrect, it raises the
   issue with the owning stage's engineer; it does not edit the fixture.

6. **Corpus revision** in any `ResponseMeta.corpus_revision` field must match
   the Git commit SHA or DVC hash of the corpus that produced the fixture, so
   eval results are reproducible.

## Adding a Fixture

```bash
# After your stage generates output, serialise it:
python -c "
from core.schemas import EvidenceReport
import json, pathlib
report = EvidenceReport(...)          # your real output
pathlib.Path('fixtures/s2_evidence/my_scenario.json').write_text(
    report.model_dump_json(indent=2)
)
"
git add fixtures/s2_evidence/my_scenario.json
```

## Validation Helper (run from repo root)

```bash
python -m pytest tests/test_fixtures.py -v
```

`tests/test_fixtures.py` (owned by P0) will be added in a future iteration
once fixtures exist.  Until then, validate manually per the command in Rule 1.
