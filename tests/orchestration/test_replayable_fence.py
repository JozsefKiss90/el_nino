"""TEST — the ADR-014 §5.3 replayable fence + the operate_live separate-paths quarantine.

``run_once`` / ``run_sequence`` (orchestration) structurally refuse a non-replayable broker port — a
live port is reachable only via ``live_runtime.operate_live``. ``operate_live`` accepts the live
:class:`LiveExecutionAdapter` and threads a SEPARATE ``(ledger, portfolio)`` pair, never touching the
canonical replay files. On the AVOID corpus the broker is never contacted (NO_ACTION before the adapter).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from execution.alpaca_adapter import AlpacaPaperAdapter
from execution.live_adapter import LiveExecutionAdapter
from orchestration import run_once, run_sequence
from orchestration.live_runtime import operate_live
from snapshot.snapshot_consumer import consume

_REPO_ROOT = Path(__file__).resolve().parents[2]
_REAL = _REPO_ROOT / "tests" / "snapshot" / "fixtures" / "latest_snapshot_pass.json"


class _NeverCalledBroker:
    """A full LiveBrokerPort whose every method fails — the AVOID corpus must never reach the broker."""

    def _boom(self, *args: object, **kwargs: object) -> object:
        raise AssertionError("AVOID corpus -> the broker must never be called")

    submit_market_buy = submit_market_sell = _boom
    get_positions = get_open_orders = get_orders = get_account = get_asset = _boom


def _replay_port() -> AlpacaPaperAdapter:
    return AlpacaPaperAdapter(client=object())  # a non-replayable ExecutionPort (replayable is False)


def _live_adapter() -> LiveExecutionAdapter:
    return LiveExecutionAdapter(client=_NeverCalledBroker())  # replayable is False; never called on AVOID


def test_run_once_refuses_non_replayable_port(tmp_path: Path) -> None:
    with pytest.raises(AssertionError, match="operate_live"):
        run_once(_REAL, tmp_path / "l.json", tmp_path / "p.json", port=_replay_port())


def test_run_sequence_refuses_non_replayable_port() -> None:
    snap = consume(_REAL)
    with pytest.raises(AssertionError):
        run_sequence([snap], port=_replay_port())


def test_run_once_accepts_the_default_replayable_port(tmp_path: Path) -> None:
    # The simulator port (replayable=True) passes the fence — the canonical path is unaffected.
    result = run_once(_REAL, tmp_path / "l.json", tmp_path / "p.json")
    assert result is not None and result.execution_record is not None
    assert result.execution_record.replayable is True


def test_operate_live_threads_separate_paths_and_leaves_canonical_untouched(tmp_path: Path) -> None:
    canonical_ledger = tmp_path / "runtime_ledger.json"
    canonical_pf = tmp_path / "portfolio_state.json"
    live_ledger = tmp_path / "runtime_ledger.live.json"
    live_pf = tmp_path / "portfolio_state.live.json"

    result = operate_live(
        _REAL, live_ledger, live_pf, _live_adapter(),
        operational_capture_path=tmp_path / "op.live.json",
    )
    assert result is not None and result.execution_record is not None
    assert result.execution_record.replayable is False  # the live adapter stamped non-replayable
    assert result.execution_record.fill is None          # AVOID -> NO_ACTION (broker never called)
    assert result.execution_record.execution_mode.value == "alpaca_paper"
    # The live files exist; the canonical replay files were never written (physical separation).
    assert live_ledger.exists() and live_pf.exists()
    assert not canonical_ledger.exists() and not canonical_pf.exists()
