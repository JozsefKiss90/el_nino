"""TEST-015 — paper-runtime determinism + runtime_policy_fingerprint coherence.

A RuntimeDecisionRecord is byte-identical across two evaluate() runs from the same prior ledger.
The runtime_policy_fingerprint pins the v0 policy set: an un-versioned require-flag edit changes it
(fails CI), while a version-only bump does not.
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
    DEFAULT_RUNTIME_POLICY_CONFIG,
    OperationalInput,
    RuntimeLedger,
    RuntimePolicyConfig,
    evaluate,
)

_SG_TRUE = SnapshotGuards(data_ok=True, freshness_ok=True, cooldown_ok=True)
_OP_OPEN = OperationalInput("GLD", tradeable=True, venue_open=True, halt=False, degraded=False)

# Pins the v0 runtime policy set (require_operational + require_snapshot_guards). An un-versioned
# edit to either flag changes this digest and fails CI (ADR-009 §7).
_DEFAULT_FINGERPRINT = "ab798cae915c1617f26c2a2793d425280d495099e593579a2ba99e74e9e56f32"


def _packet(snapshot_id: str = "S1", direction: Direction = Direction.LONG) -> GoldDecisionPacket:
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
        as_of="2026-05-01T00:00:00+00:00",
        snapshot_guards=_SG_TRUE,
    )


def test_record_byte_identical_across_two_runs() -> None:
    prior = RuntimeLedger.empty()
    rec_a, _ = evaluate(_packet(), prior, _OP_OPEN)
    rec_b, _ = evaluate(_packet(), prior, _OP_OPEN)
    assert json.dumps(rec_a.to_dict(), sort_keys=True) == json.dumps(rec_b.to_dict(), sort_keys=True)
    assert rec_a.record_id == rec_b.record_id


def test_record_id_binds_prior_ledger_state() -> None:
    # same packet, different prior ledger state => different record_id (per-evaluation identity)
    rec_a, led_a = evaluate(_packet("A"), RuntimeLedger.empty(), _OP_OPEN)
    rec_b, _ = evaluate(_packet("B"), led_a, _OP_OPEN)
    assert rec_a.record_id != rec_b.record_id


def test_runtime_policy_fingerprint_pinned() -> None:
    assert DEFAULT_RUNTIME_POLICY_CONFIG.runtime_policy_fingerprint() == _DEFAULT_FINGERPRINT


def test_fingerprint_changes_on_policy_drift() -> None:
    drifted = RuntimePolicyConfig(require_operational=False)
    assert drifted.runtime_policy_fingerprint() != _DEFAULT_FINGERPRINT


def test_fingerprint_excludes_version() -> None:
    bumped = RuntimePolicyConfig(runtime_policy_version="9.9.9")
    assert bumped.runtime_policy_fingerprint() == _DEFAULT_FINGERPRINT


def test_fingerprint_threads_into_record_id() -> None:
    # a policy with a different fingerprint yields a different record_id for the same packet/ledger
    rec_default, _ = evaluate(_packet(), RuntimeLedger.empty(), _OP_OPEN)
    rec_drifted, _ = evaluate(
        _packet(), RuntimeLedger.empty(), _OP_OPEN, RuntimePolicyConfig(require_operational=False)
    )
    assert rec_default.record_id != rec_drifted.record_id
