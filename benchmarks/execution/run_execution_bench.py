"""Execution-layer benchmark + replay harness (BENCH-004, ADR-011 §2 / gate d).

Closes ADR-011 §7 gate (d): the byte-identical sequence-replay benchmark proving the execution
determinism invariant over the STEP-2 simulator core. Deterministic and IO-light — fixed committed
inputs, a **captured** guard config (env-independent, ADR-011 gate c.4), no clock / network /
randomness. Mirrors the BENCH-003 paper-runtime harness shape (deterministic harness → committed
golden JSON → artifact-in-sync test). Two parts:

  Part 1 — REAL SEQUENCE (replay determinism on the real corpus). Build ADMIT
  ``RuntimeDecisionRecord`` s by threading the real consumable snapshots through the existing chain
  (``consume → build_features → classify → build_decision → evaluate``) under one runtime ledger
  (genuine once-ever dedup), forwarding each ADMIT's gold-packet ``direction`` and the D1 re-derived
  ``instrument_price`` (the FeatureVector's ``gold_price``). Thread the ADMITs through the execution
  ``run_sequence`` twice with the same captured guard config; assert byte-identical execution records
  and an identical ending portfolio ``state_hash``. Re-present the snapshot to evidence deterministic
  idempotency.

  NOTE on the real corpus: both banked snapshots (``952cc83a…`` 2026-05-01, and ``05c8369d…``
  2026-06-11 — the latter lives only in the Mr-Ripley truth DB, not as a committed el_nino consumable
  file) classify ``RESTRICTIVE_RATES → AVOID``, a **non-LONG** stance. The execution engine fills
  only an approved LONG on a fresh snapshot, so the real ADMIT is a deterministic **no-fill**
  (non-LONG stance) and never reaches the once-ever fill-dedup branch (no execution entry is
  appended). The real sequence therefore evidences **replay determinism + stable portfolio state** on
  real data; the fill, the no-double-fill idempotency, and the guard-block attribution are exercised
  by the synthetic sequence below.

  Part 2 — SYNTHETIC SEQUENCE (clearly labelled). Constructed ADMIT records exercising the full
  execution outcome space: APPROVE+LONG ⇒ fill; non-LONG (AVOID/FLAT) ⇒ no-fill; duplicate snapshot
  ⇒ idempotent no-fill (no double-fill); guard BLOCK ⇒ no-fill + ``blocked_by`` attribution (a
  separate sub-sequence under a restrictive captured guard config — ``position_size_ok``).

Run standalone:  python benchmarks/execution/run_execution_bench.py
Writes the golden artifact to benchmarks/execution/artifacts/execution_bench.json.
"""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))

from execution import (  # noqa: E402
    DEFAULT_EXECUTION_POLICY_CONFIG,
    DEFAULT_FILL_MODEL,
    EXEC_PRICE_SOURCE_VERSION,
    EXECUTION_SCHEMA_VERSION,
    PORTFOLIO_SCHEMA_VERSION,
    ExecutionItem,
    ExecutionRecord,
    resolve_sim_exec_ref,
    run_sequence,
)
from features.feature_builder import build_features  # noqa: E402
from features.feature_builder.models import FeatureVector  # noqa: E402
from gold.decision_builder import SnapshotGuards, build_decision  # noqa: E402
from gold.decision_builder.models import (  # noqa: E402
    DecisionMode,
    Direction,
    GoldDecisionPacket,
)
from gold.paper_runtime import (  # noqa: E402
    OperationalInput,
    RuntimeDecisionRecord,
    RuntimeLedger,
    Verdict,
    evaluate,
)
from regime.regime_classifier import classify  # noqa: E402
from risk.guardrail_engine.models import GuardrailConfig  # noqa: E402
from snapshot.snapshot_consumer import consume  # noqa: E402
from snapshot.snapshot_consumer.models import SnapshotContractError  # noqa: E402

ARTIFACT_PATH = _REPO_ROOT / "benchmarks" / "execution" / "artifacts" / "execution_bench.json"

# Captured guard configs (ADR-011 gate c.4): explicit values, NOT read from os.environ on the replay
# path, so a replayed APPROVE/BLOCK is independent of ambient env. Mirrors the TEST-019/020 idiom.
_GUARD_OK = GuardrailConfig(
    max_trade_size=10_000.0,
    max_trades_per_day=10,
    max_position_pct=0.05,
    max_positions=5,
    daily_loss_cap=5_000.0,
    allow_withdrawals=False,
)
# Blocks position_size_ok: limit = min(100000 * 1e-7, 0.5) = 0.01 < default_size 1.0.
_GUARD_BLOCK_SIZE = GuardrailConfig(
    max_trade_size=0.5,
    max_trades_per_day=10,
    max_position_pct=1e-7,
    max_positions=5,
    daily_loss_cap=5_000.0,
    allow_withdrawals=False,
)

# The real consumable snapshots the MOD-007 / BENCH-003 thread uses (all resolve to 952cc83a today).
_REAL_INPUTS: tuple[tuple[str, Path], ...] = (
    ("latest_snapshot_pass",
     _REPO_ROOT / "tests" / "snapshot" / "fixtures" / "latest_snapshot_pass.json"),
    ("src_latest_snapshot", _REPO_ROOT / "snapshot_sources" / "latest_snapshot.json"),
    ("src_snapshot", _REPO_ROOT / "snapshot_sources" / "snapshot.json"),
)

_SYNTHETIC_PRICE = 100.0  # a fixed, clearly-synthetic instrument price


def _guard_config_fingerprint(config: GuardrailConfig) -> str:
    """SHA-256 over the captured guard config — evidences it folds into the replay key (gate c.4)."""
    payload = json.dumps(asdict(config), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _result(label: str, rec: ExecutionRecord) -> dict[str, Any]:
    """One execution record's replay-relevant projection (deterministic, JSON-stable)."""
    return {
        "blocked_by": rec.guard_result.blocked_by,
        "direction": rec.direction.value,
        "execution_id": rec.execution_id,
        "fill_price": (round(rec.fill.fill_price, 6) if rec.fill is not None else None),
        "filled": rec.fill is not None,
        "guard_approved": rec.guard_result.approved,
        "label": label,
        "new_portfolio_state_hash": rec.new_portfolio_state_hash,
        "reason": rec.reason,
        "source_snapshot_id": rec.source_snapshot_id,
    }


def _replay_block(
    labels: list[str], items: list[ExecutionItem], guard_config: GuardrailConfig
) -> dict[str, Any]:
    """Run a labelled ADMIT sequence twice; record determinism + per-item outcomes + distributions."""
    records_a, pf_a = run_sequence(items, guard_config)
    records_b, pf_b = run_sequence(items, guard_config)
    dump_a = [json.dumps(r.to_dict(), sort_keys=True) for r in records_a]
    dump_b = [json.dumps(r.to_dict(), sort_keys=True) for r in records_b]
    byte_identical = dump_a == dump_b and pf_a.state_hash() == pf_b.state_hash()
    results = [_result(label, rec) for label, rec in zip(labels, records_a)]
    filled = sum(1 for r in results if r["filled"])
    return {
        "all_replays_byte_identical": byte_identical,
        "ending_portfolio_state_hash": pf_a.state_hash(),
        "fill_distribution": {"filled": filled, "no_fill": len(results) - filled},
        "guard_config_fingerprint": _guard_config_fingerprint(guard_config),
        "results": results,
        "sequence_length": len(items),
    }


# --- Part 1: real sequence ------------------------------------------------------------------


def _build_chain(path: Path) -> tuple[GoldDecisionPacket, FeatureVector, OperationalInput] | None:
    """Run consume → features → classify → build_decision for one real snapshot path (or None)."""
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
    packet = build_decision(fv, rc, snapshot_guards=sg, as_of=snap.clock_ts)
    op = OperationalInput(
        instrument="GLD", tradeable=True, venue_open=True, halt=False, degraded=False,
        as_of=snap.clock_ts,
    )
    return packet, fv, op


def run_real() -> dict[str, Any]:
    """Thread the real snapshots through the chain (one ledger), then replay the ADMITs in execution."""
    led = RuntimeLedger.empty()
    consumable: list[dict[str, Any]] = []
    admits: list[tuple[str, RuntimeDecisionRecord, Direction, float]] = []
    for label, path in _REAL_INPUTS:
        built = _build_chain(path)
        if built is None:
            continue
        packet, fv, op = built
        record, led = evaluate(packet, led, op)
        consumable.append({
            "label": label,
            "runtime_triggered_guard": record.triggered_guard,
            "runtime_verdict": record.verdict.value,
            "source_snapshot_id": record.source_snapshot_id,
        })
        if record.verdict is Verdict.ADMIT and "gold_price" in fv.features:
            # ADR-014 bucket (i): the execution reference is the GLD *share* price (derived proxy on
            # the replay path), not gold spot — mirrors run_chain's resolver, never a live read.
            exec_ref = resolve_sim_exec_ref(fv.value("gold_price"), op.as_of)
            admits.append((label, record, packet.direction, exec_ref.price))

    labels = [f"{lbl}__admit" for (lbl, _, _, _) in admits]
    items: list[ExecutionItem] = [(rec, direction, price) for (_, rec, direction, price) in admits]
    if items:  # re-present the first real ADMIT's snapshot (deterministic idempotency evidence)
        labels.append(f"{admits[0][0]}__re_presented")
        items.append(items[0])

    block = _replay_block(labels, items, _GUARD_OK)
    block["consumable_inputs"] = consumable
    block["real_admit_count"] = len(admits)
    re = next((r for r in block["results"] if r["label"].endswith("__re_presented")), None)
    block["idempotency"] = {
        "re_presented_filled": re["filled"] if re else None,
        "re_presented_label": re["label"] if re else None,
        "re_presented_reason": re["reason"] if re else None,
    }
    block["real_corpus_note"] = (
        "Both banked snapshots classify RESTRICTIVE_RATES → AVOID (non-LONG); the execution engine "
        "fills only an approved LONG, so the real ADMIT is a deterministic no-fill (non-LONG stance) "
        "and never reaches the once-ever fill-dedup branch. The fill + no-double-fill idempotency "
        "are exercised by the synthetic sequence. 05c8369d… lives only in the Mr-Ripley truth DB."
    )
    return block


# --- Part 2: synthetic sequence -------------------------------------------------------------


def _admit(snapshot_id: str, record_id: str) -> RuntimeDecisionRecord:
    """A clearly-synthetic ADMIT record (mirrors the TEST-019/020 idiom)."""
    return RuntimeDecisionRecord(
        record_id=record_id,
        record_schema_version="0.1.0",
        source_packet_id=f"gold-v0:{snapshot_id}",
        source_snapshot_id=snapshot_id,
        decision_mode=DecisionMode.PAPER_ONLY,
        verdict=Verdict.ADMIT,
        triggered_guard=None,
        reason="synthetic ADMIT",
        guard_outcomes=(),
        runtime_policy_version="0.1.0",
        as_of=None,
        prior_ledger_state_hash="synthetic-prior",
        new_ledger_state_hash="synthetic-new",
        non_execution_notice="synthetic",
        constraints=(),
    )


def run_synthetic() -> dict[str, Any]:
    """Exercise the full execution outcome space across two captured-guard-config sub-sequences."""
    # Sub-sequence A (APPROVE captured config): fill, non-LONG no-fills, and a duplicate no-double-fill.
    approve_labels = [
        "SYN1_long_fill", "SYN2_avoid_nofill", "SYN3_flat_nofill", "SYN1_long_duplicate",
    ]
    approve_items: list[ExecutionItem] = [
        (_admit("SYN1", "syn-r1"), Direction.LONG, _SYNTHETIC_PRICE),
        (_admit("SYN2", "syn-r2"), Direction.AVOID, _SYNTHETIC_PRICE),
        (_admit("SYN3", "syn-r3"), Direction.FLAT, _SYNTHETIC_PRICE),
        (_admit("SYN1", "syn-r4"), Direction.LONG, _SYNTHETIC_PRICE),  # dup snapshot → idempotent
    ]
    approve = _replay_block(approve_labels, approve_items, _GUARD_OK)

    # Sub-sequence B (BLOCK captured config): an approved LONG is guard-blocked → no-fill attribution.
    block_labels = ["SYN4_long_block"]
    block_items: list[ExecutionItem] = [(_admit("SYN4", "syn-r5"), Direction.LONG, _SYNTHETIC_PRICE)]
    guard_block = _replay_block(block_labels, block_items, _GUARD_BLOCK_SIZE)

    filled = approve["fill_distribution"]["filled"] + guard_block["fill_distribution"]["filled"]
    no_fill = approve["fill_distribution"]["no_fill"] + guard_block["fill_distribution"]["no_fill"]
    return {
        "approve": approve,
        "fill_distribution": {"filled": filled, "no_fill": no_fill},
        "guard_block": guard_block,
        "synthetic": True,
    }


def _guard_block_attribution(synthetic: dict[str, Any]) -> dict[str, str | None]:
    """Map each blocked synthetic item to the first failing predicate (guard_block_attribution)."""
    return {
        r["label"]: r["blocked_by"]
        for r in synthetic["guard_block"]["results"]
        if r["blocked_by"] is not None
    }


def build_report() -> dict[str, Any]:
    """Assemble the full, deterministic benchmark report."""
    real = run_real()
    synthetic = run_synthetic()
    all_byte_identical = (
        real["all_replays_byte_identical"]
        and synthetic["approve"]["all_replays_byte_identical"]
        and synthetic["guard_block"]["all_replays_byte_identical"]
    )
    return {
        "all_replays_byte_identical": all_byte_identical,
        "benchmark_id": "BENCH-004",
        "exec_price_source_version": EXEC_PRICE_SOURCE_VERSION,
        "execution_policy_fingerprint": DEFAULT_EXECUTION_POLICY_CONFIG.fingerprint(),
        "execution_policy_version": DEFAULT_EXECUTION_POLICY_CONFIG.execution_policy_version,
        "execution_schema_version": EXECUTION_SCHEMA_VERSION,
        "fill_model_fingerprint": DEFAULT_FILL_MODEL.fingerprint(),
        "fill_model_version": DEFAULT_FILL_MODEL.fill_model_version,
        "guard_block_attribution": _guard_block_attribution(synthetic),
        "measures": [
            "replay_determinism",
            "idempotency",
            "fill_distribution",
            "portfolio_state_hash",
            "guard_block_attribution",
        ],
        "pinned_portfolio_state_hash": synthetic["approve"]["ending_portfolio_state_hash"],
        "portfolio_schema_version": PORTFOLIO_SCHEMA_VERSION,
        "real_sequence": real,
        "synthetic_sequence": synthetic,
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
        f"admits={real['real_admit_count']} "
        f"outcomes={[(r['label'], r['filled'], r['reason']) for r in real['results']]}"
    )
    print(
        f"synthetic: byte_identical="
        f"{syn['approve']['all_replays_byte_identical'] and syn['guard_block']['all_replays_byte_identical']} "
        f"fill_distribution={syn['fill_distribution']} "
        f"guard_block_attribution={report['guard_block_attribution']}"
    )
    print(f"all_replays_byte_identical={report['all_replays_byte_identical']}")
    print(f"pinned_portfolio_state_hash={report['pinned_portfolio_state_hash']}")


if __name__ == "__main__":
    main()
