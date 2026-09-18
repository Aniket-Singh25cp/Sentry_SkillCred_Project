"""tests/test_synthesis/test_ordering.py — Unit tests for checklist tier ordering."""

from __future__ import annotations

from core.schemas import ChecklistStep, Citation
from synthesis.ordering import classify_step_tier, order_checklist_steps


def _make_step(
    order: int,
    action: str,
    *,
    is_safety_critical: bool = False,
    tools: list[str] | None = None,
    est_minutes: int = 10,
) -> ChecklistStep:
    return ChecklistStep(
        order=order,
        action=action,
        expected_observation="Normal operating indicator observed.",
        if_abnormal_then="Escalate to maintenance supervisor.",
        tools_required=tools or [],
        est_minutes=est_minutes,
        is_safety_critical=is_safety_critical,
        citation=Citation(
            chunk_id="chunk123456",
            doc_title="Pump Manual",
            revision="Rev A",
            section="Troubleshooting",
            page=12,
        ),
    )


def test_classify_step_tier() -> None:
    # Tier 1: safety critical flag
    s1 = _make_step(1, "Verify terminal voltage.", is_safety_critical=True)
    assert classify_step_tier(s1) == 1

    # Tier 1: keyword detection
    s1_kw = _make_step(1, "Apply lockout and tagout to disconnect switch.", is_safety_critical=False)
    assert classify_step_tier(s1_kw) == 1

    # Tier 2: sensory observation
    s2 = _make_step(2, "Inspect bearing sight glass for oil level.", is_safety_critical=False)
    assert classify_step_tier(s2) == 2

    # Tier 3: low-cost maintenance / checks
    s3 = _make_step(3, "Top up lube oil to upper line.", is_safety_critical=False)
    assert classify_step_tier(s3) == 3

    # Tier 4: invasive disassembly
    s4 = _make_step(4, "Disassemble bearing housing and unbolt flange.", is_safety_critical=False)
    assert classify_step_tier(s4) == 4


def test_safety_critical_steps_sort_first() -> None:
    # Provide steps where safety step is at the very end
    step_observe = _make_step(1, "Inspect oil sight glass.", is_safety_critical=False)
    step_disassemble = _make_step(2, "Remove bearing end cover and seals.", is_safety_critical=False)
    step_loto = _make_step(3, "De-energize motor and apply LOTO lock.", is_safety_critical=True)

    ordered = order_checklist_steps([step_observe, step_disassemble, step_loto])

    # Safety step must sort to index 0 (order=1)
    assert ordered[0].action == step_loto.action
    assert ordered[0].is_safety_critical is True
    assert ordered[0].order == 1

    # Observation step should be next (order=2)
    assert ordered[1].action == step_observe.action
    assert ordered[1].order == 2

    # Disassembly step should be last (order=3)
    assert ordered[2].action == step_disassemble.action
    assert ordered[2].order == 3


def test_intra_tier_order_preserved() -> None:
    # Multiple steps in the same tier should keep their relative initial position
    step_loto_1 = _make_step(1, "De-energize motor supply.", is_safety_critical=True)
    step_loto_2 = _make_step(2, "Verify zero energy with voltage tester.", is_safety_critical=True)

    step_obs_1 = _make_step(3, "Check pressure gauge reading.", is_safety_critical=False)
    step_obs_2 = _make_step(4, "Listen for bearing clicking noise.", is_safety_critical=False)

    ordered = order_checklist_steps([step_obs_1, step_loto_1, step_obs_2, step_loto_2])

    assert ordered[0].action == step_loto_1.action
    assert ordered[1].action == step_loto_2.action
    assert ordered[2].action == step_obs_1.action
    assert ordered[3].action == step_obs_2.action

    for idx, s in enumerate(ordered, start=1):
        assert s.order == idx
