"""Headless tests for the Step-3 gated-live actions (ADR-013 Tier 3).

Mocked end-to-end: the Alpaca adapter factory and the subprocess runner are injected, so NO network call
and NO PowerShell spawn ever happens. Asserts the server-side preconditions fail-closed (dormant adapter
-> REFUSE, never an order), the live run threads the Alpaca-paper port without hitting the network (AVOID
-> no fill -> the broker stub is never called), the calibration bump can ONLY ever DEFER (never mutates the
golden / a *_version), every action audits exactly once, and no credential value reaches the audit log.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path

import pytest

from execution.alpaca_adapter import AlpacaPaperAdapter
from ops import audit, gated
from ops.core import OpsPaths
from ops.proc import ProcResult

REPO = Path(__file__).resolve().parents[2]
PASS_SNAPSHOT = REPO / "tests" / "snapshot" / "fixtures" / "latest_snapshot_pass.json"

CALIB_DEFER = {
    "decision_versions": {"taxonomy_version": "1.0.0", "decision_policy_version": "0.1.0"},
    "committed_real": {"distinct_snapshots": 1, "coverage": {
        "regimes": ["RESTRICTIVE_RATES"], "directions": ["AVOID"],
        "statuses": ["pending"], "label_count": 3, "realized_count": 0}},
}
CALIB_ELIGIBLE = {
    "decision_versions": {"taxonomy_version": "1.0.0", "decision_policy_version": "0.1.0"},
    "committed_real": {"distinct_snapshots": 80, "coverage": {
        "regimes": ["A", "B", "C"], "directions": ["LONG", "AVOID"],
        "statuses": ["realized"], "label_count": 100, "realized_count": 40}},
}


def _clock() -> datetime:
    return datetime(2026, 6, 18, 12, 0, 0, tzinfo=timezone.utc)


def make_paths(tmp: Path, **over: Path) -> OpsPaths:
    base: dict[str, Path] = {
        "repo_root": REPO,
        "ledger_path": tmp / "runtime" / "chain" / "ledger.json",
        "portfolio_path": tmp / "runtime" / "chain" / "portfolio.json",
        "operational_capture_path": tmp / "runtime" / "chain" / "op.json",
        "el_nino_snapshot": tmp / "absent_snapshot.json",
        "producer_snapshot_dir": tmp / "absent_producer",
        "calibration_artifact": tmp / "calib.json",
        "daily_log_dir": tmp / "logs",
        "audit_log_path": tmp / "runtime" / "ops" / "audit.jsonl",
    }
    base.update(over)
    return OpsPaths(**base)  # type: ignore[arg-type]


class _StubBroker:
    """A broker stub that FAILS if ever called — proving no network is hit on a non-LONG run."""

    def __init__(self) -> None:
        self.calls = 0

    def submit_market_buy(self, symbol: str, qty: float) -> object:
        self.calls += 1
        raise AssertionError("the broker must never be called in tests")


def _dormant_factory() -> AlpacaPaperAdapter:
    return AlpacaPaperAdapter(client=None)


# ----------------------------------------------------------------------------- alpaca paper run
def test_alpaca_run_refuses_when_dormant(tmp_path: Path) -> None:
    paths = make_paths(tmp_path, el_nino_snapshot=PASS_SNAPSHOT)
    result = gated.run_chain_now_alpaca_paper(paths, adapter_factory=_dormant_factory, clock=_clock)
    assert result.ok is False and result.executed is False
    assert "REFUSED" in result.summary
    assert not paths.ledger_path.exists()  # run_once was never called
    entries = audit.read_audit(paths.audit_log_path)
    assert len(entries) == 1 and entries[0].action == "run-chain-now-ALPACA-PAPER" and entries[0].ok is False


def test_alpaca_run_threads_live_port_without_network(tmp_path: Path) -> None:
    stub = _StubBroker()

    def factory() -> AlpacaPaperAdapter:
        return AlpacaPaperAdapter(client=stub)

    paths = make_paths(tmp_path, el_nino_snapshot=PASS_SNAPSHOT)
    result = gated.run_chain_now_alpaca_paper(paths, adapter_factory=factory, clock=_clock)
    assert result.ok is True and result.executed is True
    assert "mode=alpaca_paper" in result.summary  # the LIVE port was threaded
    assert "no-fill" in result.summary  # AVOID stance -> no order
    assert stub.calls == 0  # the broker was NEVER called (no network)
    assert paths.ledger_path.exists()
    assert audit.read_audit(paths.audit_log_path)[0].ok is True


# ----------------------------------------------------------------------------- schedule register/unregister
def runner_ok(_cmd: Sequence[str], _paths: OpsPaths) -> ProcResult:
    return ProcResult(0, "task registered", "")


def runner_fail(_cmd: Sequence[str], _paths: OpsPaths) -> ProcResult:
    return ProcResult(1, "", "access denied")


def test_register_schedule_ok(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)  # repo_root=REPO so the real .ps1 exists (but runner is injected)
    result = gated.register_daily_schedule(paths, runner=runner_ok, clock=_clock)
    assert result.ok is True and result.executed is True and "registered" in result.summary
    assert audit.read_audit(paths.audit_log_path)[0].action == "register-daily-schedule"


def test_register_schedule_refuses_when_script_missing(tmp_path: Path) -> None:
    paths = make_paths(tmp_path, repo_root=tmp_path)  # no scripts/ dir here
    result = gated.register_daily_schedule(paths, runner=runner_ok, clock=_clock)
    assert result.ok is False and result.executed is False and "REFUSED" in result.summary


def test_unregister_schedule_ok(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    result = gated.unregister_daily_schedule(paths, runner=runner_ok, clock=_clock)
    assert result.ok is True and "unregistered" in result.summary


def test_unregister_schedule_failure_audited(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    result = gated.unregister_daily_schedule(paths, runner=runner_fail, clock=_clock)
    assert result.ok is False and result.executed is True
    assert audit.read_audit(paths.audit_log_path)[0].ok is False


# ----------------------------------------------------------------------------- calibration bump (DEFER only)
def test_calibration_bump_defers_and_never_mutates(tmp_path: Path) -> None:
    cal_path = tmp_path / "calib.json"
    cal_path.write_text(json.dumps(CALIB_DEFER), encoding="utf-8")
    before = cal_path.read_bytes()
    paths = make_paths(tmp_path, calibration_artifact=cal_path)
    result = gated.commit_calibration_bump(paths, clock=_clock)
    assert result.ok is True and result.executed is False  # NEVER executes a bump
    assert result.summary.startswith("DEFER")
    assert cal_path.read_bytes() == before  # the golden is unchanged (no bump, no *_version mutation)


def test_calibration_bump_eligible_still_does_not_bump(tmp_path: Path) -> None:
    cal_path = tmp_path / "calib.json"
    cal_path.write_text(json.dumps(CALIB_ELIGIBLE), encoding="utf-8")
    before = cal_path.read_bytes()
    paths = make_paths(tmp_path, calibration_artifact=cal_path)
    result = gated.commit_calibration_bump(paths, clock=_clock)
    assert result.executed is False  # ELIGIBLE -> still human-review-required, console never bumps
    assert "NOT auto-applied" in result.summary
    assert cal_path.read_bytes() == before


# ----------------------------------------------------------------------------- secrets + never-raise
def test_no_credential_value_in_gated_audit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    secret = "GATED_SECRET_VALUE_777"
    monkeypatch.setenv("ALPACA_API_SECRET_KEY", secret)
    monkeypatch.setenv("ALPACA_API_KEY_ID", secret)
    paths = make_paths(tmp_path, el_nino_snapshot=PASS_SNAPSHOT)
    gated.run_chain_now_alpaca_paper(paths, adapter_factory=_dormant_factory, clock=_clock)
    gated.unregister_daily_schedule(paths, runner=runner_fail, clock=_clock)
    assert secret not in paths.audit_log_path.read_text(encoding="utf-8")


def test_alpaca_run_never_raises_on_factory_error(tmp_path: Path) -> None:
    def boom_factory() -> AlpacaPaperAdapter:
        raise RuntimeError("factory blew up")

    paths = make_paths(tmp_path, el_nino_snapshot=PASS_SNAPSHOT)
    result = gated.run_chain_now_alpaca_paper(paths, adapter_factory=boom_factory, clock=_clock)
    assert result.ok is False and result.executed is False  # never raised; audited as not-executed
    assert "unexpected error" in result.summary
    assert not paths.ledger_path.exists()
    assert audit.read_audit(paths.audit_log_path)[0].ok is False


def test_gated_action_never_raises_on_audit_write_failure(tmp_path: Path) -> None:
    blocker = tmp_path / "blocker"
    blocker.write_text("file", encoding="utf-8")
    paths = make_paths(tmp_path, audit_log_path=blocker / "audit.jsonl")
    result = gated.commit_calibration_bump(paths, clock=_clock)  # must NOT raise
    assert any("AUDIT-WRITE-FAILED" in line for line in result.detail)


# ----------------------------------------------------------------------------- registry + preconditions
def test_gated_registry() -> None:
    assert set(gated.GATED_ACTIONS) == {
        "run-chain-now-ALPACA-PAPER", "register-daily-schedule",
        "unregister-daily-schedule", "commit-calibration-bump",
    }


def test_precondition_line_alpaca_dormant(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    for var in ("ALPACA_API_KEY_ID", "ALPACA_API_SECRET_KEY", "ALPACA_PAPER_BASE_URL"):
        monkeypatch.delenv(var, raising=False)
    line = gated.precondition_line(make_paths(tmp_path), "run-chain-now-ALPACA-PAPER")
    assert "FAILS" in line and "REFUSE" in line
