"""Tests for the gold benchmark + replay harness (BENCH-002 / TEST-011).

Asserts the harness is deterministic, real-snapshot packet replay is byte-identical, the
real PASS packet pins RESTRICTIVE_RATES -> AVOID / confidence 0.39744 / the full-key
packet_id, the synthetic sweep reaches every direction, the observed regime->direction map
matches the policy table, and the committed golden artifact stays in sync.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_BENCH_DIR = Path(__file__).resolve().parents[2] / "benchmarks" / "gold"
if str(_BENCH_DIR) not in sys.path:
    sys.path.insert(0, str(_BENCH_DIR))

from gold.decision_builder import DEFAULT_DECISION_POLICY_CONFIG  # noqa: E402

import run_gold_bench as bench  # type: ignore[import-not-found]  # noqa: E402


def test_report_is_deterministic() -> None:
    a = bench.build_report()
    b = bench.build_report()
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_real_replays_byte_identical() -> None:
    report = bench.build_report()
    assert report["determinism"]["all_replays_byte_identical"] is True
    assert report["determinism"]["consumable_count"] == 3


def test_real_pass_packet_pinned() -> None:
    inputs = {i["name"]: i for i in bench.build_report()["determinism"]["inputs"]}
    real = inputs["latest_snapshot_pass"]
    assert real["regime"] == "RESTRICTIVE_RATES"
    assert real["direction"] == "AVOID"
    assert real["confidence"] == 0.39744
    assert real["uncertainty"] == 0.136
    assert real["packet_id"] == "gold-v0:0ebde87216151527"
    # the FAIL/forced fixtures are non-consumable upstream (fail-closed)
    assert inputs["snapshot_fail"]["consumable"] is False
    assert inputs["snapshot_forced"]["consumable"] is False


def test_synthetic_sweep_all_directions_reachable() -> None:
    freq = bench.build_report()["synthetic_sweep"]["direction_frequency"]
    assert all(freq[d] > 0 for d in ("LONG", "FLAT", "AVOID", "WATCH"))


def test_regime_direction_map_matches_policy() -> None:
    sweep = bench.build_report()["synthetic_sweep"]
    for regime_value, direction_value in sweep["regime_direction_map"].items():
        assert DEFAULT_DECISION_POLICY_CONFIG.direction_for(regime_value).value == direction_value


def test_committed_artifact_in_sync() -> None:
    artifact = json.loads(bench.ARTIFACT_PATH.read_text(encoding="utf-8"))
    assert artifact == bench.build_report()
