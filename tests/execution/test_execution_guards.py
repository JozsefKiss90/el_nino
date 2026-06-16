"""TEST — guard-wiring (GATE-001 + PRED-001..005) in the execution orchestrator (ADR-011 gate c).

run_guard maps a GuardrailEngine APPROVE/BLOCK to a forwarded GuardResult; a block yields a no-fill
execution record naming the first failing predicate; the captured guard config drives the outcome
regardless of the environment (gate c.4 — replay determinism).
"""

from __future__ import annotations

from gold.decision_builder.models import DecisionMode, Direction
from gold.paper_runtime.models import RuntimeDecisionRecord, Verdict
from risk.guardrail_engine.models import GuardrailConfig
from execution import ExecutionItem, PortfolioState, run_guard, run_sequence

_GUARD_OK = GuardrailConfig(
    max_trade_size=10_000.0,
    max_trades_per_day=10,
    max_position_pct=0.05,
    max_positions=5,
    daily_loss_cap=5_000.0,
    allow_withdrawals=False,
)
# blocks position_size_ok: limit = min(100000 * 1e-7, 0.5) = 0.01 < default_size 1.0
_GUARD_BLOCK_SIZE = GuardrailConfig(
    max_trade_size=0.5,
    max_trades_per_day=10,
    max_position_pct=1e-7,
    max_positions=5,
    daily_loss_cap=5_000.0,
    allow_withdrawals=False,
)
_GUARD_BLOCK_WITHDRAWAL = GuardrailConfig(
    max_trade_size=10_000.0,
    max_trades_per_day=10,
    max_position_pct=0.05,
    max_positions=5,
    daily_loss_cap=5_000.0,
    allow_withdrawals=True,
)


def _admit(snapshot_id: str = "S1", record_id: str = "r1") -> RuntimeDecisionRecord:
    return RuntimeDecisionRecord(
        record_id=record_id,
        record_schema_version="0.1.0",
        source_packet_id=f"gold-v0:{snapshot_id}",
        source_snapshot_id=snapshot_id,
        decision_mode=DecisionMode.PAPER_ONLY,
        verdict=Verdict.ADMIT,
        triggered_guard=None,
        reason="ok",
        guard_outcomes=(),
        runtime_policy_version="0.1.0",
        as_of=None,
        prior_ledger_state_hash="p",
        new_ledger_state_hash="n",
        non_execution_notice="x",
        constraints=(),
    )


def test_run_guard_approves() -> None:
    gr = run_guard(Direction.LONG, PortfolioState.empty(), _GUARD_OK)
    assert gr.approved is True
    assert gr.blocked_by is None


def test_run_guard_blocks_on_position_size() -> None:
    gr = run_guard(Direction.LONG, PortfolioState.empty(), _GUARD_BLOCK_SIZE)
    assert gr.approved is False
    assert gr.blocked_by == "position_size_ok"


def test_run_guard_blocks_on_withdrawal_enabled() -> None:
    gr = run_guard(Direction.LONG, PortfolioState.empty(), _GUARD_BLOCK_WITHDRAWAL)
    assert gr.approved is False
    assert gr.blocked_by == "withdrawal_disabled"


def test_blocked_guard_produces_no_fill_record() -> None:
    items: list[ExecutionItem] = [(_admit("S1", "r1"), Direction.LONG, 2000.0)]
    recs, pf = run_sequence(items, _GUARD_BLOCK_SIZE)
    assert recs[0].fill is None
    assert recs[0].guard_result.approved is False
    assert recs[0].guard_result.blocked_by == "position_size_ok"
    assert pf.next_seq() == 0


def test_captured_config_overrides_environment(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    # If the orchestrator read env, MAX_TRADE_SIZE=0 would block; it uses the captured config (gate c.4).
    monkeypatch.setenv("MAX_TRADE_SIZE", "0")
    monkeypatch.setenv("MAX_POSITION_PCT", "0")
    gr = run_guard(Direction.LONG, PortfolioState.empty(), _GUARD_OK)
    assert gr.approved is True
