"""TEST — side/order-based LIVE Alpaca paper adapter + order state machine (ADR-014 §6, stub-only).

Every broker is a stub implementing the full :class:`LiveBrokerPort`; NO network is ever touched. Covers:
the startup account-status gate, cash-capped + fractionable sizing, deterministic ``client_order_id``,
the submit state machine (QUEUED on accept; EXECUTION_UNCERTAIN on reject/timeout/429/auth; NO_ACTION on
a 422 duplicate), the typed-error path (4xx reject body parsed + persisted, never dropped), and
fill resolution from the broker ORDER read (never the synchronous POST echo).
"""

from __future__ import annotations

import io
from urllib.error import HTTPError, URLError

import pytest

from execution import ExecutionMode, ExecutionRecord, ExecutionStatus, GuardResult
from execution.alpaca_adapter import AlpacaExecutionError
from execution.live_adapter import (
    LiveExecutionAdapter,
    live_adapter_from_env,
    make_client_order_id,
)
from gold.decision_builder.models import Direction

GLD = "GLD"
_ACTIVE_ACCOUNT = {"status": "ACTIVE", "trading_blocked": False, "account_blocked": False, "cash": "10000"}


def _http_error(code: int, body: str, headers: dict[str, str] | None = None) -> HTTPError:
    return HTTPError(
        url="https://paper-api.alpaca.markets/v2/orders", code=code, msg="err",
        hdrs=headers or {}, fp=io.BytesIO(body.encode("utf-8")),
    )


class _StubBroker:
    """A full LiveBrokerPort stub — every method is canned; submit calls are counted (no network)."""

    def __init__(
        self, *, account=None, asset=None, positions=(), orders=(),
        buy_result=None, sell_result=None, error: Exception | None = None, latest_trade=None,
    ) -> None:
        self._account = account if account is not None else dict(_ACTIVE_ACCOUNT)
        self._asset = asset if asset is not None else {"symbol": GLD, "fractionable": True, "tradable": True}
        self._positions = list(positions)
        self._orders = list(orders)
        self._buy_result = buy_result
        self._sell_result = sell_result
        self._error = error
        self._latest_trade = (
            latest_trade if latest_trade is not None
            else {"symbol": GLD, "trade": {"p": "431.5", "t": "2026-05-01T20:00:00Z"}}
        )
        self.buy_calls = 0
        self.sell_calls = 0

    def submit_market_buy(self, symbol, *, qty=None, notional=None, client_order_id):
        self.buy_calls += 1
        if self._error is not None:
            raise self._error
        return self._buy_result

    def submit_market_sell(self, symbol, *, qty=None, notional=None, client_order_id):
        self.sell_calls += 1
        if self._error is not None:
            raise self._error
        return self._sell_result

    def get_positions(self):
        return self._positions

    def get_open_orders(self):
        return [o for o in self._orders if str(o.get("status", "")).lower() != "filled"]

    def get_orders(self):
        return self._orders

    def get_account(self):
        return self._account

    def get_asset(self, symbol):
        return self._asset

    def get_latest_trade(self, symbol):
        return self._latest_trade


# --- account-status gate ----------------------------------------------------------------------

def test_account_gate_passes_for_active_unblocked() -> None:
    adapter = LiveExecutionAdapter(client=_StubBroker())
    account = adapter.assert_account_tradeable()
    assert account["status"] == "ACTIVE"


@pytest.mark.parametrize("account", [
    {"status": "ONBOARDING", "trading_blocked": False, "account_blocked": False, "cash": "1"},
    {"status": "ACTIVE", "trading_blocked": True, "account_blocked": False, "cash": "1"},
    {"status": "ACTIVE", "trading_blocked": False, "account_blocked": True, "cash": "1"},
    {"status": "ACTIVE", "cash": "1"},  # missing flags -> fail-closed (treated as blocked)
])
def test_account_gate_refuses_blocked_or_malformed(account: dict) -> None:
    adapter = LiveExecutionAdapter(client=_StubBroker(account=account))
    with pytest.raises(AlpacaExecutionError, match="not tradeable"):
        adapter.assert_account_tradeable()


def test_settled_cash_reads_cash_field_never_buying_power() -> None:
    account = {"cash": "12345.67", "buying_power": "99999", "regt_buying_power": "99999"}
    assert LiveExecutionAdapter.settled_cash(account) == pytest.approx(12345.67)


def test_settled_cash_missing_field_fails_closed() -> None:
    with pytest.raises(AlpacaExecutionError, match="settled-cash"):
        LiveExecutionAdapter.settled_cash({"buying_power": "99999"})


# --- live submit mark: the REAL live GLD share mark, never the sim proxy (ADR-014 §5.1) -------

def test_live_submit_mark_reads_the_real_broker_mark() -> None:
    broker = _StubBroker(latest_trade={"symbol": GLD, "trade": {"p": "430.25", "t": "2026-05-01T20:00:00Z"}})
    ref = LiveExecutionAdapter(client=broker).live_submit_mark(GLD)
    assert ref.price == pytest.approx(430.25)          # the REAL mark, read live
    assert ref.basis == "live_submit_mark"             # pinned + labelled live submit provenance
    assert ref.ts == "2026-05-01T20:00:00Z"            # the mark's own pinned timestamp


def test_live_submit_mark_accepts_bare_trade_shape_and_falls_back_to_as_of() -> None:
    # A bare {"p": ..} payload (no wrapper, no ts) is accepted; ts falls back to the snapshot as_of.
    broker = _StubBroker(latest_trade={"p": 431.0})
    ref = LiveExecutionAdapter(client=broker).live_submit_mark(GLD, as_of="2026-05-01T13:00:00+00:00")
    assert ref.price == pytest.approx(431.0)
    assert ref.ts == "2026-05-01T13:00:00+00:00"


def test_live_submit_mark_missing_price_fails_closed() -> None:
    broker = _StubBroker(latest_trade={"symbol": GLD, "trade": {"t": "2026-05-01T20:00:00Z"}})
    with pytest.raises(AlpacaExecutionError, match="trade price"):
        LiveExecutionAdapter(client=broker).live_submit_mark(GLD)


def test_live_submit_mark_nonpositive_fails_closed() -> None:
    # A zero/negative mark must NEVER silently become a 0 reference (that fabricates a nonsense slippage).
    with pytest.raises(AlpacaExecutionError, match="non-positive"):
        LiveExecutionAdapter(client=_StubBroker(latest_trade={"trade": {"p": "0"}})).live_submit_mark(GLD)


def test_live_submit_mark_without_client_fails_closed() -> None:
    with pytest.raises(AlpacaExecutionError):
        LiveExecutionAdapter(client=None).live_submit_mark(GLD)


# --- sizing: cash-cap + fractionable ----------------------------------------------------------

def test_sizing_fractionable_uses_notional_capped_to_cash() -> None:
    adapter = LiveExecutionAdapter(client=_StubBroker())
    qty, notional = adapter.resolve_order_qty(5000.0, 1200.0, fractionable=True, mark=431.5)
    assert qty is None and notional == pytest.approx(1200.0)  # capped to settled cash, notional order


def test_sizing_non_fractionable_floors_integer_shares() -> None:
    adapter = LiveExecutionAdapter(client=_StubBroker())
    qty, notional = adapter.resolve_order_qty(5000.0, 1200.0, fractionable=False, mark=431.5)
    assert notional is None and qty == 2.0  # floor(1200 / 431.5) = 2


def test_sizing_nothing_affordable_returns_none() -> None:
    adapter = LiveExecutionAdapter(client=_StubBroker())
    assert adapter.resolve_order_qty(5000.0, 0.0, fractionable=True, mark=431.5) == (None, None)
    assert adapter.resolve_order_qty(5000.0, 100.0, fractionable=False, mark=431.5) == (None, None)


# --- deterministic client_order_id ------------------------------------------------------------

def test_client_order_id_is_deterministic_and_within_budget() -> None:
    a = make_client_order_id("952cc83a", "buy")
    b = make_client_order_id("952cc83a", "buy")
    assert a == b and len(a) <= 48 and a.startswith("eln-buy-")
    assert make_client_order_id("952cc83a", "sell") != a  # side-distinct


# --- submit state machine: accept -> QUEUED (never trusts the echo) ----------------------------

def test_submit_buy_queued_even_when_echo_says_filled() -> None:
    # The POST echo claims a fill; the adapter still returns QUEUED — the fill is resolved on reconcile.
    echo = {"id": "o1", "client_order_id": "c1", "status": "filled", "filled_qty": "1",
            "filled_avg_price": "431.5"}
    adapter = LiveExecutionAdapter(client=_StubBroker(buy_result=echo))
    out = adapter.submit_buy(GLD, "c1", qty=1.0)
    assert out.status is ExecutionStatus.QUEUED
    assert out.alpaca_order_id == "o1"
    assert out.filled_qty == 0.0  # NOT taken from the echo
    assert out.raw_payload is not None and out.halt is False


@pytest.mark.parametrize("accept_status", ["accepted", "pending_new", "new"])
def test_submit_buy_async_accept_is_queued(accept_status: str) -> None:
    echo = {"id": "o2", "status": accept_status}
    adapter = LiveExecutionAdapter(client=_StubBroker(buy_result=echo))
    assert adapter.submit_buy(GLD, "c1", qty=1.0).status is ExecutionStatus.QUEUED


def test_submit_terminal_reject_status_is_uncertain() -> None:
    echo = {"id": "o3", "status": "rejected"}
    out = LiveExecutionAdapter(client=_StubBroker(buy_result=echo)).submit_buy(GLD, "c1", qty=1.0)
    assert out.status is ExecutionStatus.EXECUTION_UNCERTAIN and out.halt is True


# --- typed error path: 4xx reject body parsed + persisted, never dropped -----------------------

def test_submit_4xx_reject_routes_uncertain_and_persists_body() -> None:
    body = '{"code":40310000,"message":"insufficient buying power"}'
    broker = _StubBroker(error=_http_error(403, body))
    out = LiveExecutionAdapter(client=broker).submit_buy(GLD, "c1", qty=1.0)
    assert out.status is ExecutionStatus.EXECUTION_UNCERTAIN
    assert out.halt is True
    assert out.raw_payload == body          # the reject body is persisted, not discarded
    assert broker.buy_calls == 1            # submitted once, never blind-resent


def test_submit_422_duplicate_client_order_id_is_no_action() -> None:
    body = '{"code":42210000,"message":"client_order_id must be unique"}'
    out = LiveExecutionAdapter(client=_StubBroker(error=_http_error(422, body))).submit_buy(GLD, "c1", qty=1.0)
    assert out.status is ExecutionStatus.NO_ACTION   # idempotent: the prior order stands
    assert out.halt is False
    assert out.raw_payload == body


def test_submit_422_wash_trade_is_uncertain_not_dedup() -> None:
    # A non-duplicate 422 (e.g. wash trade) must NOT be mistaken for an idempotent duplicate.
    body = '{"code":42210000,"message":"potential wash trade detected"}'
    out = LiveExecutionAdapter(client=_StubBroker(error=_http_error(422, body))).submit_buy(GLD, "c1", qty=1.0)
    assert out.status is ExecutionStatus.EXECUTION_UNCERTAIN and out.halt is True


def test_submit_429_honors_retry_after_without_resend() -> None:
    broker = _StubBroker(error=_http_error(429, "rate limited", headers={"Retry-After": "2"}))
    out = LiveExecutionAdapter(client=broker).submit_buy(GLD, "c1", qty=1.0)
    assert out.status is ExecutionStatus.EXECUTION_UNCERTAIN
    assert "Retry-After=2" in out.reason
    assert broker.buy_calls == 1  # NOT blind-resent


def test_submit_timeout_is_uncertain_and_not_resent() -> None:
    broker = _StubBroker(error=URLError("timed out"))
    out = LiveExecutionAdapter(client=broker).submit_buy(GLD, "c1", qty=1.0)
    assert out.status is ExecutionStatus.EXECUTION_UNCERTAIN and out.halt is True
    assert broker.buy_calls == 1


def test_submit_without_client_fails_closed() -> None:
    with pytest.raises(AlpacaExecutionError):
        LiveExecutionAdapter(client=None).submit_buy(GLD, "c1", qty=1.0)


# --- reconcile-resolve: fill from the ORDER read, never the echo -------------------------------

def test_resolve_fill_filled_from_order_read() -> None:
    orders = [{"id": "o1", "client_order_id": "c1", "status": "filled", "filled_qty": "1",
               "filled_avg_price": "431.55"}]
    out = LiveExecutionAdapter(client=_StubBroker(orders=orders)).resolve_fill("c1", 1.0)
    assert out.status is ExecutionStatus.FILLED
    assert out.filled_qty == 1.0 and out.filled_avg_price == pytest.approx(431.55)


def test_resolve_fill_partial() -> None:
    orders = [{"id": "o1", "client_order_id": "c1", "status": "partially_filled", "filled_qty": "0.4",
               "filled_avg_price": "431.5"}]
    out = LiveExecutionAdapter(client=_StubBroker(orders=orders)).resolve_fill("c1", 1.0)
    assert out.status is ExecutionStatus.PARTIAL and out.filled_qty == pytest.approx(0.4)


def test_resolve_fill_still_open_is_queued() -> None:
    orders = [{"id": "o1", "client_order_id": "c1", "status": "new", "filled_qty": "0"}]
    out = LiveExecutionAdapter(client=_StubBroker(orders=orders)).resolve_fill("c1", 1.0)
    assert out.status is ExecutionStatus.QUEUED


def test_resolve_fill_missing_order_is_uncertain() -> None:
    out = LiveExecutionAdapter(client=_StubBroker(orders=[])).resolve_fill("c1", 1.0)
    assert out.status is ExecutionStatus.EXECUTION_UNCERTAIN and out.halt is True


# --- SCHEMA-014: the live statuses + traceability are representable on the record --------------

def test_execution_record_carries_live_status_and_traceability() -> None:
    rec = ExecutionRecord(
        execution_id="exec-v0:x", execution_schema_version="0.1.0", source_record_id="r1",
        source_snapshot_id="S1", instrument=GLD, direction=Direction.LONG, size=1.0,
        instrument_price=431.5, fill=None, guard_result=GuardResult(True, None, "ok"),
        execution_mode=ExecutionMode.ALPACA_PAPER, replayable=False, fill_model_version="0.1.0",
        prior_portfolio_state_hash="p", new_portfolio_state_hash="n", reason="QUEUED",
        status=ExecutionStatus.QUEUED, client_order_id="eln-buy-abc", alpaca_order_id="o1",
        raw_payload='{"status":"accepted"}',
    )
    d = rec.to_dict()
    assert d["status"] == "queued"
    assert d["client_order_id"] == "eln-buy-abc"
    assert d["alpaca_order_id"] == "o1"
    assert d["raw_payload"] == '{"status":"accepted"}'


def test_sim_record_leaves_live_fields_none() -> None:
    # A default (sim) record has no live state-machine fields — keeps the deterministic records unchanged.
    rec = ExecutionRecord(
        execution_id="exec-v0:y", execution_schema_version="0.1.0", source_record_id="r1",
        source_snapshot_id="S1", instrument=GLD, direction=Direction.LONG, size=1.0,
        instrument_price=431.5, fill=None, guard_result=GuardResult(True, None, "ok"),
        execution_mode=ExecutionMode.SIMULATED, replayable=True, fill_model_version="0.1.0",
        prior_portfolio_state_hash="p", new_portfolio_state_hash="n", reason="filled",
    )
    d = rec.to_dict()
    assert d["status"] is None and d["client_order_id"] is None and d["raw_payload"] is None


# --- factory: fail-closed + paper-only boundary (inherited) ------------------------------------

def test_live_adapter_from_env_fail_closed_without_creds(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ALPACA_API_KEY_ID", raising=False)
    monkeypatch.delenv("ALPACA_API_SECRET_KEY", raising=False)
    assert live_adapter_from_env().client is None


def test_live_adapter_from_env_refuses_non_paper_host(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALPACA_API_KEY_ID", "k")
    monkeypatch.setenv("ALPACA_API_SECRET_KEY", "s")
    monkeypatch.setenv("ALPACA_PAPER_BASE_URL", "https://api.alpaca.markets")  # LIVE host -> refuse
    assert live_adapter_from_env().client is None
    assert LiveExecutionAdapter().replayable is False  # never on the replay path
