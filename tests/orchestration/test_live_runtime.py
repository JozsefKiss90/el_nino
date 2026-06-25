"""TEST — live_runtime.operate_live reconcile-then-act (ADR-014 §6, bucket ii).

Three seams, all stub-driven (NO network):
  * ``plan_reconcile`` — the pure reconcile delta → side-based action / discrepancy decision;
  * ``reconcile_and_act`` — the act core: account gate, cash-capped buy, FLAT sell-fold (realized P&L),
    discrepancy → terminal-refuse + reconcile-heal, idempotency bifurcation;
  * ``operate_live`` — the end-to-end live shell over the real AVOID fixture: NO_ACTION before the
    adapter (broker never contacted), separate live paths, the chain advancing, and idempotency.
"""

from __future__ import annotations

from pathlib import Path
from urllib.error import URLError

import pytest

from execution import (
    ExecutionEntry,
    ExecutionStatus,
    GuardResult,
    PendingOrder,
    PortfolioState,
    Position,
)
from execution.live_adapter import LiveExecutionAdapter, make_client_order_id
from execution.models import PORTFOLIO_SCHEMA_VERSION
from execution.price_reference import BASIS_LIVE_SUBMIT, OZ_PER_SHARE, ExecPriceRef
from gold.decision_builder.models import DecisionMode, Direction
from gold.paper_runtime.models import RECORD_SCHEMA_VERSION, RuntimeDecisionRecord, Verdict
from risk.guardrail_engine.models import GuardrailConfig

from orchestration.live_runtime import (
    LiveExecutionConfig,
    operate_live,
    plan_reconcile,
    reconcile_and_act,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_REAL = _REPO_ROOT / "tests" / "snapshot" / "fixtures" / "latest_snapshot_pass.json"
_SNAPSHOT_ID = "952cc83a8f930e27a7c3636cb03cf1c5d9b93a5363fa8d9b1a4891f6af7afaef"
GLD = "GLD"
_OK = GuardResult(True, None, "ok")
_REF = ExecPriceRef(price=431.5, ts="2026-05-01T20:00:00+00:00", basis=BASIS_LIVE_SUBMIT)


def _admit(snapshot_id: str = "S1", as_of: str = "2026-05-01T20:00:00+00:00") -> RuntimeDecisionRecord:
    return RuntimeDecisionRecord(
        record_id="rec-1", record_schema_version=RECORD_SCHEMA_VERSION, source_packet_id="pkt-1",
        source_snapshot_id=snapshot_id, decision_mode=DecisionMode.PAPER_ONLY, verdict=Verdict.ADMIT,
        triggered_guard=None, reason="admit", guard_outcomes=(), runtime_policy_version="0.1.0",
        as_of=as_of, prior_ledger_state_hash="h0", new_ledger_state_hash="h1",
        non_execution_notice="paper", constraints=(),
    )


class _Broker:
    """A full LiveBrokerPort stub (canned reads; submit calls recorded). NO network."""

    _ACTIVE = {"status": "ACTIVE", "trading_blocked": False, "account_blocked": False, "cash": "10000"}

    def __init__(
        self, *, account=None, asset=None, positions=(), open_orders=(), orders=(),
        submit_status: str = "accepted", mark: float = 431.5,
    ) -> None:
        self._account = dict(self._ACTIVE) if account is None else account
        self._asset = {"symbol": GLD, "fractionable": True, "tradable": True} if asset is None else asset
        self._positions = list(positions)
        self._open_orders = list(open_orders)
        self._orders = list(orders)
        self._submit_status = submit_status
        self._mark = mark
        self.buy_calls: list[dict] = []
        self.sell_calls: list[dict] = []

    def submit_market_buy(self, symbol, *, qty=None, notional=None, client_order_id):
        self.buy_calls.append({"qty": qty, "notional": notional, "coid": client_order_id})
        return {"id": "ob", "status": self._submit_status, "client_order_id": client_order_id}

    def submit_market_sell(self, symbol, *, qty=None, notional=None, client_order_id):
        self.sell_calls.append({"qty": qty, "notional": notional, "coid": client_order_id})
        return {"id": "os", "status": self._submit_status, "client_order_id": client_order_id}

    def get_positions(self):
        return list(self._positions)

    def get_open_orders(self):
        return list(self._open_orders)

    def get_orders(self):
        return list(self._orders)

    def get_account(self):
        return self._account

    def get_asset(self, symbol):
        return self._asset

    def get_latest_trade(self, symbol):
        # The REAL live GLD mark (ADR-014 §5.1) — a single canned print; tests vary ``mark`` to prove
        # slippage is recorded fill-vs-real-mark, never against the sim derived proxy.
        return {"symbol": symbol, "trade": {"p": self._mark, "t": "2026-05-01T20:00:00Z"}}


def _pos(qty: float, avg: float = 400.0) -> Position:
    return Position(GLD, qty, avg, 0.0, 0.0)


def _portfolio_with_position(qty: float, avg: float = 400.0, snapshot_id: str = "S1") -> PortfolioState:
    entry = ExecutionEntry(
        source_snapshot_id=snapshot_id, source_record_id="rec-0", instrument=GLD, fill_price=avg,
        quantity=qty, fill_model_version="0.1.0", prior_portfolio_state_hash="h", seq=0,
        as_of="2026-05-01T13:00:00+00:00",
    )
    return PortfolioState(PORTFOLIO_SCHEMA_VERSION, (_pos(qty, avg),), (entry,))


# ===================================================================== plan_reconcile (pure delta)

def test_plan_long_flat_buys() -> None:
    plan = plan_reconcile(Direction.LONG, GLD, [], [], None)
    assert plan.action == "buy"


def test_plan_long_already_long_no_action() -> None:
    plan = plan_reconcile(Direction.LONG, GLD, [{"symbol": GLD, "qty": "2", "avg_entry_price": "400"}], [], _pos(2))
    assert plan.action == "no_action"


def test_plan_long_ours_open_buy_nets_no_action() -> None:
    # The cross-snapshot queue: an ours BUY already in flight covers the target → NO_ACTION (ADR-014 §6.3).
    coid = make_client_order_id("S0", "buy")
    plan = plan_reconcile(
        Direction.LONG, GLD, [], [{"symbol": GLD, "client_order_id": coid, "side": "buy", "status": "new"}], None,
    )
    assert plan.action == "no_action"


def test_plan_foreign_open_order_is_discrepancy() -> None:
    plan = plan_reconcile(
        Direction.LONG, GLD, [],
        [{"symbol": GLD, "client_order_id": "someone-else-123", "side": "buy", "status": "new"}], None,
    )
    assert plan.action == "discrepancy" and plan.marker == "unexpected_open_order"


def test_plan_wrong_side_open_order_is_discrepancy() -> None:
    coid = make_client_order_id("S0", "sell")
    plan = plan_reconcile(
        Direction.LONG, GLD, [], [{"symbol": GLD, "client_order_id": coid, "side": "sell", "status": "new"}], None,
    )
    assert plan.action == "discrepancy" and plan.marker == "wrong_side_open_order"


def test_plan_flat_with_lineage_sells() -> None:
    plan = plan_reconcile(Direction.FLAT, GLD, [{"symbol": GLD, "qty": "2", "avg_entry_price": "400"}], [], _pos(2))
    assert plan.action == "sell" and plan.sell_qty == 2.0


def test_plan_flat_unexplained_position_is_discrepancy() -> None:
    # FLAT but the broker holds a position we have no local lineage for → refuse (no auto-flatten).
    plan = plan_reconcile(Direction.FLAT, GLD, [{"symbol": GLD, "qty": "2", "avg_entry_price": "400"}], [], None)
    assert plan.action == "discrepancy" and plan.marker == "unexplained_position"


def test_plan_flat_already_flat_no_action() -> None:
    assert plan_reconcile(Direction.FLAT, GLD, [], [], None).action == "no_action"


def test_plan_flat_exit_in_flight_nets_no_action() -> None:
    coid = make_client_order_id("S0", "sell")
    plan = plan_reconcile(
        Direction.FLAT, GLD, [{"symbol": GLD, "qty": "2", "avg_entry_price": "400"}],
        [{"symbol": GLD, "client_order_id": coid, "side": "sell", "status": "new"}], _pos(2),
    )
    assert plan.action == "no_action"


# ===================================================================== reconcile_and_act (the core)

def test_guard_block_no_broker_contact() -> None:
    broker = _Broker()
    rec, pf = reconcile_and_act(
        _admit(), Direction.LONG, PortfolioState.empty(),
        GuardResult(False, "position_size_ok", "blocked"), LiveExecutionAdapter(client=broker), _REF,
    )
    assert rec.status is ExecutionStatus.NO_ACTION
    assert "blocked by position_size_ok" in rec.reason
    assert rec.fill is None
    assert broker.buy_calls == [] and broker.sell_calls == []  # never reached the broker


def test_idempotent_already_executed_no_broker_contact() -> None:
    broker = _Broker()
    prior = _portfolio_with_position(1.0, snapshot_id="S1")  # has_execution("S1") is True
    rec, pf = reconcile_and_act(
        _admit("S1"), Direction.LONG, prior, _OK, LiveExecutionAdapter(client=broker), _REF,
    )
    assert rec.status is ExecutionStatus.NO_ACTION and "idempotent" in rec.reason
    assert broker.buy_calls == []


def test_avoid_resolved_before_adapter() -> None:
    broker = _Broker()
    rec, pf = reconcile_and_act(
        _admit(), Direction.AVOID, PortfolioState.empty(), _OK, LiveExecutionAdapter(client=broker), _REF,
    )
    assert rec.status is ExecutionStatus.NO_ACTION
    assert broker.buy_calls == [] and broker.sell_calls == []  # AVOID never contacts the broker


def test_long_buy_is_cash_capped_and_folds_the_fill() -> None:
    coid = make_client_order_id("S1", "buy")
    orders = [{"id": "ob", "client_order_id": coid, "symbol": GLD, "status": "filled",
               "filled_qty": "2.31", "filled_avg_price": "431.5"}]
    broker = _Broker(
        account={"status": "ACTIVE", "trading_blocked": False, "account_blocked": False, "cash": "500"},
        orders=orders,
    )
    rec, pf = reconcile_and_act(
        _admit("S1"), Direction.LONG, PortfolioState.empty(), _OK, LiveExecutionAdapter(client=broker), _REF,
        live_config=LiveExecutionConfig(target_notional=1000.0),
    )
    # cash-cap: min(1000, 500) = 500; fractionable → a NOTIONAL order capped to settled cash.
    assert broker.buy_calls[0]["notional"] == pytest.approx(500.0)
    assert broker.buy_calls[0]["qty"] is None
    assert rec.status is ExecutionStatus.FILLED
    assert rec.fill is not None and rec.fill.fill_price == pytest.approx(431.5)
    assert rec.client_order_id == coid and rec.alpaca_order_id == "ob"
    # the fill folded into the live portfolio (a buy realizes nothing)
    assert pf.position(GLD).quantity == pytest.approx(2.31)
    assert pf.position(GLD).realized_pnl == 0.0
    assert len(pf.executions) == 1


def test_long_buy_nothing_affordable_no_action() -> None:
    broker = _Broker(account={"status": "ACTIVE", "trading_blocked": False, "account_blocked": False, "cash": "0"})
    rec, pf = reconcile_and_act(
        _admit(), Direction.LONG, PortfolioState.empty(), _OK, LiveExecutionAdapter(client=broker), _REF,
    )
    assert rec.status is ExecutionStatus.NO_ACTION and "affordable" in rec.reason
    assert broker.buy_calls == []  # nothing submitted


def test_flat_exit_sell_fold_realizes_pnl() -> None:
    coid = make_client_order_id("S2", "sell")
    orders = [{"id": "os", "client_order_id": coid, "symbol": GLD, "status": "filled",
               "filled_qty": "2", "filled_avg_price": "450"}]
    broker = _Broker(positions=[{"symbol": GLD, "qty": "2", "avg_entry_price": "400"}], orders=orders)
    prior = _portfolio_with_position(2.0, avg=400.0, snapshot_id="S1")
    rec, pf = reconcile_and_act(
        _admit("S2"), Direction.FLAT, prior, _OK, LiveExecutionAdapter(client=broker), _REF,
    )
    assert rec.status is ExecutionStatus.FILLED
    assert broker.sell_calls[0]["qty"] == pytest.approx(2.0)  # sold the broker position to close
    # SELL-fold (live only): realized_pnl += 2 * (450 - 400) = 100; position -> 0.
    assert pf.position(GLD).quantity == 0.0
    assert pf.position(GLD).realized_pnl == pytest.approx(100.0)


def test_discrepancy_refuses_execution_and_appends_heal_entry() -> None:
    broker = _Broker(
        open_orders=[{"symbol": GLD, "client_order_id": "foreign-999", "side": "buy", "status": "new"}],
    )
    rec, pf = reconcile_and_act(
        _admit(), Direction.LONG, PortfolioState.empty(), _OK, LiveExecutionAdapter(client=broker), _REF,
    )
    assert rec.status is ExecutionStatus.EXECUTION_UNCERTAIN  # terminal-refuse execution
    assert rec.fill is None
    assert "unexpected open order" in rec.reason
    assert broker.buy_calls == [] and broker.sell_calls == []  # NO auto-flatten / no order
    # a reconcile-heal entry is appended (observed broker state recorded), distinct from an execution.
    assert len(pf.reconciles) == 1
    assert pf.reconciles[0].marker == "discrepancy:unexpected_open_order"
    assert len(pf.executions) == 0  # not adopted into the local position


def test_account_gate_failure_refuses_and_halts() -> None:
    broker = _Broker(account={"status": "ONBOARDING", "trading_blocked": False, "account_blocked": False, "cash": "1"})
    rec, pf = reconcile_and_act(
        _admit(), Direction.LONG, PortfolioState.empty(), _OK, LiveExecutionAdapter(client=broker), _REF,
    )
    assert rec.status is ExecutionStatus.EXECUTION_UNCERTAIN and "startup reconcile failed" in rec.reason
    assert broker.buy_calls == []
    assert pf.executions == ()  # chain may advance, but execution did not


def test_long_async_accept_is_queued_no_fold() -> None:
    # A genuinely-async broker (order stays open) → QUEUED record, no local fold (resolved next cycle).
    coid = make_client_order_id("S1", "buy")
    orders = [{"id": "ob", "client_order_id": coid, "symbol": GLD, "status": "new", "filled_qty": "0"}]
    broker = _Broker(orders=orders)
    rec, pf = reconcile_and_act(
        _admit("S1"), Direction.LONG, PortfolioState.empty(), _OK, LiveExecutionAdapter(client=broker), _REF,
    )
    assert rec.status is ExecutionStatus.QUEUED
    assert rec.fill is None
    assert pf.position(GLD) is None  # no fold while the order is still open
    assert len(broker.buy_calls) == 1
    # the in-flight order is tracked (the durable lineage the next reconcile folds — ADR-014 §6.3)
    assert len(pf.pending) == 1 and pf.pending[0].client_order_id == coid and pf.pending[0].side == "buy"


# ============================================ Blocker 1: live slippage vs the REAL mark (ADR-014 §5.1)

def test_live_buy_slippage_is_against_real_broker_mark_not_proxy() -> None:
    # exec_ref omitted → reconcile_and_act reads the REAL broker GLD mark (get_latest_trade), NEVER the
    # sim derived proxy. The recorded mark + slippage are provably fill-vs-real-mark.
    real_mark = 430.0
    fill_price = 431.29  # broker fills 1.29 above the real mark → +30.0 bps execution slippage
    coid = make_client_order_id("S1", "buy")
    orders = [{"id": "ob", "client_order_id": coid, "symbol": GLD, "status": "filled",
               "filled_qty": "1", "filled_avg_price": str(fill_price)}]
    broker = _Broker(
        asset={"symbol": GLD, "fractionable": False, "tradable": True},  # integer share → known qty
        orders=orders, mark=real_mark,
    )
    rec, pf = reconcile_and_act(
        _admit("S1"), Direction.LONG, PortfolioState.empty(), _OK, LiveExecutionAdapter(client=broker),
        live_config=LiveExecutionConfig(target_notional=500.0),
    )
    assert rec.status is ExecutionStatus.FILLED
    assert rec.instrument_price == pytest.approx(real_mark)        # the recorded reference IS the real mark
    assert rec.exec_ref_gld_price == pytest.approx(real_mark)
    assert rec.exec_ref_gld_price_basis == BASIS_LIVE_SUBMIT       # pinned live-submit provenance
    expected_bps = (fill_price - real_mark) / real_mark * 10_000.0
    assert rec.fill is not None and rec.fill.slippage_bps == pytest.approx(expected_bps)  # fill-vs-REAL-mark
    # decisively NOT the sim proxy: the derived proxy mark would have been a different number.
    proxy_mark = 4624.5 * OZ_PER_SHARE  # ≈431.5 — what the old code used; not what we recorded
    assert rec.instrument_price != pytest.approx(proxy_mark)


def test_live_mark_read_failure_refuses_execution_no_proxy_fallback() -> None:
    # If the real GLD mark cannot be read, the live path REFUSES (it never falls back to the proxy) — §5.1.
    class _NoMark(_Broker):
        def get_latest_trade(self, symbol):
            raise URLError("market data unavailable")

    broker = _NoMark()
    rec, pf = reconcile_and_act(
        _admit("S1"), Direction.LONG, PortfolioState.empty(), _OK, LiveExecutionAdapter(client=broker),
    )
    assert rec.status is ExecutionStatus.EXECUTION_UNCERTAIN
    assert rec.fill is None
    assert broker.buy_calls == []  # no order is ever submitted without a real mark


# ============================================ Blocker 2: cross-run async-fill fold (ADR-014 §6.3)

def _active(cash: str = "10000") -> dict:
    return {"status": "ACTIVE", "trading_blocked": False, "account_blocked": False, "cash": cash}


def test_cross_run_async_fill_is_folded_next_reconcile_exactly_once() -> None:
    coid = make_client_order_id("S1", "buy")
    # Run N — the order is accepted but stays open at resolve → QUEUED + a PendingOrder recorded.
    open_order = {"id": "ob", "client_order_id": coid, "symbol": GLD, "status": "new", "filled_qty": "0"}
    broker_n = _Broker(
        account=_active(), asset={"symbol": GLD, "fractionable": False, "tradable": True},
        orders=[open_order], mark=430.0,
    )
    rec_n, pf_n = reconcile_and_act(
        _admit("S1"), Direction.LONG, PortfolioState.empty(), _OK, LiveExecutionAdapter(client=broker_n),
        live_config=LiveExecutionConfig(target_notional=500.0),
    )
    assert rec_n.status is ExecutionStatus.QUEUED
    assert pf_n.position(GLD) is None and len(pf_n.pending) == 1  # not folded yet; in-flight tracked

    # Between runs the order FILLS at the broker. Run N+1 (a later snapshot, still LONG): the startup
    # reconcile folds the now-filled order exactly once, then nets to NO_ACTION (no double-buy).
    filled = {"id": "ob", "client_order_id": coid, "symbol": GLD, "status": "filled",
              "filled_qty": "1", "filled_avg_price": "431.0"}
    broker_n1 = _Broker(
        account=_active(), asset={"symbol": GLD, "fractionable": False, "tradable": True},
        positions=[{"symbol": GLD, "qty": "1", "avg_entry_price": "431.0"}], orders=[filled], mark=430.0,
    )
    rec_n1, pf_n1 = reconcile_and_act(
        _admit("S2"), Direction.LONG, pf_n, _OK, LiveExecutionAdapter(client=broker_n1),
        live_config=LiveExecutionConfig(target_notional=500.0),
    )
    assert pf_n1.position(GLD) is not None and pf_n1.position(GLD).quantity == pytest.approx(1.0)
    assert len(pf_n1.executions) == 1 and pf_n1.executions[0].source_snapshot_id == "S1"  # booked w/ lineage
    assert pf_n1.pending == ()                       # the pending order was dropped after the fold
    assert rec_n1.status is ExecutionStatus.NO_ACTION and broker_n1.buy_calls == []  # double-submit prevented

    # Run N+2 — nothing left to fold (exactly once; never folded twice).
    broker_n2 = _Broker(
        account=_active(), positions=[{"symbol": GLD, "qty": "1", "avg_entry_price": "431.0"}],
        orders=[filled], mark=430.0,
    )
    _, pf_n2 = reconcile_and_act(
        _admit("S3"), Direction.LONG, pf_n1, _OK, LiveExecutionAdapter(client=broker_n2),
        live_config=LiveExecutionConfig(target_notional=500.0),
    )
    assert len(pf_n2.executions) == 1 and pf_n2.pending == ()


def test_cross_run_buy_fold_then_flat_sells_not_discrepancy() -> None:
    # The pre-fix bug: a cross-run fill made a later FLAT mis-flag the position as an unexplained
    # discrepancy. After the fold the local lineage is present, so FLAT SELLS (realizes P&L) instead.
    coid_buy = make_client_order_id("S1", "buy")
    pending = PendingOrder(
        source_snapshot_id="S1", source_record_id="rec-0", instrument=GLD, side="buy", requested_qty=1.0,
        client_order_id=coid_buy, seq=0, as_of="2026-05-01T20:00:00+00:00",
    )
    prior = PortfolioState(PORTFOLIO_SCHEMA_VERSION, (), (), (), (pending,))
    filled_buy = {"id": "ob", "client_order_id": coid_buy, "symbol": GLD, "status": "filled",
                  "filled_qty": "1", "filled_avg_price": "431.0"}
    coid_sell = make_client_order_id("S2", "sell")
    filled_sell = {"id": "os", "client_order_id": coid_sell, "symbol": GLD, "status": "filled",
                   "filled_qty": "1", "filled_avg_price": "450.0"}
    broker = _Broker(
        account=_active(), positions=[{"symbol": GLD, "qty": "1", "avg_entry_price": "431.0"}],
        orders=[filled_buy, filled_sell], mark=430.0,
    )
    rec, pf = reconcile_and_act(
        _admit("S2"), Direction.FLAT, prior, _OK, LiveExecutionAdapter(client=broker),
    )
    assert rec.status is ExecutionStatus.FILLED
    assert broker.sell_calls[0]["qty"] == pytest.approx(1.0)   # sold to close
    assert pf.position(GLD).quantity == 0.0
    assert pf.position(GLD).realized_pnl == pytest.approx(19.0)  # 1 * (450 - 431), realized by the sell-fold
    assert pf.reconciles == () and len(pf.executions) == 2       # NOT a discrepancy/heal


# ===================================================================== operate_live (end-to-end)

def _avoid_adapter() -> LiveExecutionAdapter:
    # On the AVOID corpus the broker is never contacted, so any client works; use one that fails if touched.
    class _NeverCalled:
        def _boom(self, *a, **k):
            raise AssertionError("AVOID corpus -> the broker must never be called")
        submit_market_buy = submit_market_sell = _boom
        get_positions = get_open_orders = get_orders = get_account = get_asset = get_latest_trade = _boom

    return LiveExecutionAdapter(client=_NeverCalled())


def test_operate_live_avoid_no_action_chain_advances(tmp_path: Path) -> None:
    live_ledger = tmp_path / "ledger.live.json"
    live_pf = tmp_path / "portfolio.live.json"
    result = operate_live(
        _REAL, live_ledger, live_pf, _avoid_adapter(), operational_capture_path=tmp_path / "op.live.json",
    )
    assert result is not None
    assert result.runtime_record.verdict is Verdict.ADMIT
    assert result.packet.direction is Direction.AVOID
    ex = result.execution_record
    assert ex is not None and ex.status is ExecutionStatus.NO_ACTION
    assert ex.execution_mode.value == "alpaca_paper" and ex.replayable is False
    assert ex.exec_ref_gld_price_basis == BASIS_LIVE_SUBMIT  # live submit-mark provenance
    assert len(result.ledger.entries) == 1  # the decision/observation chain advanced
    assert result.portfolio.executions == ()  # no fill, no reconcile
    assert live_ledger.exists() and live_pf.exists()


def test_operate_live_idempotent_second_run_rejects(tmp_path: Path) -> None:
    live_ledger = tmp_path / "ledger.live.json"
    live_pf = tmp_path / "portfolio.live.json"
    op = tmp_path / "op.live.json"
    first = operate_live(_REAL, live_ledger, live_pf, _avoid_adapter(), operational_capture_path=op)
    second = operate_live(_REAL, live_ledger, live_pf, _avoid_adapter(), operational_capture_path=op)
    assert first is not None and second is not None
    assert first.runtime_record.verdict is Verdict.ADMIT
    assert second.runtime_record.verdict is Verdict.REJECT  # duplicate_ok blocks the re-presentation
    assert second.runtime_record.triggered_guard == "duplicate_ok"
    assert second.execution_record is None


def test_operate_live_guard_block_refuses_but_chain_advances(tmp_path: Path) -> None:
    # A restrictive captured guard blocks the trade; execution refuses (no broker) but the ledger advances.
    block = GuardrailConfig(
        max_trade_size=0.5, max_trades_per_day=10, max_position_pct=1e-7,
        max_positions=5, daily_loss_cap=5_000.0, allow_withdrawals=False,
    )
    result = operate_live(
        _REAL, tmp_path / "l.json", tmp_path / "p.json", _avoid_adapter(),
        operational_capture_path=tmp_path / "op.json", guard_config=block,
    )
    assert result is not None and result.execution_record is not None
    assert result.execution_record.guard_result.approved is False
    assert result.execution_record.fill is None
    assert len(result.ledger.entries) == 1  # chain still advanced under the execution refusal
