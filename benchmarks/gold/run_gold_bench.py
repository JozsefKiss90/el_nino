"""Gold decision benchmark + replay harness (BENCH-002, ADR-006/ADR-008).

Deterministic and replayable — fixed inputs, fixed synthetic grid, no randomness, no clock.
Two parts:

  Part 1 — DETERMINISM EVIDENCE (real snapshots): replay every consumable real snapshot
  through consume -> build_features -> classify -> build_decision, twice each, and assert the
  serialized packet is byte-identical. Records each real packet (regime, direction, confidence,
  uncertainty, full-key packet_id). Non-consumable snapshots produce no packet (fail-closed).

  Part 2 — SYNTHETIC SWEEP (clearly labelled synthetic): the same fixed regime feature grid as
  the regime benchmark, swept to measure the direction distribution, the observed regime->
  direction map, and confidence/uncertainty stats.

Run standalone:  python benchmarks/gold/run_gold_bench.py
Writes the golden artifact to benchmarks/gold/artifacts/gold_bench.json.
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))

from features.feature_builder import build_features  # noqa: E402
from features.feature_builder.models import Feature, FeatureVector  # noqa: E402
from gold.decision_builder import (  # noqa: E402
    DECISION_POLICY_VERSION,
    DEFAULT_DECISION_POLICY_CONFIG,
    PACKET_SCHEMA_VERSION,
    Direction,
    build_decision,
)
from regime.regime_classifier import classify  # noqa: E402
from snapshot.snapshot_consumer import consume  # noqa: E402
from snapshot.snapshot_consumer.models import SnapshotContractError  # noqa: E402

ARTIFACT_PATH = _REPO_ROOT / "benchmarks" / "gold" / "artifacts" / "gold_bench.json"

_REAL_INPUTS: tuple[tuple[str, Path], ...] = (
    ("latest_snapshot_pass", _REPO_ROOT / "tests" / "snapshot" / "fixtures" / "latest_snapshot_pass.json"),
    ("snapshot_fail", _REPO_ROOT / "tests" / "snapshot" / "fixtures" / "snapshot_fail.json"),
    ("snapshot_forced", _REPO_ROOT / "tests" / "snapshot" / "fixtures" / "snapshot_forced.json"),
    ("src_latest_snapshot", _REPO_ROOT / "snapshot_sources" / "latest_snapshot.json"),
    ("src_snapshot", _REPO_ROOT / "snapshot_sources" / "snapshot.json"),
)

# Same calm, mid-band NEUTRAL baseline + grid as the regime benchmark (synthetic).
_BASELINE: dict[str, float] = {
    "real_yield_10y": 0.9,
    "real_yield_5y": 0.8,
    "breakeven_10y": 2.3,
    "breakeven_5y": 2.3,
    "breakeven_5y5y_fwd": 2.25,
    "curve_2s10s": 0.5,
    "curve_5s10s": 0.4,
    "policy_spread": 0.0,
    "usd_level": 110.0,
    "vol_level": 18.5,
    "rates_vol": 72.0,
    "equity_level": 5000.0,
    "gold_price": 4000.0,
    "gold_flow": 1_000_000.0,
}

_GRID_AXES: dict[str, tuple[float, ...]] = {
    "vol_level": (10.0, 18.0, 28.0, 40.0),
    "real_yield_10y": (0.5, 1.2, 2.0),
    "breakeven_5y5y_fwd": (1.8, 2.25, 2.6),
    "curve_2s10s": (-0.3, 0.5),
    "usd_level": (110.0, 125.0),
    "rates_vol": (60.0, 130.0),
}


def _make_fv(overrides: dict[str, float], drop: tuple[str, ...] = ()) -> FeatureVector:
    values: dict[str, float] = dict(_BASELINE)
    values.update(overrides)
    for name in drop:
        values.pop(name, None)
    features = {
        name: Feature(name, float(val), (f"SRC_{name}",), 0, False) for name, val in values.items()
    }
    return FeatureVector("synthetic", "0.1.0", features, tuple(sorted(drop)))


def run_determinism() -> dict[str, Any]:
    """Replay each real snapshot twice; assert byte-identical packet serialization."""
    inputs: list[dict[str, Any]] = []
    for label, path in _REAL_INPUTS:
        try:
            snap = consume(path)
        except SnapshotContractError:
            inputs.append({"name": label, "consumable": False, "reason": "snapshot_contract_error"})
            continue
        if snap is None:
            inputs.append({"name": label, "consumable": False, "reason": "gate_not_passed"})
            continue
        fv = build_features(snap)
        rc = classify(fv)
        first = json.dumps(build_decision(fv, rc).to_dict(), sort_keys=True)
        second = json.dumps(build_decision(fv, rc).to_dict(), sort_keys=True)
        pkt = build_decision(fv, rc)
        inputs.append(
            {
                "name": label,
                "consumable": True,
                "snapshot_id": pkt.source_snapshot_id,
                "regime": pkt.regime,
                "direction": pkt.direction.value,
                "confidence": round(pkt.confidence, 6),
                "uncertainty": round(pkt.uncertainty, 6),
                "packet_id": pkt.packet_id,
                "byte_identical_replay": first == second,
            }
        )
    classified = [i for i in inputs if i.get("consumable")]
    return {
        "inputs": inputs,
        "consumable_count": len(classified),
        "all_replays_byte_identical": all(i["byte_identical_replay"] for i in classified),
    }


def _stats(values: list[float]) -> dict[str, float]:
    return {
        "min": round(min(values), 6),
        "max": round(max(values), 6),
        "mean": round(sum(values) / len(values), 6),
    }


def run_synthetic_sweep() -> dict[str, Any]:
    """Sweep the fixed synthetic grid (+ edge cells) and compute direction/confidence metrics."""
    direction_freq: dict[str, int] = {d.value: 0 for d in Direction}
    regime_direction: dict[str, str] = {}
    confidences: list[float] = []
    uncertainties: list[float] = []
    total = 0

    names = tuple(_GRID_AXES.keys())
    for combo in itertools.product(*(_GRID_AXES[n] for n in names)):
        fv = _make_fv(dict(zip(names, combo)))
        pkt = build_decision(fv, classify(fv))
        direction_freq[pkt.direction.value] += 1
        regime_direction[pkt.regime] = pkt.direction.value
        confidences.append(pkt.confidence)
        uncertainties.append(pkt.uncertainty)
        total += 1

    for fv in (
        _make_fv({"vol_level": 10.0}, drop=("equity_level",)),  # LOW_VOL
        _make_fv({}, drop=("usd_level",)),  # INDETERMINATE
    ):
        pkt = build_decision(fv, classify(fv))
        direction_freq[pkt.direction.value] += 1
        regime_direction[pkt.regime] = pkt.direction.value
        confidences.append(pkt.confidence)
        uncertainties.append(pkt.uncertainty)
        total += 1

    return {
        "synthetic": True,
        "grid_axes": {k: list(v) for k, v in _GRID_AXES.items()},
        "grid_cells": total,
        "direction_frequency": {d: direction_freq[d] for d in sorted(direction_freq)},
        "direction_distribution_pct": {
            d: round(100.0 * direction_freq[d] / total, 4) for d in sorted(direction_freq)
        },
        "regime_direction_map": {r: regime_direction[r] for r in sorted(regime_direction)},
        "confidence_stats": _stats(confidences),
        "uncertainty_stats": _stats(uncertainties),
    }


def build_report() -> dict[str, Any]:
    """Assemble the full, deterministic benchmark report."""
    return {
        "benchmark_id": "BENCH-002",
        "decision_policy_version": DECISION_POLICY_VERSION,
        "decision_policy_fingerprint": DEFAULT_DECISION_POLICY_CONFIG.decision_policy_fingerprint(),
        "packet_schema_version": PACKET_SCHEMA_VERSION,
        "determinism": run_determinism(),
        "synthetic_sweep": run_synthetic_sweep(),
    }


def main() -> None:
    report = build_report()
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    det = report["determinism"]
    sweep = report["synthetic_sweep"]
    print(f"wrote {ARTIFACT_PATH.relative_to(_REPO_ROOT)}")
    print(
        f"determinism: all_replays_byte_identical={det['all_replays_byte_identical']} "
        f"({det['consumable_count']} consumable)"
    )
    print(f"direction_frequency={sweep['direction_frequency']}")
    print(f"confidence_stats={sweep['confidence_stats']}")


if __name__ == "__main__":
    main()
