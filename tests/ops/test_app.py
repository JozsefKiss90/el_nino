"""Headless app-level tests for the Operations Control Plane TUI (ADR-013 Step 2).

Driven via Textual's headless ``run_test`` driver (wrapped in ``asyncio.run`` so no pytest-asyncio is
needed). These verify the worker dispatch is crash-proof: a raising action must NOT stick the UI on
'[running]' or exit the app (Textual's default ``exit_on_error``).
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from ops import actions
from ops.app import OpsConsole
from ops.core import OpsPaths

REPO = Path(__file__).resolve().parents[2]


def _paths(tmp: Path) -> OpsPaths:
    return OpsPaths(
        repo_root=REPO,
        ledger_path=tmp / "l.json",
        portfolio_path=tmp / "p.json",
        operational_capture_path=tmp / "op.json",
        el_nino_snapshot=tmp / "absent.json",
        producer_snapshot_dir=tmp / "absent_producer",
        calibration_artifact=tmp / "c.json",
        daily_log_dir=tmp / "logs",
        audit_log_path=tmp / "audit.jsonl",
    )


def test_app_survives_a_raising_action(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(_paths: OpsPaths) -> actions.ActionResult:
        raise RuntimeError("kaboom")

    monkeypatch.setitem(actions.SAFE_ACTIONS, "run-chain-now", boom)

    async def go() -> None:
        app = OpsConsole(_paths(tmp_path))
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            app.action_run_chain()  # dispatches the (now raising) action into the worker
            await app.workers.wait_for_complete()
            await pilot.pause()
            assert app.is_running  # the worker caught the exception; the app did NOT exit

    asyncio.run(go())


def test_app_runs_a_safe_action_and_audits(tmp_path: Path) -> None:
    pass_snapshot = REPO / "tests" / "snapshot" / "fixtures" / "latest_snapshot_pass.json"
    paths = OpsPaths(
        repo_root=REPO,
        ledger_path=tmp_path / "l.json",
        portfolio_path=tmp_path / "p.json",
        operational_capture_path=tmp_path / "op.json",
        el_nino_snapshot=pass_snapshot,
        producer_snapshot_dir=tmp_path / "absent_producer",
        calibration_artifact=tmp_path / "c.json",
        daily_log_dir=tmp_path / "logs",
        audit_log_path=tmp_path / "audit.jsonl",
    )

    async def go() -> None:
        app = OpsConsole(paths)
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            app.action_run_chain()
            await app.workers.wait_for_complete()
            await pilot.pause()
            assert app.is_running

    asyncio.run(go())
    from ops.audit import read_audit
    entries = read_audit(paths.audit_log_path)
    assert len(entries) == 1 and entries[0].action == "run-chain-now" and entries[0].ok is True


def _clear_alpaca_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for var in ("ALPACA_API_KEY_ID", "ALPACA_API_SECRET_KEY", "ALPACA_PAPER_BASE_URL"):
        monkeypatch.delenv(var, raising=False)


def test_gated_action_confirm_runs_and_audits(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_alpaca_env(monkeypatch)  # no creds -> the gated Alpaca run REFUSES (safe; no network)
    paths = _paths(tmp_path)

    async def go() -> None:
        app = OpsConsole(paths)
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            await pilot.press("a")  # open the Alpaca confirm modal
            await pilot.pause()
            await pilot.press("y")  # confirm
            await app.workers.wait_for_complete()
            await pilot.pause()
            assert app.is_running

    asyncio.run(go())
    from ops.audit import read_audit
    entries = read_audit(paths.audit_log_path)
    assert len(entries) == 1
    assert entries[0].action == "run-chain-now-ALPACA-PAPER" and entries[0].ok is False  # refused


def test_gated_action_cancel_does_nothing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_alpaca_env(monkeypatch)
    paths = _paths(tmp_path)

    async def go() -> None:
        app = OpsConsole(paths)
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            await pilot.press("a")  # open modal
            await pilot.pause()
            await pilot.press("n")  # cancel
            await pilot.pause()
            assert app.is_running

    asyncio.run(go())
    from ops.audit import read_audit
    assert read_audit(paths.audit_log_path) == ()  # nothing executed, nothing audited
