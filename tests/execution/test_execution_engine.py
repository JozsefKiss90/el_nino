"""TEST — execution engine (execute): fill paths, portfolio math, fail-closed, idempotency.

ADMIT + approved + LONG fills (at adverse slippage, mark-to-snapshot P&L); a blocked guard, a
non-LONG stance, or an already-executed snapshot yields a no-fill record (portfolio unchanged); a
non-ADMIT input raises; the ExecutionRecord fail-closed __post_init__ holds.
"""

from __future__ import annotations

import pytest

from gold.decision_builder.models import DecisionMode, Direction
from gold.paper_runtime.models import RuntimeDecisionRecord, Verdict
from execution import (
    DEFAULT_EXECUTION_POLICY_CONFIG,
    DEFAULT_FILL_MODEL,
    ExecutionContractError,
    ExecutionMode,
    ExecutionRecord,
    Fill,
    GuardResult,
    PortfolioState,
    execute,
)

PRICE = 2000.0


def _admit(snapshot_id: str = "S1", record_id: str = "paper-v0:r1") -> RuntimeDecisionRecord:
    return RuntimeDecisionRecord(
        record_id=record_id,
        record_schema_version="0.1.0",
        source_packet_id=f"gold-v0:{snapshot_id}",
        source_snapshot_id=snapshot_id,
        decision_mode=DecisionMode.PAPER_ONLY,
        verdict=Verdict.ADMIT,
        triggered_guard=None,
        reason="all required guards passed",
        guard_outcomes=(),
        runtime_policy_version="0.1.0",
        as_of="2026-05-01T00:00:00+00:00",
        prior_ledger_state_hash="p",
        new_ledger_state_hash="n",
        non_execution_notice="x",
        constraints=(),
    )


def _reject() -> RuntimeDecisionRecord:
    return RuntimeDecisionRecord(
        record_id="paper-v0:rej",
        record_schema_version="0.1.0",
        source_packet_id="gold-v0:S1",
        source_snapshot_id="S1",
        decision_mode=DecisionMode.PAPER_ONLY,
        verdict=Verdict.REJECT,
        triggered_guard="duplicate_ok",
        reason="dup",
        guard_outcomes=(),
        runtime_policy_version="0.1.0",
        as_of=None,
        prior_ledger_state_hash="p",
        new_ledger_state_hash="n",
        non_execution_notice="x",
        constraints=(),
    )


def _approved() -> GuardResult:
    return GuardResult(approved=True, blocked_by=None, reason="all guardrails passed")


def _blocked(predicate: str = "position_size_ok") -> GuardResult:
    return GuardResult(approved=False, blocked_by=predicate, reason="blocked")


# --- fill path --------------------------------------------------------------------------------

def test_long_approved_fills_with_adverse_slippage() -> None:
    rec, pf = execute(_admit(), Direction.LONG, PRICE, PortfolioState.empty(), _approved())
    assert rec.fill is not None
    assert rec.reason == "filled"
    assert rec.execution_mode is ExecutionMode.SIMULATED
    assert rec.replayable is True
    assert rec.paper_only is True
    # default slippage 5 bps -> fill at 2000 * 1.0005 = 2001.0
    assert rec.fill.fill_price == pytest.approx(2001.0)
    assert len(pf.executions) == 1
    pos = pf.position("GLD")
    assert pos is not None
    assert pos.quantity == pytest.approx(1.0)
    assert pos.avg_cost == pytest.approx(2001.0)
    assert pos.unrealized_pnl == pytest.approx(-1.0)  # mark 2000 - cost 2001


def test_accumulation_averages_cost() -> None:
    _, pf1 = execute(_admit("S1", "r1"), Direction.LONG, 2000.0, PortfolioState.empty(), _approved())
    _, pf2 = execute(_admit("S2", "r2"), Direction.LONG, 2010.0, pf1, _approved())
    pos = pf2.position("GLD")
    assert pos is not None
    assert pos.quantity == pytest.approx(2.0)
    # fills 2001.0 and 2011.005 -> avg 2006.0025
    assert pos.avg_cost == pytest.approx(2006.0025)
    assert len(pf2.executions) == 2


# --- fail-closed no-fill paths ----------------------------------------------------------------

def test_blocked_guard_yields_no_fill_unchanged_portfolio() -> None:
    rec, pf = execute(_admit(), Direction.LONG, PRICE, PortfolioState.empty(), _blocked())
    assert rec.fill is None
    assert "blocked by position_size_ok" in rec.reason
    assert pf.state_hash() == PortfolioState.empty().state_hash()
    assert rec.new_portfolio_state_hash == rec.prior_portfolio_state_hash


@pytest.mark.parametrize("direction", [Direction.FLAT, Direction.AVOID])
def test_non_long_stance_yields_no_fill(direction: Direction) -> None:
    rec, pf = execute(_admit(), direction, PRICE, PortfolioState.empty(), _approved())
    assert rec.fill is None
    assert "non-LONG" in rec.reason
    assert len(pf.executions) == 0


def test_idempotent_on_repeated_snapshot() -> None:
    rec1, pf1 = execute(_admit("S1", "r1"), Direction.LONG, PRICE, PortfolioState.empty(), _approved())
    rec2, pf2 = execute(_admit("S1", "r2"), Direction.LONG, PRICE, pf1, _approved())
    assert rec1.fill is not None
    assert rec2.fill is None
    assert "already executed" in rec2.reason
    assert pf2.state_hash() == pf1.state_hash()  # no double-fill
    assert len(pf2.executions) == 1


def test_non_admit_input_raises() -> None:
    with pytest.raises(ExecutionContractError, match="requires an ADMIT"):
        execute(_reject(), Direction.LONG, PRICE, PortfolioState.empty(), _approved())


# --- record / guard invariants ----------------------------------------------------------------

def test_guardresult_failclosed_invariants() -> None:
    with pytest.raises(ExecutionContractError):
        GuardResult(approved=True, blocked_by="x", reason="r")
    with pytest.raises(ExecutionContractError):
        GuardResult(approved=False, blocked_by=None, reason="r")


def test_execution_record_rejects_fill_without_approval() -> None:
    with pytest.raises(ExecutionContractError, match="fill requires an approved"):
        ExecutionRecord(
            execution_id="exec-v0:x",
            execution_schema_version="0.1.0",
            source_record_id="paper-v0:r1",
            source_snapshot_id="S1",
            instrument="GLD",
            direction=Direction.LONG,
            size=1.0,
            instrument_price=PRICE,
            fill=Fill(fill_price=2001.0, quantity=1.0, slippage_bps=5.0),
            guard_result=_blocked(),
            execution_mode=ExecutionMode.SIMULATED,
            replayable=True,
            fill_model_version=DEFAULT_FILL_MODEL.fill_model_version,
            prior_portfolio_state_hash="p",
            new_portfolio_state_hash="n",
            reason="x",
        )


def test_execution_id_binds_prior_state() -> None:
    # same admit, different prior portfolio state -> different execution_id
    rec_empty, pf = execute(_admit("S1", "r1"), Direction.LONG, PRICE, PortfolioState.empty(), _approved())
    rec_after, _ = execute(_admit("S2", "r2"), Direction.LONG, PRICE, pf, _approved())
    assert rec_empty.execution_id != rec_after.execution_id
    assert DEFAULT_EXECUTION_POLICY_CONFIG.instrument == "GLD"
