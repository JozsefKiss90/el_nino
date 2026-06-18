"""Tests for the Gold Forward-Return Labeler (MOD-009 / BENCH-005, ADR-012 gate G3 prereq).

The real corpus is monochromatic (1/12 regimes, 1/4 directions, no realizable forward return
yet), so correctness is established SYNTHETICALLY: the return math, the horizon / gap /
nearest-exit selection, the realized/pending/no_exit_in_tolerance statuses, and per-direction
correctness across all four directions and multiple regimes. Plus: the committed artifact stays
in sync, the committed real corpus dedups to one honest PIT point, and — the non-negotiable —
the decision chain never imports the labeler (look-ahead containment).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_BENCH_DIR = _REPO_ROOT / "benchmarks" / "calibration"
if str(_BENCH_DIR) not in sys.path:
    sys.path.insert(0, str(_BENCH_DIR))

import run_forward_return_labels as flh  # type: ignore[import-not-found]  # noqa: E402


# --------------------------------------------------------------------------------------
# Determinism + artifact-in-sync (BENCH idiom)
# --------------------------------------------------------------------------------------
def test_report_is_deterministic() -> None:
    a = flh.build_report()
    b = flh.build_report()
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_committed_artifact_in_sync() -> None:
    artifact = json.loads(flh.ARTIFACT_PATH.read_text(encoding="utf-8"))
    assert artifact == flh.build_report()


# --------------------------------------------------------------------------------------
# Pure return / correctness math
# --------------------------------------------------------------------------------------
def test_forward_return() -> None:
    assert flh.forward_return(100.0, 110.0) == 0.10
    assert flh.forward_return(110.0, 99.0) == -0.10
    assert flh.forward_return(99.0, 99.0) == 0.0


def test_move_sign() -> None:
    assert flh.move_sign(0.05) == "up"
    assert flh.move_sign(-0.05) == "down"
    assert flh.move_sign(0.0) == "flat"


def test_direction_correct_all_directions() -> None:
    # LONG correct on up, wrong on down
    assert flh.direction_correct("LONG", 0.05) is True
    assert flh.direction_correct("LONG", -0.05) is False
    # AVOID correct on down, wrong on up
    assert flh.direction_correct("AVOID", -0.05) is True
    assert flh.direction_correct("AVOID", 0.05) is False
    # FLAT correct only within the flat band
    assert flh.direction_correct("FLAT", 0.0) is True
    assert flh.direction_correct("FLAT", 0.05) is False
    # WATCH is never a directional claim
    assert flh.direction_correct("WATCH", 0.05) is None
    assert flh.direction_correct("WATCH", -0.05) is None


def test_directional_pnl() -> None:
    assert flh.directional_pnl("LONG", 0.05) == 0.05
    assert flh.directional_pnl("AVOID", -0.05) == 0.05  # short-bias: -r
    assert flh.directional_pnl("AVOID", 0.05) == -0.05
    assert flh.directional_pnl("FLAT", 0.05) == 0.0
    assert flh.directional_pnl("WATCH", 0.05) is None


def test_horizon_offsets_and_gap_tolerance() -> None:
    assert flh.target_offset_days(5) == 7
    assert flh.target_offset_days(20) == 28
    assert flh.target_offset_days(60) == 84
    assert flh.max_gap_days(5) == 2  # ceil(0.25 * 7)
    assert flh.max_gap_days(20) == 7  # ceil(0.25 * 28)
    assert flh.max_gap_days(60) == 21  # ceil(0.25 * 84)


# --------------------------------------------------------------------------------------
# Exit-selection: realized / pending / no_exit_in_tolerance (the main correctness risk)
# --------------------------------------------------------------------------------------
def _pt(date: str, price: float, direction: str = "LONG", regime: str = "REFLATION") -> "flh.DecisionPoint":
    return flh.DecisionPoint(f"ID_{date}", f"{date}T22:00:00+00:00", price, regime, direction)


def test_single_point_all_pending() -> None:
    p = _pt("2030-01-01", 100.0)
    for h in flh.HORIZONS_TD:
        lbl = flh.label_point(p, [p], h)
        assert lbl["status"] == "pending"
        assert lbl["forward_return"] is None


def test_realized_exit_at_horizon() -> None:
    entry = _pt("2030-01-01", 100.0)
    exit_pt = _pt("2030-01-08", 110.0)  # +7 days == H5 target, gap 0
    lbl = flh.label_point(entry, [entry, exit_pt], 5)
    assert lbl["status"] == "realized"
    assert lbl["exit_snapshot_id"] == exit_pt.source_snapshot_id
    assert lbl["forward_return"] == 0.1
    assert lbl["actual_offset_days"] == 7


def test_gap_beyond_tolerance_is_no_exit() -> None:
    entry = _pt("2030-01-01", 100.0)
    # nearest at-or-after H5 target (01-08) is 01-20 -> gap 12 > max_gap(5)=2
    far = _pt("2030-01-20", 130.0)
    lbl = flh.label_point(entry, [entry, far], 5)
    assert lbl["status"] == "no_exit_in_tolerance"
    assert lbl["exit_snapshot_id"] is None


def test_nearest_at_or_after_is_chosen() -> None:
    entry = _pt("2030-01-01", 100.0)
    before = _pt("2030-01-05", 105.0)  # before the 01-08 target -> not a candidate
    on1 = _pt("2030-01-09", 108.0)  # at-or-after target, gap 1 <= 2
    on2 = _pt("2030-01-10", 120.0)  # later candidate
    lbl = flh.label_point(entry, [entry, before, on1, on2], 5)
    assert lbl["status"] == "realized"
    assert lbl["exit_snapshot_id"] == on1.source_snapshot_id  # the EARLIEST at-or-after


def test_no_price_entry_is_marked() -> None:
    other = _pt("2030-01-08", 110.0)
    for bad in (None, 0.0, -5.0):  # fail-closed: missing or non-positive price -> no_price
        entry = flh.DecisionPoint("BADPRICE", "2030-01-01T22:00:00+00:00", bad, "NEUTRAL", "FLAT")
        lbl = flh.label_point(entry, [entry, other], 5)
        assert lbl["status"] == "no_price", bad


def test_non_positive_exit_price_is_not_a_candidate() -> None:
    # a later snapshot with a non-positive price cannot serve as an exit (fail-closed) -> pending
    entry = _pt("2030-01-01", 100.0)
    bad_exit = flh.DecisionPoint("BADEXIT", "2030-01-08T22:00:00+00:00", 0.0, "REFLATION", "LONG")
    lbl = flh.label_point(entry, [entry, bad_exit], 5)
    assert lbl["status"] == "pending"


# --------------------------------------------------------------------------------------
# Synthetic validation set: every branch the monochromatic real corpus cannot reach
# --------------------------------------------------------------------------------------
def _syn_index() -> dict[tuple[str, int], dict]:
    labels = flh.build_report()["synthetic"]["labels"]
    return {(lbl["entry_clock_ts"][:10], lbl["horizon_td"]): lbl for lbl in labels}


def test_synthetic_exercises_all_directions_and_statuses() -> None:
    cov = flh.build_report()["synthetic"]["coverage"]
    assert set(cov["directions"]) == {"LONG", "FLAT", "AVOID", "WATCH"}
    assert set(cov["statuses"]) == {"realized", "pending", "no_exit_in_tolerance"}
    assert cov["realized_count"] == 9
    assert len(cov["regimes"]) >= 4


def test_synthetic_pinned_labels() -> None:
    idx = _syn_index()
    # LONG captures an up-move (correct)
    a = idx[("2030-01-01", 5)]
    assert (a["status"], a["forward_return"], a["direction_correct"], a["directional_pnl"]) == (
        "realized", 0.1, True, 0.1,
    )
    # AVOID dodges a down-move (correct); pnl is the short-bias +0.1
    b = idx[("2030-01-08", 5)]
    assert (b["status"], b["forward_return"], b["direction_correct"], b["directional_pnl"]) == (
        "realized", -0.1, True, 0.1,
    )
    # AVOID during an up-move (incorrect — missed it)
    c = idx[("2030-01-22", 5)]
    assert (c["status"], c["direction_correct"], c["directional_pnl"]) == ("realized", False, -0.1)
    # FLAT with a flat move (correct)
    d = idx[("2030-01-29", 5)]
    assert (d["status"], d["move_sign"], d["direction_correct"]) == ("realized", "flat", True)
    # WATCH never scored, never a position
    e = idx[("2030-02-05", 5)]
    assert (e["status"], e["direction_correct"], e["directional_pnl"]) == ("realized", None, None)
    # the entry just before the deliberate gap: no clean exit at H5
    assert idx[("2030-02-12", 5)]["status"] == "no_exit_in_tolerance"
    # H60 extends past the synthetic series everywhere -> pending
    assert all(idx[(day, 60)]["status"] == "pending"
               for day in ("2030-01-01", "2030-01-08", "2030-03-20"))


def test_synthetic_aggregate_hit_rates() -> None:
    agg = flh.build_report()["synthetic"]["aggregate_by_regime_horizon"]
    assert agg["REFLATION"]["5"]["hit_rate"] == 1.0      # LONG, up-move
    assert agg["RISK_OFF"]["5"]["hit_rate"] == 0.0       # LONG, down-move
    assert agg["STRONG_USD"]["5"]["hit_rate"] == 0.0     # AVOID, up-move
    assert agg["LOW_VOL"]["5"]["hit_rate"] == 1.0        # FLAT, flat
    assert agg["REFLATION"]["5"]["mean_directional_pnl"] == 0.1


# --------------------------------------------------------------------------------------
# Real corpus today: honest, sparse, deduped
# --------------------------------------------------------------------------------------
def test_committed_real_dedups_to_one_pending_point() -> None:
    real = flh.build_report()["committed_real"]
    # three committed JSONs all resolve to the SAME banked snapshot -> exactly one point
    assert real["distinct_snapshots"] == 1
    snap = real["snapshots"][0]
    assert snap["regime"] == "RESTRICTIVE_RATES"
    assert snap["direction"] == "AVOID"
    assert snap["entry_price"] == 4624.5
    # one point can yield no forward return -> every horizon pending, nothing realized
    assert real["coverage"]["realized_count"] == 0
    assert {lbl["status"] for lbl in real["labels"]} == {"pending"}
    assert len(real["labels"]) == len(flh.HORIZONS_TD)


# --------------------------------------------------------------------------------------
# LOOK-AHEAD CONTAINMENT — the non-negotiable wall (static regression guard)
# --------------------------------------------------------------------------------------
def test_decision_chain_does_not_import_the_labeler() -> None:
    """No file under the decision chain (src/{snapshot,features,regime,gold}) may IMPORT the
    labeler or anything under benchmarks/. Forward returns must never reach the decision path.

    The guard is structural: if the chain never imports the labeler, the labeler cannot influence
    a decision. We flag the unambiguous module name anywhere, and ``benchmarks``/``calibration``
    only on import lines (those words legitimately appear in config docstrings as prose about the
    version axis ADR-012 governs — that is not a code dependency).
    """
    chain_dirs = ("snapshot", "features", "regime", "gold")
    offenders: list[str] = []
    for d in chain_dirs:
        for py in (_REPO_ROOT / "src" / d).rglob("*.py"):
            for raw in py.read_text(encoding="utf-8").splitlines():
                line = raw.strip()
                rel = py.relative_to(_REPO_ROOT)
                if "run_forward_return_labels" in line:
                    offenders.append(f"{rel}: {line}")
                elif (line.startswith(("import ", "from "))
                      and ("benchmarks" in line or "calibration" in line)):
                    offenders.append(f"{rel}: {line}")
    assert offenders == [], f"look-ahead containment breach: {offenders}"


def test_decision_point_carries_no_forward_data() -> None:
    """The labeler's input row holds only entry-side facts — no exit/return/label fields."""
    fields = set(flh.DecisionPoint.__dataclass_fields__)
    assert fields == {"source_snapshot_id", "clock_ts", "entry_price", "regime", "direction"}
