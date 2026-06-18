"""TEST-026 — live operational-status feed adapter (MOD-010 seam, ADR-009 amendment).

The deterministic ``MarketCalendarFeed`` (open on a trading day, fail-closed on weekend / holiday /
unparseable), the capture round-trip (the produced ``OperationalInput`` reloads via ``load_operational``),
and — the non-negotiable — the **replay-path quarantine**: the captured value is frozen at read time and
a replay threads it without ever re-reading the feed (mirrors the execution layer's captured-config
env-independence test). The pure ``OperationalInput`` contract is unchanged.
"""

from __future__ import annotations

from pathlib import Path

from gold.paper_runtime import OperationalInput, load_operational
from snapshot.snapshot_consumer import consume

from orchestration import MarketCalendarFeed, read_and_capture, run_once, run_sequence

_REPO_ROOT = Path(__file__).resolve().parents[2]
_REAL = _REPO_ROOT / "tests" / "snapshot" / "fixtures" / "latest_snapshot_pass.json"

_FRIDAY = "2026-05-01T22:00:00+00:00"      # trading day
_SATURDAY = "2026-05-02T22:00:00+00:00"    # weekend
_XMAS_FRIDAY = "2026-12-25T22:00:00+00:00"  # a holiday that falls on a weekday (isolates holiday logic)


class _StubFeed:
    """A non-deterministic stand-in: returns a queued OperationalInput per read, counting calls.

    Used to prove that *capture* freezes the value — a later replay must use the captured artifact, not
    whatever the (now-different) feed would return.
    """

    def __init__(self, *ops: OperationalInput) -> None:
        self._ops = list(ops)
        self.calls = 0

    def read(self, as_of: str | None) -> OperationalInput:
        op = self._ops[min(self.calls, len(self._ops) - 1)]
        self.calls += 1
        return op


# --- MarketCalendarFeed: deterministic + fail-closed -------------------------------------------

def test_feed_open_on_trading_day() -> None:
    op = MarketCalendarFeed().read(_FRIDAY)
    assert op.tradeable and op.venue_open and not op.halt and not op.degraded
    assert op.instrument == "GLD" and op.as_of == _FRIDAY


def test_feed_closed_on_weekend() -> None:
    op = MarketCalendarFeed().read(_SATURDAY)
    assert op.tradeable is False and op.venue_open is False


def test_feed_closed_on_weekday_holiday() -> None:
    # 2026-12-25 (Christmas) is a Friday — closed by the holiday rule, not the weekend rule.
    op = MarketCalendarFeed().read(_XMAS_FRIDAY)
    assert op.tradeable is False


def test_feed_fail_closed_on_unparseable_or_absent() -> None:
    assert MarketCalendarFeed().read("not-a-timestamp").tradeable is False
    assert MarketCalendarFeed().read(None).tradeable is False


def test_feed_is_deterministic() -> None:
    assert MarketCalendarFeed().read(_FRIDAY) == MarketCalendarFeed().read(_FRIDAY)


# --- capture round-trip -----------------------------------------------------------------------

def test_capture_round_trips_through_load_operational(tmp_path: Path) -> None:
    path = tmp_path / "op.json"
    produced = read_and_capture(MarketCalendarFeed(), _FRIDAY, path)
    assert path.exists()
    # the captured artifact is exactly what paper_runtime.load_operational reads (the replay source).
    assert load_operational(path).to_dict() == produced.to_dict()


def test_read_and_capture_without_path_does_not_persist(tmp_path: Path) -> None:
    produced = read_and_capture(MarketCalendarFeed(), _FRIDAY, None)
    assert produced.tradeable is True
    assert not any(tmp_path.iterdir())  # nothing written


# --- the non-negotiable: replay-path quarantine -----------------------------------------------

def test_capture_freezes_value_independent_of_later_feed(tmp_path: Path) -> None:
    open_op = OperationalInput("GLD", tradeable=True, venue_open=True, halt=False, degraded=False)
    closed_op = OperationalInput.closed()
    feed = _StubFeed(open_op, closed_op)  # first read open, every later read closed
    path = tmp_path / "op.json"

    captured = read_and_capture(feed, _FRIDAY, path)
    assert captured == open_op
    assert feed.calls == 1

    # a replay reconstructs the operational decision from the CAPTURED artifact — never the feed.
    reloaded = load_operational(path)
    assert reloaded.tradeable is True          # the frozen open value, not the feed's later closed value
    assert feed.calls == 1                      # the feed was not re-read


def test_run_sequence_replay_never_reads_the_feed(tmp_path: Path) -> None:
    # capture once on the live path, then replay via run_sequence threading the captured value.
    feed = _StubFeed(
        OperationalInput("GLD", tradeable=True, venue_open=True, halt=False, degraded=False),
        OperationalInput.closed(),  # would flip the verdict if the feed were re-read on replay
    )
    captured = read_and_capture(feed, _FRIDAY, tmp_path / "op.json")
    assert feed.calls == 1

    snap = consume(_REAL)
    assert snap is not None
    # run_sequence takes an explicit OperationalInput (the captured one) — it has no feed parameter.
    results_a, _, _ = run_sequence([snap], operational_input=captured)
    results_b, _, _ = run_sequence([snap], operational_input=captured)
    assert results_a[0].runtime_record.verdict.value == results_b[0].runtime_record.verdict.value == "ADMIT"
    assert feed.calls == 1  # replay did not touch the feed


# --- live run_once integration ----------------------------------------------------------------

def test_run_once_with_feed_captures_and_uses_it(tmp_path: Path) -> None:
    capture = tmp_path / "op.json"
    result = run_once(
        _REAL,
        tmp_path / "ledger.json",
        tmp_path / "portfolio.json",
        operational_feed=MarketCalendarFeed(),
        operational_capture_path=capture,
    )
    assert result is not None
    assert result.runtime_record.verdict.value == "ADMIT"   # 2026-05-01 is a trading day ⇒ tradeable
    # the captured operational input is persisted for replay and is tradeable.
    assert capture.exists()
    assert load_operational(capture).tradeable is True
