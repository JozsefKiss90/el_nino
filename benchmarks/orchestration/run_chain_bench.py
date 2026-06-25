"""Full-chain orchestrator benchmark + replay harness (BENCH-006, MOD-010).

Proves the **end-to-end** Layer-3 replay determinism + admission idempotency the chain orchestrator
threads — ``consume → build_features → classify → build_decision → evaluate → [GATE-001] → execute``
in one deterministic call. Deterministic and IO-light: fixed committed inputs, a **captured** guard
config + a **captured** operational input (env-independent, ADR-011 gate c.4 / ADR-009 §3), no clock /
network / randomness. Mirrors the BENCH-003 / BENCH-004 harness shape (deterministic harness →
committed golden JSON → artifact-in-sync test).

REAL SEQUENCE: thread the real consumable snapshots through the orchestrator ``run_sequence`` (one
runtime ledger + one portfolio — genuine once-ever dedup) **twice**; assert byte-identical *all five*
record types (feature / regime / packet / runtime / execution) and identical ending ledger + portfolio
``state_hash``. Re-present the first snapshot to evidence end-to-end idempotency.

HONEST CAVEAT (carried forward from BENCH-004): the real corpus is monochromatic
``RESTRICTIVE_RATES → AVOID`` (a non-LONG stance), so the end-to-end real path is a deterministic
**ADMIT + no-fill**, and the re-presentation **REJECTs** on ``duplicate_ok`` (no second admit, no
double-fill). This bench therefore proves **end-to-end replay determinism + admission idempotency**,
**not** a real fill — the fill path is covered by BENCH-004's synthetic execution sweep.

``measures`` carries the **full replay key** — the union of every composed layer's version axis + the
captured guard / operational fingerprints.

Run standalone:  python benchmarks/orchestration/run_chain_bench.py
Writes the golden artifact to benchmarks/orchestration/artifacts/chain_bench.json.
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

from execution.config import (  # noqa: E402
    DEFAULT_EXECUTION_POLICY_CONFIG,
    DEFAULT_FILL_MODEL,
)
from execution.models import EXECUTION_SCHEMA_VERSION, PORTFOLIO_SCHEMA_VERSION  # noqa: E402
from execution.price_reference import EXEC_PRICE_SOURCE_VERSION  # noqa: E402
from features.feature_builder.models import FEATURE_SCHEMA_VERSION  # noqa: E402
from gold.decision_builder.config import DEFAULT_DECISION_POLICY_CONFIG  # noqa: E402
from gold.decision_builder.models import PACKET_SCHEMA_VERSION  # noqa: E402
from gold.paper_runtime.config import DEFAULT_RUNTIME_POLICY_CONFIG  # noqa: E402
from gold.paper_runtime.models import (  # noqa: E402
    LEDGER_SCHEMA_VERSION,
    RECORD_SCHEMA_VERSION,
    Verdict,
)
from orchestration import DEFAULT_GUARD_CONFIG, DEFAULT_OPERATIONAL_INPUT, run_sequence  # noqa: E402
from orchestration.models import ChainResult  # noqa: E402
from regime.regime_classifier.models import (  # noqa: E402
    CLASSIFICATION_TRACE_VERSION,
    CLASSIFIER_VERSION,
    TAXONOMY_VERSION,
)
from snapshot.snapshot_consumer import consume  # noqa: E402
from snapshot.snapshot_consumer.models import Snapshot, SnapshotContractError  # noqa: E402

ARTIFACT_PATH = _REPO_ROOT / "benchmarks" / "orchestration" / "artifacts" / "chain_bench.json"

# The real consumable snapshots (the same corpus MOD-007 / MOD-008 thread — all resolve to 952cc83a).
_REAL_INPUTS: tuple[tuple[str, Path], ...] = (
    ("latest_snapshot_pass",
     _REPO_ROOT / "tests" / "snapshot" / "fixtures" / "latest_snapshot_pass.json"),
    ("src_latest_snapshot", _REPO_ROOT / "snapshot_sources" / "latest_snapshot.json"),
    ("src_snapshot", _REPO_ROOT / "snapshot_sources" / "snapshot.json"),
)


def _guard_config_fingerprint() -> str:
    """SHA-256 over the captured guard config — evidences it folds into the replay key (gate c.4)."""
    payload = json.dumps(asdict(DEFAULT_GUARD_CONFIG), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _replay_key() -> dict[str, str]:
    """The full replay key: the union of every composed layer's version axis + captured fingerprints."""
    return {
        "classification_trace_version": CLASSIFICATION_TRACE_VERSION,
        "classifier_version": CLASSIFIER_VERSION,
        "decision_policy_fingerprint": DEFAULT_DECISION_POLICY_CONFIG.decision_policy_fingerprint(),
        "decision_policy_version": DEFAULT_DECISION_POLICY_CONFIG.decision_policy_version,
        "exec_price_source_version": EXEC_PRICE_SOURCE_VERSION,
        "execution_policy_fingerprint": DEFAULT_EXECUTION_POLICY_CONFIG.fingerprint(),
        "execution_policy_version": DEFAULT_EXECUTION_POLICY_CONFIG.execution_policy_version,
        "execution_schema_version": EXECUTION_SCHEMA_VERSION,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "fill_model_fingerprint": DEFAULT_FILL_MODEL.fingerprint(),
        "fill_model_version": DEFAULT_FILL_MODEL.fill_model_version,
        "guard_config_fingerprint": _guard_config_fingerprint(),
        "ledger_schema_version": LEDGER_SCHEMA_VERSION,
        "operational_input_fingerprint": DEFAULT_OPERATIONAL_INPUT.fingerprint(),
        "packet_schema_version": PACKET_SCHEMA_VERSION,
        "portfolio_schema_version": PORTFOLIO_SCHEMA_VERSION,
        "record_schema_version": RECORD_SCHEMA_VERSION,
        "runtime_policy_fingerprint": DEFAULT_RUNTIME_POLICY_CONFIG.runtime_policy_fingerprint(),
        "runtime_policy_version": DEFAULT_RUNTIME_POLICY_CONFIG.runtime_policy_version,
        "taxonomy_version": TAXONOMY_VERSION,
    }


def _result(label: str, r: ChainResult) -> dict[str, Any]:
    """One run's replay-relevant projection (deterministic, JSON-stable)."""
    ex = r.execution_record
    return {
        "direction": r.packet.direction.value,
        "execution_filled": (ex is not None and ex.fill is not None),
        "execution_reason": (ex.reason if ex is not None else None),
        "label": label,
        "ledger_state_hash": r.ledger.state_hash(),
        "packet_id": r.packet.packet_id,
        "portfolio_state_hash": r.portfolio.state_hash(),
        "regime": r.packet.regime,
        "source_snapshot_id": r.runtime_record.source_snapshot_id,
        "triggered_guard": r.runtime_record.triggered_guard,
        "verdict": r.runtime_record.verdict.value,
    }


def _load_real() -> tuple[list[str], list[Snapshot]]:
    """Load the consumable real snapshots (skipping absent / malformed), labelled in input order."""
    labels: list[str] = []
    snaps: list[Snapshot] = []
    for label, path in _REAL_INPUTS:
        try:
            snap = consume(path)
        except SnapshotContractError:
            continue
        if snap is None:
            continue
        labels.append(label)
        snaps.append(snap)
    return labels, snaps


def run_real() -> dict[str, Any]:
    """Thread the real snapshots through the chain twice; assert byte-identical all-record replay."""
    labels, snaps = _load_real()
    if snaps:  # re-present the first consumable snapshot (end-to-end idempotency evidence)
        labels = [*labels, f"{labels[0]}__re_presented"]
        snaps = [*snaps, snaps[0]]

    results_a, ledger_a, pf_a = run_sequence(snaps)
    results_b, ledger_b, pf_b = run_sequence(snaps)
    dump_a = [json.dumps(r.to_dict(), sort_keys=True) for r in results_a]
    dump_b = [json.dumps(r.to_dict(), sort_keys=True) for r in results_b]
    byte_identical = (
        dump_a == dump_b
        and ledger_a.state_hash() == ledger_b.state_hash()
        and pf_a.state_hash() == pf_b.state_hash()
    )

    results = [_result(label, r) for label, r in zip(labels, results_a)]
    verdicts = {v.value: sum(1 for r in results if r["verdict"] == v.value) for v in Verdict}
    filled = sum(1 for r in results if r["execution_filled"])
    re = next((r for r in results if r["label"].endswith("__re_presented")), None)
    return {
        "all_replays_byte_identical": byte_identical,
        "consumable_inputs": [
            {"label": lbl, "source_snapshot_id": r["source_snapshot_id"], "verdict": r["verdict"]}
            for lbl, r in zip(labels, results)
        ],
        "ending_ledger_state_hash": ledger_a.state_hash(),
        "ending_portfolio_state_hash": pf_a.state_hash(),
        "fill_distribution": {"filled": filled, "no_fill": len(results) - filled},
        "idempotency": {
            "re_presented_execution_filled": (re["execution_filled"] if re else None),
            "re_presented_triggered_guard": (re["triggered_guard"] if re else None),
            "re_presented_verdict": (re["verdict"] if re else None),
        },
        "real_admit_count": sum(1 for r in results if r["verdict"] == Verdict.ADMIT.value),
        "real_corpus_note": (
            "The real corpus is monochromatic RESTRICTIVE_RATES → AVOID (non-LONG): the end-to-end "
            "path is a deterministic ADMIT + no-fill, and the re-presentation REJECTs on duplicate_ok "
            "(no second admit, no double-fill). This proves end-to-end replay determinism + admission "
            "idempotency, not a real fill — the fill path is covered by BENCH-004's synthetic sweep."
        ),
        "results": results,
        "sequence_length": len(snaps),
        "verdict_distribution": verdicts,
    }


def build_report() -> dict[str, Any]:
    """Assemble the full, deterministic benchmark report."""
    real = run_real()
    return {
        "all_replays_byte_identical": real["all_replays_byte_identical"],
        "benchmark_id": "BENCH-006",
        "measures": [
            "end_to_end_replay_determinism",
            "admission_idempotency",
            "verdict_distribution",
            "fill_distribution",
            "ledger_state_hash",
            "portfolio_state_hash",
            "full_replay_key",
        ],
        "pinned_ledger_state_hash": real["ending_ledger_state_hash"],
        "pinned_portfolio_state_hash": real["ending_portfolio_state_hash"],
        "real_sequence": real,
        "replay_key": _replay_key(),
    }


def main() -> None:
    report = build_report()
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    real = report["real_sequence"]
    print(f"wrote {ARTIFACT_PATH.relative_to(_REPO_ROOT)}")
    print(
        f"real: byte_identical={real['all_replays_byte_identical']} "
        f"admits={real['real_admit_count']} "
        f"verdicts={[(r['label'], r['verdict'], r['execution_filled']) for r in real['results']]}"
    )
    print(f"idempotency={real['idempotency']}")
    print(f"all_replays_byte_identical={report['all_replays_byte_identical']}")
    print(f"pinned_ledger_state_hash={report['pinned_ledger_state_hash']}")
    print(f"pinned_portfolio_state_hash={report['pinned_portfolio_state_hash']}")


if __name__ == "__main__":
    main()
