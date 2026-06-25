"""TEST — operator kill switch (audited Tier-2 halt, ADR-014 §6.6).

The write/governance side is the gated action (tested in tests/ops/test_gated.py); here we test the
**honor** side: :func:`operator_halt_active` (absent ⇒ run, present-halt ⇒ honored, unreadable ⇒
fail-closed), the :class:`OperatorHaltFeed` decorator that forces ``halt=True`` so the **existing**
``operational_ok`` predicate REJECTs, and ``operate_live`` refusing execution (chain still advances)
when the kill switch is engaged.
"""

from __future__ import annotations

from pathlib import Path

from execution.live_adapter import LiveExecutionAdapter
from gold.paper_runtime.models import OperationalInput, Verdict
from orchestration.live_runtime import operate_live
from orchestration.operational_feed import (
    MarketCalendarFeed,
    OperatorHaltFeed,
    operator_halt_active,
    persist_operational,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_REAL = _REPO_ROOT / "tests" / "snapshot" / "fixtures" / "latest_snapshot_pass.json"
_AS_OF = "2026-05-01T22:00:00+00:00"  # a trading day (the feed would be open absent a halt)

_HALT = OperationalInput("GLD", tradeable=False, venue_open=True, halt=True, degraded=False)
_RESUME = OperationalInput("GLD", tradeable=True, venue_open=True, halt=False, degraded=False)


def _engage(path: Path) -> None:
    persist_operational(path, _HALT)


# --- operator_halt_active: absent runs, present-halt honored, unreadable fails closed -------------

def test_halt_inactive_when_marker_absent(tmp_path: Path) -> None:
    assert operator_halt_active(tmp_path / "absent.json") is False  # default is RUN, never halt-by-default


def test_halt_active_when_marker_engaged(tmp_path: Path) -> None:
    path = tmp_path / "operator_halt.json"
    _engage(path)
    assert operator_halt_active(path) is True


def test_halt_inactive_when_marker_cleared(tmp_path: Path) -> None:
    path = tmp_path / "operator_halt.json"
    persist_operational(path, _RESUME)
    assert operator_halt_active(path) is False


def test_unreadable_marker_fails_closed(tmp_path: Path) -> None:
    path = tmp_path / "operator_halt.json"
    path.write_text("{not json", encoding="utf-8")
    assert operator_halt_active(path) is True  # a present-but-unreadable kill switch is honored as HALTED


# --- OperatorHaltFeed: passthrough when not engaged; forces halt when engaged ---------------------

def test_feed_passthrough_when_not_engaged(tmp_path: Path) -> None:
    feed = OperatorHaltFeed(MarketCalendarFeed(), tmp_path / "absent.json")
    op = feed.read(_AS_OF)
    assert op.tradeable is True and op.halt is False  # the inner feed's open value is unchanged


def test_feed_forces_halt_when_engaged(tmp_path: Path) -> None:
    path = tmp_path / "operator_halt.json"
    _engage(path)
    feed = OperatorHaltFeed(MarketCalendarFeed(), path)
    op = feed.read(_AS_OF)
    assert op.halt is True and op.tradeable is False  # operational_ok will REJECT on this


# --- operate_live under the kill switch: REJECT, no execution, chain advances ---------------------

def test_operate_live_rejects_under_engaged_halt(tmp_path: Path) -> None:
    halt_path = tmp_path / "operator_halt.json"
    _engage(halt_path)
    feed = OperatorHaltFeed(MarketCalendarFeed(), halt_path)

    class _NeverCalled:
        def _boom(self, *a, **k):
            raise AssertionError("halted -> the broker must never be called")
        submit_market_buy = submit_market_sell = _boom
        get_positions = get_open_orders = get_orders = get_account = get_asset = _boom

    result = operate_live(
        _REAL, tmp_path / "l.live.json", tmp_path / "p.live.json", LiveExecutionAdapter(client=_NeverCalled()),
        operational_feed=feed, operational_capture_path=tmp_path / "op.live.json",
    )
    assert result is not None
    assert result.runtime_record.verdict is Verdict.REJECT          # honored via the existing operational_ok
    assert result.runtime_record.triggered_guard == "operational_ok"
    assert result.execution_record is None                          # no order placed
    assert len(result.ledger.entries) == 1                          # the chain still advanced


def test_resume_marker_lets_operate_live_admit_again(tmp_path: Path) -> None:
    halt_path = tmp_path / "operator_halt.json"
    persist_operational(halt_path, _RESUME)  # cleared kill switch
    feed = OperatorHaltFeed(MarketCalendarFeed(), halt_path)

    class _NeverCalled:
        def _boom(self, *a, **k):
            raise AssertionError("AVOID corpus -> the broker must never be called")
        submit_market_buy = submit_market_sell = _boom
        get_positions = get_open_orders = get_orders = get_account = get_asset = _boom

    result = operate_live(
        _REAL, tmp_path / "l.live.json", tmp_path / "p.live.json", LiveExecutionAdapter(client=_NeverCalled()),
        operational_feed=feed, operational_capture_path=tmp_path / "op.live.json",
    )
    assert result is not None and result.runtime_record.verdict is Verdict.ADMIT  # resumes normally
