"""TEST — execution determinism + idempotency (the BENCH-004 core, ADR-011 §2).

run_sequence twice over the same items + captured guard config yields byte-identical records and an
identical ending portfolio state_hash; a persist/load round-trip preserves the state_hash; a repeated
snapshot in the sequence does not double-fill.
"""

from __future__ import annotations

from gold.decision_builder.models import DecisionMode, Direction
from gold.paper_runtime.models import RuntimeDecisionRecord, Verdict
from risk.guardrail_engine.models import GuardrailConfig
from execution import (
    ExecutionItem,
    PortfolioState,
    load_portfolio,
    persist_portfolio,
    run_sequence,
)

_GUARD_OK = GuardrailConfig(
    max_trade_size=10_000.0,
    max_trades_per_day=10,
    max_position_pct=0.05,
    max_positions=5,
    daily_loss_cap=5_000.0,
    allow_withdrawals=False,
)


def _admit(snapshot_id: str, record_id: str) -> RuntimeDecisionRecord:
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


def _items() -> list[ExecutionItem]:
    return [
        (_admit("S1", "r1"), Direction.LONG, 2000.0),
        (_admit("S2", "r2"), Direction.LONG, 2010.0),
        (_admit("S3", "r3"), Direction.FLAT, 2005.0),   # no fill
        (_admit("S4", "r4"), Direction.AVOID, 1995.0),  # no fill
    ]


def test_replay_is_byte_identical() -> None:
    recs1, pf1 = run_sequence(_items(), _GUARD_OK)
    recs2, pf2 = run_sequence(_items(), _GUARD_OK)
    assert [r.to_dict() for r in recs1] == [r.to_dict() for r in recs2]
    assert pf1.state_hash() == pf2.state_hash()
    # two LONG fills, two non-LONG no-fills
    assert sum(1 for r in recs1 if r.fill is not None) == 2
    assert pf1.next_seq() == 2


def test_persist_load_round_trip_preserves_state_hash(tmp_path) -> None:  # type: ignore[no-untyped-def]
    _, pf = run_sequence(_items(), _GUARD_OK)
    path = tmp_path / "portfolio.json"
    persist_portfolio(path, pf)
    loaded = load_portfolio(path)
    assert loaded.state_hash() == pf.state_hash()
    assert loaded.to_dict() == pf.to_dict()


def test_missing_portfolio_file_is_empty(tmp_path) -> None:  # type: ignore[no-untyped-def]
    loaded = load_portfolio(tmp_path / "nope.json")
    assert loaded.state_hash() == PortfolioState.empty().state_hash()


def test_repeated_snapshot_in_sequence_does_not_double_fill() -> None:
    items: list[ExecutionItem] = [
        (_admit("S1", "r1"), Direction.LONG, 2000.0),
        (_admit("S1", "r2"), Direction.LONG, 2000.0),  # same snapshot — idempotent
    ]
    recs, pf = run_sequence(items, _GUARD_OK)
    assert recs[0].fill is not None
    assert recs[1].fill is None
    assert pf.next_seq() == 1
