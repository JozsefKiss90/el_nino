"""TEST-017 — paper-runtime benchmark (BENCH-003): determinism, idempotency, artifact-in-sync.

Mirrors test_gold_bench.py: the harness is deterministic, both sequences replay byte-identically, the
re-presented snapshot is flagged a duplicate, packets are never enriched in place, the synthetic
sequence reaches every verdict, and the committed golden artifact stays in sync.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_BENCH_DIR = Path(__file__).resolve().parents[2] / "benchmarks" / "gold"
if str(_BENCH_DIR) not in sys.path:
    sys.path.insert(0, str(_BENCH_DIR))

import run_paper_runtime_bench as bench  # type: ignore[import-not-found]  # noqa: E402


def test_report_is_deterministic() -> None:
    a = bench.build_report()
    b = bench.build_report()
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_real_sequence_byte_identical() -> None:
    assert bench.build_report()["real_sequence"]["all_replays_byte_identical"] is True


def test_packets_not_enriched_in_place() -> None:
    # the runtime wraps; the planning packet's guard_refs stay unevaluated (no enrich-back)
    assert bench.build_report()["real_sequence"]["no_enrich_back"] is True
    assert bench.build_report()["synthetic_sequence"]["no_enrich_back"] is True


def test_real_idempotency_re_presented_is_duplicate_reject() -> None:
    idem = bench.build_report()["real_sequence"]["idempotency"]
    assert idem["re_presented_verdict"] == "REJECT"
    assert idem["re_presented_triggered_guard"] == "duplicate_ok"


def test_synthetic_sequence_byte_identical() -> None:
    assert bench.build_report()["synthetic_sequence"]["all_replays_byte_identical"] is True


def test_synthetic_reaches_every_verdict() -> None:
    dist = bench.build_report()["synthetic_sequence"]["verdict_distribution"]
    assert dist["ADMIT"] == 3   # SYN1/2/3 (LONG/AVOID/FLAT) admit
    assert dist["HOLD"] == 1    # SYN4 (WATCH)
    assert dist["REJECT"] == 3  # operational / data / duplicate


def test_synthetic_reject_attribution() -> None:
    results = {r["label"]: r for r in bench.build_report()["synthetic_sequence"]["results"]}
    assert results["SYN5_reject_operational"]["triggered_guard"] == "operational_ok"
    assert results["SYN6_reject_data"]["triggered_guard"] == "data_ok"
    assert results["SYN1_reject_duplicate"]["triggered_guard"] == "duplicate_ok"


def test_committed_artifact_in_sync() -> None:
    artifact = json.loads(bench.ARTIFACT_PATH.read_text(encoding="utf-8"))
    assert artifact == bench.build_report()
