"""TEST-027 — live Alpaca clock/calendar OperationalFeed plug (MOD-010 seam, ADR-009 amendment / gate f).

Covers: the calendar-driven open/closed decision; the **holiday-gap closure** (a movable feast the
fixed-date ``MarketCalendarFeed`` wrongly reports open, this plug correctly reports closed); fail-closed
on a client error / missing client / unparseable as_of; the ``from_env`` factory fail-closing on
missing creds and **refusing a non-paper base URL**; and the **replay-path quarantine** — the captured
Alpaca-produced ``OperationalInput`` reloads via ``load_operational`` and ``run_sequence`` threads it
without ever re-reading the feed. NO real network: every client is a stub.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from gold.paper_runtime import load_operational
from snapshot.snapshot_consumer import consume

from orchestration import MarketCalendarFeed, read_and_capture, run_sequence
from orchestration.alpaca_clock_feed import AlpacaClockFeed, clock_feed_from_env

_REPO_ROOT = Path(__file__).resolve().parents[2]
_REAL = _REPO_ROOT / "tests" / "snapshot" / "fixtures" / "latest_snapshot_pass.json"

_FRIDAY = "2026-05-01T22:00:00+00:00"        # an ordinary trading day
_SATURDAY = "2026-05-02T22:00:00+00:00"      # weekend
_GOOD_FRIDAY = "2026-04-03T22:00:00+00:00"   # Good Friday 2026 — a weekday holiday the NYSE closes for


class _StubCalendar:
    """A stand-in Alpaca ``/v2/calendar`` client: returns a fixed set of trading dates, counts calls."""

    def __init__(self, *trading_days: str) -> None:
        self._trading = set(trading_days)
        self.calls = 0

    def trading_days(self, start: str, end: str) -> tuple[str, ...]:
        self.calls += 1
        # Membership is per-day here; the feed only ever queries a single day (start == end).
        return tuple(sorted({d for d in (start, end) if d in self._trading}))


class _RaisingCalendar:
    """A client whose every call fails — to prove the feed fail-closes on any IO/auth error."""

    def trading_days(self, start: str, end: str) -> tuple[str, ...]:
        raise RuntimeError("simulated Alpaca API / auth error")


# --- calendar-driven open / closed -----------------------------------------------------------

def test_open_on_scheduled_trading_day() -> None:
    feed = AlpacaClockFeed(client=_StubCalendar("2026-05-01"))
    op = feed.read(_FRIDAY)
    assert op.tradeable and op.venue_open and not op.halt and not op.degraded
    assert op.instrument == "GLD" and op.as_of == _FRIDAY


def test_closed_on_weekend_not_in_calendar() -> None:
    feed = AlpacaClockFeed(client=_StubCalendar())  # 2026-05-02 not a trading day
    assert feed.read(_SATURDAY).tradeable is False


def test_closes_holiday_gap_the_fixed_date_feed_misses() -> None:
    # The KEY behaviour: Good Friday (movable feast) is a weekday NOT in the fixed-date holiday set,
    # so MarketCalendarFeed wrongly reports it OPEN; Alpaca's calendar omits it ⇒ this plug closes.
    assert MarketCalendarFeed().read(_GOOD_FRIDAY).tradeable is True   # the v0 gap (wrong)
    alpaca = AlpacaClockFeed(client=_StubCalendar("2026-05-01"))       # 2026-04-03 omitted ⇒ closed
    assert alpaca.read(_GOOD_FRIDAY).tradeable is False                # gap closed (correct)


# --- fail-closed -----------------------------------------------------------------------------

def test_fail_closed_on_client_error() -> None:
    assert AlpacaClockFeed(client=_RaisingCalendar()).read(_FRIDAY).tradeable is False


def test_fail_closed_without_client() -> None:
    assert AlpacaClockFeed(client=None).read(_FRIDAY).tradeable is False


def test_fail_closed_on_unparseable_or_absent_as_of() -> None:
    feed = AlpacaClockFeed(client=_StubCalendar("2026-05-01"))
    assert feed.read("not-a-timestamp").tradeable is False
    assert feed.read(None).tradeable is False


# --- from_env factory: fail-closed + paper-only refusal --------------------------------------

def test_from_env_without_creds_is_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ALPACA_API_KEY_ID", raising=False)
    monkeypatch.delenv("ALPACA_API_SECRET_KEY", raising=False)
    feed = clock_feed_from_env()
    assert feed.client is None
    assert feed.read(_FRIDAY).tradeable is False  # no creds ⇒ closed, no network


def test_from_env_refuses_non_paper_base_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALPACA_API_KEY_ID", "dummy-key")
    monkeypatch.setenv("ALPACA_API_SECRET_KEY", "dummy-secret")
    monkeypatch.setenv("ALPACA_PAPER_BASE_URL", "https://api.alpaca.markets")  # LIVE host — must refuse
    feed = clock_feed_from_env()
    assert feed.client is None  # paper-only invariant enforced at the credential boundary


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
    assert clock_feed_from_env().client is None


def test_from_env_accepts_mixed_case_paper_host(monkeypatch: pytest.MonkeyPatch) -> None:
    # DNS/HTTP hostnames are case-insensitive; a mixed-case paper host is the real endpoint (no network).
    monkeypatch.setenv("ALPACA_API_KEY_ID", "dummy-key")
    monkeypatch.setenv("ALPACA_API_SECRET_KEY", "dummy-secret")
    monkeypatch.setenv("ALPACA_PAPER_BASE_URL", "https://PAPER-API.ALPACA.MARKETS")
    assert clock_feed_from_env().client is not None


def test_from_env_with_paper_creds_builds_a_client_no_network(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALPACA_API_KEY_ID", "dummy-key")
    monkeypatch.setenv("ALPACA_API_SECRET_KEY", "dummy-secret")
    monkeypatch.delenv("ALPACA_PAPER_BASE_URL", raising=False)  # defaults to the paper host
    feed = clock_feed_from_env()
    assert feed.client is not None  # a real client is constructed but never invoked here (no network)


# --- the non-negotiable: replay-path quarantine ----------------------------------------------

def test_capture_round_trips_and_replay_never_reads_the_feed(tmp_path: Path) -> None:
    # First read open, every later read closed — proves the captured value is frozen, not re-read.
    feed = AlpacaClockFeed(client=_StubCalendar("2026-05-01"))
    capture = tmp_path / "op.json"
    produced = read_and_capture(feed, _FRIDAY, capture)
    assert produced.tradeable is True
    assert feed.client.calls == 1  # type: ignore[union-attr]

    # The captured artifact is exactly what paper_runtime.load_operational reads (the replay source).
    reloaded = load_operational(capture)
    assert reloaded.to_dict() == produced.to_dict()

    snap = consume(_REAL)
    assert snap is not None
    # run_sequence takes the captured OperationalInput explicitly — it has no feed parameter at all.
    results, _, _ = run_sequence([snap], operational_input=reloaded)
    assert results[0].runtime_record.verdict.value == "ADMIT"
    assert feed.client.calls == 1  # type: ignore[union-attr]  # replay did not touch the feed


def test_alpaca_produced_input_matches_calendar_feed_shape() -> None:
    # The Alpaca plug produces the same OperationalInput shape as the deterministic feed (drop-in).
    alpaca = AlpacaClockFeed(client=_StubCalendar("2026-05-01")).read(_FRIDAY)
    calendar = MarketCalendarFeed().read(_FRIDAY)
    assert alpaca.to_dict() == calendar.to_dict()
