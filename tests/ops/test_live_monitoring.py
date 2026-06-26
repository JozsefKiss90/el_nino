"""Headless tests for the Operations Control Plane LIVE read-model + governed adopt (ADR-013 / ADR-014).

ISSUE-07. All tests are headless + mocked: no Textual rendering, no network / Alpaca call. They exercise
the additive LIVE surfaces in ``ops.core`` against fixture ``*.live`` artefacts and the one governed Tier-3
``adopt-broker-position`` action in ``ops.gated``. Key invariants asserted:

- the live ledger / portfolio views read the **separate** live files and are **independent** of the SIM
  views (live empty when no live run; the SIM panels unchanged);
- the live portfolio surfaces **realized P&L** (the REAL paper P&L), distinct from the accumulate-only SIM
  portfolio (a model number, NOT performance);
- ``reconcile_view`` surfaces DISCREPANCY markers + the DERIVED ``execution_refused`` / ``adoptable`` state;
- the SIM/LIVE badging metadata is correct (the two are never confusable);
- **no credential value appears** in any live read-model output (ADR-013 §6);
- the adopt action is **append-only**, **precondition-gated** (refuses with nothing to adopt), heals the
  discrepancy (clears the refuse), audits exactly once, and NEVER raises.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ops import audit, core, gated
from ops.core import OpsPaths

REPO = Path(__file__).resolve().parents[2]
PASS_SNAPSHOT = REPO / "tests" / "snapshot" / "fixtures" / "latest_snapshot_pass.json"

LIVE_LEDGER = {
    "ledger_schema_version": "0.1.0",
    "entries": [
        {"as_of": "2026-06-25T00:00:00+00:00", "operational_fingerprint": "f" * 64, "seq": 0,
         "snapshot_guards_digest": "d" * 64, "source_packet_id": "pkt-live-1",
         "source_snapshot_id": "snap-live-1", "triggered_guard": None, "verdict": "ADMIT"},
    ],
}

# A live portfolio with a CLOSED position — REAL paper P&L realized on the exit (the live SELL-fold).
LIVE_PORTFOLIO_REALIZED = {
    "portfolio_schema_version": "0.2.0",
    "positions": [
        {"avg_cost": 0.0, "instrument": "GLD", "quantity": 0.0,
         "realized_pnl": 12.5, "unrealized_pnl": 0.0},
    ],
    "executions": [
        {"fill_model_version": "0.1.0", "fill_price": 100.0, "instrument": "GLD",
         "prior_portfolio_state_hash": "h" * 64, "quantity": 3.0, "seq": 0,
         "source_record_id": "rec-live-1", "source_snapshot_id": "snap-live-1",
         "as_of": "2026-06-25T00:00:00+00:00"},
    ],
}

# A live portfolio with an UNHEALED unexplained-position discrepancy (FLAT-time broker position with no
# local lineage) + an in-flight pending order. This is the state the governed adopt action heals.
LIVE_PORTFOLIO_DISCREPANCY = {
    "portfolio_schema_version": "0.2.0",
    "positions": [],
    "executions": [],
    "reconciles": [
        {"as_of": "2026-06-25T00:00:00+00:00", "instrument": "GLD",
         "marker": "discrepancy:unexplained_position", "observed_avg_price": 101.5,
         "observed_qty": 3.0, "seq": 0, "source_snapshot_id": "snap-live-1"},
    ],
    "pending": [
        {"as_of": "2026-06-25T00:00:00+00:00", "client_order_id": "eln-buy-abcd1234",
         "instrument": "GLD", "requested_qty": 0.0, "seq": 0, "side": "buy",
         "source_record_id": "rec-live-1", "source_snapshot_id": "snap-live-1"},
    ],
}

# A live portfolio that ALREADY realized P&L (flat GLD, realized 12.5 — the residue a live SELL-fold
# leaves) AND now carries a fresh unexplained-position discrepancy. Adopting must CARRY the realized P&L
# forward (regression for the review finding: adopt must not wipe the LIVE real-paper-P&L track record).
LIVE_PORTFOLIO_REALIZED_THEN_DISCREPANCY = {
    "portfolio_schema_version": "0.2.0",
    "positions": [
        {"avg_cost": 0.0, "instrument": "GLD", "quantity": 0.0,
         "realized_pnl": 12.5, "unrealized_pnl": 0.0},
    ],
    "executions": [
        {"fill_model_version": "0.1.0", "fill_price": 100.0, "instrument": "GLD",
         "prior_portfolio_state_hash": "h" * 64, "quantity": 3.0, "seq": 0,
         "source_record_id": "rec-live-1", "source_snapshot_id": "snap-live-1",
         "as_of": "2026-06-25T00:00:00+00:00"},
    ],
    "reconciles": [
        {"as_of": "2026-06-25T00:00:00+00:00", "instrument": "GLD",
         "marker": "discrepancy:unexplained_position", "observed_avg_price": 101.5,
         "observed_qty": 3.0, "seq": 0, "source_snapshot_id": "snap-live-2"},
    ],
}

# A MIXED multi-instrument discrepancy: GLD unexplained-position (adoptable) + SLV foreign order (not).
# Adopt heals only the GLD one, so the banner must NOT claim it "clears the refuse".
LIVE_PORTFOLIO_MIXED_DISCREPANCY = {
    "portfolio_schema_version": "0.2.0",
    "positions": [],
    "executions": [],
    "reconciles": [
        {"as_of": "2026-06-25T00:00:00+00:00", "instrument": "GLD",
         "marker": "discrepancy:unexplained_position", "observed_avg_price": 101.5,
         "observed_qty": 3.0, "seq": 0, "source_snapshot_id": "snap-live-1"},
        {"as_of": "2026-06-25T00:00:00+00:00", "instrument": "SLV",
         "marker": "discrepancy:unexpected_open_order", "observed_avg_price": 0.0,
         "observed_qty": 0.0, "seq": 1, "source_snapshot_id": "snap-live-1"},
    ],
}

# A live portfolio whose only standing discrepancy is a FOREIGN open order (NOT position-adoptable).
LIVE_PORTFOLIO_FOREIGN_ORDER = {
    "portfolio_schema_version": "0.2.0",
    "positions": [],
    "executions": [],
    "reconciles": [
        {"as_of": "2026-06-25T00:00:00+00:00", "instrument": "GLD",
         "marker": "discrepancy:unexpected_open_order", "observed_avg_price": 0.0,
         "observed_qty": 0.0, "seq": 0, "source_snapshot_id": "snap-live-1"},
    ],
}

SIM_PORTFOLIO = {
    "portfolio_schema_version": "0.2.0",
    "positions": [
        {"avg_cost": 100.0, "instrument": "GLD", "quantity": 2.0,
         "realized_pnl": 0.0, "unrealized_pnl": 1.0},
    ],
    "executions": [
        {"fill_model_version": "0.1.0", "fill_price": 100.0, "instrument": "GLD",
         "prior_portfolio_state_hash": "h" * 64, "quantity": 2.0, "seq": 0,
         "source_record_id": "rec-1", "source_snapshot_id": "snap-1"},
    ],
}


def _write(path: Path, payload: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def make_paths(tmp: Path, **over: Path) -> OpsPaths:
    """OpsPaths over a tmp ``runtime/chain`` so the ``*.live`` siblings derive correctly."""
    chain = tmp / "runtime" / "chain"
    base: dict[str, Path] = {
        "repo_root": REPO,
        "ledger_path": chain / "runtime_ledger.json",
        "portfolio_path": chain / "portfolio_state.json",
        "operational_capture_path": chain / "operational_capture.json",
        "el_nino_snapshot": tmp / "absent_snapshot.json",
        "producer_snapshot_dir": tmp / "absent_producer",
        "calibration_artifact": tmp / "absent_calib.json",
        "daily_log_dir": tmp / "absent_logs",
        "audit_log_path": tmp / "runtime" / "ops" / "audit.jsonl",
    }
    base.update(over)
    return OpsPaths(**base)  # type: ignore[arg-type]


# ----------------------------------------------------------------------------- live ledger / portfolio
def test_live_ledger_view_reads_the_live_file(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _write(paths.live_ledger_path, LIVE_LEDGER)
    view = core.live_ledger_view(paths)
    assert view.exists and view.entry_count == 1 and view.latest_verdict == "ADMIT"
    assert view.verdict_counts == {"ADMIT": 1, "HOLD": 0, "REJECT": 0}
    assert view.state_hash and view.error is None


def test_live_portfolio_view_surfaces_realized_pnl(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _write(paths.live_portfolio_path, LIVE_PORTFOLIO_REALIZED)
    view = core.live_portfolio_view(paths)
    assert view.exists and view.realized_pnl == 12.5  # REAL paper P&L realized on the exit
    assert view.execution_count == 1 and view.open_position_count == 0
    assert view.positions[0].instrument == "GLD" and view.error is None


def test_live_views_absent_when_no_live_run(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    assert core.live_ledger_view(paths).exists is False
    assert core.live_portfolio_view(paths).exists is False
    assert core.reconcile_view(paths).exists is False
    assert core.pending_orders_view(paths).exists is False


def test_sim_and_live_views_are_independent(tmp_path: Path) -> None:
    """A SIM portfolio present must NOT leak into the live views, and vice-versa (separate files)."""
    paths = make_paths(tmp_path)
    _write(paths.portfolio_path, SIM_PORTFOLIO)             # SIM file present
    _write(paths.live_portfolio_path, LIVE_PORTFOLIO_REALIZED)  # LIVE file present, different content
    sim, live = core.portfolio_view(paths), core.live_portfolio_view(paths)
    assert sim.realized_pnl == 0.0 and sim.open_position_count == 1   # SIM: accumulate-only, open
    assert live.realized_pnl == 12.5 and live.open_position_count == 0  # LIVE: realized, closed
    assert sim.state_hash != live.state_hash


def test_live_portfolio_malformed_surfaces_error(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    paths.live_portfolio_path.parent.mkdir(parents=True, exist_ok=True)
    paths.live_portfolio_path.write_text("{not valid", encoding="utf-8")
    view = core.live_portfolio_view(paths)
    assert view.exists is True and view.error is not None  # surfaced, NOT raised


# ----------------------------------------------------------------------------- reconcile / discrepancy
def test_reconcile_view_surfaces_discrepancy_and_refused(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _write(paths.live_portfolio_path, LIVE_PORTFOLIO_DISCREPANCY)
    rec = core.reconcile_view(paths)
    assert rec.exists and rec.entry_count == 1 and rec.discrepancy_count == 1
    obs = rec.observations[0]
    assert obs.is_discrepancy and obs.marker == "discrepancy:unexplained_position"
    assert obs.observed_qty == 3.0 and obs.observed_avg_price == 101.5
    assert rec.execution_refused is True
    assert rec.refuse_reason is not None and "unexplained_position" in rec.refuse_reason
    assert rec.adoptable is True  # an unexplained-position discrepancy → governed adopt available


def test_reconcile_view_foreign_order_refused_but_not_adoptable(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _write(paths.live_portfolio_path, LIVE_PORTFOLIO_FOREIGN_ORDER)
    rec = core.reconcile_view(paths)
    assert rec.execution_refused is True          # a foreign open order still refuses execution
    assert rec.adoptable is False                 # ...but adopt heals POSITION discrepancies only
    assert core.adoptable_discrepancy(paths) is None


def test_reconcile_view_not_refused_when_no_discrepancy(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _write(paths.live_portfolio_path, LIVE_PORTFOLIO_REALIZED)  # has executions, no reconciles
    rec = core.reconcile_view(paths)
    assert rec.exists and rec.entry_count == 0
    assert rec.execution_refused is False and rec.adoptable is False


def test_reconcile_view_malformed_surfaces_error(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    paths.live_portfolio_path.parent.mkdir(parents=True, exist_ok=True)
    paths.live_portfolio_path.write_text("{nope", encoding="utf-8")
    rec = core.reconcile_view(paths)
    assert rec.exists is True and rec.error is not None and rec.execution_refused is False


# ----------------------------------------------------------------------------- pending orders
def test_pending_orders_view(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _write(paths.live_portfolio_path, LIVE_PORTFOLIO_DISCREPANCY)
    pend = core.pending_orders_view(paths)
    assert pend.exists and pend.order_count == 1
    o = pend.orders[0]
    assert o.side == "buy" and o.instrument == "GLD" and o.client_order_id == "eln-buy-abcd1234"


# ----------------------------------------------------------------------------- live-state strip
def test_live_state_refused_banner(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _write(paths.live_portfolio_path, LIVE_PORTFOLIO_DISCREPANCY)
    dash = core.assemble_dashboard(paths)
    ls = dash.live_state
    assert ls.execution_refused is True and ls.adoptable is True
    assert ls.banner is not None and "REFUSED" in ls.banner
    assert "advisory" in ls.banner  # the DERIVED refuse is honestly labelled advisory (re-checked live)


def test_live_state_kill_switch_banner(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    gated.set_operator_halt(paths)  # engage the kill switch (writes the marker)
    dash = core.assemble_dashboard(paths)
    ls = dash.live_state
    assert ls.kill_switch_engaged is True
    assert ls.banner is not None and "KILL SWITCH" in ls.banner


def test_live_state_clear_when_idle(tmp_path: Path) -> None:
    dash = core.assemble_dashboard(make_paths(tmp_path))
    ls = dash.live_state
    assert ls.execution_refused is False and ls.kill_switch_engaged is False and ls.banner is None


# ----------------------------------------------------------------------------- badging (never confusable)
def test_badging_metadata_in_render(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _write(paths.portfolio_path, SIM_PORTFOLIO)
    _write(paths.live_portfolio_path, LIVE_PORTFOLIO_REALIZED)
    dash = core.assemble_dashboard(paths)
    blob = "\n".join(core.render_text_dashboard(dash))
    assert core.SIM_BADGE in blob and core.LIVE_BADGE in blob
    # the SIM portfolio value is explicitly NOT a track record; the LIVE one IS the real paper P&L.
    assert "NOT performance" in core.SIM_BADGE
    assert "model value, never a P&L track record" in blob
    assert "real paper P&L" in core.LIVE_BADGE
    assert "REAL paper P&L" in blob  # the LIVE section body labels the live portfolio as the REAL P&L
    assert "SIM ledger=" in blob  # the always-on pipeline headline figures are SIM-scoped (not the live book)
    # SIM and LIVE sections are distinct headers (never interleaved into one panel).
    assert blob.index(f"[{core.SIM_BADGE}]") < blob.index(f"[{core.LIVE_BADGE}]")


def test_assemble_dashboard_live_fields_serializable(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _write(paths.live_portfolio_path, LIVE_PORTFOLIO_DISCREPANCY)
    _write(paths.live_ledger_path, LIVE_LEDGER)
    dash = core.assemble_dashboard(paths)
    assert dash.pipeline.paper_only is True
    d = dash.to_dict()
    assert json.dumps(d)  # fully serializable, including the live sub-views
    assert d["reconcile"]["execution_refused"] is True
    assert d["live_portfolio"]["exists"] is True


# ----------------------------------------------------------------------------- secrets never shown (live)
def test_no_credential_value_in_live_output(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    secret_key = "LIVE_SECRET_KEY_ID_ZZZ"
    secret_val = "LIVE_SECRET_VALUE_QQQ"
    monkeypatch.setenv("ALPACA_API_KEY_ID", secret_key)
    monkeypatch.setenv("ALPACA_API_SECRET_KEY", secret_val)
    monkeypatch.delenv("ALPACA_PAPER_BASE_URL", raising=False)  # default = paper host
    paths = make_paths(tmp_path)
    _write(paths.live_portfolio_path, LIVE_PORTFOLIO_DISCREPANCY)
    _write(paths.live_ledger_path, LIVE_LEDGER)
    dash = core.assemble_dashboard(paths)
    assert dash.live_state.plug_status == "creds-present"  # creds ARE present (meaningful negative)
    blob = json.dumps(dash.to_dict()) + "\n".join(core.render_text_dashboard(dash))
    assert secret_key not in blob and secret_val not in blob


# ----------------------------------------------------------------------------- governed adopt (Tier 3)
def test_adopt_refuses_when_nothing_to_adopt(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)  # no live portfolio at all
    result = gated.adopt_broker_position(paths)
    assert result.ok is True and result.executed is False  # benign no-op (precondition not met)
    assert "no unhealed" in result.summary
    assert not paths.live_portfolio_path.exists()  # nothing written
    entries = audit.read_audit(paths.audit_log_path)
    assert len(entries) == 1 and entries[0].action == "adopt-broker-position"


def test_adopt_refuses_on_non_position_discrepancy(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _write(paths.live_portfolio_path, LIVE_PORTFOLIO_FOREIGN_ORDER)
    before = paths.live_portfolio_path.read_bytes()
    result = gated.adopt_broker_position(paths)
    assert result.executed is False  # a foreign-order discrepancy is not position-adoptable
    assert paths.live_portfolio_path.read_bytes() == before  # untouched


def test_adopt_heals_unexplained_position_append_only(tmp_path: Path) -> None:
    from execution.runtime import load_portfolio

    paths = make_paths(tmp_path)
    _write(paths.live_portfolio_path, LIVE_PORTFOLIO_DISCREPANCY)

    result = gated.adopt_broker_position(paths)
    assert result.ok is True and result.executed is True and "ADOPTED" in result.summary

    pf = load_portfolio(paths.live_portfolio_path)
    # the observed broker position is now local (so the next FLAT cycle can sell to close)
    pos = pf.position("GLD")
    assert pos is not None and pos.quantity == 3.0 and pos.avg_cost == 101.5 and pos.realized_pnl == 0.0
    # APPEND-ONLY: the original discrepancy entry is preserved; exactly one adopt entry appended.
    assert len(pf.reconciles) == 2
    assert pf.reconciles[0].marker == "discrepancy:unexplained_position"
    assert pf.reconciles[1].marker == "adopt:reconcile-adopt"
    assert len(pf.executions) == 0  # adopt is NOT a fake execution
    # the refuse is cleared — the read-model no longer reports refused/adoptable.
    rec = core.reconcile_view(paths)
    assert rec.execution_refused is False and rec.adoptable is False
    assert audit.read_audit(paths.audit_log_path)[-1].ok is True


def test_adopt_carries_forward_prior_realized_pnl(tmp_path: Path) -> None:
    """Adopting over a flat-but-realized position must NOT wipe the accumulated LIVE realized P&L."""
    from execution.runtime import load_portfolio

    paths = make_paths(tmp_path)
    _write(paths.live_portfolio_path, LIVE_PORTFOLIO_REALIZED_THEN_DISCREPANCY)
    assert core.live_portfolio_view(paths).realized_pnl == 12.5  # before: the prior round-trip's P&L

    result = gated.adopt_broker_position(paths)
    assert result.executed is True

    pf = load_portfolio(paths.live_portfolio_path)
    pos = pf.position("GLD")
    assert pos is not None and pos.quantity == 3.0 and pos.avg_cost == 101.5
    assert pos.realized_pnl == 12.5  # CARRIED FORWARD, not reset to 0
    assert core.live_portfolio_view(paths).realized_pnl == 12.5  # the LIVE track record is intact


def test_mixed_discrepancy_banner_does_not_overstate_adopt(tmp_path: Path) -> None:
    """With a second (non-adoptable) discrepancy present, the banner must not claim adopt clears the refuse."""
    paths = make_paths(tmp_path)
    _write(paths.live_portfolio_path, LIVE_PORTFOLIO_MIXED_DISCREPANCY)
    rec = core.reconcile_view(paths)
    assert rec.refusing_count == 2 and rec.adoptable is True
    ls = core.assemble_dashboard(paths).live_state
    assert ls.banner is not None
    assert "clears the refuse" not in ls.banner  # adopt heals only the position discrepancy, not all
    assert "resolved broker-side" in ls.banner


def test_adopt_precondition_lines(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    assert "FAILS" in gated.precondition_line(paths, "adopt-broker-position")
    _write(paths.live_portfolio_path, LIVE_PORTFOLIO_DISCREPANCY)
    line = gated.precondition_line(paths, "adopt-broker-position")
    assert "OK" in line and "GLD" in line


def test_adopt_never_raises_on_malformed_live_portfolio(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    paths.live_portfolio_path.parent.mkdir(parents=True, exist_ok=True)
    paths.live_portfolio_path.write_text("{broken", encoding="utf-8")
    result = gated.adopt_broker_position(paths)  # must NOT raise
    # a malformed live portfolio yields no adoptable discrepancy → benign no-op refusal
    assert result.executed is False


def test_adopt_in_gated_registry() -> None:
    assert gated.GATED_ACTIONS["adopt-broker-position"] is gated.adopt_broker_position
