"""TEST-025 — full-chain orchestrator benchmark (BENCH-006): determinism, idempotency, artifact-in-sync.

Mirrors test_execution_bench.py (TEST-021): the harness is deterministic, the real sequence replays
byte-identically across all five record types, the real ADMIT is grounded in the consumable corpus
(952cc83a, never invented), the monochromatic-AVOID corpus is an ADMIT-then-idempotent-REJECT no-fill,
the full replay key is complete, and the committed golden artifact stays in sync.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_BENCH_DIR = Path(__file__).resolve().parents[2] / "benchmarks" / "orchestration"
if str(_BENCH_DIR) not in sys.path:
    sys.path.insert(0, str(_BENCH_DIR))

import run_chain_bench as bench  # type: ignore[import-not-found]  # noqa: E402

_PACKET_ID = "gold-v0:5653d07a0b3949d5"
_EXPECTED_REPLAY_KEY = {
    "classification_trace_version", "classifier_version",
    "decision_policy_fingerprint", "decision_policy_version",
    "execution_policy_fingerprint", "execution_policy_version", "execution_schema_version",
    "feature_schema_version",
    "fill_model_fingerprint", "fill_model_version",
    "guard_config_fingerprint",
    "ledger_schema_version",
    "operational_input_fingerprint",
    "packet_schema_version", "portfolio_schema_version", "record_schema_version",
    "runtime_policy_fingerprint", "runtime_policy_version",
    "taxonomy_version",
}


def test_report_is_deterministic() -> None:
    a = bench.build_report()
    b = bench.build_report()
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_all_replays_byte_identical() -> None:
    assert bench.build_report()["all_replays_byte_identical"] is True


def test_real_sequence_byte_identical() -> None:
    assert bench.build_report()["real_sequence"]["all_replays_byte_identical"] is True


def test_real_admit_grounded_in_corpus() -> None:
    real = bench.build_report()["real_sequence"]
    assert real["real_admit_count"] == 1
    admit = next(r for r in real["results"] if r["verdict"] == "ADMIT")
    assert admit["source_snapshot_id"].startswith("952cc83a")
    assert admit["packet_id"] == _PACKET_ID
    assert admit["regime"] == "RESTRICTIVE_RATES"
    assert admit["direction"] == "AVOID"


def test_real_corpus_is_admit_then_idempotent_reject_no_fill() -> None:
    real = bench.build_report()["real_sequence"]
    # monochromatic AVOID ⇒ no fill anywhere; re-presentation REJECTs on duplicate_ok (no second admit).
    assert real["fill_distribution"]["filled"] == 0
    assert real["verdict_distribution"]["ADMIT"] == 1
    assert real["idempotency"]["re_presented_verdict"] == "REJECT"
    assert real["idempotency"]["re_presented_triggered_guard"] == "duplicate_ok"
    assert real["idempotency"]["re_presented_execution_filled"] is False


def test_full_replay_key_complete() -> None:
    key = bench.build_report()["replay_key"]
    assert set(key) == _EXPECTED_REPLAY_KEY
    # the version axis carries the real values (spot-check the union spans every layer).
    assert key["feature_schema_version"] == "0.1.0"
    assert key["taxonomy_version"] == "1.0.0"
    assert key["packet_schema_version"] == "0.2.0"
    assert all(len(key[k]) == 64 for k in key if k.endswith("_fingerprint"))


def test_measures_declared() -> None:
    assert bench.build_report()["measures"] == [
        "end_to_end_replay_determinism",
        "admission_idempotency",
        "verdict_distribution",
        "fill_distribution",
        "ledger_state_hash",
        "portfolio_state_hash",
        "full_replay_key",
    ]


def test_pinned_hashes() -> None:
    report = bench.build_report()
    for key in ("pinned_ledger_state_hash", "pinned_portfolio_state_hash"):
        value = report[key]
        assert isinstance(value, str) and len(value) == 64
    assert report["pinned_ledger_state_hash"] == report["real_sequence"]["ending_ledger_state_hash"]
    assert report["pinned_portfolio_state_hash"] == report["real_sequence"]["ending_portfolio_state_hash"]


def test_committed_artifact_in_sync() -> None:
    artifact = json.loads(bench.ARTIFACT_PATH.read_text(encoding="utf-8"))
    assert artifact == bench.build_report()
