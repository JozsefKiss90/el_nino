"""Side/order-based LIVE Alpaca **paper** adapter + order state machine (ADR-014 §6, bucket ii).

The broker-realistic live plug. It **supersedes** the v0 LONG-only ``AlpacaPaperAdapter.fill`` on the
live path (it does not extend it): the live path is reconcile-driven (LONG→buy, FLAT→sell), so this
adapter is **side/order-based** — ``submit_buy`` / ``submit_sell`` — and resolves fills from the broker's
**positions + orders reads**, never from the synchronous POST echo. It depends on a widened
:class:`LiveBrokerPort` (buy/sell + positions/open-orders/orders/account/asset + the latest-trade market
read); every test injects a stub for the whole surface — **never the network**.

**Live execution reference (ADR-014 §5.1).** :meth:`LiveExecutionAdapter.live_submit_mark` reads the
**real live GLD share mark** (``get_latest_trade``, a read-only market-data host) and pins it as the
submit-time reference, so recorded slippage is fill-vs-real-mark — **not** the sim derived proxy
(``gold_price_proxy × OZ_PER_SHARE``), which is the "plausible-but-wrong slippage" defect §5.1 removes. ``replayable = False`` keeps it quarantined off the
deterministic replay/benchmark path (the ``run_once`` / ``run_sequence`` ``assert port.replayable`` fence).

**State machine** (ADR-014 §6): a market + ``time_in_force=day`` order →

* ``accepted`` / ``pending_new`` / ``new`` (any non-reject accept) ⇒ **QUEUED** — *not* an error, *not*
  resent; the fill is resolved on the next reconcile (this fixes the v0 sync-fill raise);
* on reconcile, ``filled_qty >= requested`` ⇒ **FILLED**, ``0 < filled_qty < requested`` ⇒ **PARTIAL**,
  still-open ⇒ **QUEUED** — all read from the broker order/positions, never the echo;
* a broker reject (4xx/5xx), a 429 (honoured via ``Retry-After``, **no blind resend**), an auth error,
  or a timeout / no-response ⇒ **EXECUTION_UNCERTAIN** (the caller halts that instrument, no blind retry);
* a 422 duplicate ``client_order_id`` ⇒ **NO_ACTION** (idempotent — the prior order stands, no second
  order created).

The raw broker response / reject body is **always** captured (``raw_payload``) — no reject is silently
dropped. Sizing is **cash-capped against the literal settled-cash field** (never any ``*_buying_power``)
and honours GLD ``fractionable`` (true → notional order; false → integer shares). Paper-only / KA-008
credential isolation are inherited from :mod:`execution.alpaca_adapter` (same parsed-host guard).
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import urllib.request
from dataclasses import dataclass
from typing import Any, Mapping, Protocol, Sequence, cast
from urllib.error import HTTPError, URLError

from .alpaca_adapter import (
    AlpacaExecutionError,
    _DEFAULT_BASE_URL,
    _HTTP_TIMEOUT_S,
    _is_paper_base_url,
)
from .models import ExecutionMode, ExecutionStatus
from .price_reference import BASIS_LIVE_SUBMIT, ExecPriceRef

# --- empirical-precondition constants (close B1/B3 before any live run; documented assumptions) -----

# B1: deterministic ``client_order_id`` (same lineage ⇒ same id) so a duplicate submit is broker-deduped
# and a retry never double-orders. NOTE (doc-verified 2026-06-25, Alpaca POST /v2/orders reference): the
# REST limit is **128 chars** — the 48 here is a *self-imposed conservative cap* (the 48 figure is the
# FIX-protocol ClOrdID limit, a different interface), well within the REST max, so it needs no change. The
# charset is undocumented; the ASCII ``eln-<side>-<hex>`` alphabet is a safe subset. The duplicate ⇒ HTTP
# 422 ("client_order_id must be unique") dedup is the commonly-observed behaviour but is NOT in the docs —
# the operator probe (scripts/alpaca_paper_e2e_probe.py) confirms the exact 422 status/body before it is relied on.
_COID_PREFIX = "eln"
_COID_MAXLEN = 48

# B3: the literal cash-balance field on the account read. NEVER any ``*_buying_power`` (every one is a
# derived/margin-inflated figure — even ``buying_power == cash`` only when ``multiplier == 1``), so "no
# margin" is structural on any account type. Doc-verified 2026-06-25 (Alpaca GET /v2/account): ``cash`` is
# the "Cash Balance" field and ``multiplier`` distinguishes cash (1) vs margin (2/4) — both confirmed. The
# docs label it "Cash Balance" (not literally "settled"); the operator probe confirms cash-vs-settlement
# behaviour + ``multiplier == "1"`` on the paper account.
_SETTLED_CASH_FIELD = "cash"

# Live market-data read for the REAL GLD share mark (ADR-014 §5.1 — the live execution reference). The
# market-data host is a SEPARATE, READ-ONLY host (no order path) — orders still go ONLY to the paper
# trading host behind ``_is_paper_base_url``; this is a price *read*, never a credential-exfil order
# surface, so it is not subject to (and must never be confused with) the paper-host order guard. Field
# names CONFIRMED against the Alpaca Market Data OpenAPI spec (doc-verified 2026-06-25): the latest-trade
# payload at ``data.alpaca.markets/v2/stocks/{sym}/trades/latest`` carries the price under ``trade.p`` and
# an RFC-3339 timestamp under ``trade.t`` (free IEX feed; paper keys valid). The operator probe is an
# optional liveness sanity check on the real account.
_DEFAULT_DATA_BASE_URL = "https://data.alpaca.markets"
_MARK_PRICE_FIELD = "p"
_MARK_TS_FIELD = "t"

_EPS = 1e-9

# Alpaca order ``status`` vocabulary. A non-reject accept is QUEUED; rejects/cancels are uncertain.
_ACCEPTED_STATUSES = frozenset(
    {"accepted", "pending_new", "new", "accepted_for_bidding", "calculated", "held",
     "partially_filled", "filled", "done_for_day", "pending_replace", "replaced"}
)
_FILLED_STATUSES = frozenset({"filled"})
_OPEN_STATUSES = frozenset(
    {"accepted", "pending_new", "new", "accepted_for_bidding", "calculated", "held", "pending_replace"}
)
_REJECT_STATUSES = frozenset({"rejected", "canceled", "cancelled", "expired", "suspended", "stopped"})


# --- the widened broker port (the primary live seam) ---------------------------------------------


class LiveBrokerPort(Protocol):
    """The full broker surface the reconcile loop + state machine need (tests inject a stub for all of it).

    Methods may raise :class:`urllib.error.HTTPError` / :class:`urllib.error.URLError` — the adapter
    catches and classifies them (it never lets a raw broker error propagate as a fill).
    """

    def submit_market_buy(
        self, symbol: str, *, qty: float | None = None, notional: float | None = None,
        client_order_id: str,
    ) -> Mapping[str, Any]:
        """Submit a market BUY (``time_in_force=day``); return the raw order payload."""
        ...

    def submit_market_sell(
        self, symbol: str, *, qty: float | None = None, notional: float | None = None,
        client_order_id: str,
    ) -> Mapping[str, Any]:
        """Submit a market SELL (``time_in_force=day``); return the raw order payload."""
        ...

    def get_positions(self) -> Sequence[Mapping[str, Any]]:
        """All open broker positions (the authority for position truth)."""
        ...

    def get_open_orders(self) -> Sequence[Mapping[str, Any]]:
        """Currently open (un-filled / partially-filled) orders."""
        ...

    def get_orders(self) -> Sequence[Mapping[str, Any]]:
        """Recent orders (open + closed) — used to resolve a queued order's fill on reconcile."""
        ...

    def get_account(self) -> Mapping[str, Any]:
        """The account read (status / blocked flags / settled cash)."""
        ...

    def get_asset(self, symbol: str) -> Mapping[str, Any]:
        """The asset read (``fractionable`` / ``tradable``)."""
        ...

    def get_latest_trade(self, symbol: str) -> Mapping[str, Any]:
        """The latest market-data **trade** for ``symbol`` — the real live GLD share mark (ADR-014 §5.1).

        Read-only market data (a separate host); never an order path. Used as the submit-time execution
        reference so live slippage is recorded fill-vs-**real-mark** (not against the sim derived proxy).
        """
        ...


# --- the outcome of one live order interaction ---------------------------------------------------


@dataclass(frozen=True)
class LiveOrderOutcome:
    """The classified result of a submit or a reconcile-resolve (maps onto SCHEMA-014 fields).

    ``status`` drives the live state machine; ``raw_payload`` is the captured broker body (never
    dropped). ``halt`` marks an EXECUTION_UNCERTAIN result that must halt the instrument (no blind
    retry) — the orchestration (operate_live) honours it.
    """

    status: ExecutionStatus
    reason: str
    client_order_id: str | None = None
    alpaca_order_id: str | None = None
    filled_qty: float = 0.0
    filled_avg_price: float = 0.0
    raw_payload: str | None = None
    halt: bool = False


# --- helpers -------------------------------------------------------------------------------------


def make_client_order_id(snapshot_id: str, side: str, seq: int = 0) -> str:
    """A deterministic ``client_order_id`` (same lineage ⇒ same id ⇒ broker 422 dedup on retry).

    ``eln-<side>-<32 hex of sha256(snapshot_id|side|seq)>`` truncated to the B1 length budget. Side is
    folded in so a buy and a sell of the same snapshot never collide; ``seq`` allows >1 order per lineage.
    """
    digest = hashlib.sha256(f"{snapshot_id}|{side}|{seq}".encode("utf-8")).hexdigest()[:32]
    return f"{_COID_PREFIX}-{side}-{digest}"[:_COID_MAXLEN]


def _http_error_parts(exc: HTTPError) -> tuple[int | None, str]:
    """``(status_code, body_text)`` from an HTTPError — the reject body is parsed, never discarded."""
    code = getattr(exc, "code", None)
    try:
        raw = exc.read()
        body = raw.decode("utf-8", "replace") if isinstance(raw, (bytes, bytearray)) else str(raw)
    except Exception:  # noqa: BLE001 — a body we cannot read still must not crash the classifier
        body = str(exc)
    return code, body


def _retry_after(exc: HTTPError) -> str | None:
    headers = getattr(exc, "headers", None)
    return headers.get("Retry-After") if headers is not None else None


def _is_duplicate_client_order_id(body: str) -> bool:
    """True iff a 422 body indicates a duplicate ``client_order_id`` (vs wash/insufficient-BP/etc.)."""
    low = body.lower()
    return "client_order_id" in low and ("exist" in low or "duplicate" in low or "unique" in low)


def _extract_mark(payload: Mapping[str, Any]) -> tuple[float, str | None]:
    """``(price, ts)`` from a latest-trade payload — the real live GLD mark (ADR-014 §5.1).

    Accepts either the wrapped Alpaca shape ``{"trade": {"p": .., "t": ..}}`` or a bare ``{"p": .., "t":
    ..}``. Fail-closed: a missing / non-positive price raises (a bad mark must never silently become a 0
    reference that fabricates a nonsense slippage — the very defect §5.1 removes).
    """
    trade = payload.get("trade", payload) if isinstance(payload, Mapping) else {}
    if not isinstance(trade, Mapping) or _MARK_PRICE_FIELD not in trade:
        raise AlpacaExecutionError(
            f"market-data read missing trade price field {_MARK_PRICE_FIELD!r} (refusing to mark)"
        )
    price = float(trade[_MARK_PRICE_FIELD])
    if price <= 0:
        raise AlpacaExecutionError(f"non-positive live GLD mark ({price}) — refusing to mark")
    ts = trade.get(_MARK_TS_FIELD)
    return price, (str(ts) if ts is not None else None)


# --- the live adapter ----------------------------------------------------------------------------


@dataclass(frozen=True)
class LiveExecutionAdapter:
    """Side/order-based live Alpaca paper adapter (non-replayable, default-OFF; see module docstring).

    ``client=None`` (the fail-closed default) makes every broker interaction raise
    :class:`AlpacaExecutionError`. Construct via :func:`live_adapter_from_env` for the real plug, or
    inject a stub ``client`` in tests.
    """

    client: LiveBrokerPort | None = None
    mode: ExecutionMode = ExecutionMode.ALPACA_PAPER
    replayable: bool = False

    def _require_client(self) -> LiveBrokerPort:
        if self.client is None:
            raise AlpacaExecutionError(
                "fail-closed: no Alpaca paper client (missing or non-paper credentials)"
            )
        return self.client

    # --- startup gate -----------------------------------------------------------------------------

    def assert_account_tradeable(self) -> Mapping[str, Any]:
        """Startup account-status gate: refuse to trade unless ACTIVE and not blocked (fail-closed).

        Returns the account read so the caller can size against settled cash without a second call.
        """
        account = self._require_client().get_account()
        status = str(account.get("status", ""))
        # Missing flags default to BLOCKED (fail-closed): a malformed account read never enables trading.
        trading_blocked = bool(account.get("trading_blocked", True))
        account_blocked = bool(account.get("account_blocked", True))
        if not (status == "ACTIVE" and not trading_blocked and not account_blocked):
            raise AlpacaExecutionError(
                f"account not tradeable (status={status!r}, trading_blocked={trading_blocked}, "
                f"account_blocked={account_blocked})"
            )
        return account

    @staticmethod
    def settled_cash(account: Mapping[str, Any]) -> float:
        """The literal settled-cash field from the account read (never any ``*_buying_power``).

        Fail-closed: a missing settled-cash field raises rather than silently sizing against 0 or margin.
        """
        if _SETTLED_CASH_FIELD not in account:
            raise AlpacaExecutionError(
                f"account read missing settled-cash field {_SETTLED_CASH_FIELD!r} (refusing to size)"
            )
        return float(account[_SETTLED_CASH_FIELD])

    # --- live execution reference (the REAL GLD mark, ADR-014 §5.1) --------------------------------

    def live_submit_mark(self, symbol: str, *, as_of: str | None = None) -> ExecPriceRef:
        """Read the **real live GLD mark** and pin it as the live submit-time execution reference.

        This is the Q2/§5.1 correctness gate: the live path marks + slips against the broker's real GLD
        **share** price (read live, non-replayable), **never** the sim derived proxy (``gold_price_proxy ×
        OZ_PER_SHARE``) — so the recorded ``slippage_bps`` is fill-vs-real-mark (true execution slippage),
        not fill-vs-proxy (the "plausible-but-wrong slippage" defect). Returns an :class:`ExecPriceRef`
        with ``basis = BASIS_LIVE_SUBMIT`` (the intraday/EOD submit mark) and the mark's own pinned
        timestamp (falling back to the snapshot ``as_of``). Fail-closed: no client / an unreadable or
        non-positive mark raises :class:`AlpacaExecutionError` (the caller refuses execution — it never
        falls back to the proxy on the live path).
        """
        payload = self._require_client().get_latest_trade(symbol)
        price, ts = _extract_mark(payload)
        return ExecPriceRef(price=price, ts=ts or as_of, basis=BASIS_LIVE_SUBMIT)

    # --- sizing -----------------------------------------------------------------------------------

    def resolve_order_qty(
        self, target_notional: float, settled_cash: float, *, fractionable: bool, mark: float,
    ) -> tuple[float | None, float | None]:
        """Cash-capped, fractionability-aware sizing → ``(qty, notional)`` (exactly one set, or both None).

        Effective target = ``min(target_notional, settled_cash)`` (never exceeds available cash, and the
        cash bound is the literal settled-cash field). ``fractionable`` → a notional market order; else →
        integer shares = ``floor(capped / mark)``. Returns ``(None, None)`` when nothing is affordable.
        """
        capped = min(target_notional, settled_cash)
        if capped <= 0:
            return (None, None)
        if fractionable:
            return (None, round(capped, 2))  # notional market order (cents precision)
        if mark <= 0:
            raise AlpacaExecutionError("cannot size integer shares against a non-positive mark")
        qty = math.floor(capped / mark)
        if qty <= 0:
            return (None, None)  # one share unaffordable
        return (float(qty), None)

    # --- submit (state machine on the accept response + typed errors) -----------------------------

    def submit_buy(
        self, symbol: str, client_order_id: str, *, qty: float | None = None,
        notional: float | None = None,
    ) -> LiveOrderOutcome:
        """Submit a market BUY; classify the response into the live state machine (never trusts the echo)."""
        return self._submit("buy", symbol, client_order_id, qty=qty, notional=notional)

    def submit_sell(
        self, symbol: str, client_order_id: str, *, qty: float | None = None,
        notional: float | None = None,
    ) -> LiveOrderOutcome:
        """Submit a market SELL; classify the response into the live state machine (never trusts the echo)."""
        return self._submit("sell", symbol, client_order_id, qty=qty, notional=notional)

    def _submit(
        self, side: str, symbol: str, client_order_id: str, *, qty: float | None,
        notional: float | None,
    ) -> LiveOrderOutcome:
        client = self._require_client()
        submit = client.submit_market_buy if side == "buy" else client.submit_market_sell
        try:
            order = submit(symbol, qty=qty, notional=notional, client_order_id=client_order_id)
        except HTTPError as exc:
            return self._classify_http_error(exc, client_order_id)
        except URLError as exc:  # timeout / connection failure / no response — execution UNCERTAIN
            return LiveOrderOutcome(
                status=ExecutionStatus.EXECUTION_UNCERTAIN,
                reason=f"no broker response ({getattr(exc, 'reason', exc)}); execution uncertain — "
                       "halt, no blind retry",
                client_order_id=client_order_id,
                raw_payload=str(exc),
                halt=True,
            )
        # Accepted (any non-reject status): QUEUED. The fill is resolved on the NEXT reconcile from the
        # broker positions/orders — never from this synchronous POST echo (ADR-014 §6).
        status_str = str(order.get("status", "")).lower()
        alpaca_order_id = str(order["id"]) if order.get("id") is not None else None
        raw = json.dumps(dict(order), sort_keys=True)
        if status_str in _REJECT_STATUSES:
            return LiveOrderOutcome(
                status=ExecutionStatus.EXECUTION_UNCERTAIN,
                reason=f"order returned terminal status {status_str!r} on submit — halt, no retry",
                client_order_id=client_order_id, alpaca_order_id=alpaca_order_id, raw_payload=raw,
                halt=True,
            )
        if status_str not in _ACCEPTED_STATUSES:
            return LiveOrderOutcome(
                status=ExecutionStatus.EXECUTION_UNCERTAIN,
                reason=f"unrecognized order status {status_str!r} on submit — halt, no retry",
                client_order_id=client_order_id, alpaca_order_id=alpaca_order_id, raw_payload=raw,
                halt=True,
            )
        return LiveOrderOutcome(
            status=ExecutionStatus.QUEUED,
            reason=f"order accepted ({status_str}) — QUEUED; fill resolved on next reconcile",
            client_order_id=client_order_id, alpaca_order_id=alpaca_order_id, raw_payload=raw,
        )

    def _classify_http_error(self, exc: HTTPError, client_order_id: str) -> LiveOrderOutcome:
        code, body = _http_error_parts(exc)
        if code == 429:  # rate-limited: honour Retry-After, NEVER blind-resend
            ra = _retry_after(exc)
            return LiveOrderOutcome(
                status=ExecutionStatus.EXECUTION_UNCERTAIN,
                reason=f"429 rate-limited (Retry-After={ra}); not resent — halt, retry next cycle",
                client_order_id=client_order_id, raw_payload=body, halt=True,
            )
        if code == 422 and _is_duplicate_client_order_id(body):  # idempotent duplicate submit
            return LiveOrderOutcome(
                status=ExecutionStatus.NO_ACTION,
                reason="duplicate client_order_id (422) — idempotent; the prior order stands, none created",
                client_order_id=client_order_id, raw_payload=body,
            )
        kind = "auth error" if code in (401, 403) else "broker reject"
        return LiveOrderOutcome(  # every other 4xx/5xx: route to EXECUTION_UNCERTAIN + halt, persist body
            status=ExecutionStatus.EXECUTION_UNCERTAIN,
            reason=f"{kind} (HTTP {code}) — halt, no blind retry; reject body persisted",
            client_order_id=client_order_id, raw_payload=body, halt=True,
        )

    # --- reconcile-resolve (fill from positions/orders, never the POST echo) -----------------------

    def resolve_fill(self, client_order_id: str, requested_qty: float) -> LiveOrderOutcome:
        """Resolve a queued order's fill from the broker ORDER read (authority), not the submit echo.

        ``filled_qty >= requested`` ⇒ FILLED; ``0 < filled_qty < requested`` ⇒ PARTIAL (next reconcile
        corrects); still-open / unfilled ⇒ QUEUED; order absent or unreadable ⇒ EXECUTION_UNCERTAIN.
        """
        client = self._require_client()
        try:
            orders = client.get_orders()
        except (HTTPError, URLError) as exc:
            body = _http_error_parts(exc)[1] if isinstance(exc, HTTPError) else str(exc)
            return LiveOrderOutcome(
                status=ExecutionStatus.EXECUTION_UNCERTAIN,
                reason="could not read orders to resolve fill — uncertain, halt",
                client_order_id=client_order_id, raw_payload=body, halt=True,
            )
        order = next(
            (o for o in orders if str(o.get("client_order_id")) == client_order_id), None
        )
        if order is None:
            return LiveOrderOutcome(
                status=ExecutionStatus.EXECUTION_UNCERTAIN,
                reason=f"order {client_order_id!r} not found on reconcile — uncertain, halt",
                client_order_id=client_order_id, halt=True,
            )
        status_str = str(order.get("status", "")).lower()
        filled_qty = float(order.get("filled_qty") or 0.0)
        filled_avg = float(order.get("filled_avg_price") or 0.0)
        alpaca_order_id = str(order["id"]) if order.get("id") is not None else None
        raw = json.dumps(dict(order), sort_keys=True)
        if status_str in _FILLED_STATUSES and filled_qty >= requested_qty - _EPS:
            status = ExecutionStatus.FILLED
            reason = "order filled (resolved from broker order read)"
        elif 0.0 < filled_qty < requested_qty:
            status = ExecutionStatus.PARTIAL
            reason = f"partial fill {filled_qty}/{requested_qty} — corrected on next reconcile"
        elif status_str in _OPEN_STATUSES or filled_qty <= _EPS:
            status = ExecutionStatus.QUEUED
            reason = f"order still open ({status_str}) — QUEUED, fill not yet resolved"
        else:
            status = ExecutionStatus.EXECUTION_UNCERTAIN
            reason = f"unresolved order status {status_str!r} on reconcile — uncertain, halt"
        return LiveOrderOutcome(
            status=status, reason=reason, client_order_id=client_order_id,
            alpaca_order_id=alpaca_order_id, filled_qty=filled_qty, filled_avg_price=filled_avg,
            raw_payload=raw, halt=(status is ExecutionStatus.EXECUTION_UNCERTAIN),
        )


# --- real stdlib REST broker (built only by the factory; never exercised by tests) ---------------


class _AlpacaRestLiveBroker:
    """stdlib-only Alpaca PAPER broker implementing the full :class:`LiveBrokerPort` (no third-party SDK)."""

    def __init__(
        self, key_id: str, secret_key: str, base_url: str,
        data_base_url: str = _DEFAULT_DATA_BASE_URL,
    ) -> None:
        self._key_id = key_id
        self._secret_key = secret_key
        self._base_url = base_url.rstrip("/")
        # The market-data host (a separate, READ-ONLY host — never the order path).
        self._data_base_url = data_base_url.rstrip("/")

    def _headers(self) -> dict[str, str]:
        return {
            "APCA-API-KEY-ID": self._key_id,
            "APCA-API-SECRET-KEY": self._secret_key,
            "content-type": "application/json",
            "accept": "application/json",
        }

    def _get(self, path: str) -> Any:
        return self._get_from(self._base_url, path)

    def _get_from(self, base: str, path: str) -> Any:
        request = urllib.request.Request(
            f"{base}{path}", headers=self._headers(), method="GET"
        )
        with urllib.request.urlopen(request, timeout=_HTTP_TIMEOUT_S) as response:
            return json.loads(response.read().decode("utf-8"))

    def _submit(
        self, symbol: str, side: str, qty: float | None, notional: float | None, client_order_id: str,
    ) -> Mapping[str, Any]:
        payload: dict[str, Any] = {
            "symbol": symbol, "side": side, "type": "market", "time_in_force": "day",
            "client_order_id": client_order_id,
        }
        if notional is not None:
            payload["notional"] = round(notional, 2)
        else:
            payload["qty"] = qty
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self._base_url}/v2/orders", data=body, headers=self._headers(), method="POST"
        )
        with urllib.request.urlopen(request, timeout=_HTTP_TIMEOUT_S) as response:
            return cast("Mapping[str, Any]", json.loads(response.read().decode("utf-8")))

    def submit_market_buy(
        self, symbol: str, *, qty: float | None = None, notional: float | None = None,
        client_order_id: str,
    ) -> Mapping[str, Any]:
        return self._submit(symbol, "buy", qty, notional, client_order_id)

    def submit_market_sell(
        self, symbol: str, *, qty: float | None = None, notional: float | None = None,
        client_order_id: str,
    ) -> Mapping[str, Any]:
        return self._submit(symbol, "sell", qty, notional, client_order_id)

    def get_positions(self) -> Sequence[Mapping[str, Any]]:
        return cast("Sequence[Mapping[str, Any]]", self._get("/v2/positions"))

    def get_open_orders(self) -> Sequence[Mapping[str, Any]]:
        return cast("Sequence[Mapping[str, Any]]", self._get("/v2/orders?status=open"))

    def get_orders(self) -> Sequence[Mapping[str, Any]]:
        return cast("Sequence[Mapping[str, Any]]", self._get("/v2/orders?status=all"))

    def get_account(self) -> Mapping[str, Any]:
        return cast("Mapping[str, Any]", self._get("/v2/account"))

    def get_asset(self, symbol: str) -> Mapping[str, Any]:
        return cast("Mapping[str, Any]", self._get(f"/v2/assets/{symbol}"))

    def get_latest_trade(self, symbol: str) -> Mapping[str, Any]:
        # Market-data host (read-only): the real live GLD share mark for the §5.1 execution reference.
        return cast(
            "Mapping[str, Any]", self._get_from(self._data_base_url, f"/v2/stocks/{symbol}/trades/latest")
        )


def live_adapter_from_env() -> LiveExecutionAdapter:
    """Build a :class:`LiveExecutionAdapter` from env credentials (fail-closed; never raises).

    Same paper-only credential boundary as :func:`execution.alpaca_adapter.paper_adapter_from_env`:
    missing creds **or** a non-paper base URL ⇒ ``client=None`` (every interaction fails closed). There
    is no code path here to a live-money endpoint (ADR-011 §3 / KA-008 / PRED-005).
    """
    key_id = os.environ.get("ALPACA_API_KEY_ID")
    secret_key = os.environ.get("ALPACA_API_SECRET_KEY")
    base_url = os.environ.get("ALPACA_PAPER_BASE_URL", _DEFAULT_BASE_URL)
    data_base_url = os.environ.get("ALPACA_DATA_BASE_URL", _DEFAULT_DATA_BASE_URL)
    if not key_id or not secret_key or not _is_paper_base_url(base_url):
        return LiveExecutionAdapter(client=None)
    return LiveExecutionAdapter(
        client=_AlpacaRestLiveBroker(key_id, secret_key, base_url, data_base_url)
    )
