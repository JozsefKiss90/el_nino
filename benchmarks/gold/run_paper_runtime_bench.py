"""Paper-trading runtime benchmark + replay harness (BENCH-003, ADR-009).

Deterministic and replayable — fixed inputs, no randomness, no wall-clock. Two parts:

  Part 1 — REAL SEQUENCE (determinism + idempotency): build gold packets from the real consumable
  snapshots (``consume -> build_features -> classify -> build_decision`` with forwarded
  ``snapshot_guards`` + ``as_of``, ``guards`` left ``None`` — no enrich-back), pair each with a fixed
  open ``OperationalInput``, thread through ``run_sequence`` twice; assert byte-identical records +
  ending ledger. Re-present the first snapshot to evidence idempotency. (All three real paths are the
  same underlying snapshot today, so the real corpus is one snapshot replayed — honest, deterministic.)

  Part 2 — SYNTHETIC SEQUENCE (clearly labelled): a fixed sequence over constructed packets that
  exercises the full verdict space — ADMIT, HOLD (WATCH), REJECT (operational / data / duplicate) —
  and records the verdict distribution. Replayed twice; asserted byte-identical.

Run standalone:  python benchmarks/gold/run_paper_runtime_bench.py
Writes the golden artifact to benchmarks/gold/artifacts/paper_runtime_bench.json.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))

from features.feature_builder import build_features  # noqa: E402
from gold.decision_builder import GuardRefs, SnapshotGuards, build_decision  # noqa: E402
from gold.decision_builder.models import (  # noqa: E402
    ConfidenceInputs,
    DecisionMode,
    Direction,
    GoldDecisionPacket,
)
from gold.paper_runtime import (  # noqa: E402
    DEFAULT_RUNTIME_POLICY_CONFIG,
    LEDGER_SCHEMA_VERSION,
    RECORD_SCHEMA_VERSION,
    OperationalInput,
    Verdict,
    run_sequence,
)
from regime.regime_classifier import classify  # noqa: E402
from snapshot.snapshot_consumer import consume  # noqa: E402
from snapshot.snapshot_consumer.models import SnapshotContractError  # noqa: E402

ARTIFACT_PATH = _REPO_ROOT / "benchmarks" / "gold" / "artifacts" / "paper_runtime_bench.json"

_Item = tuple[GoldDecisionPacket, OperationalInput]

_OP_OPEN = OperationalInput("GLD", tradeable=True, venue_open=True, halt=False, degraded=False)
_OP_HALT = OperationalInput("GLD", tradeable=False, venue_open=False, halt=True, degraded=False)

_REAL_INPUTS: tuple[tuple[str, Path], ...] = (
    ("latest_snapshot_pass",
     _REPO_ROOT / "tests" / "snapshot" / "fixtures" / "latest_snapshot_pass.json"),
    ("src_latest_snapshot", _REPO_ROOT / "snapshot_sources" / "latest_snapshot.json"),
    ("src_snapshot", _REPO_ROOT / "snapshot_sources" / "snapshot.json"),
)


def _replay_block(labels: list[str], items: list[_Item]) -> dict[str, Any]:
    """Run a labelled (packet, op) sequence twice; record determinism + per-item outcomes."""
    records_a, ledger_a = run_sequence(items)
    records_b, ledger_b = run_sequence(items)
    dump_a = [json.dumps(r.to_dict(), sort_keys=True) for r in records_a]
    dump_b = [json.dumps(r.to_dict(), sort_keys=True) for r in records_b]
    byte_identical = dump_a == dump_b and ledger_a.state_hash() == ledger_b.state_hash()
    results = [
        {
            "label": label,
            "source_snapshot_id": rec.source_snapshot_id,
            "verdict": rec.verdict.value,
            "triggered_guard": rec.triggered_guard,
            "record_id": rec.record_id,
        }
        for label, rec in zip(labels, records_a)
    ]
    distribution = {v.value: sum(1 for r in results if r["verdict"] == v.value) for v in Verdict}
    return {
        "sequence_length": len(items),
        "all_replays_byte_identical": byte_identical,
        "no_enrich_back": all(p.guard_refs == GuardRefs() for p, _ in items),
        "ending_ledger_state_hash": ledger_a.state_hash(),
        "verdict_distribution": distribution,
        "results": results,
    }


# --- Part 1: real sequence ------------------------------------------------------------------


def _build_real_item(path: Path) -> _Item | None:
    try:
        snap = consume(path)
    except SnapshotContractError:
        return None
    if snap is None:
        return None
    fv = build_features(snap)
    rc = classify(fv)
    sg = SnapshotGuards(
        data_ok=snap.guards.data_ok,
        freshness_ok=snap.guards.freshness_ok,
        cooldown_ok=snap.guards.cooldown_ok,
    )
    # guards left None (the wrap invariant — no enrich-back); snapshot_guards is forwarded provenance.
    packet = build_decision(fv, rc, snapshot_guards=sg, as_of=snap.clock_ts)
    op = OperationalInput(
        instrument="GLD", tradeable=True, venue_open=True, halt=False, degraded=False,
        as_of=snap.clock_ts,
    )
    return packet, op


def run_real() -> dict[str, Any]:
    labels: list[str] = []
    items: list[_Item] = []
    for label, path in _REAL_INPUTS:
        built = _build_real_item(path)
        if built is None:
            continue
        labels.append(label)
        items.append(built)
    if items:  # re-present the first consumable snapshot (idempotency evidence)
        labels.append(f"{labels[0]}__re_presented")
        items.append(items[0])
    block = _replay_block(labels, items)
    dup = next((r for r in block["results"] if r["label"].endswith("__re_presented")), None)
    block["idempotency"] = {
        "re_presented_verdict": dup["verdict"] if dup else None,
        "re_presented_triggered_guard": dup["triggered_guard"] if dup else None,
    }
    return block


# --- Part 2: synthetic sequence -------------------------------------------------------------


def _synthetic_packet(
    snapshot_id: str,
    direction: Direction,
    sg: SnapshotGuards,
    regime: str = "RESTRICTIVE_RATES",
) -> GoldDecisionPacket:
    return GoldDecisionPacket(
        packet_id=f"gold-v0:{snapshot_id}",
        packet_schema_version="0.2.0",
        instrument="GLD",
        decision_mode=DecisionMode.PAPER_ONLY,
        regime=regime,
        direction=direction,
        confidence=0.5,
        uncertainty=0.5,
        rationale="synthetic",
        source_snapshot_id=snapshot_id,
        source_feature_schema_version="0.1.0",
        regime_taxonomy_version="1.0.0",
        regime_classifier_version="0.1.0",
        regime_classification_trace_version="0.1.0",
        matched_rule_id="rule",
        cited_features=(),
        decision_policy_version="0.1.0",
        confidence_inputs=ConfidenceInputs(0.5, 0, 0, 0, False, 0),
        guard_refs=GuardRefs(),
        non_execution_notice="n",
        constraints=(),
        as_of=f"2026-06-0{snapshot_id[-1]}T00:00:00+00:00",
        snapshot_guards=sg,
    )


def run_synthetic() -> dict[str, Any]:
    sg_ok = SnapshotGuards(data_ok=True, freshness_ok=True, cooldown_ok=True)
    sg_bad = SnapshotGuards(data_ok=False, freshness_ok=True, cooldown_ok=True)
    spec: tuple[tuple[str, GoldDecisionPacket, OperationalInput], ...] = (
        ("SYN1_long_admit", _synthetic_packet("SYN1", Direction.LONG, sg_ok), _OP_OPEN),
        ("SYN2_avoid_admit", _synthetic_packet("SYN2", Direction.AVOID, sg_ok), _OP_OPEN),
        ("SYN3_flat_admit", _synthetic_packet("SYN3", Direction.FLAT, sg_ok), _OP_OPEN),
        ("SYN4_watch_hold",
         _synthetic_packet("SYN4", Direction.WATCH, sg_ok, regime="CURVE_INVERSION"), _OP_OPEN),
        ("SYN5_reject_operational", _synthetic_packet("SYN5", Direction.LONG, sg_ok), _OP_HALT),
        ("SYN6_reject_data", _synthetic_packet("SYN6", Direction.LONG, sg_bad), _OP_OPEN),
        ("SYN1_reject_duplicate", _synthetic_packet("SYN1", Direction.LONG, sg_ok), _OP_OPEN),
    )
    labels = [s[0] for s in spec]
    items = [(s[1], s[2]) for s in spec]
    block = _replay_block(labels, items)
    block["synthetic"] = True
    return block


def build_report() -> dict[str, Any]:
    """Assemble the full, deterministic benchmark report."""
    return {
        "benchmark_id": "BENCH-003",
        "runtime_policy_version": DEFAULT_RUNTIME_POLICY_CONFIG.runtime_policy_version,
        "runtime_policy_fingerprint": DEFAULT_RUNTIME_POLICY_CONFIG.runtime_policy_fingerprint(),
        "record_schema_version": RECORD_SCHEMA_VERSION,
        "ledger_schema_version": LEDGER_SCHEMA_VERSION,
        "real_sequence": run_real(),
        "synthetic_sequence": run_synthetic(),
    }


def main() -> None:
    report = build_report()
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    real = report["real_sequence"]
    syn = report["synthetic_sequence"]
    print(f"wrote {ARTIFACT_PATH.relative_to(_REPO_ROOT)}")
    print(
        f"real: byte_identical={real['all_replays_byte_identical']} "
        f"no_enrich_back={real['no_enrich_back']} verdicts={[r['verdict'] for r in real['results']]}"
    )
    print(
        f"synthetic: byte_identical={syn['all_replays_byte_identical']} "
        f"distribution={syn['verdict_distribution']}"
    )


if __name__ == "__main__":
    main()
