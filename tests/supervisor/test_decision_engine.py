"""Behavioral tests for the Decision Engine (covers decision_engine.py / MOD-002)."""
from __future__ import annotations

from typing import Any

import pytest

from supervisor.decision_engine.decision_engine import DecisionEngine
from supervisor.decision_engine.models import (
    DecisionPacket,
    EvaluationScorecard,
    RankedOption,
    TreasuryState,
    UpgradeOption,
)


def card(**overrides: Any) -> EvaluationScorecard:
    base: dict[str, Any] = dict(realized_pnl=-10.0, calibration=0.5, drawdown=0.2, disagreement=0.3)
    base.update(overrides)
    return EvaluationScorecard(**base)


# a: 0.5 * 0.8 / 100 = 0.004 ; b: 1.0 * 0.5 / 50 = 0.01  -> b ranks above a
CATALOG = [
    UpgradeOption("a", cost=100.0, target_dimension="calibration", expected_improvement=0.8),
    UpgradeOption("b", cost=50.0, target_dimension="pnl", expected_improvement=0.5),
]
TREASURY = TreasuryState(budget=500.0, deployed=0.0)


def test_early_exit_when_promotable() -> None:
    packet = DecisionEngine().decide(card(realized_pnl=10.0, calibration=0.7), CATALOG, TREASURY)
    assert packet.selected_upgrade_id is None
    assert packet.ranked_options == ()
    assert "no upgrade needed" in packet.rationale


def test_selects_highest_scoring_allowed_and_burns_treasury() -> None:
    packet = DecisionEngine().decide(card(), CATALOG, TREASURY)
    assert packet.selected_upgrade_id == "b"
    assert packet.treasury_state_after.deployed == 50.0


def test_budget_filter_blocks_unaffordable() -> None:
    packet = DecisionEngine().decide(card(), CATALOG, TreasuryState(budget=40.0, deployed=0.0))
    assert packet.selected_upgrade_id is None
    assert all(not r.allowed for r in packet.ranked_options)
    assert "all options blocked" in packet.rationale


def test_exclusion_filter_skips_excluded() -> None:
    packet = DecisionEngine().decide(card(), CATALOG, TREASURY, excluded_ids={"b"})
    assert packet.selected_upgrade_id == "a"
    blocked_b = next(r for r in packet.ranked_options if r.upgrade_id == "b")
    assert blocked_b.allowed is False
    assert "institutional memory" in (blocked_b.blocked_reason or "")


def test_decision_is_deterministic() -> None:
    engine = DecisionEngine()
    assert engine.decide(card(), CATALOG, TREASURY) == engine.decide(card(), CATALOG, TREASURY)


def test_packet_invariant_rejects_selected_not_allowed() -> None:
    with pytest.raises(ValueError):
        DecisionPacket(
            selected_upgrade_id="x",
            ranked_options=(RankedOption("x", 0.0, False, "blocked"),),
            rationale="bad",
            treasury_state_after=TREASURY,
        )


def test_ranked_option_requires_blocked_reason() -> None:
    with pytest.raises(ValueError):
        RankedOption("x", 0.0, False, None)
