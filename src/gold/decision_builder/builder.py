"""Gold Decision Builder (MOD-006) — (FeatureVector, RegimeClassification) -> GoldDecisionPacket.

``build_decision`` is a total, pure function: it reads only the two upstream contracts
(SCHEMA-009 + SCHEMA-010), the optional L3 guard outcomes, and a versioned
``DecisionPolicyConfig``, and returns a frozen ``GoldDecisionPacket``. No IO, clock,
randomness, history, global state, or ML (ADR-006 §3). Same snapshot + same regime versions
+ same ``decision_policy_version`` + same configuration => identical packet. Paper-only
(ADR-006 §1): the packet is a planning artifact, never a live order.
"""

from __future__ import annotations

from features.feature_builder.models import FeatureVector
from regime.regime_classifier import RegimeClassification

from .config import DEFAULT_DECISION_POLICY_CONFIG, DecisionPolicyConfig
from .models import (
    PACKET_SCHEMA_VERSION,
    DecisionMode,
    Direction,
    FeatureCitation,
    GoldDecisionPacket,
    GuardRefs,
    compute_packet_id,
)
from .policy import direction_for, trust_score

_NON_EXECUTION_NOTICE = (
    "PAPER TRADING PLAN — not a live order, broker instruction, or execution command (ADR-006)."
)

_CONSTRAINTS: tuple[str, ...] = (
    "snapshot-local: derived only from one FeatureVector + RegimeClassification",
    "cited_features are MOD-004 features read verbatim (never invented)",
    "deterministic: same inputs + versions => identical packet",
    "paper_only: a planning artifact, never a live order",
)


def _rationale(
    rc: RegimeClassification,
    direction: Direction,
    confidence: float,
    uncertainty: float,
    cited: tuple[FeatureCitation, ...],
) -> str:
    """Deterministic, templated explanation (no free text, no clock, no randomness)."""
    drivers = ", ".join(f"{c.name}={c.value:g}" for c in cited) or "no deciding feature"
    return (
        f"Regime {rc.regime.value} (rule {rc.matched_rule_id}, margin {rc.rule_margin:.2f}) "
        f"=> gold {direction.value} [paper]. Drivers: {drivers}. "
        f"confidence {confidence:.2f}, uncertainty {uncertainty:.2f} "
        f"(secondary={len(rc.secondary_matching_rules)}, near={len(rc.near_matching_rules)})."
    )


def build_decision(
    fv: FeatureVector,
    rc: RegimeClassification,
    guards: GuardRefs | None = None,
    config: DecisionPolicyConfig | None = None,
    as_of: str | None = None,
) -> GoldDecisionPacket:
    """Build a deterministic, paper-only Gold DecisionPacket (SCHEMA-011) for one snapshot."""
    cfg = config if config is not None else DEFAULT_DECISION_POLICY_CONFIG

    # Fail-closed: the FeatureVector and RegimeClassification must describe the same snapshot.
    if rc.snapshot_id != fv.snapshot_id:
        raise ValueError("FeatureVector and RegimeClassification snapshot_id mismatch")
    if rc.feature_schema_version != fv.schema_version:
        raise ValueError("FeatureVector and RegimeClassification feature_schema_version mismatch")

    confidence, uncertainty, confidence_inputs = trust_score(rc, fv, cfg)
    direction = direction_for(rc, cfg)
    cited = tuple(
        FeatureCitation(p.name, p.value, p.inputs, p.max_staleness_days, p.revision_risk)
        for p in rc.provenance
    )
    rationale = _rationale(rc, direction, confidence, uncertainty, cited)
    guard_refs = guards if guards is not None else GuardRefs()

    packet_id = compute_packet_id(
        source_snapshot_id=rc.snapshot_id,
        source_feature_schema_version=rc.feature_schema_version,
        regime_taxonomy_version=rc.taxonomy_version,
        regime_classifier_version=rc.classifier_version,
        decision_policy_version=cfg.decision_policy_version,
        decision_policy_fingerprint=cfg.decision_policy_fingerprint(),
    )

    return GoldDecisionPacket(
        packet_id=packet_id,
        packet_schema_version=PACKET_SCHEMA_VERSION,
        instrument=cfg.instrument,
        decision_mode=DecisionMode.PAPER_ONLY,
        regime=rc.regime.value,
        direction=direction,
        confidence=confidence,
        uncertainty=uncertainty,
        rationale=rationale,
        source_snapshot_id=rc.snapshot_id,
        source_feature_schema_version=rc.feature_schema_version,
        regime_taxonomy_version=rc.taxonomy_version,
        regime_classifier_version=rc.classifier_version,
        regime_classification_trace_version=rc.classification_trace_version,
        matched_rule_id=rc.matched_rule_id,
        cited_features=cited,
        decision_policy_version=cfg.decision_policy_version,
        confidence_inputs=confidence_inputs,
        guard_refs=guard_refs,
        non_execution_notice=_NON_EXECUTION_NOTICE,
        constraints=_CONSTRAINTS,
        as_of=as_of,
    )
