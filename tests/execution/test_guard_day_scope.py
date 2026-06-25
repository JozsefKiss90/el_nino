"""TEST — the guard's daily inputs are day-scoped by the snapshot as_of (ADR-014 §5.2).

``trades_today`` counts only executions on the SAME trading day as the request ``as_of``, so
``max_trades_per_day`` is a genuine daily cap that resets per day — not the lifetime fill count that
silently became a forever-block once enough fills accumulated. Mirrors the runtime cooldown discipline
(keys off the snapshot clock, never wall-clock).
"""

from __future__ import annotations

from execution import build_guard_request, run_guard
from execution.models import PORTFOLIO_SCHEMA_VERSION, ExecutionEntry, PortfolioState
from gold.decision_builder.models import Direction
from risk.guardrail_engine.models import GuardrailConfig


def _entry(seq: int, as_of: str | None) -> ExecutionEntry:
    return ExecutionEntry(
        source_snapshot_id=f"S{seq}",
        source_record_id=f"r{seq}",
        instrument="GLD",
        fill_price=100.0,
        quantity=1.0,
        fill_model_version="0.1.0",
        prior_portfolio_state_hash="h",
        seq=seq,
        as_of=as_of,
    )


def _portfolio(*entries: ExecutionEntry) -> PortfolioState:
    return PortfolioState(PORTFOLIO_SCHEMA_VERSION, (), tuple(entries))


_TWO_DAYS = _portfolio(
    _entry(0, "2026-05-01T13:00:00+00:00"),
    _entry(1, "2026-05-01T20:00:00+00:00"),
    _entry(2, "2026-05-02T13:00:00+00:00"),
)


def test_trades_today_counts_only_the_current_trading_day() -> None:
    # Lifetime fill count is 3; day-scoping returns the per-day count and resets across the boundary.
    assert build_guard_request(Direction.LONG, _TWO_DAYS, as_of="2026-05-01T23:59:00+00:00").trades_today == 2
    assert build_guard_request(Direction.LONG, _TWO_DAYS, as_of="2026-05-02T09:00:00+00:00").trades_today == 1
    assert build_guard_request(Direction.LONG, _TWO_DAYS, as_of="2026-05-03T09:00:00+00:00").trades_today == 0


def test_max_trades_per_day_resets_and_does_not_block_forever() -> None:
    # A cap of 2/day: lifetime counting (3 fills) would block forever; day-scoping approves on a new
    # day because only that day's fills count toward the cap.
    cap2 = GuardrailConfig(
        max_trade_size=10_000.0, max_trades_per_day=2, max_position_pct=0.05,
        max_positions=5, daily_loss_cap=5_000.0, allow_withdrawals=False,
    )
    # Day 1 already has 2 fills → at the cap → blocked.
    blocked = run_guard(Direction.LONG, _TWO_DAYS, cap2, as_of="2026-05-01T23:59:00+00:00")
    assert blocked.approved is False
    assert blocked.blocked_by == "max_trades_ok"
    # Day 2 has only 1 fill → below the cap → approved (lifetime counting would still block at 3).
    approved = run_guard(Direction.LONG, _TWO_DAYS, cap2, as_of="2026-05-02T09:00:00+00:00")
    assert approved.approved is True


def test_unparseable_as_of_groups_with_none_dated_entries() -> None:
    # Synthetic / None-dated entries (no snapshot clock) group together deterministically — preserving
    # the prior lifetime-count behavior for that degenerate case without raising.
    none_pf = _portfolio(_entry(0, None), _entry(1, None))
    assert build_guard_request(Direction.LONG, none_pf, as_of=None).trades_today == 2
    assert build_guard_request(Direction.LONG, none_pf, as_of="not-a-date").trades_today == 2
