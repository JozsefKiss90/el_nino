"""Live Alpaca clock/calendar ``OperationalFeed`` plug (MOD-010 seam) — closes ADR-009's holiday gap.

A **non-replayable live plug** behind the same ``OperationalFeed`` port the deterministic
``MarketCalendarFeed`` implements (ADR-011 §2 / gate-f quarantine). It is read **only** on the
``run_once`` live path; the produced ``OperationalInput`` is captured by ``read_and_capture`` so any
``run_sequence`` replay threads the captured value and **never** re-reads Alpaca (live runs logged,
never replayed, never in benchmarks).

**Why it exists.** The fixed-date ``MarketCalendarFeed`` is a deterministic v0 approximation: it
cannot model movable feasts (Good Friday) or observed-date shifts (a holiday landing on a weekend and
observed on the adjacent weekday). Alpaca's ``/v2/calendar`` is the authoritative venue calendar that
does — so this plug *closes the holiday-calendar gap* for ``operational_ok``.

**Default-OFF.** ``MarketCalendarFeed`` stays the canonical, credential-free source; this plug is
enabled only by explicit operator opt-in (``orchestration.runtime --operational-feed-source alpaca``).
It is deliberately **not** re-exported from the ``orchestration`` package so the default import graph
stays network-free.

**Fail-closed (ADR-009 + KA-008).** Missing / non-paper creds, an API error, or an
ambiguous/unparseable ``as_of`` ⇒ ``OperationalInput.closed()`` (not tradeable). Credentials live in
**env / a git-ignored ``.secrets`` ONLY** — never in the repo, a memory file, a dev_graph node, a
test, or any committed artifact (KA-008 credential isolation).
"""

from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from urllib.parse import urlparse

from gold.paper_runtime.models import OperationalInput

# Alpaca PAPER host — the ONLY endpoint this plug will talk to (paper_only invariant, ADR-011 §3).
_PAPER_HOST = "paper-api.alpaca.markets"
_DEFAULT_BASE_URL = f"https://{_PAPER_HOST}"
_HTTP_TIMEOUT_S = 10.0


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


def _calendar_date(as_of: str | None) -> str | None:
    """The ``YYYY-MM-DD`` venue date of ``as_of`` (ISO-8601), or ``None`` if absent/unparseable."""
    if not as_of:
        return None
    try:
        return datetime.fromisoformat(as_of).strftime("%Y-%m-%d")
    except ValueError:
        return None


class AlpacaCalendarClient(Protocol):
    """The thin venue-calendar port the feed depends on (so tests inject a mock — never the network)."""

    def trading_days(self, start: str, end: str) -> tuple[str, ...]:
        """Venue trading dates (``YYYY-MM-DD``) within ``[start, end]`` per Alpaca ``/v2/calendar``."""
        ...


@dataclass(frozen=True)
class AlpacaClockFeed:
    """Live Alpaca clock/calendar feed behind the ``OperationalFeed`` port (non-replayable, default-OFF).

    ``client=None`` (the fail-closed default — e.g. missing creds) makes every ``read`` resolve to
    ``OperationalInput.closed()``. Construct via :func:`clock_feed_from_env` for the real plug, or pass
    a stub ``client`` in tests. ``halt`` / ``degraded`` are not modelled by a calendar (a real-time
    market-data feed would); a scheduled trading day is reported open, everything else fail-closed.
    """

    client: AlpacaCalendarClient | None = None
    instrument: str = "GLD"

    def read(self, as_of: str | None) -> OperationalInput:
        if self.client is None:
            return OperationalInput.closed(instrument=self.instrument, as_of=as_of)
        day = _calendar_date(as_of)
        if day is None:
            return OperationalInput.closed(instrument=self.instrument, as_of=as_of)
        try:
            trading = self.client.trading_days(day, day)
        except Exception:
            # Any IO / parse / auth failure is fail-closed, never fail-open (ADR-009).
            return OperationalInput.closed(instrument=self.instrument, as_of=as_of)
        if day not in trading:
            # Weekend or a (movable / observed) holiday Alpaca knows but the fixed-date feed cannot.
            return OperationalInput.closed(instrument=self.instrument, as_of=as_of)
        return OperationalInput(
            instrument=self.instrument,
            tradeable=True,
            venue_open=True,
            halt=False,
            degraded=False,
            as_of=as_of,
        )


class _AlpacaRestCalendarClient:
    """stdlib-only Alpaca PAPER ``/v2/calendar`` client (no third-party SDK). Built only by the factory."""

    def __init__(self, key_id: str, secret_key: str, base_url: str) -> None:
        self._key_id = key_id
        self._secret_key = secret_key
        self._base_url = base_url.rstrip("/")

    def trading_days(self, start: str, end: str) -> tuple[str, ...]:
        url = f"{self._base_url}/v2/calendar?start={start}&end={end}"
        request = urllib.request.Request(
            url,
            headers={
                "APCA-API-KEY-ID": self._key_id,
                "APCA-API-SECRET-KEY": self._secret_key,
                "accept": "application/json",
            },
        )
        with urllib.request.urlopen(request, timeout=_HTTP_TIMEOUT_S) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return tuple(str(entry["date"]) for entry in payload if "date" in entry)


def clock_feed_from_env(instrument: str = "GLD") -> AlpacaClockFeed:
    """Build an :class:`AlpacaClockFeed` from environment credentials (KA-008 credential isolation).

    **Fail-closed, never raises:** missing ``ALPACA_API_KEY_ID`` / ``ALPACA_API_SECRET_KEY`` **or** a
    base URL that is not the Alpaca **paper** host ⇒ a feed with ``client=None`` (every ``read`` ⇒
    ``closed()``). The non-paper-URL refusal enforces the ``paper_only`` invariant (ADR-011 §3,
    PRED-005) at the credential boundary — there is no code path here to a live-money endpoint.
    """
    key_id = os.environ.get("ALPACA_API_KEY_ID")
    secret_key = os.environ.get("ALPACA_API_SECRET_KEY")
    base_url = os.environ.get("ALPACA_PAPER_BASE_URL", _DEFAULT_BASE_URL)
    if not key_id or not secret_key:
        return AlpacaClockFeed(client=None, instrument=instrument)  # no creds ⇒ fail-closed
    if not _is_paper_base_url(base_url):
        return AlpacaClockFeed(client=None, instrument=instrument)  # non-paper endpoint ⇒ refuse
    return AlpacaClockFeed(
        client=_AlpacaRestCalendarClient(key_id, secret_key, base_url),
        instrument=instrument,
    )
