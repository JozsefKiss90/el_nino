"""TEST-021 — execution-layer benchmark (BENCH-004): determinism, idempotency, artifact-in-sync.

Mirrors test_paper_runtime_bench.py (TEST-017): the harness is deterministic, every block replays
byte-identically, the real sequence is grounded in the real corpus (not invented), the synthetic
sequence reaches the full execution outcome space (fill / non-LONG no-fill / idempotent no-double-fill
/ guard-block attribution), and the committed golden artifact stays in sync. Closes ADR-011 gate (d).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

_BENCH_DIR = Path(__file__).resolve().parents[2] / "benchmarks" / "execution"
if str(_BENCH_DIR) not in sys.path:
    sys.path.insert(0, str(_BENCH_DIR))

import run_execution_bench as bench  # type: ignore[import-not-found]  # noqa: E402


def _approve_results() -> dict[str, Any]:
    res = bench.build_report()["synthetic_sequence"]["approve"]["results"]
    return {r["label"]: r for r in res}


def test_report_is_deterministic() -> None:
    a = bench.build_report()
    b = bench.build_report()
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_all_replays_byte_identical() -> None:
    assert bench.build_report()["all_replays_byte_identical"] is True


def test_real_sequence_byte_identical() -> None:
    assert bench.build_report()["real_sequence"]["all_replays_byte_identical"] is True


def test_real_sequence_grounded_in_corpus() -> None:
    # The real ADMIT(s) must come from the consumable corpus (952cc83a today) — never invented.
    real = bench.build_report()["real_sequence"]
    assert real["real_admit_count"] >= 1
    admit = next(r for r in real["results"] if r["label"].endswith("__admit"))
    assert admit["source_snapshot_id"].startswith("952cc83a")


def test_real_corpus_is_non_long_no_fill() -> None:
    # Honest corpus reality: RESTRICTIVE_RATES → AVOID (non-LONG) ⇒ deterministic no-fill; the
    # re-presentation cannot reach the fill-dedup branch (no fill was ever appended).
    real = bench.build_report()["real_sequence"]
    assert real["fill_distribution"]["filled"] == 0
    assert real["idempotency"]["re_presented_filled"] is False


def test_synthetic_blocks_byte_identical() -> None:
    syn = bench.build_report()["synthetic_sequence"]
    assert syn["approve"]["all_replays_byte_identical"] is True
    assert syn["guard_block"]["all_replays_byte_identical"] is True


def test_synthetic_fill_distribution() -> None:
    dist = bench.build_report()["synthetic_sequence"]["fill_distribution"]
    assert dist["filled"] == 1   # only SYN1's first LONG presentation fills
    assert dist["no_fill"] == 4  # AVOID + FLAT + duplicate + guard-block


def test_synthetic_long_fills_at_slippage() -> None:
    fill = _approve_results()["SYN1_long_fill"]
    assert fill["filled"] is True
    assert fill["fill_price"] == 100.05  # 100.0 * (1 + 5bps/1e4)


def test_synthetic_non_long_does_not_fill() -> None:
    res = _approve_results()
    assert res["SYN2_avoid_nofill"]["filled"] is False
    assert res["SYN3_flat_nofill"]["filled"] is False


def test_synthetic_duplicate_is_idempotent_no_double_fill() -> None:
    res = _approve_results()
    dup = res["SYN1_long_duplicate"]
    assert dup["filled"] is False
    assert "idempotent" in dup["reason"]
    # the duplicate leaves the post-fill portfolio unchanged (no double-fill)
    assert dup["new_portfolio_state_hash"] == res["SYN1_long_fill"]["new_portfolio_state_hash"]


def test_guard_block_attribution() -> None:
    report = bench.build_report()
    assert report["guard_block_attribution"]["SYN4_long_block"] == "position_size_ok"
    blocked = report["synthetic_sequence"]["guard_block"]["results"][0]
    assert blocked["filled"] is False
    assert blocked["guard_approved"] is False


def test_captured_guard_config_is_replay_keyed() -> None:
    # The APPROVE and BLOCK captured configs fingerprint differently — they fold into the replay key
    # (gate c.4); the replay path never reads os.environ.
    syn = bench.build_report()["synthetic_sequence"]
    assert (
        syn["approve"]["guard_config_fingerprint"]
        != syn["guard_block"]["guard_config_fingerprint"]
    )


def test_measures_declared() -> None:
    assert bench.build_report()["measures"] == [
        "replay_determinism",
        "idempotency",
        "fill_distribution",
        "portfolio_state_hash",
        "guard_block_attribution",
    ]


def test_pinned_portfolio_state_hash() -> None:
    report = bench.build_report()
    pinned = report["pinned_portfolio_state_hash"]
    assert pinned == report["synthetic_sequence"]["approve"]["ending_portfolio_state_hash"]
    assert isinstance(pinned, str) and len(pinned) == 64


def test_committed_artifact_in_sync() -> None:
    artifact = json.loads(bench.ARTIFACT_PATH.read_text(encoding="utf-8"))
    assert artifact == bench.build_report()
