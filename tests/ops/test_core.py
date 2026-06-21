"""Headless unit tests for the Operations Control Plane read-model (ADR-013 Step 1).

All tests are headless and mocked: no Textual rendering, no real network / Alpaca call, no OS scheduled
task registration. They exercise ``ops.core`` against crafted fixture artefacts + the committed
consumable snapshot fixture. Key invariants asserted: the read-model is pure (the preview never persists
state), fail-closed (malformed artefacts surface as an ``error`` field, never an exception), calibration
derives DEFER on a monochromatic corpus, the live plugs fail-closed to dormant without paper creds/host,
and **no credential value ever appears in any read-model output** (ADR-013 sec.6).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ops import core
from ops.core import OpsPaths

REPO = Path(__file__).resolve().parents[2]
PASS_SNAPSHOT = REPO / "tests" / "snapshot" / "fixtures" / "latest_snapshot_pass.json"
FAIL_SNAPSHOT = REPO / "tests" / "snapshot" / "fixtures" / "snapshot_fail.json"

LEDGER = {
    "ledger_schema_version": "0.1.0",
    "entries": [
        {
            "as_of": "2026-05-01T00:00:00+00:00", "operational_fingerprint": "f" * 64, "seq": 0,
            "snapshot_guards_digest": "d" * 64, "source_packet_id": "pkt-1",
            "source_snapshot_id": "snap-1", "triggered_guard": None, "verdict": "ADMIT",
        },
        {
            "as_of": "2026-05-02T00:00:00+00:00", "operational_fingerprint": "f" * 64, "seq": 1,
            "snapshot_guards_digest": "d" * 64, "source_packet_id": "pkt-2",
            "source_snapshot_id": "snap-2", "triggered_guard": "duplicate_ok", "verdict": "REJECT",
        },
    ],
}

PORTFOLIO = {
    "portfolio_schema_version": "0.1.0",
    "positions": [
        {"avg_cost": 100.0, "instrument": "GLD", "quantity": 2.0,
         "realized_pnl": 5.0, "unrealized_pnl": 1.0},
    ],
    "executions": [
        {"fill_model_version": "0.1.0", "fill_price": 100.0, "instrument": "GLD",
         "prior_portfolio_state_hash": "h" * 64, "quantity": 2.0, "seq": 0,
         "source_record_id": "rec-1", "source_snapshot_id": "snap-1"},
    ],
}

OPERATIONAL = {
    "as_of": "2026-05-01T00:00:00+00:00", "degraded": False, "halt": False,
    "instrument": "GLD", "source_version": "0.1.0", "tradeable": True, "venue_open": True,
}

CALIB_DEFER = {
    "decision_versions": {
        "taxonomy_version": "1.0.0", "decision_policy_version": "0.1.0",
        "classifier_version": "0.1.0", "feature_schema_version": "0.1.0",
    },
    "committed_real": {
        "distinct_snapshots": 1,
        "coverage": {"regimes": ["RESTRICTIVE_RATES"], "directions": ["AVOID"],
                     "statuses": ["pending"], "label_count": 3, "realized_count": 0},
    },
}

CALIB_ELIGIBLE = {
    "decision_versions": {"taxonomy_version": "1.0.0", "decision_policy_version": "0.1.0"},
    "committed_real": {
        "distinct_snapshots": 80,
        "coverage": {"regimes": ["A", "B", "C"], "directions": ["LONG", "AVOID"],
                     "statuses": ["realized"], "label_count": 100, "realized_count": 40},
    },
}


def _write(path: Path, payload: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def make_paths(tmp: Path, **over: Path) -> OpsPaths:
    """An OpsPaths defaulting every artefact to an ABSENT tmp path; override selectively."""
    base: dict[str, Path] = {
        "ledger_path": tmp / "absent_ledger.json",
        "portfolio_path": tmp / "absent_portfolio.json",
        "operational_capture_path": tmp / "absent_op.json",
        "el_nino_snapshot": tmp / "absent_snapshot.json",
        "producer_snapshot_dir": tmp / "absent_producer_dir",
        "calibration_artifact": tmp / "absent_calib.json",
        "daily_log_dir": tmp / "absent_logs",
        "audit_log_path": tmp / "audit_log.jsonl",
    }
    base.update(over)
    return OpsPaths(repo_root=REPO, **base)  # type: ignore[arg-type]


# ----------------------------------------------------------------------------- ledger
def test_ledger_view_absent(tmp_path: Path) -> None:
    view = core.ledger_view(make_paths(tmp_path))
    assert view.exists is False
    assert view.entry_count == 0
    assert view.error is None


def test_ledger_view_populated(tmp_path: Path) -> None:
    paths = make_paths(tmp_path, ledger_path=_write(tmp_path / "led.json", LEDGER))
    view = core.ledger_view(paths)
    assert view.exists and view.entry_count == 2
    assert view.latest_verdict == "REJECT"
    assert view.latest_triggered_guard == "duplicate_ok"
    assert view.latest_snapshot_id == "snap-2"
    assert view.verdict_counts == {"ADMIT": 1, "HOLD": 0, "REJECT": 1}
    assert view.state_hash and view.error is None


def test_ledger_view_malformed_surfaces_error(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{not valid json", encoding="utf-8")
    view = core.ledger_view(make_paths(tmp_path, ledger_path=bad))
    assert view.exists is True
    assert view.error is not None  # surfaced, NOT raised


# ----------------------------------------------------------------------------- portfolio
def test_portfolio_view_absent(tmp_path: Path) -> None:
    view = core.portfolio_view(make_paths(tmp_path))
    assert view.exists is False and view.position_count == 0 and view.error is None


def test_portfolio_view_populated(tmp_path: Path) -> None:
    paths = make_paths(tmp_path, portfolio_path=_write(tmp_path / "pf.json", PORTFOLIO))
    view = core.portfolio_view(paths)
    assert view.exists and view.position_count == 1 and view.open_position_count == 1
    assert view.realized_pnl == 5.0 and view.execution_count == 1
    assert view.positions[0].instrument == "GLD" and view.error is None


def test_portfolio_view_malformed_surfaces_error(tmp_path: Path) -> None:
    bad = _write(tmp_path / "pf_bad.json", {"positions": "not-a-list"})
    view = core.portfolio_view(make_paths(tmp_path, portfolio_path=bad))
    assert view.exists is True and view.error is not None


# ----------------------------------------------------------------------------- operational
def test_operational_view_absent_is_default_closed(tmp_path: Path) -> None:
    view = core.operational_view(make_paths(tmp_path))
    assert view.tradeable is False  # default-closed
    assert "absent" in view.source


def test_operational_view_captured_file(tmp_path: Path) -> None:
    paths = make_paths(tmp_path, operational_capture_path=_write(tmp_path / "op.json", OPERATIONAL))
    view = core.operational_view(paths)
    assert view.tradeable is True and view.venue_open is True and view.source == "captured file"


# ----------------------------------------------------------------------------- preview (purity!)
def test_decision_preview_is_pure_no_persistence(tmp_path: Path) -> None:
    paths = make_paths(tmp_path, el_nino_snapshot=PASS_SNAPSHOT)
    preview = core.decision_preview(paths)
    assert preview.available and preview.consumable
    assert preview.verdict in {"ADMIT", "HOLD", "REJECT"}
    assert preview.regime and preview.direction
    assert len(preview.guards) == 6  # the full six-guard block
    # READ-ONLY: the preview ran run_sequence (pure) and persisted NOTHING.
    assert not paths.ledger_path.exists()
    assert not paths.portfolio_path.exists()


def test_decision_preview_non_consumable(tmp_path: Path) -> None:
    paths = make_paths(tmp_path, el_nino_snapshot=FAIL_SNAPSHOT)
    preview = core.decision_preview(paths)
    assert preview.available is True and preview.consumable is False
    assert "not consumable" in preview.note


def test_decision_preview_no_snapshot(tmp_path: Path) -> None:
    preview = core.decision_preview(make_paths(tmp_path))
    assert preview.available is False and preview.consumable is False


def _raise_oserror(*_args: object, **_kw: object) -> Path:
    raise OSError("permission denied")


def test_decision_preview_survives_producer_oserror(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An exists-but-unreadable producer dir must not crash the read-model; it falls back to el_nino."""
    producer = tmp_path / "producer"
    producer.mkdir()
    monkeypatch.setattr(core, "find_latest_snapshot", _raise_oserror)
    paths = make_paths(tmp_path, producer_snapshot_dir=producer, el_nino_snapshot=PASS_SNAPSHOT)
    preview = core.decision_preview(paths)  # must NOT raise
    assert preview.consumable is True  # fell back to the el_nino pointer


def test_process_infos_survives_producer_oserror(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    producer = tmp_path / "producer"
    producer.mkdir()
    monkeypatch.setattr(core, "find_latest_snapshot", _raise_oserror)
    infos = {p.name: p for p in core.process_infos(
        make_paths(tmp_path, producer_snapshot_dir=producer), task_fetcher=None,
    )}
    assert infos["producer-freshness"].status == "error"  # surfaced, not raised


# ----------------------------------------------------------------------------- calibration
def test_calibration_readiness_defer(tmp_path: Path) -> None:
    paths = make_paths(tmp_path, calibration_artifact=_write(tmp_path / "c.json", CALIB_DEFER))
    cal = core.calibration_readiness(paths)
    assert cal.available and cal.overall == "DEFER" and cal.eligible is False
    assert cal.n_committed == 1 and cal.realized_count == 0
    assert all(g.status == "fail" for g in cal.per_gate)
    assert "never bumps" in cal.note


def test_calibration_readiness_eligible_branch(tmp_path: Path) -> None:
    paths = make_paths(tmp_path, calibration_artifact=_write(tmp_path / "c.json", CALIB_ELIGIBLE))
    cal = core.calibration_readiness(paths)
    assert cal.overall.startswith("ELIGIBLE") and cal.eligible is True
    assert all(g.status == "pass" for g in cal.per_gate)


def test_calibration_eligible_flag_matches_overall(tmp_path: Path) -> None:
    # the discrete flag and the display string must always agree (the gated bump branches on the flag)
    for payload, expect in ((CALIB_DEFER, False), (CALIB_ELIGIBLE, True)):
        cal = core.calibration_readiness(
            make_paths(tmp_path, calibration_artifact=_write(tmp_path / "c.json", payload))
        )
        assert cal.eligible is expect
        assert cal.overall.startswith("DEFER") is (not expect)


def test_calibration_readiness_absent_defers(tmp_path: Path) -> None:
    cal = core.calibration_readiness(make_paths(tmp_path))
    assert cal.available is False and cal.overall == "DEFER"


def test_gate_board_adr011_all_closed(tmp_path: Path) -> None:
    cal = core.calibration_readiness(make_paths(tmp_path))
    board = core.gate_board(cal)
    assert {g.gate_id for g in board.adr011} == {"a", "b", "c", "d", "e", "f"}
    assert all(g.status == "closed" for g in board.adr011)
    assert board.adr012 == cal.per_gate


# ----------------------------------------------------------------------------- plugs (fail-closed)
def test_plugs_dormant_without_creds(monkeypatch: pytest.MonkeyPatch) -> None:
    for var in ("ALPACA_API_KEY_ID", "ALPACA_API_SECRET_KEY", "ALPACA_PAPER_BASE_URL"):
        monkeypatch.delenv(var, raising=False)
    plugs = core.plug_statuses()
    assert {p.status for p in plugs} == {"dormant"}


def test_plugs_creds_present_with_paper_host(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALPACA_API_KEY_ID", "FAKEKEY")
    monkeypatch.setenv("ALPACA_API_SECRET_KEY", "FAKESECRET")
    monkeypatch.delenv("ALPACA_PAPER_BASE_URL", raising=False)  # default = paper host
    plugs = core.plug_statuses()
    assert {p.status for p in plugs} == {"creds-present"}


def test_plugs_dormant_on_non_paper_host(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALPACA_API_KEY_ID", "FAKEKEY")
    monkeypatch.setenv("ALPACA_API_SECRET_KEY", "FAKESECRET")
    monkeypatch.setenv("ALPACA_PAPER_BASE_URL", "https://evil.example.com")
    plugs = core.plug_statuses()
    assert {p.status for p in plugs} == {"dormant"}  # non-paper host refused -> fail-closed


# ----------------------------------------------------------------------------- secrets never shown
def test_no_credential_value_in_any_output(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    secret_key = "SUPER_SECRET_KEY_ID_ZZZ"
    secret_val = "SUPER_SECRET_VALUE_QQQ"
    monkeypatch.setenv("ALPACA_API_KEY_ID", secret_key)
    monkeypatch.setenv("ALPACA_API_SECRET_KEY", secret_val)
    monkeypatch.delenv("ALPACA_PAPER_BASE_URL", raising=False)
    paths = make_paths(
        tmp_path,
        el_nino_snapshot=PASS_SNAPSHOT,
        ledger_path=_write(tmp_path / "l.json", LEDGER),
        portfolio_path=_write(tmp_path / "p.json", PORTFOLIO),
        calibration_artifact=_write(tmp_path / "c.json", CALIB_DEFER),
    )
    dash = core.assemble_dashboard(paths)
    # creds ARE present (so this is a meaningful negative) ...
    assert {p.status for p in dash.plugs} == {"creds-present"}
    # ... yet NO credential value appears anywhere in the serialized read-model or the text render.
    blob = json.dumps(dash.to_dict()) + "\n".join(core.render_text_dashboard(dash))
    assert secret_key not in blob
    assert secret_val not in blob


# ----------------------------------------------------------------------------- processes
def test_process_infos_not_queried_without_fetcher(tmp_path: Path) -> None:
    infos = {p.name: p for p in core.process_infos(make_paths(tmp_path), task_fetcher=None)}
    assert infos["daily-chain-task"].status == "not-queried"
    assert infos["producer-freshness"].status == "absent"


def test_process_infos_registered_with_fetcher(tmp_path: Path) -> None:
    def fake_fetcher(name: str) -> dict[str, object]:
        return {"LastRunTime": "2026-06-18T23:45:00", "NextRunTime": "2026-06-19T23:45:00",
                "LastTaskResult": 0}

    infos = {p.name: p for p in core.process_infos(make_paths(tmp_path), task_fetcher=fake_fetcher)}
    assert infos["daily-chain-task"].status == "registered"
    assert "2026-06-18" in infos["daily-chain-task"].detail


def test_process_infos_not_registered_when_fetcher_returns_none(tmp_path: Path) -> None:
    infos = {p.name: p for p in core.process_infos(make_paths(tmp_path), task_fetcher=lambda _n: None)}
    assert infos["daily-chain-task"].status == "not-registered"


def test_process_infos_producer_freshness(tmp_path: Path) -> None:
    producer = tmp_path / "producer"
    producer.mkdir()
    _write(producer / "snapshot_2026-06-15__abcd1234.json", {"x": 1})
    infos = {p.name: p for p in core.process_infos(
        make_paths(tmp_path, producer_snapshot_dir=producer), task_fetcher=None,
    )}
    assert infos["producer-freshness"].status == "ok"
    assert "snapshot_2026-06-15__abcd1234.json" in infos["producer-freshness"].detail


# ----------------------------------------------------------------------------- policy / dashboard
def test_policy_versions() -> None:
    pol = core.policy_versions()
    assert pol.runtime_policy_version == "0.2.0"
    assert pol.execution_policy_version == "0.1.0"
    assert pol.fill_model_version == "0.1.0"
    assert len(pol.runtime_policy_fingerprint) == 16


def test_assemble_dashboard_paper_only_and_serializable(tmp_path: Path) -> None:
    paths = make_paths(
        tmp_path, el_nino_snapshot=PASS_SNAPSHOT,
        calibration_artifact=_write(tmp_path / "c.json", CALIB_DEFER),
    )
    dash = core.assemble_dashboard(paths)
    assert dash.pipeline.paper_only is True  # ALWAYS, never weakened
    assert json.dumps(dash.to_dict())  # fully serializable
    assert core.render_text_dashboard(dash)  # renders non-empty


def test_assemble_dashboard_never_persists(tmp_path: Path) -> None:
    paths = make_paths(tmp_path, el_nino_snapshot=PASS_SNAPSHOT)
    core.assemble_dashboard(paths)
    # The whole read-only pass created / mutated NO runtime artefact.
    assert not paths.ledger_path.exists()
    assert not paths.portfolio_path.exists()
    assert not paths.operational_capture_path.exists()
