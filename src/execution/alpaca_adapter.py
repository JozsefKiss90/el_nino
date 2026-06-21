"""Live Alpaca **paper** ``ExecutionPort`` plug (INT-011 / ADR-011 gate f) — non-replayable, default-OFF.

Behind the same ``ExecutionPort`` the ``SimulatedBrokerAdapter`` implements (ADR-011 §2). It declares
``mode = ExecutionMode.ALPACA_PAPER`` and ``replayable = False`` — so it is **quarantined off** the
``run_sequence`` / benchmark replay path (live runs are logged, never replayed). The deterministic
``SimulatedBrokerAdapter`` stays the hard-wired default port everywhere (``_DEFAULT_PORT``); this plug
is used only when a caller passes it explicitly to ``run_once`` (the live IO path). There is no default
wiring that reaches it, and it is deliberately **not** re-exported from the ``execution`` package.

**Built-but-dormant (ADR-011 §5).** ``execute()`` calls ``fill()`` only for an *approved LONG* on a
fresh snapshot; the provisional decision logic emits **no LONG** until calibration lands (ADR-012), so
this adapter ships behind the port **unused** — it cannot fill until a LONG exists.

**Paper-only ALWAYS (ADR-011 §3, PRED-005 Withdrawal Disabled).** Submits *virtual-money* orders to
the Alpaca **paper** endpoint only; the factory **refuses any non-paper base URL** and fail-closes on
missing creds. Withdrawals are never enabled. Credentials live in **env / a git-ignored ``.secrets``
ONLY** (KA-008) — never in the repo, a memory file, a dev_graph node, a test, or a committed artifact.

**Fail-closed.** A missing client, a non-LONG direction, or a broker order that does not confirm
filled raises :class:`AlpacaExecutionError` — **no order is silently placed and no synthetic fill is
ever returned**. The error propagates out of ``execute`` / ``run_once`` loudly.
"""

from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass
from typing import Protocol
from urllib.parse import urlparse

from gold.decision_builder.models import Direction

from .config import FillModelConfig
from .models import ExecutionMode, Fill

_BPS_DENOMINATOR = 10_000.0
_PAPER_HOST = "paper-api.alpaca.markets"
_DEFAULT_BASE_URL = f"https://{_PAPER_HOST}"
_HTTP_TIMEOUT_S = 10.0
_FILLED_STATUSES = frozenset({"filled", "FILLED"})


def _is_paper_base_url(base_url: str) -> bool:
    """True iff ``base_url`` is exactly the Alpaca **paper** host over https (the paper_only boundary).

    A parsed-**hostname** equality check (case-insensitive via ``urlparse``), never a substring match: a
    substring test would admit a sub-/super-domain (``evil.paper-api.alpaca.markets``,
    ``paper-api.alpaca.markets.evil.com``) or a URL carrying the host only in a query/fragment
    (``attacker.com?x=paper-api.alpaca.markets``) — credential-exfil bypasses of the paper-only invariant
    (ADR-011 §3 / KA-008 / PRED-005). ``urlparse().hostname`` is lowercased and excludes
    port/userinfo/path/query/fragment, so mixed-case legitimate URLs pass and only the exact host does.
    """
    parsed = urlparse(base_url)
    return parsed.scheme == "https" and parsed.hostname == _PAPER_HOST


class AlpacaExecutionError(RuntimeError):
    """Fail-closed: the Alpaca paper adapter could not place / confirm a paper fill (loud, never silent)."""


@dataclass(frozen=True)
class PaperOrderResult:
    """The echoed result of a submitted Alpaca **paper** market order (what the broker port returns)."""

    filled_avg_price: float
    filled_qty: float
    status: str


class AlpacaPaperBroker(Protocol):
    """The thin paper-broker port the adapter depends on (so tests inject a mock — never the network)."""

    def submit_market_buy(self, symbol: str, qty: float) -> PaperOrderResult:
        """Submit a market BUY of ``qty`` ``symbol`` to the Alpaca **paper** venue; return the fill echo."""
        ...


@dataclass(frozen=True)
class AlpacaPaperAdapter:
    """Live Alpaca paper-trading execution adapter (non-replayable, default-OFF; see module docstring).

    ``client=None`` (the fail-closed default) makes every ``fill`` raise :class:`AlpacaExecutionError`
    (no order placed). Construct via :func:`paper_adapter_from_env` for the real plug, or pass a stub
    ``client`` in tests. ``replayable=False`` keeps it off the deterministic replay / benchmark path.
    """

    client: AlpacaPaperBroker | None = None
    mode: ExecutionMode = ExecutionMode.ALPACA_PAPER
    replayable: bool = False

    def fill(
        self,
        instrument: str,
        direction: Direction,
        size: float,
        instrument_price: float,
        fill_model: FillModelConfig,
    ) -> Fill:
        """Submit a paper BUY and echo the paper fill. Fail-closed (raises) — never a synthetic fill."""
        if self.client is None:
            raise AlpacaExecutionError(
                "fail-closed: no Alpaca paper client (missing or non-paper credentials)"
            )
        if direction is not Direction.LONG:
            # Defensive: the engine only routes an approved LONG here; never place a non-LONG live order.
            raise AlpacaExecutionError(
                f"alpaca paper adapter fills only an approved LONG, got {direction.value}"
            )
        result = self.client.submit_market_buy(instrument, size)
        if result.status not in _FILLED_STATUSES:
            raise AlpacaExecutionError(f"alpaca paper order not filled (status={result.status!r})")
        fill_price = float(result.filled_avg_price)
        quantity = float(result.filled_qty)
        # Echo realized slippage vs the orchestrator's mark (ADR-011 D1) — recorded, not modelled.
        slippage_bps = (
            (fill_price - instrument_price) / instrument_price * _BPS_DENOMINATOR
            if instrument_price
            else 0.0
        )
        return Fill(fill_price=fill_price, quantity=quantity, slippage_bps=slippage_bps)


class _AlpacaRestPaperBroker:
    """stdlib-only Alpaca PAPER trading client (no third-party SDK). Built only by the factory."""

    def __init__(self, key_id: str, secret_key: str, base_url: str) -> None:
        self._key_id = key_id
        self._secret_key = secret_key
        self._base_url = base_url.rstrip("/")

    def _headers(self) -> dict[str, str]:
        return {
            "APCA-API-KEY-ID": self._key_id,
            "APCA-API-SECRET-KEY": self._secret_key,
            "content-type": "application/json",
            "accept": "application/json",
        }

    def submit_market_buy(self, symbol: str, qty: float) -> PaperOrderResult:
        body = json.dumps(
            {"symbol": symbol, "qty": qty, "side": "buy", "type": "market", "time_in_force": "day"}
        ).encode("utf-8")
        request = urllib.request.Request(
            f"{self._base_url}/v2/orders", data=body, headers=self._headers(), method="POST"
        )
        with urllib.request.urlopen(request, timeout=_HTTP_TIMEOUT_S) as response:
            order = json.loads(response.read().decode("utf-8"))
        return PaperOrderResult(
            filled_avg_price=float(order.get("filled_avg_price") or 0.0),
            filled_qty=float(order.get("filled_qty") or 0.0),
            status=str(order.get("status", "")),
        )


def paper_adapter_from_env() -> AlpacaPaperAdapter:
    """Build an :class:`AlpacaPaperAdapter` from environment credentials (KA-008 credential isolation).

    **Fail-closed, never raises:** missing ``ALPACA_API_KEY_ID`` / ``ALPACA_API_SECRET_KEY`` **or** a
    base URL that is not the Alpaca **paper** host ⇒ ``client=None`` (every ``fill`` raises). The
    non-paper-URL refusal enforces ``paper_only`` (ADR-011 §3, PRED-005) at the credential boundary —
    there is no code path here to a live-money endpoint.
    """
    key_id = os.environ.get("ALPACA_API_KEY_ID")
    secret_key = os.environ.get("ALPACA_API_SECRET_KEY")
    base_url = os.environ.get("ALPACA_PAPER_BASE_URL", _DEFAULT_BASE_URL)
    if not key_id or not secret_key or not _is_paper_base_url(base_url):
        return AlpacaPaperAdapter(client=None)
    return AlpacaPaperAdapter(client=_AlpacaRestPaperBroker(key_id, secret_key, base_url))
