"""TEST-023 — chain orchestrator core (MOD-010): the pure ``run_chain`` composition.

Behavioral tests of the end-to-end core over the real consumable fixture: ADMIT + no-fill on the
monochromatic AVOID corpus, the in-hand price/direction forwarding (ADR-011 D1), wrap-not-enrich
(packet stays pure, ADR-009 §2), forwarded snapshot provenance + as_of, the GATE-001 guard-wiring
(block attribution), the non-ADMIT → no-execute branch, end-to-end idempotency, the fail-closed
ADMIT-without-price guard, and bounded-context hygiene (only the orchestrator imports ``src/risk``).
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from execution import resolve_sim_exec_ref
from execution.models import PortfolioState
from gold.decision_builder.models import Direction
from gold.paper_runtime.models import OperationalInput, RuntimeLedger, Verdict
from risk.guardrail_engine.models import GuardrailConfig
from snapshot.snapshot_consumer import consume
from snapshot.snapshot_consumer.models import Snapshot

from orchestration import run_chain
from orchestration.models import ChainContractError

_REPO_ROOT = Path(__file__).resolve().parents[2]
_REAL = _REPO_ROOT / "tests" / "snapshot" / "fixtures" / "latest_snapshot_pass.json"
_SNAPSHOT_ID = "952cc83a8f930e27a7c3636cb03cf1c5d9b93a5363fa8d9b1a4891f6af7afaef"
_PACKET_ID = "gold-v0:5653d07a0b3949d5"
_GOLD_PRICE = 4624.5

# A captured restrictive guard config that blocks position_size_ok (mirrors BENCH-004 _GUARD_BLOCK_SIZE):
# limit = min(100000 * 1e-7, 0.5) = 0.01 < default_size 1.0.
_GUARD_BLOCK = GuardrailConfig(
    max_trade_size=0.5, max_trades_per_day=10, max_position_pct=1e-7,
    max_positions=5, daily_loss_cap=5_000.0, allow_withdrawals=False,
)


def _snap() -> Snapshot:
    snap = consume(_REAL)
    assert snap is not None
    return snap


def test_real_chain_admits_no_fill_avoid() -> None:
    r = run_chain(_snap(), RuntimeLedger.empty(), PortfolioState.empty())
    assert r.regime.regime.value == "RESTRICTIVE_RATES"
    assert r.packet.direction is Direction.AVOID
    assert r.runtime_record.verdict is Verdict.ADMIT
    assert r.runtime_record.triggered_guard is None
    # ADMIT ⇒ an execution record exists; AVOID is a non-LONG stance ⇒ no paper fill.
    assert r.execution_record is not None
    assert r.execution_record.fill is None
    assert "non-LONG" in r.execution_record.reason


def test_exec_ref_gld_price_forwarded_and_gold_price_severed() -> None:
    # ADR-014 bucket (i): the orchestrator forwards packet.direction + the resolved GLD *share*
    # reference (derived proxy on the replay path) into execute — never gold spot, never re-derived by
    # reloading the snapshot. gold_price ($/oz) is severed from execution and stays a decision feature.
    r = run_chain(_snap(), RuntimeLedger.empty(), PortfolioState.empty())
    assert r.execution_record is not None
    gold_spot = r.feature_vector.value("gold_price")
    assert gold_spot == _GOLD_PRICE  # the spot feature is unchanged (still a decision-context input)
    expected_ref = resolve_sim_exec_ref(gold_spot, _snap().clock_ts)
    assert r.execution_record.instrument_price == expected_ref.price
    assert r.execution_record.exec_ref_gld_price == expected_ref.price
    assert r.execution_record.exec_ref_gld_price == r.execution_record.instrument_price
    assert r.execution_record.exec_ref_gld_price_basis == expected_ref.basis
    assert r.execution_record.exec_ref_gld_price != gold_spot  # severed: a GLD share price, not $/oz
    assert r.execution_record.direction is r.packet.direction is Direction.AVOID


def test_wrap_not_enrich_packet_stays_pure() -> None:
    # The pure packet never carries runtime state: guard_refs are all None (guards=None into build_decision).
    r = run_chain(_snap(), RuntimeLedger.empty(), PortfolioState.empty())
    refs = r.packet.guard_refs.to_dict()
    assert refs == {name: None for name in refs}


def test_snapshot_guards_and_as_of_forwarded() -> None:
    snap = _snap()
    r = run_chain(snap, RuntimeLedger.empty(), PortfolioState.empty())
    assert r.packet.snapshot_guards is not None
    assert r.packet.snapshot_guards.data_ok == snap.guards.data_ok
    assert r.packet.snapshot_guards.freshness_ok == snap.guards.freshness_ok
    assert r.packet.snapshot_guards.cooldown_ok == snap.guards.cooldown_ok
    assert r.packet.as_of == snap.clock_ts  # deterministic clock, never wall-clock


def test_packet_id_matches_established_chain() -> None:
    # The orchestrator reproduces the same gold packet the standalone chain / e2e test pins.
    r = run_chain(_snap(), RuntimeLedger.empty(), PortfolioState.empty())
    assert r.packet.packet_id == _PACKET_ID
    assert r.runtime_record.source_snapshot_id == _SNAPSHOT_ID


def test_ledger_always_advances_by_one() -> None:
    r = run_chain(_snap(), RuntimeLedger.empty(), PortfolioState.empty())
    assert len(r.ledger.entries) == 1  # one self-describing entry per evaluation


def test_non_admit_leaves_portfolio_unchanged_and_no_exec() -> None:
    # Captured CLOSED operational input ⇒ operational_ok fails ⇒ REJECT ⇒ no execute, portfolio unchanged.
    prior_pf = PortfolioState.empty()
    r = run_chain(
        _snap(), RuntimeLedger.empty(), prior_pf,
        operational_input=OperationalInput.closed(),
    )
    assert r.runtime_record.verdict is Verdict.REJECT
    assert r.runtime_record.triggered_guard == "operational_ok"
    assert r.execution_record is None
    assert r.portfolio.state_hash() == prior_pf.state_hash()


def test_end_to_end_idempotency_no_double_admit() -> None:
    snap = _snap()
    r1 = run_chain(snap, RuntimeLedger.empty(), PortfolioState.empty())
    r2 = run_chain(snap, r1.ledger, r1.portfolio)  # re-present the same snapshot
    assert r1.runtime_record.verdict is Verdict.ADMIT
    assert r2.runtime_record.verdict is Verdict.REJECT
    assert r2.runtime_record.triggered_guard == "duplicate_ok"
    assert r2.execution_record is None
    assert r2.portfolio.state_hash() == r1.portfolio.state_hash()  # no double-fill


def test_guard_block_attributed_no_fill() -> None:
    # ADMIT but a restrictive captured guard BLOCKs the trade ⇒ no fill, attributed, portfolio unchanged.
    prior_pf = PortfolioState.empty()
    r = run_chain(_snap(), RuntimeLedger.empty(), prior_pf, guard_config=_GUARD_BLOCK)
    assert r.runtime_record.verdict is Verdict.ADMIT
    assert r.execution_record is not None
    assert r.execution_record.guard_result.approved is False
    assert r.execution_record.guard_result.blocked_by == "position_size_ok"
    assert r.execution_record.fill is None
    assert r.execution_record.reason.startswith("blocked by")
    assert r.portfolio.state_hash() == prior_pf.state_hash()


def test_admit_without_in_hand_price_fails_closed() -> None:
    # Defensive ADR-011 D1 invariant: an ADMIT with no in-hand gold_price raises (unreachable for a real
    # consumable snapshot, which always carries the Tier-1 gold_price_proxy — gold is not a regime
    # required-feature, so a gold-stripped snapshot still classifies RESTRICTIVE_RATES → AVOID → ADMIT).
    stripped = replace(
        _snap(),
        values={k: v for k, v in _snap().values.items() if k != "gold_price_proxy"},
    )
    with pytest.raises(ChainContractError):
        run_chain(stripped, RuntimeLedger.empty(), PortfolioState.empty())


def test_to_dict_is_deterministic() -> None:
    import json

    a = run_chain(_snap(), RuntimeLedger.empty(), PortfolioState.empty()).to_dict()
    b = run_chain(_snap(), RuntimeLedger.empty(), PortfolioState.empty()).to_dict()
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_bounded_context_hygiene_only_orchestrator_imports_risk() -> None:
    # ADR-009 §3 / ADR-011 gate c: the per-layer pure cores never import src/risk; the orchestrator
    # (the composition root) is the single cross-context importer that wires the GATE-001 guard.
    import execution.engine as exec_engine
    import gold.paper_runtime.engine as runtime_engine

    import orchestration.engine as orch_engine

    exec_src = Path(exec_engine.__file__).read_text(encoding="utf-8")
    runtime_src = Path(runtime_engine.__file__).read_text(encoding="utf-8")
    orch_src = Path(orch_engine.__file__).read_text(encoding="utf-8")
    assert "import risk" not in exec_src and "from risk" not in exec_src
    assert "import risk" not in runtime_src and "from risk" not in runtime_src
    assert "from risk" in orch_src and "run_guard" in orch_src
