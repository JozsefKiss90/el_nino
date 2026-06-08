"""Pure decision-policy helpers — the ADR-008 confidence model + regime->direction lookup.

No IO, clock, randomness, history, or global state. ``trust_score`` and ``direction_for``
are pure functions of (RegimeClassification, FeatureVector, DecisionPolicyConfig).
"""

from __future__ import annotations

from features.feature_builder.models import FeatureVector
from regime.regime_classifier import Regime, RegimeClassification

from .config import DecisionPolicyConfig
from .models import ConfidenceInputs, Direction


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def trust_score(
    rc: RegimeClassification,
    fv: FeatureVector,
    config: DecisionPolicyConfig,
) -> tuple[float, float, ConfidenceInputs]:
    """ADR-008 ordinal trust score + structural-penalty-aggregate uncertainty.

    - ``confidence`` = anchor x (the four structural discount factors), clamped to [0, 1].
      The anchor is the within-rule normalized ``rule_margin`` for signal regimes, or the
      NEUTRAL confident-quiet floor for NEUTRAL.
    - ``uncertainty`` = ``1 - (product of the discount factors)`` — the structural penalty
      aggregate, **independent of the anchor** (NOT ``1 - confidence``).
    - INDETERMINATE is fail-closed: minimum confidence, maximum uncertainty.

    Returns ``(confidence, uncertainty, confidence_inputs)``. Pure and deterministic.
    """
    secondary_count = len(rc.secondary_matching_rules)
    near_count = len(rc.near_matching_rules)
    max_staleness = max((p.max_staleness_days for p in rc.provenance), default=0)
    revision_risk = any(p.revision_risk for p in rc.provenance)
    unavailable_count = len(fv.unavailable_features)

    if rc.regime is Regime.INDETERMINATE:
        inputs = ConfidenceInputs(
            anchor=0.0,
            secondary_count=secondary_count,
            near_count=near_count,
            max_staleness_days=max_staleness,
            revision_risk=revision_risk,
            unavailable_count=unavailable_count,
        )
        return (config.indeterminate_confidence, config.indeterminate_uncertainty, inputs)

    # Structural discount factors, each in [0, 1] (1.0 = no penalty).
    ambiguity = 1.0 - min(1.0, config.ambiguity_weight * secondary_count)
    fragility = 1.0 - min(1.0, config.fragility_weight * near_count)
    staleness = 1.0 - min(config.staleness_cap, config.staleness_weight * max_staleness)
    revision = 1.0 - (config.revision_penalty if revision_risk else 0.0)
    data_quality = revision * staleness
    coverage = 1.0 - min(config.coverage_cap, config.coverage_weight * unavailable_count)

    structural = ambiguity * fragility * data_quality * coverage

    anchor = (
        config.neutral_confidence_floor
        if rc.regime is Regime.NEUTRAL
        else rc.rule_margin
    )
    confidence = _clamp01(anchor * structural)
    uncertainty = _clamp01(1.0 - structural)

    inputs = ConfidenceInputs(
        anchor=anchor,
        secondary_count=secondary_count,
        near_count=near_count,
        max_staleness_days=max_staleness,
        revision_risk=revision_risk,
        unavailable_count=unavailable_count,
    )
    return (confidence, uncertainty, inputs)


def direction_for(rc: RegimeClassification, config: DecisionPolicyConfig) -> Direction:
    """The gold direction for the classified regime (versioned policy table lookup)."""
    return config.direction_for(rc.regime.value)
