"""Headless tests for the Step-2 safe actions (ADR-013 Tier 2).

Mocked: subprocess actions use an injected runner (no real process spawned); the chain action runs the
real in-process governed ``run_once`` against the committed consumable snapshot fixture (deterministic,
paper-only, simulator port). Asserts: each action audits exactly one entry, failures are caught (never
raised) and audited ok=False, the calibration action never bumps, and no credential value reaches the
audit log even with creds in the environment.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path

import pytest

from ops import actions, audit
from ops.core import OpsPaths

REPO = Path(__file__).resolve().parents[2]
PASS_SNAPSHOT = REPO / "tests" / "snapshot" / "fixtures" / "latest_snapshot_pass.json"

CALIB_DEFER = {
    "decision_versions": {"taxonomy_version": "1.0.0", "decision_policy_version": "0.1.0"},
    "committed_real": {
        "distinct_snapshots": 1,
        "coverage": {"regimes": ["RESTRICTIVE_RATES"], "directions": ["AVOID"],
                     "statuses": ["pending"], "label_count": 3, "realized_count": 0},
    },
}


def _fixed_clock() -> datetime:
    return datetime(2026, 6, 18, 12, 0, 0, tzinfo=timezone.utc)


def make_paths(tmp: Path, **over: Path) -> OpsPaths:
    base: dict[str, Path] = {
        "repo_root": REPO,
        "ledger_path": tmp / "runtime" / "chain" / "runtime_ledger.json",
        "portfolio_path": tmp / "runtime" / "chain" / "portfolio_state.json",
        "operational_capture_path": tmp / "runtime" / "chain" / "operational_capture.json",
        "el_nino_snapshot": tmp / "absent_snapshot.json",
        "producer_snapshot_dir": tmp / "absent_producer",
        "calibration_artifact": tmp / "calib.json",
        "daily_log_dir": tmp / "logs",
        "audit_log_path": tmp / "runtime" / "ops" / "audit_log.jsonl",
    }
    base.update(over)
    return OpsPaths(**base)  # type: ignore[arg-type]


def runner_ok(_cmd: Sequence[str], _paths: OpsPaths) -> actions.ProcResult:
    return actions.ProcResult(0, "wrote artifact\ncoverage: {...}", "")


def runner_fail(_cmd: Sequence[str], _paths: OpsPaths) -> actions.ProcResult:
    return actions.ProcResult(1, "", "boom: missing NEO4J_PASSWORD")


# ----------------------------------------------------------------------------- run chain now
def test_run_chain_now_persists_and_audits(tmp_path: Path) -> None:
    paths = make_paths(tmp_path, el_nino_snapshot=PASS_SNAPSHOT)
    result = actions.run_chain_now(paths, clock=_fixed_clock)
    assert result.ok is True
    assert result.action == "run-chain-now"
    assert "verdict=" in result.summary
    # the governed run_once persisted the canonical artefacts
    assert paths.ledger_path.exists() and paths.portfolio_path.exists()
    # exactly one audit entry, marked ok
    entries = audit.read_audit(paths.audit_log_path)
    assert len(entries) == 1 and entries[0].action == "run-chain-now" and entries[0].ok is True


def test_run_chain_now_no_snapshot_is_nothing_to_do(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)  # no producer dir, no el_nino snapshot
    result = actions.run_chain_now(paths, clock=_fixed_clock)
    assert result.ok is True
    assert "nothing to do" in result.summary
    assert not paths.ledger_path.exists()  # nothing persisted
    assert len(audit.read_audit(paths.audit_log_path)) == 1  # still audited


def test_run_chain_now_idempotent_audits_each_call(tmp_path: Path) -> None:
    paths = make_paths(tmp_path, el_nino_snapshot=PASS_SNAPSHOT)
    actions.run_chain_now(paths, clock=_fixed_clock)
    second = actions.run_chain_now(paths, clock=_fixed_clock)  # same snapshot -> dedup, no double-fill
    assert second.ok is True
    assert len(audit.read_audit(paths.audit_log_path)) == 2


# ----------------------------------------------------------------------------- calibration re-run
def test_rerun_calibration_ok(tmp_path: Path) -> None:
    cal_path = tmp_path / "calib.json"
    cal_path.write_text(json.dumps(CALIB_DEFER), encoding="utf-8")
    paths = make_paths(tmp_path, calibration_artifact=cal_path)
    result = actions.rerun_calibration_readiness(paths, runner=runner_ok, clock=_fixed_clock)
    assert result.ok is True
    assert "calibration=DEFER" in result.summary  # re-read the golden after the run
    entries = audit.read_audit(paths.audit_log_path)
    assert len(entries) == 1 and entries[0].action == "rerun-calibration" and entries[0].ok is True


def test_rerun_calibration_failure_is_caught_and_audited(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    result = actions.rerun_calibration_readiness(paths, runner=runner_fail, clock=_fixed_clock)
    assert result.ok is False
    assert "exit=1" in result.summary
    entries = audit.read_audit(paths.audit_log_path)
    assert len(entries) == 1 and entries[0].ok is False


# ----------------------------------------------------------------------------- neo4j re-sync
def test_resync_neo4j_ok(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    result = actions.resync_neo4j(paths, runner=runner_ok, clock=_fixed_clock)
    assert result.ok is True and "synced" in result.summary
    assert audit.read_audit(paths.audit_log_path)[0].action == "resync-neo4j"


def test_resync_neo4j_failure_is_caught_and_audited(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    result = actions.resync_neo4j(paths, runner=runner_fail, clock=_fixed_clock)
    assert result.ok is False and "failed" in result.summary
    assert audit.read_audit(paths.audit_log_path)[0].ok is False


# ----------------------------------------------------------------------------- secrets never in audit
def test_no_credential_value_in_audit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    secret = "TOP_SECRET_ALPACA_VALUE_999"
    monkeypatch.setenv("ALPACA_API_KEY_ID", secret)
    monkeypatch.setenv("ALPACA_API_SECRET_KEY", secret)
    paths = make_paths(tmp_path, el_nino_snapshot=PASS_SNAPSHOT)
    r1 = actions.run_chain_now(paths, clock=_fixed_clock)
    r2 = actions.resync_neo4j(paths, runner=runner_fail, clock=_fixed_clock)
    blob = paths.audit_log_path.read_text(encoding="utf-8")
    blob += r1.summary + "".join(r1.detail) + r2.summary + "".join(r2.detail)
    assert secret not in blob


# ----------------------------------------------------------------------------- never-raise on audit fail
def test_action_never_raises_when_audit_write_fails(tmp_path: Path) -> None:
    blocker = tmp_path / "blocker"
    blocker.write_text("i am a file, not a directory", encoding="utf-8")
    # audit_log_path's parent is a FILE -> mkdir/write raises OSError; the action must catch + survive.
    paths = make_paths(tmp_path, audit_log_path=blocker / "audit.jsonl")
    result = actions.resync_neo4j(paths, runner=runner_ok, clock=_fixed_clock)  # must NOT raise
    assert result.ok is True  # the action itself still succeeded
    assert any("AUDIT-WRITE-FAILED" in line for line in result.detail)


# ----------------------------------------------------------------------------- redaction of leaked secrets
def test_subprocess_output_secret_is_redacted(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NEO4J_PASSWORD", "HUNTER2_SECRET_VALUE")

    def leaky_runner(_cmd: Sequence[str], _paths: OpsPaths) -> actions.ProcResult:
        return actions.ProcResult(0, "connecting with HUNTER2_SECRET_VALUE ... ok", "")

    paths = make_paths(tmp_path)
    result = actions.resync_neo4j(paths, runner=leaky_runner, clock=_fixed_clock)
    joined = "".join(result.detail)
    assert "HUNTER2_SECRET_VALUE" not in joined  # scrubbed from the Log-pane view
    assert "***" in joined


# ----------------------------------------------------------------------------- registry
def test_safe_actions_registry() -> None:
    assert set(actions.SAFE_ACTIONS) == {"run-chain-now", "rerun-calibration", "resync-neo4j"}
