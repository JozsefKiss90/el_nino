"""TEST — SCHEMA-015 ReconcileEntry + PendingOrder + PortfolioState (ADR-014 §6.2 / §6.3).

The two new live-path-only kinds and their shared determinism trick: a portfolio with **no** reconcile
entries / **no** pending orders serializes and hashes **byte-identically** to the pre-ADR-014 form (each
key is omitted while empty), so the sim/replay portfolio + benchmarks are undisturbed. A portfolio that
carries either kind round-trips through ``to_dict`` / ``from_dict``; ``append_reconcile`` /
``append_pending`` leave positions + executions untouched (no auto-adopt).
"""

from __future__ import annotations

import json

from execution import ExecutionEntry, PendingOrder, PortfolioState, Position, ReconcileEntry
from execution.models import PORTFOLIO_SCHEMA_VERSION


def _entry(snapshot_id: str = "S1") -> ExecutionEntry:
    return ExecutionEntry(
        source_snapshot_id=snapshot_id, source_record_id="r1", instrument="GLD", fill_price=431.5,
        quantity=1.0, fill_model_version="0.1.0", prior_portfolio_state_hash="h", seq=0,
        as_of="2026-05-01T20:00:00+00:00",
    )


def _reconcile(seq: int = 0) -> ReconcileEntry:
    return ReconcileEntry(
        source_snapshot_id="S2", instrument="GLD", observed_qty=3.0, observed_avg_price=400.0,
        marker="discrepancy:unexplained_position", seq=seq, as_of="2026-05-02T20:00:00+00:00",
    )


# --- the determinism trick: empty reconciles serialize byte-identically to the pre-ADR-014 form ----

def test_empty_reconciles_omitted_from_to_dict() -> None:
    pf = PortfolioState.empty().append(Position("GLD", 1.0, 431.5, 0.0, 0.0), _entry())
    d = pf.to_dict()
    assert "reconciles" not in d  # omitted while empty — the sim/replay portfolio stays byte-identical
    assert set(d) == {"executions", "portfolio_schema_version", "positions"}


def test_empty_reconcile_state_hash_unchanged_by_the_field() -> None:
    # Two portfolios identical but for the (defaulted-empty) reconciles tuple hash the same — the field
    # is inert on the sim path (this is what keeps BENCH-004/006 from re-pinning).
    a = PortfolioState(PORTFOLIO_SCHEMA_VERSION, (), (_entry(),))
    b = PortfolioState(PORTFOLIO_SCHEMA_VERSION, (), (_entry(),), ())
    assert a.state_hash() == b.state_hash()
    assert a.to_dict() == b.to_dict()


# --- reconcile entries round-trip + append_reconcile semantics -------------------------------------

def test_reconciles_present_round_trip() -> None:
    pf = PortfolioState.empty().append_reconcile(_reconcile(0)).append_reconcile(_reconcile(1))
    d = pf.to_dict()
    assert "reconciles" in d and len(d["reconciles"]) == 2
    # canonical JSON round-trips through from_dict (the live portfolio reloads its history)
    reloaded = PortfolioState.from_dict(json.loads(json.dumps(d)))
    assert reloaded.reconciles == pf.reconciles
    assert reloaded.state_hash() == pf.state_hash()


def test_append_reconcile_does_not_touch_positions_or_executions() -> None:
    pf = PortfolioState.empty().append(Position("GLD", 1.0, 431.5, 0.0, 0.0), _entry())
    healed = pf.append_reconcile(_reconcile())
    assert healed.positions == pf.positions  # no auto-adopt of the observed broker position
    assert healed.executions == pf.executions
    assert len(healed.reconciles) == 1
    assert pf.reconciles == ()  # immutability — the original is unchanged


def test_reconcile_entry_has_no_source_record_id_or_guard_result() -> None:
    # Distinct from ExecutionEntry: a reconcile observation is not a fill we placed (ADR-014 §6.2).
    d = _reconcile().to_dict()
    assert "source_record_id" not in d and "guard_result" not in d
    assert d["observed_qty"] == 3.0 and d["marker"] == "discrepancy:unexplained_position"


# --- PendingOrder (ADR-014 §6.3): same determinism trick + round-trip ------------------------------

def _pending(seq: int = 0) -> PendingOrder:
    return PendingOrder(
        source_snapshot_id="S1", source_record_id="r1", instrument="GLD", side="buy", requested_qty=1.0,
        client_order_id="eln-buy-deadbeef", seq=seq, as_of="2026-05-01T20:00:00+00:00",
    )


def test_empty_pending_omitted_from_to_dict() -> None:
    pf = PortfolioState.empty().append(Position("GLD", 1.0, 431.5, 0.0, 0.0), _entry())
    d = pf.to_dict()
    assert "pending" not in d  # omitted while empty — the sim/replay portfolio stays byte-identical
    assert set(d) == {"executions", "portfolio_schema_version", "positions"}


def test_empty_pending_state_hash_unchanged_by_the_field() -> None:
    # A portfolio with the defaulted-empty pending tuple hashes identically — inert on the sim path
    # (this is what keeps BENCH-004/006 from re-pinning for the cross-run-fold kind).
    a = PortfolioState(PORTFOLIO_SCHEMA_VERSION, (), (_entry(),))
    b = PortfolioState(PORTFOLIO_SCHEMA_VERSION, (), (_entry(),), (), ())
    assert a.state_hash() == b.state_hash()
    assert a.to_dict() == b.to_dict()


def test_pending_present_round_trip() -> None:
    pf = PortfolioState.empty().append_pending(_pending(0)).append_pending(_pending(1))
    d = pf.to_dict()
    assert "pending" in d and len(d["pending"]) == 2
    reloaded = PortfolioState.from_dict(json.loads(json.dumps(d)))
    assert reloaded.pending == pf.pending
    assert reloaded.state_hash() == pf.state_hash()


def test_append_pending_does_not_touch_positions_or_executions() -> None:
    pf = PortfolioState.empty().append(Position("GLD", 1.0, 431.5, 0.0, 0.0), _entry())
    queued = pf.append_pending(_pending())
    assert queued.positions == pf.positions and queued.executions == pf.executions
    assert len(queued.pending) == 1 and pf.pending == ()  # immutability — the original is unchanged


def test_with_pending_replaces_the_in_flight_list() -> None:
    # The fold drops a resolved order by replacing the pending list (compose with append to book the fill).
    pf = PortfolioState.empty().append_pending(_pending(0)).append_pending(_pending(1))
    dropped = pf.with_pending((pf.pending[1],))
    assert len(dropped.pending) == 1 and dropped.pending[0].seq == 1
    assert pf.pending != dropped.pending  # immutable replacement
