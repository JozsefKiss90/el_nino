"""Regime taxonomy benchmark + replay harness (BENCH-001 / STEP 9 + STEP 10, ADR-007).

Deterministic and replayable — fixed inputs, fixed synthetic grid, no randomness, no clock.
Two parts:

  Part 1 — DETERMINISM EVIDENCE (real snapshots): replay every available real snapshot
  (the 3 test fixtures + the 2 source snapshots) through consume -> build_features ->
  classify, twice each, and assert the serialized classification is byte-identical
  (STEP 10: same snapshot -> same regime, 100%). Non-consumable snapshots (FAIL / forced /
  malformed) are recorded as such and produce no classification (fail-closed upstream).

  Part 2 — SYNTHETIC SWEEP (clearly labelled synthetic): a fixed Cartesian feature grid
  plus targeted edge cells, swept to measure distribution, coverage, Shannon entropy,
  classification balance, unclassified%, rule utilization, and regime frequency (STEP 9).

Run standalone:  python benchmarks/regime/run_regime_bench.py
Writes the golden artifact to benchmarks/regime/artifacts/regime_bench.json.
"""

from __future__ import annotations

import itertools
import json
import math
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))

from features.feature_builder import build_features  # noqa: E402
from features.feature_builder.models import Feature, FeatureVector  # noqa: E402
from regime.regime_classifier import (  # noqa: E402
    CLASSIFICATION_TRACE_VERSION,
    CLASSIFIER_VERSION,
    DEFAULT_REGIME_CONFIG,
    TAXONOMY_VERSION,
    Regime,
    classify,
)
from snapshot.snapshot_consumer import consume  # noqa: E402
from snapshot.snapshot_consumer.models import SnapshotContractError  # noqa: E402

ARTIFACT_PATH = _REPO_ROOT / "benchmarks" / "regime" / "artifacts" / "regime_bench.json"

# Real snapshots available in the repo (label -> path). There is no historical corpus, so
# this is the full real population; the synthetic sweep below provides coverage breadth.
_REAL_INPUTS: tuple[tuple[str, Path], ...] = (
    ("latest_snapshot_pass", _REPO_ROOT / "tests" / "snapshot" / "fixtures" / "latest_snapshot_pass.json"),
    ("snapshot_fail", _REPO_ROOT / "tests" / "snapshot" / "fixtures" / "snapshot_fail.json"),
    ("snapshot_forced", _REPO_ROOT / "tests" / "snapshot" / "fixtures" / "snapshot_forced.json"),
    ("src_latest_snapshot", _REPO_ROOT / "snapshot_sources" / "latest_snapshot.json"),
    ("src_snapshot", _REPO_ROOT / "snapshot_sources" / "snapshot.json"),
)

# Baseline for synthetic FeatureVectors (a calm, mid-band NEUTRAL point). SYNTHETIC.
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

# The fixed synthetic grid axes (deterministic; no randomness).
_GRID_AXES: dict[str, tuple[float, ...]] = {
    "vol_level": (10.0, 18.0, 28.0, 40.0),
    "real_yield_10y": (0.5, 1.2, 2.0),
    "breakeven_5y5y_fwd": (1.8, 2.25, 2.6),
    "curve_2s10s": (-0.3, 0.5),
    "usd_level": (110.0, 125.0),
    "rates_vol": (60.0, 130.0),
}

_SIGNAL_REGIMES: tuple[Regime, ...] = tuple(r for r in Regime if r is not Regime.INDETERMINATE)


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
    """Replay each real snapshot twice; assert byte-identical classification (STEP 10)."""
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
        first = json.dumps(classify(fv).to_dict(), sort_keys=True)
        second = json.dumps(classify(fv).to_dict(), sort_keys=True)
        rc = classify(fv)
        inputs.append(
            {
                "name": label,
                "consumable": True,
                "snapshot_id": rc.snapshot_id,
                "regime": rc.regime.value,
                "rule_id": rc.matched_rule_id,
                "rule_margin": round(rc.rule_margin, 6),
                "byte_identical_replay": first == second,
            }
        )
    classified = [i for i in inputs if i.get("consumable")]
    return {
        "inputs": inputs,
        "consumable_count": len(classified),
        "all_replays_byte_identical": all(i["byte_identical_replay"] for i in classified),
    }


def run_synthetic_sweep() -> dict[str, Any]:
    """Sweep the fixed synthetic grid (+ edge cells) and compute the distribution metrics."""
    regime_freq: dict[str, int] = {r.value: 0 for r in Regime}
    rule_util: dict[str, int] = {}
    total = 0
    indeterminate = 0

    names = tuple(_GRID_AXES.keys())
    for combo in itertools.product(*(_GRID_AXES[n] for n in names)):
        overrides = dict(zip(names, combo))
        rc = classify(_make_fv(overrides))
        regime_freq[rc.regime.value] += 1
        rule_util[rc.matched_rule_id] = rule_util.get(rc.matched_rule_id, 0) + 1
        total += 1
        if rc.regime is Regime.INDETERMINATE:
            indeterminate += 1

    # Targeted edge cells so every regime is exercised (LOW_VOL needs equity absent;
    # INDETERMINATE needs a required feature absent).
    for label, fv in (
        ("low_vol_edge", _make_fv({"vol_level": 10.0}, drop=("equity_level",))),
        ("indeterminate_edge", _make_fv({}, drop=("usd_level",))),
    ):
        rc = classify(fv)
        regime_freq[rc.regime.value] += 1
        rule_util[rc.matched_rule_id] = rule_util.get(rc.matched_rule_id, 0) + 1
        total += 1
        if rc.regime is Regime.INDETERMINATE:
            indeterminate += 1

    signal_total = total - indeterminate
    distribution_pct = {
        r: round(100.0 * regime_freq[r] / total, 4) for r in sorted(regime_freq)
    }
    # Shannon entropy (bits) over the non-INDETERMINATE regime distribution.
    entropy = 0.0
    for r in _SIGNAL_REGIMES:
        count = regime_freq[r.value]
        if count:
            p = count / signal_total
            entropy -= p * math.log2(p)
    regimes_hit = sum(1 for r in _SIGNAL_REGIMES if regime_freq[r.value] > 0)
    max_entropy = math.log2(regimes_hit) if regimes_hit > 1 else 1.0

    return {
        "synthetic": True,
        "grid_axes": {k: list(v) for k, v in _GRID_AXES.items()},
        "grid_cells": total,
        "regime_frequency": {r: regime_freq[r] for r in sorted(regime_freq)},
        "rule_utilization": {r: rule_util[r] for r in sorted(rule_util)},
        "distribution_pct": distribution_pct,
        "coverage": {
            "regimes_hit": regimes_hit,
            "regimes_total": len(_SIGNAL_REGIMES),
            "all_reachable": regimes_hit == len(_SIGNAL_REGIMES),
        },
        "entropy_bits": round(entropy, 6),
        "classification_balance": round(entropy / max_entropy, 6),
        "unclassified_pct": round(100.0 * indeterminate / total, 4),
        "indeterminate_cells": indeterminate,
    }


def build_report() -> dict[str, Any]:
    """Assemble the full, deterministic benchmark report."""
    return {
        "benchmark_id": "BENCH-001",
        "classifier_version": CLASSIFIER_VERSION,
        "taxonomy_version": TAXONOMY_VERSION,
        "classification_trace_version": CLASSIFICATION_TRACE_VERSION,
        "feature_schema_version": "0.1.0",
        "decision_fingerprint": DEFAULT_REGIME_CONFIG.decision_fingerprint(),
        "determinism": run_determinism(),
        "synthetic_sweep": run_synthetic_sweep(),
    }


def main() -> None:
    report = build_report()
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    sweep = report["synthetic_sweep"]
    det = report["determinism"]
    print(f"wrote {ARTIFACT_PATH.relative_to(_REPO_ROOT)}")
    print(f"determinism: all_replays_byte_identical={det['all_replays_byte_identical']} "
          f"({det['consumable_count']} consumable)")
    print(f"coverage: {sweep['coverage']['regimes_hit']}/{sweep['coverage']['regimes_total']} "
          f"all_reachable={sweep['coverage']['all_reachable']}")
    print(f"entropy_bits={sweep['entropy_bits']} balance={sweep['classification_balance']} "
          f"unclassified_pct={sweep['unclassified_pct']}")


if __name__ == "__main__":
    main()
