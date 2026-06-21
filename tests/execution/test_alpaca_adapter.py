"""TEST-028 — live Alpaca **paper** ExecutionPort plug (MOD-008 / INT-011, ADR-011 gate f).

Covers: the fill echo (a stub paper order maps to a ``Fill``); the determinism-boundary flags
(``mode == ALPACA_PAPER``, ``replayable is False``); fail-closed on a missing client / non-LONG
direction / non-filled order; the ``from_env`` factory fail-closing on missing creds and **refusing a
non-paper base URL**; and the **quarantine** — through the pure ``execute`` engine the adapter stamps
``replayable=False`` onto the record, and a no-fill path never touches the broker, while the default
port stays the deterministic ``SimulatedBrokerAdapter``. NO real network: every broker is a stub.
"""

from __future__ import annotations

import pytest

from gold.decision_builder.models import DecisionMode, Direction
from gold.paper_runtime.models import RuntimeDecisionRecord, Verdict
from execution import ExecutionMode, GuardResult, PortfolioState, SimulatedBrokerAdapter, execute
from execution.alpaca_adapter import (
    AlpacaExecutionError,
    AlpacaPaperAdapter,
    PaperOrderResult,
    paper_adapter_from_env,
)

PRICE = 2000.0


class _StubBroker:
    """A stand-in Alpaca paper broker: returns a queued order result, counting submissions."""

    def __init__(self, result: PaperOrderResult) -> None:
        self._result = result
        self.calls = 0

    def submit_market_buy(self, symbol: str, qty: float) -> PaperOrderResult:
        self.calls += 1
        return self._result


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


def _approved() -> GuardResult:
    return GuardResult(approved=True, blocked_by=None, reason="all guardrails passed")


def _blocked(predicate: str = "position_size_ok") -> GuardResult:
    return GuardResult(approved=False, blocked_by=predicate, reason="blocked")


def _filled(price: float = 2002.0, qty: float = 1.0) -> _StubBroker:
    return _StubBroker(PaperOrderResult(filled_avg_price=price, filled_qty=qty, status="filled"))


# --- fill echo + determinism-boundary flags ---------------------------------------------------

def test_fill_echoes_paper_order() -> None:
    adapter = AlpacaPaperAdapter(client=_filled(price=2002.0, qty=1.0))
    from execution import DEFAULT_FILL_MODEL
    fill = adapter.fill("GLD", Direction.LONG, 1.0, PRICE, DEFAULT_FILL_MODEL)
    assert fill.fill_price == pytest.approx(2002.0)
    assert fill.quantity == pytest.approx(1.0)
    # realized slippage vs the 2000 mark = (2002-2000)/2000 * 1e4 = 10 bps
    assert fill.slippage_bps == pytest.approx(10.0)


def test_mode_and_replayable_flags() -> None:
    adapter = AlpacaPaperAdapter(client=_filled())
    assert adapter.mode is ExecutionMode.ALPACA_PAPER
    assert adapter.replayable is False


# --- fail-closed ------------------------------------------------------------------------------

def test_fill_without_client_raises() -> None:
    from execution import DEFAULT_FILL_MODEL
    adapter = AlpacaPaperAdapter(client=None)
    with pytest.raises(AlpacaExecutionError):
        adapter.fill("GLD", Direction.LONG, 1.0, PRICE, DEFAULT_FILL_MODEL)


@pytest.mark.parametrize("direction", [Direction.FLAT, Direction.AVOID, Direction.WATCH])
def test_fill_rejects_non_long(direction: Direction) -> None:
    from execution import DEFAULT_FILL_MODEL
    broker = _filled()
    adapter = AlpacaPaperAdapter(client=broker)
    with pytest.raises(AlpacaExecutionError):
        adapter.fill("GLD", direction, 1.0, PRICE, DEFAULT_FILL_MODEL)
    assert broker.calls == 0  # never placed an order for a non-LONG stance


def test_fill_raises_on_unfilled_order() -> None:
    from execution import DEFAULT_FILL_MODEL
    broker = _StubBroker(PaperOrderResult(filled_avg_price=0.0, filled_qty=0.0, status="rejected"))
    adapter = AlpacaPaperAdapter(client=broker)
    with pytest.raises(AlpacaExecutionError):
        adapter.fill("GLD", Direction.LONG, 1.0, PRICE, DEFAULT_FILL_MODEL)


# --- from_env factory: fail-closed + paper-only refusal --------------------------------------

def test_from_env_without_creds_is_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    from execution import DEFAULT_FILL_MODEL
    monkeypatch.delenv("ALPACA_API_KEY_ID", raising=False)
    monkeypatch.delenv("ALPACA_API_SECRET_KEY", raising=False)
    adapter = paper_adapter_from_env()
    assert adapter.client is None
    with pytest.raises(AlpacaExecutionError):  # no creds ⇒ fill fails closed, no network
        adapter.fill("GLD", Direction.LONG, 1.0, PRICE, DEFAULT_FILL_MODEL)


def test_from_env_refuses_non_paper_base_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALPACA_API_KEY_ID", "dummy-key")
    monkeypatch.setenv("ALPACA_API_SECRET_KEY", "dummy-secret")
    monkeypatch.setenv("ALPACA_PAPER_BASE_URL", "https://api.alpaca.markets")  # LIVE host — must refuse
    assert paper_adapter_from_env().client is None  # paper-only invariant at the credential boundary


@pytest.mark.parametrize("spoof", [
    "https://paper-api.alpaca.markets.evil.com",              # super-domain
    "https://evil.paper-api.alpaca.markets",                  # sub-domain
    "https://attacker.com?target=paper-api.alpaca.markets",   # host only in the query
    "https://attacker.com#paper-api.alpaca.markets",          # host only in the fragment
    "http://paper-api.alpaca.markets",                        # non-https — creds must never go cleartext
])
def test_from_env_refuses_spoofed_base_urls(monkeypatch: pytest.MonkeyPatch, spoof: str) -> None:
    # The boundary is a parsed-hostname equality check, NOT a substring match — no spoof slips through.
    monkeypatch.setenv("ALPACA_API_KEY_ID", "dummy-key")
    monkeypatch.setenv("ALPACA_API_SECRET_KEY", "dummy-secret")
    monkeypatch.setenv("ALPACA_PAPER_BASE_URL", spoof)
    assert paper_adapter_from_env().client is None


def test_from_env_accepts_mixed_case_paper_host(monkeypatch: pytest.MonkeyPatch) -> None:
    # DNS/HTTP hostnames are case-insensitive; a mixed-case paper host is the real endpoint (no network).
    monkeypatch.setenv("ALPACA_API_KEY_ID", "dummy-key")
    monkeypatch.setenv("ALPACA_API_SECRET_KEY", "dummy-secret")
    monkeypatch.setenv("ALPACA_PAPER_BASE_URL", "https://PAPER-API.ALPACA.MARKETS")
    assert paper_adapter_from_env().client is not None


def test_from_env_with_paper_creds_builds_a_client_no_network(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALPACA_API_KEY_ID", "dummy-key")
    monkeypatch.setenv("ALPACA_API_SECRET_KEY", "dummy-secret")
    monkeypatch.delenv("ALPACA_PAPER_BASE_URL", raising=False)
    adapter = paper_adapter_from_env()
    assert adapter.client is not None  # constructed but never invoked here (no network)
    assert adapter.replayable is False


# --- the quarantine: through the pure engine, stamped non-replayable; default stays simulated --

def test_execute_with_alpaca_port_stamps_non_replayable() -> None:
    broker = _filled(price=2002.0, qty=1.0)
    rec, pf = execute(_admit(), Direction.LONG, PRICE, PortfolioState.empty(), _approved(),
                      port=AlpacaPaperAdapter(client=broker))
    assert rec.fill is not None
    assert rec.execution_mode is ExecutionMode.ALPACA_PAPER
    assert rec.replayable is False           # off the deterministic replay / benchmark path
    assert rec.paper_only is True
    assert broker.calls == 1


def test_no_fill_path_never_touches_the_broker() -> None:
    # A blocked guard yields a no-fill record — the live broker must NOT be called, but the record
    # still carries the adapter's non-replayable boundary flags.
    broker = _filled()
    rec, _ = execute(_admit(), Direction.LONG, PRICE, PortfolioState.empty(), _blocked(),
                     port=AlpacaPaperAdapter(client=broker))
    assert rec.fill is None
    assert broker.calls == 0
    assert rec.execution_mode is ExecutionMode.ALPACA_PAPER
    assert rec.replayable is False


def test_default_port_is_the_deterministic_simulator() -> None:
    # The canonical core path is unchanged: the simulator is replay-safe and remains the default.
    assert SimulatedBrokerAdapter().replayable is True
    assert SimulatedBrokerAdapter().mode is ExecutionMode.SIMULATED
    # And the Alpaca adapter is the explicit, non-replayable opt-in — never a default.
    assert AlpacaPaperAdapter().replayable is False
