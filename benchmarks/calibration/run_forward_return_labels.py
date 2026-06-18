"""Gold Forward-Return Labeler (MOD-009) — the ADR-012 gate G3 prerequisite.

A deterministic, **strictly-downstream, read-only** measurement tool. It labels each
already-produced gold decision with the gold return realized *after* its timestamp, and
aggregates per regime x horizon. This is the per-regime outcome data ADR-012 gate G3
(regime->direction table calibration) will eventually consume. It produces labels; it
**never** calibrates the direction table, changes any config, or bumps any ``*_version``
(G3 stays deferred — the corpus is still monochromatic).

LOOK-AHEAD CONTAINMENT (non-negotiable, ADR-012 §5 PIT honesty):
  - This module is downstream of ``consume -> build_features -> classify -> build_decision``.
    It *imports from* the chain to re-derive each decision (read-only); the chain never
    imports this module, and no forward price/return/label is ever passed back into
    ``build_decision`` (it is called with only ``fv``/``rc`` — no future data).
  - Forward returns are computed from snapshots banked AFTER the entry's ``clock_ts``. That is
    legitimate for an *outcome label* and poison on the decision path; the wall between them
    is this file's position (offline, under ``benchmarks/``, never imported by ``src/``).
  - Determinism/PIT: pure computation over the immutable, content-addressed corpus; ISO
    timestamps parsed deterministically (no wall-clock); only honestly-banked snapshots; no
    back-fabricated prices; canonical sorted-key JSON.

Run standalone:  python benchmarks/calibration/run_forward_return_labels.py [--include-external]
Writes the committed golden to benchmarks/calibration/artifacts/forward_return_labels.json
(committed scope = el_nino-committed consumables only, so it is reproducible in CI).
``--include-external`` additionally reports the full corpus (+ Mr-Ripley archives) to stdout;
that richer run is NOT written to the committed artifact (the archives live in a separate repo).
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))

# Strictly-downstream imports: this tool reads the decision chain; the chain never reads it.
from features.feature_builder import build_features  # noqa: E402
from features.feature_builder.models import FEATURE_SCHEMA_VERSION  # noqa: E402
from gold.decision_builder import DECISION_POLICY_VERSION, build_decision  # noqa: E402
from regime.regime_classifier import classify  # noqa: E402
from regime.regime_classifier.config import DEFAULT_REGIME_CONFIG  # noqa: E402
from snapshot.snapshot_consumer import consume  # noqa: E402
from snapshot.snapshot_consumer.models import SnapshotContractError  # noqa: E402

ARTIFACT_PATH = _REPO_ROOT / "benchmarks" / "calibration" / "artifacts" / "forward_return_labels.json"
ARTIFACT_SCHEMA = "forward_return_labels/v0"

# --- design parameters (documented; tunable; NOT a calibration *_version) ---
HORIZONS_TD: tuple[int, ...] = (5, 20, 60)  # holding horizons in trading-day-equivalents
CAL_PER_TD = 1.4  # 7 calendar days / 5 trading days; the corpus banks ~per calendar day
MAX_GAP_FRACTION = 0.25  # exit must land within 25% of the horizon past the target date
FLAT_BAND = 0.0  # |return| <= band => "flat" (0.0: flat only if exactly zero); tunable
PRICE_FEATURE = "gold_price"  # the gold thesis is about this series (pluggable)
PRICE_SERIES = "gold_price_proxy"  # the SCHEMA-001 series backing PRICE_FEATURE
_ROUND = 6

# Committed scope: el_nino-committed consumables only (reproducible in CI). The three paths
# below resolve to the SAME banked snapshot (952cc83a, 2026-05-01) — dedup by snapshot_id
# collapses them to one honest PIT point.
_COMMITTED_INPUTS: tuple[Path, ...] = (
    _REPO_ROOT / "tests" / "snapshot" / "fixtures" / "latest_snapshot_pass.json",
    _REPO_ROOT / "snapshot_sources" / "latest_snapshot.json",
    _REPO_ROOT / "snapshot_sources" / "snapshot.json",
)
# External (NOT committed): the Mr-Ripley producer's per-day immutable archives (separate repo).
_EXTERNAL_ARCHIVE_DIR = Path(r"C:\Code\Mr-Ripley\runtime\snapshots")


@dataclass(frozen=True)
class DecisionPoint:
    """One already-produced decision + its entry gold price (the labeler's input row).

    Built by re-running the read-only chain over a banked snapshot. Carries no forward data.
    """

    source_snapshot_id: str
    clock_ts: str
    entry_price: float | None
    regime: str
    direction: str

    @property
    def dt(self) -> datetime:
        return datetime.fromisoformat(self.clock_ts)


# --------------------------------------------------------------------------------------
# Pure label/return math (no IO, no chain, no clock) — unit-tested synthetically.
# --------------------------------------------------------------------------------------
def forward_return(entry_price: float, exit_price: float) -> float:
    """(exit - entry) / entry. Entry price is assumed > 0 (a real gold level)."""
    return (exit_price - entry_price) / entry_price


def move_sign(r: float, flat_band: float = FLAT_BAND) -> str:
    if r > flat_band:
        return "up"
    if r < -flat_band:
        return "down"
    return "flat"


def direction_correct(direction: str, r: float, flat_band: float = FLAT_BAND) -> bool | None:
    """Was the assigned stance directionally right against the realized move?

    LONG (bet gold rises)        -> correct iff up-move.
    AVOID (gold headwind, weak)  -> correct iff down-move.
    FLAT (no edge)               -> correct iff the move was within the flat band.
    WATCH (no stance)            -> None (not a directional claim; not scored).
    """
    if direction == "LONG":
        return r > flat_band
    if direction == "AVOID":
        return r < -flat_band
    if direction == "FLAT":
        return abs(r) <= flat_band
    return None  # WATCH (or any non-directional stance)


def directional_pnl(direction: str, r: float) -> float | None:
    """P&L a unit position implied by the stance realizes (the headline G3 metric).

    LONG -> +r ; AVOID -> -r (short-bias view) ; FLAT -> 0.0 ; WATCH -> None (no position).
    """
    if direction == "LONG":
        return r
    if direction == "AVOID":
        return -r
    if direction == "FLAT":
        return 0.0
    return None


def target_offset_days(horizon_td: int) -> int:
    """Calendar-day offset for a trading-day horizon (documented CAL_PER_TD approximation)."""
    return round(horizon_td * CAL_PER_TD)


def max_gap_days(horizon_td: int) -> int:
    """Tolerance: the nearest at-or-after exit may sit at most this far past the target."""
    return math.ceil(MAX_GAP_FRACTION * target_offset_days(horizon_td))


def select_exit(
    entry: DecisionPoint, points: list[DecisionPoint], horizon_td: int
) -> tuple[str, DecisionPoint | None]:
    """Nearest banked snapshot at or after entry.clock_ts + horizon, within the gap tolerance.

    Returns (status, exit_point_or_None). Status is one of:
      - "pending"               : target is beyond the latest banked snapshot (knowable later).
      - "no_exit_in_tolerance"  : a later snapshot exists but the nearest one is past the gap
                                  (a permanent corpus hole at this horizon).
      - "realized"              : a clean exit within tolerance was found.
    Points with no entry price cannot serve as an exit and are excluded as candidates.
    """
    target = entry.dt + timedelta(days=target_offset_days(horizon_td))
    # An exit needs a usable (positive) price; a missing/non-positive price is a data fault,
    # never a valid exit (fail-closed, mirroring the chain's ADR-003 posture).
    candidates = [p for p in points if p.entry_price is not None and p.entry_price > 0 and p.dt >= target]
    if not candidates:
        return "pending", None
    exit_point = min(candidates, key=lambda p: (p.dt, p.source_snapshot_id))
    gap = (exit_point.dt - target).days
    if gap > max_gap_days(horizon_td):
        return "no_exit_in_tolerance", None
    return "realized", exit_point


def label_point(entry: DecisionPoint, points: list[DecisionPoint], horizon_td: int) -> dict[str, Any]:
    """Label one (decision x horizon). All keys always present (null where N/A) for a stable schema."""
    target = entry.dt + timedelta(days=target_offset_days(horizon_td))
    label: dict[str, Any] = {
        "source_snapshot_id": entry.source_snapshot_id,
        "entry_clock_ts": entry.clock_ts,
        "regime": entry.regime,
        "direction": entry.direction,
        "horizon_td": horizon_td,
        "target_offset_days": target_offset_days(horizon_td),
        "target_clock_ts": target.isoformat(),
        "max_gap_days": max_gap_days(horizon_td),
        "entry_price": entry.entry_price,
        "status": None,
        "exit_snapshot_id": None,
        "exit_clock_ts": None,
        "actual_offset_days": None,
        "exit_price": None,
        "forward_return": None,
        "move_sign": None,
        "direction_correct": None,
        "directional_pnl": None,
    }
    if entry.entry_price is None or entry.entry_price <= 0:
        # Fail-closed: a missing or non-positive entry price cannot anchor a return.
        label["status"] = "no_price"
        return label

    status, exit_point = select_exit(entry, points, horizon_td)
    label["status"] = status
    if status != "realized" or exit_point is None:
        return label

    assert exit_point.entry_price is not None  # guaranteed by select_exit candidate filter
    r = forward_return(entry.entry_price, exit_point.entry_price)
    pnl = directional_pnl(entry.direction, r)
    label.update(
        {
            "exit_snapshot_id": exit_point.source_snapshot_id,
            "exit_clock_ts": exit_point.clock_ts,
            "actual_offset_days": (exit_point.dt - entry.dt).days,
            "exit_price": exit_point.entry_price,
            "forward_return": round(r, _ROUND),
            "move_sign": move_sign(r),
            "direction_correct": direction_correct(entry.direction, r),
            "directional_pnl": None if pnl is None else round(pnl, _ROUND),
        }
    )
    return label


def label_all(points: list[DecisionPoint], horizons: tuple[int, ...] = HORIZONS_TD) -> list[dict[str, Any]]:
    """Every (decision x horizon) label, deterministically ordered."""
    ordered = sorted(points, key=lambda p: (p.dt, p.source_snapshot_id))
    out: list[dict[str, Any]] = []
    for entry in ordered:
        for h in horizons:
            out.append(label_point(entry, ordered, h))
    return out


def _mean(xs: list[float]) -> float | None:
    return round(sum(xs) / len(xs), _ROUND) if xs else None


def _median(xs: list[float]) -> float | None:
    if not xs:
        return None
    s = sorted(xs)
    n = len(s)
    mid = n // 2
    val = s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2.0
    return round(val, _ROUND)


def _aggregate_cell(rows: list[dict[str, Any]]) -> dict[str, Any]:
    realized = [r for r in rows if r["status"] == "realized"]
    returns = [r["forward_return"] for r in realized]
    pnls = [r["directional_pnl"] for r in realized if r["directional_pnl"] is not None]
    scored = [r for r in realized if r["direction_correct"] is not None]
    correct = [r for r in scored if r["direction_correct"] is True]

    by_direction: dict[str, Any] = {}
    for r in rows:
        d = r["direction"]
        cell = by_direction.setdefault(
            d, {"count": 0, "realized": 0, "returns": [], "scored": 0, "correct": 0}
        )
        cell["count"] += 1
        if r["status"] == "realized":
            cell["realized"] += 1
            cell["returns"].append(r["forward_return"])
            if r["direction_correct"] is not None:
                cell["scored"] += 1
                if r["direction_correct"] is True:
                    cell["correct"] += 1
    for d, cell in by_direction.items():
        rets = cell.pop("returns")
        cell["mean_forward_return"] = _mean(rets)

    return {
        "count_total": len(rows),
        "count_realized": len(realized),
        "count_pending": sum(1 for r in rows if r["status"] == "pending"),
        "count_no_exit_in_tolerance": sum(1 for r in rows if r["status"] == "no_exit_in_tolerance"),
        "count_no_price": sum(1 for r in rows if r["status"] == "no_price"),
        "mean_forward_return": _mean(returns),
        "median_forward_return": _median(returns),
        "mean_directional_pnl": _mean(pnls),
        "scored_count": len(scored),
        "hit_count": len(correct),
        "hit_rate": round(len(correct) / len(scored), _ROUND) if scored else None,
        "by_direction": {d: by_direction[d] for d in sorted(by_direction)},
    }


def aggregate_by_regime_horizon(labels: list[dict[str, Any]]) -> dict[str, Any]:
    """Per regime x horizon aggregation — the G3 input. Nested, sorted-key stable."""
    out: dict[str, dict[str, Any]] = {}
    regimes = sorted({lbl["regime"] for lbl in labels})
    for regime in regimes:
        out[regime] = {}
        for h in sorted({lbl["horizon_td"] for lbl in labels}):
            rows = [lbl for lbl in labels if lbl["regime"] == regime and lbl["horizon_td"] == h]
            if rows:
                out[regime][str(h)] = _aggregate_cell(rows)
    return out


def coverage(labels: list[dict[str, Any]]) -> dict[str, Any]:
    """What the label set exercised — for validation/visibility."""
    return {
        "regimes": sorted({lbl["regime"] for lbl in labels}),
        "directions": sorted({lbl["direction"] for lbl in labels}),
        "statuses": sorted({lbl["status"] for lbl in labels}),
        "label_count": len(labels),
        "realized_count": sum(1 for lbl in labels if lbl["status"] == "realized"),
    }


# --------------------------------------------------------------------------------------
# Corpus drivers (the ONLY place that touches the real chain — strictly read-only).
# --------------------------------------------------------------------------------------
def decision_points_from_corpus(paths: tuple[Path, ...]) -> list[DecisionPoint]:
    """Run the read-only chain over each consumable snapshot; dedup by snapshot_id.

    consume -> build_features -> classify -> build_decision (downstream read only). No forward
    data is fed back. Non-consumable snapshots (fail-closed / missing) are skipped. Multiple
    committed JSONs that resolve to the same banked snapshot collapse to one honest PIT point.
    """
    seen: dict[str, DecisionPoint] = {}
    for path in paths:
        if not path.exists():
            continue
        try:
            snap = consume(path)
        except SnapshotContractError:
            continue
        if snap is None:  # fail-closed: gate not passed / forced / dry-run
            continue
        fv = build_features(snap)
        rc = classify(fv)
        pkt = build_decision(fv, rc)  # only (fv, rc) — no future data on the decision path
        price = fv.value(PRICE_FEATURE) if PRICE_FEATURE in fv.features else None
        point = DecisionPoint(
            source_snapshot_id=pkt.source_snapshot_id,
            clock_ts=snap.clock_ts,
            entry_price=price,
            regime=rc.regime.value,
            direction=pkt.direction.value,
        )
        seen.setdefault(point.source_snapshot_id, point)
    return sorted(seen.values(), key=lambda p: (p.dt, p.source_snapshot_id))


def external_corpus_paths() -> tuple[Path, ...]:
    """Committed inputs + (if present) the Mr-Ripley producer archives (NOT committed)."""
    extra = (
        tuple(sorted(_EXTERNAL_ARCHIVE_DIR.glob("snapshot_*.json")))
        if _EXTERNAL_ARCHIVE_DIR.exists()
        else ()
    )
    return _COMMITTED_INPUTS + extra


# --------------------------------------------------------------------------------------
# Synthetic validation set (clearly labelled; proves the math the monochromatic corpus can't).
# Weekly grid 2030-01-01..02-12 (gap 0 at H=5) + a far point 03-20 (a deliberate gap), prices
# chosen so every branch is hand-verifiable. Maps mirror the real DEFAULT_DIRECTION_TABLE.
# --------------------------------------------------------------------------------------
def _syn(date: str, price: float, regime: str, direction: str) -> DecisionPoint:
    return DecisionPoint(f"SYN_{date}", f"{date}T22:00:00+00:00", price, regime, direction)


SYNTHETIC_POINTS: tuple[DecisionPoint, ...] = (
    _syn("2030-01-01", 100.0, "REFLATION", "LONG"),          # H5 -> 01-08 +0.10  LONG  correct (up)
    _syn("2030-01-08", 110.0, "RESTRICTIVE_RATES", "AVOID"),  # H5 -> 01-15 -0.10  AVOID correct (down)
    _syn("2030-01-15", 99.0, "RISK_OFF", "LONG"),            # H5 -> 01-22 -0.0909 LONG incorrect (down)
    _syn("2030-01-22", 90.0, "STRONG_USD", "AVOID"),          # H5 -> 01-29 +0.10  AVOID incorrect (up)
    _syn("2030-01-29", 99.0, "LOW_VOL", "FLAT"),             # H5 -> 02-05  0.0   FLAT  correct (flat)
    _syn("2030-02-05", 99.0, "CURVE_INVERSION", "WATCH"),     # H5 -> 02-12 +0.0606 WATCH None (no stance)
    _syn("2030-02-12", 105.0, "REFLATION", "LONG"),          # H5 -> gap -> no_exit_in_tolerance
    _syn("2030-03-20", 120.0, "LOW_VOL", "FLAT"),            # far point: every horizon pending
)


# --------------------------------------------------------------------------------------
# Report assembly (deterministic).
# --------------------------------------------------------------------------------------
def _build_section(points: list[DecisionPoint], corpus_source: str) -> dict[str, Any]:
    labels = label_all(points)
    return {
        "corpus_source": corpus_source,
        "distinct_snapshots": len(points),
        "snapshots": [
            {
                "source_snapshot_id": p.source_snapshot_id,
                "clock_ts": p.clock_ts,
                "regime": p.regime,
                "direction": p.direction,
                "entry_price": p.entry_price,
            }
            for p in points
        ],
        "labels": labels,
        "aggregate_by_regime_horizon": aggregate_by_regime_horizon(labels),
        "coverage": coverage(labels),
    }


def build_report(include_external: bool = False) -> dict[str, Any]:
    """The deterministic label report. Committed scope by default (the golden).

    ``include_external=True`` adds an ``external_real`` section over the full corpus (committed
    + Mr-Ripley archives) for operator diagnostics — never written to the committed artifact.
    """
    report: dict[str, Any] = {
        "tool": "MOD-009 Gold Forward-Return Labeler",
        "artifact_schema": ARTIFACT_SCHEMA,
        "purpose": (
            "ADR-012 gate G3 prerequisite: label each banked gold decision with the realized "
            "forward gold return, per regime x horizon. Measurement only — never calibrates the "
            "regime->direction table; G3 stays deferred (corpus monochromatic)."
        ),
        "horizons_td": list(HORIZONS_TD),
        "params": {
            "cal_per_td": CAL_PER_TD,
            "max_gap_fraction": MAX_GAP_FRACTION,
            "flat_band": FLAT_BAND,
            "price_feature": PRICE_FEATURE,
            "price_series": PRICE_SERIES,
            "round": _ROUND,
        },
        "decision_versions": {
            "feature_schema_version": FEATURE_SCHEMA_VERSION,
            "taxonomy_version": DEFAULT_REGIME_CONFIG.taxonomy_version,
            "classifier_version": DEFAULT_REGIME_CONFIG.classifier_version,
            "decision_policy_version": DECISION_POLICY_VERSION,
        },
        "committed_real": _build_section(
            decision_points_from_corpus(_COMMITTED_INPUTS),
            "el_nino-committed consumables (dedup by snapshot_id)",
        ),
        "synthetic": _build_section(
            list(SYNTHETIC_POINTS),
            "synthetic validation set (clearly synthetic; proves the label/gap/horizon math)",
        ),
    }
    if include_external:
        report["external_real"] = _build_section(
            decision_points_from_corpus(external_corpus_paths()),
            "el_nino fixture + Mr-Ripley runtime archives (NOT committed — separate repo)",
        )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Gold forward-return labeler (ADR-012 gate G3 prerequisite)")
    parser.add_argument(
        "--include-external",
        action="store_true",
        help="Also report the full corpus (+ Mr-Ripley archives) to stdout (not committed).",
    )
    args = parser.parse_args()

    report = build_report()  # committed scope -> the golden
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {ARTIFACT_PATH.relative_to(_REPO_ROOT)}")
    cr = report["committed_real"]["coverage"]
    sy = report["synthetic"]["coverage"]
    print(f"committed_real: {cr}")
    print(f"synthetic:      {sy}")

    if args.include_external:
        ext = build_report(include_external=True)["external_real"]
        print("\n--- external_real (full corpus; NOT committed) ---")
        print(f"corpus_source: {ext['corpus_source']}")
        print(f"distinct_snapshots: {ext['distinct_snapshots']}")
        print(f"coverage: {ext['coverage']}")
        print("aggregate_by_regime_horizon:")
        print(json.dumps(ext["aggregate_by_regime_horizon"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
