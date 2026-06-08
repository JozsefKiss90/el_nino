"""Tests for the regime benchmark + replay harness (BENCH-001 / TEST-009).

Asserts the harness is itself deterministic, that real-snapshot replay is byte-identical
(STEP 10 determinism evidence), that the synthetic sweep reaches every regime (STEP 9
coverage), and that the committed golden artifact stays in sync with a freshly built report.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_BENCH_DIR = Path(__file__).resolve().parents[2] / "benchmarks" / "regime"
if str(_BENCH_DIR) not in sys.path:
    sys.path.insert(0, str(_BENCH_DIR))

import run_regime_bench as bench  # type: ignore[import-not-found]  # noqa: E402


def test_report_is_deterministic() -> None:
    a = bench.build_report()
    b = bench.build_report()
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_real_replays_byte_identical() -> None:
    report = bench.build_report()
    assert report["determinism"]["all_replays_byte_identical"] is True
    assert report["determinism"]["consumable_count"] == 3


def test_real_pass_is_restrictive_rates_and_gate_fails_closed() -> None:
    inputs = {i["name"]: i for i in bench.build_report()["determinism"]["inputs"]}
    assert inputs["latest_snapshot_pass"]["regime"] == "RESTRICTIVE_RATES"
    assert inputs["src_latest_snapshot"]["regime"] == "RESTRICTIVE_RATES"
    assert inputs["snapshot_fail"]["consumable"] is False
    assert inputs["snapshot_forced"]["consumable"] is False


def test_synthetic_sweep_full_coverage() -> None:
    coverage = bench.build_report()["synthetic_sweep"]["coverage"]
    assert coverage["all_reachable"] is True
    assert coverage["regimes_hit"] == coverage["regimes_total"] == 11


def test_committed_artifact_in_sync() -> None:
    artifact = json.loads(bench.ARTIFACT_PATH.read_text(encoding="utf-8"))
    assert artifact == bench.build_report()
