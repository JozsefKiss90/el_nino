"""TEST-024 — chain orchestrator determinism + IO round-trip (MOD-010).

Byte-identical end-to-end replay through ``run_sequence`` (all five record types + ending ledger +
portfolio state), end-to-end admission idempotency, the captured-input replay invariant (the replay
path never reads ``os.environ``), and the ``run_once`` IO shell: persist (portfolio-then-ledger) +
reload round-trip, the non-consumable → ``None`` fail-closed branch, and on-disk idempotency.
"""

from __future__ import annotations

import json
from pathlib import Path

from execution.runtime import load_portfolio
from gold.paper_runtime.models import Verdict
from gold.paper_runtime.runtime import load_ledger
from snapshot.snapshot_consumer import consume
from snapshot.snapshot_consumer.models import Snapshot

from orchestration import run_once, run_sequence

_REPO_ROOT = Path(__file__).resolve().parents[2]
_REAL = _REPO_ROOT / "tests" / "snapshot" / "fixtures" / "latest_snapshot_pass.json"
_FAIL = _REPO_ROOT / "tests" / "snapshot" / "fixtures" / "snapshot_fail.json"


def _snap() -> Snapshot:
    snap = consume(_REAL)
    assert snap is not None
    return snap


def test_sequence_byte_identical_replay() -> None:
    seq = [_snap(), _snap(), _snap()]
    results_a, ledger_a, pf_a = run_sequence(seq)
    results_b, ledger_b, pf_b = run_sequence(seq)
    dump_a = [json.dumps(r.to_dict(), sort_keys=True) for r in results_a]
    dump_b = [json.dumps(r.to_dict(), sort_keys=True) for r in results_b]
    assert dump_a == dump_b
    assert ledger_a.state_hash() == ledger_b.state_hash()
    assert pf_a.state_hash() == pf_b.state_hash()


def test_end_to_end_idempotency_through_sequence() -> None:
    # First presentation admits; every re-presentation of the same snapshot_id REJECTs on duplicate_ok
    # (no second admit) and never executes (no double-fill). Portfolio is stable after the first step.
    results, _ledger, _pf = run_sequence([_snap(), _snap(), _snap()])
    verdicts = [r.runtime_record.verdict for r in results]
    assert verdicts == [Verdict.ADMIT, Verdict.REJECT, Verdict.REJECT]
    assert all(r.runtime_record.triggered_guard == "duplicate_ok" for r in results[1:])
    assert results[1].execution_record is None and results[2].execution_record is None
    assert results[1].portfolio.state_hash() == results[0].portfolio.state_hash()
    assert results[2].portfolio.state_hash() == results[0].portfolio.state_hash()


def test_replay_path_ignores_os_environ(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    # The captured guard config is passed explicitly; the replay path never reads env. Poisoning the
    # guardrail env vars must not change the deterministic records.
    baseline = run_sequence([_snap()])[0][0].to_dict()
    for name in ("MAX_TRADE_SIZE", "MAX_TRADES_PER_DAY", "MAX_POSITION_PCT", "MAX_POSITIONS", "DAILY_LOSS_CAP"):
        monkeypatch.setenv(name, "0.000001")
    poisoned = run_sequence([_snap()])[0][0].to_dict()
    assert json.dumps(baseline, sort_keys=True) == json.dumps(poisoned, sort_keys=True)


def test_run_once_persists_and_reloads(tmp_path: Path) -> None:
    ledger_path = tmp_path / "chain" / "runtime_ledger.json"
    portfolio_path = tmp_path / "chain" / "portfolio_state.json"
    result = run_once(_REAL, ledger_path, portfolio_path)
    assert result is not None
    assert result.runtime_record.verdict is Verdict.ADMIT
    # both state files were written and reload to the exact persisted state.
    assert ledger_path.exists() and portfolio_path.exists()
    assert load_ledger(ledger_path).state_hash() == result.ledger.state_hash()
    assert load_portfolio(portfolio_path).state_hash() == result.portfolio.state_hash()


def test_run_once_is_idempotent_on_disk(tmp_path: Path) -> None:
    ledger_path = tmp_path / "runtime_ledger.json"
    portfolio_path = tmp_path / "portfolio_state.json"
    first = run_once(_REAL, ledger_path, portfolio_path)
    second = run_once(_REAL, ledger_path, portfolio_path)  # re-present the banked snapshot
    assert first is not None and second is not None
    assert first.runtime_record.verdict is Verdict.ADMIT
    assert second.runtime_record.verdict is Verdict.REJECT
    assert second.runtime_record.triggered_guard == "duplicate_ok"
    # the portfolio on disk is unchanged by the duplicate (no double-fill).
    assert load_portfolio(portfolio_path).state_hash() == first.portfolio.state_hash()


def test_run_once_non_consumable_returns_none(tmp_path: Path) -> None:
    ledger_path = tmp_path / "runtime_ledger.json"
    portfolio_path = tmp_path / "portfolio_state.json"
    result = run_once(_FAIL, ledger_path, portfolio_path)
    assert result is None
    # nothing persisted for a non-consumable snapshot (Layer-3 outputs nothing).
    assert not ledger_path.exists() and not portfolio_path.exists()
