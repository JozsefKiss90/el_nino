"""TEST-016 — paper-runtime ledger: idempotency, append-only, seq continuity, sequence replay.

The append-only, self-describing ledger is the runtime's replay state. Replaying the same sequence
from the same starting ledger reproduces identical records AND an identical ending state_hash; a
re-presented snapshot is flagged duplicate; seq continues across persist/reload; a halted operation
mid-sequence REJECTs while the ledger still advances.
"""

from __future__ import annotations

import json

from gold.decision_builder.models import (
    ConfidenceInputs,
    DecisionMode,
    Direction,
    GoldDecisionPacket,
    GuardRefs,
    SnapshotGuards,
)
from gold.paper_runtime import (
    LedgerEntry,
    OperationalInput,
    RuntimeLedger,
    Verdict,
    evaluate,
    load_ledger,
    load_operational,
    run_once,
    run_sequence,
)

_SG_TRUE = SnapshotGuards(data_ok=True, freshness_ok=True, cooldown_ok=True)
_OP_OPEN = OperationalInput("GLD", tradeable=True, venue_open=True, halt=False, degraded=False)
_OP_HALT = OperationalInput("GLD", tradeable=False, venue_open=False, halt=True, degraded=False)


def _packet(snapshot_id: str, direction: Direction = Direction.LONG) -> GoldDecisionPacket:
    return GoldDecisionPacket(
        packet_id=f"gold-v0:{snapshot_id}",
        packet_schema_version="0.2.0",
        instrument="GLD",
        decision_mode=DecisionMode.PAPER_ONLY,
        regime="RESTRICTIVE_RATES",
        direction=direction,
        confidence=0.5,
        uncertainty=0.5,
        rationale="r",
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
        as_of=f"2026-05-0{snapshot_id[-1]}T00:00:00+00:00",
        snapshot_guards=_SG_TRUE,
    )


def _seq() -> list[tuple[GoldDecisionPacket, OperationalInput]]:
    # three distinct snapshots, then a re-presentation of the first (idempotency demonstration)
    return [
        (_packet("S1"), _OP_OPEN),
        (_packet("S2"), _OP_OPEN),
        (_packet("S3"), _OP_OPEN),
        (_packet("S1"), _OP_OPEN),
    ]


# --- sequence replay determinism --------------------------------------------------------------

def test_run_sequence_twice_identical_records_and_ending_ledger() -> None:
    records_a, led_a = run_sequence(_seq())
    records_b, led_b = run_sequence(_seq())
    dump_a = [json.dumps(r.to_dict(), sort_keys=True) for r in records_a]
    dump_b = [json.dumps(r.to_dict(), sort_keys=True) for r in records_b]
    assert dump_a == dump_b
    assert led_a.state_hash() == led_b.state_hash()


def test_re_presented_snapshot_is_duplicate_non_admit() -> None:
    records, led = run_sequence(_seq())
    assert records[0].verdict is Verdict.ADMIT          # S1 first time
    assert records[3].verdict is Verdict.REJECT         # S1 re-presented
    assert records[3].triggered_guard == "duplicate_ok"
    assert len(led.entries) == 4                        # every presentation appends one entry


def test_has_admit_only_counts_admits() -> None:
    _, led = run_sequence([(_packet("S1"), _OP_HALT)])  # S1 REJECTed (operational)
    assert led.has_admit("S1") is False                 # a REJECT does not count as admitted
    # so a later genuine admission of S1 (operational restored) is NOT blocked as a duplicate
    rec, _ = evaluate(_packet("S1"), led, _OP_OPEN)
    assert rec.verdict is Verdict.ADMIT


# --- append-only + seq ------------------------------------------------------------------------

def test_append_is_immutable_and_seq_is_length_derived() -> None:
    led0 = RuntimeLedger.empty()
    entry = LedgerEntry("S1", "gold-v0:S1", "t", Verdict.ADMIT.value, None, "d", "f", led0.next_seq())
    led1 = led0.append(entry)
    assert len(led0.entries) == 0       # original ledger unchanged (immutable)
    assert len(led1.entries) == 1
    assert led1.entries[0].seq == 0
    assert led1.next_seq() == 1


def test_halted_op_mid_sequence_rejects_but_ledger_advances() -> None:
    items = [(_packet("S1"), _OP_OPEN), (_packet("S2"), _OP_HALT), (_packet("S3"), _OP_OPEN)]
    records, led = run_sequence(items)
    assert [r.verdict for r in records] == [Verdict.ADMIT, Verdict.REJECT, Verdict.ADMIT]
    assert len(led.entries) == 3                 # the REJECT still advanced the ledger
    assert [e.seq for e in led.entries] == [0, 1, 2]


# --- serialization + IO round-trip ------------------------------------------------------------

def test_state_hash_stable_through_serialization() -> None:
    _, led = run_sequence(_seq())
    reparsed = RuntimeLedger.from_dict(json.loads(json.dumps(led.to_dict())))
    assert reparsed.state_hash() == led.state_hash()


def test_seq_continuity_across_persist_and_reload(tmp_path) -> None:  # type: ignore[no-untyped-def]
    ledger_path = tmp_path / "ledger.json"
    # first invocation persists a 1-entry ledger
    rec1 = run_once(_packet("S1"), ledger_path, tmp_path / "op_absent.json")  # op absent -> closed
    assert rec1.verdict is Verdict.REJECT  # default-closed operational input blocks admission
    reloaded = load_ledger(ledger_path)
    assert reloaded.next_seq() == 1
    # second invocation continues seq from the reloaded ledger
    rec2 = run_once(_packet("S2"), ledger_path, tmp_path / "op_absent.json")
    assert rec2.verdict is Verdict.REJECT
    final = load_ledger(ledger_path)
    assert [e.seq for e in final.entries] == [0, 1]


def test_load_defaults_absent_ledger_empty_and_operational_closed(tmp_path) -> None:  # type: ignore[no-untyped-def]
    assert load_ledger(tmp_path / "nope.json").entries == ()
    op = load_operational(tmp_path / "nope.json")
    assert op.tradeable is False  # default-closed
