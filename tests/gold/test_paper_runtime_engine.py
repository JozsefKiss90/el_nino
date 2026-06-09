"""TEST-014 — paper-runtime engine (evaluate): conjunction order, fail-closed verdict, HOLD.

Exercises the verdict logic end-to-end: ADMIT when required guards pass, REJECT naming the first
failing required guard (in _GUARD_NAMES order), HOLD on a WATCH/INDETERMINATE packet, the config
require-flags, the supervisor_ok None stub, and the RuntimeDecisionRecord fail-closed __post_init__.
"""

from __future__ import annotations

import pytest

from gold.decision_builder.models import (
    ConfidenceInputs,
    DecisionMode,
    Direction,
    GoldDecisionPacket,
    GuardRefs,
    SnapshotGuards,
)
from gold.paper_runtime import (
    DEFAULT_RUNTIME_POLICY_CONFIG,
    GuardOutcome,
    OperationalInput,
    RuntimeContractError,
    RuntimeDecisionRecord,
    RuntimeLedger,
    RuntimePolicyConfig,
    Verdict,
    evaluate,
)
from gold.paper_runtime.models import GUARD_NAMES

_SG_TRUE = SnapshotGuards(data_ok=True, freshness_ok=True, cooldown_ok=True)
_OP_OPEN = OperationalInput("GLD", tradeable=True, venue_open=True, halt=False, degraded=False)
_OP_HALT = OperationalInput("GLD", tradeable=False, venue_open=False, halt=True, degraded=False)


def _packet(
    snapshot_id: str = "S1",
    direction: Direction = Direction.LONG,
    sg: SnapshotGuards | None = _SG_TRUE,
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
        as_of="2026-05-01T00:00:00+00:00",
        snapshot_guards=sg,
    )


def _record(verdict: Verdict, triggered: str | None) -> RuntimeDecisionRecord:
    return RuntimeDecisionRecord(
        record_id="paper-v0:x",
        record_schema_version="0.1.0",
        source_packet_id="gold-v0:S1",
        source_snapshot_id="S1",
        decision_mode=DecisionMode.PAPER_ONLY,
        verdict=verdict,
        triggered_guard=triggered,
        reason="r",
        guard_outcomes=(),
        runtime_policy_version="0.1.0",
        as_of=None,
        prior_ledger_state_hash="p",
        new_ledger_state_hash="n",
        non_execution_notice="x",
        constraints=(),
    )


# --- verdict paths ----------------------------------------------------------------------------

def test_admit_when_all_required_pass() -> None:
    rec, led = evaluate(_packet(), RuntimeLedger.empty(), _OP_OPEN)
    assert rec.verdict is Verdict.ADMIT
    assert rec.triggered_guard is None
    assert rec.decision_mode is DecisionMode.PAPER_ONLY
    assert len(led.entries) == 1  # exactly one ledger entry appended


def test_reject_on_duplicate_first() -> None:
    _, led1 = evaluate(_packet("S1"), RuntimeLedger.empty(), _OP_OPEN)
    rec2, _ = evaluate(_packet("S1"), led1, _OP_OPEN)
    assert rec2.verdict is Verdict.REJECT
    assert rec2.triggered_guard == "duplicate_ok"


def test_reject_on_operational() -> None:
    rec, _ = evaluate(_packet(), RuntimeLedger.empty(), _OP_HALT)
    assert rec.verdict is Verdict.REJECT
    assert rec.triggered_guard == "operational_ok"


def test_hold_on_watch_direction() -> None:
    rec, led = evaluate(_packet(direction=Direction.WATCH, regime="CURVE_INVERSION"),
                        RuntimeLedger.empty(), _OP_OPEN)
    assert rec.verdict is Verdict.HOLD
    assert rec.triggered_guard == "actionable_stance"
    assert len(led.entries) == 1  # a HOLD still records exactly one entry


def test_hold_on_indeterminate_regime() -> None:
    # INDETERMINATE always maps to direction WATCH (packet invariant) -> HOLD
    rec, _ = evaluate(_packet(direction=Direction.WATCH, regime="INDETERMINATE"),
                     RuntimeLedger.empty(), _OP_OPEN)
    assert rec.verdict is Verdict.HOLD


def test_first_failure_names_guard_in_canonical_order() -> None:
    # data_ok (echo False) AND operational (halt) both fail; data_ok precedes operational_ok
    pkt = _packet(sg=SnapshotGuards(data_ok=False, freshness_ok=True, cooldown_ok=True))
    rec, _ = evaluate(pkt, RuntimeLedger.empty(), _OP_HALT)
    assert rec.verdict is Verdict.REJECT
    assert rec.triggered_guard == "data_ok"


# --- config require-flags ---------------------------------------------------------------------

def test_require_operational_false_admits_through_halt() -> None:
    cfg = RuntimePolicyConfig(require_operational=False)
    rec, _ = evaluate(_packet(), RuntimeLedger.empty(), _OP_HALT, cfg)
    assert rec.verdict is Verdict.ADMIT


def test_require_snapshot_guards_false_admits_through_bad_data() -> None:
    cfg = RuntimePolicyConfig(require_snapshot_guards=False)
    pkt = _packet(sg=SnapshotGuards(data_ok=False, freshness_ok=False, cooldown_ok=False))
    rec, _ = evaluate(pkt, RuntimeLedger.empty(), _OP_OPEN, cfg)
    assert rec.verdict is Verdict.ADMIT


# --- guard block shape ------------------------------------------------------------------------

def test_guard_outcomes_full_block_in_canonical_order() -> None:
    rec, _ = evaluate(_packet(), RuntimeLedger.empty(), _OP_OPEN)
    assert tuple(g.name for g in rec.guard_outcomes) == GUARD_NAMES


def test_supervisor_ok_is_none_stub_not_gating() -> None:
    rec, _ = evaluate(_packet(), RuntimeLedger.empty(), _OP_OPEN)
    supervisor = next(g for g in rec.guard_outcomes if g.name == "supervisor_ok")
    assert isinstance(supervisor, GuardOutcome)
    assert supervisor.passed is None
    assert rec.verdict is Verdict.ADMIT  # the None stub does not block ADMIT


def test_default_config_used_when_omitted() -> None:
    rec, _ = evaluate(_packet(), RuntimeLedger.empty(), _OP_OPEN)
    assert rec.runtime_policy_version == DEFAULT_RUNTIME_POLICY_CONFIG.runtime_policy_version


# --- record fail-closed invariant -------------------------------------------------------------

def test_record_admit_must_not_name_guard() -> None:
    with pytest.raises(RuntimeContractError, match="ADMIT record must not"):
        _record(Verdict.ADMIT, "data_ok")


def test_record_non_admit_must_name_guard() -> None:
    with pytest.raises(RuntimeContractError, match="must name its triggering guard"):
        _record(Verdict.REJECT, None)


def test_record_valid_combinations_construct() -> None:
    assert _record(Verdict.ADMIT, None).verdict is Verdict.ADMIT
    assert _record(Verdict.REJECT, "operational_ok").triggered_guard == "operational_ok"
    assert _record(Verdict.HOLD, "actionable_stance").verdict is Verdict.HOLD
