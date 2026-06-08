"""Market Regime Classifier (MOD-005) — deterministic FeatureVector -> RegimeClassification.

``classify(fv)`` is a total, pure function: it reads only the feature vector and a fixed
(versioned) ``RegimeConfig``, and returns a ``RegimeClassification``. No IO, clock,
randomness, history, global state, or ML (ADR-007). Same ``snapshot_id`` +
``taxonomy_version`` + ``classifier_version`` always yield the same decision.

It is a rule-selection engine: a single full pass over the ordered ``RULE_TABLE`` records,
per rule, eligibility / predicate-match / near-activation; the highest-priority matching
rule wins and its regime is projected onto the result. Conflict/ambiguity is surfaced as
trace metadata (``secondary_matching_rules`` / ``near_matching_rules``), never as a label —
``NEUTRAL`` is the sole catch-all. Fail-closed: a missing globally-required feature yields
``INDETERMINATE`` (never a guessed regime).
"""

from __future__ import annotations

from features.feature_builder.models import FeatureVector

from .config import DEFAULT_REGIME_CONFIG, RegimeConfig
from .models import (
    INDETERMINATE_RULE_ID,
    FeatureProvenance,
    Regime,
    RegimeClassification,
)
from .taxonomy import RULE_TABLE, RegimeRule, margin_value, near_proximity


def _provenance(fv: FeatureVector, feature_names: tuple[str, ...]) -> tuple[FeatureProvenance, ...]:
    """Build name-sorted provenance for the cited features, read verbatim from the vector."""
    return tuple(
        FeatureProvenance(f.name, f.value, f.inputs, f.max_staleness_days, f.revision_risk)
        for f in sorted((fv.features[n] for n in feature_names), key=lambda feat: feat.name)
    )


def classify(
    fv: FeatureVector,
    config: RegimeConfig | None = None,
    as_of: str | None = None,
) -> RegimeClassification:
    """Classify a single FeatureVector into exactly one regime (deterministic, fail-closed)."""
    c = config if config is not None else DEFAULT_REGIME_CONFIG

    # (1) Global fail-closed gate: a missing required feature => INDETERMINATE.
    missing_global = tuple(name for name in c.required_features if name not in fv.features)
    if missing_global:
        ordered = tuple(sorted(missing_global))
        return RegimeClassification(
            matched_rule_id=INDETERMINATE_RULE_ID,
            regime=Regime.INDETERMINATE,
            rule_priority=0,
            rule_margin=0.0,
            rule_threshold=None,
            rule_scale=None,
            trigger_features=(),
            snapshot_id=fv.snapshot_id,
            feature_schema_version=fv.schema_version,
            provenance=(),
            taxonomy_version=c.taxonomy_version,
            classifier_version=c.classifier_version,
            classification_trace_version=c.classification_trace_version,
            failed_required_features=ordered,
            as_of=as_of,
            indeterminate_reason="missing required features: " + ", ".join(ordered),
        )

    # (2) Single full pass: record eligibility, matches, and near-activations.
    evaluated: list[str] = []
    skipped: list[str] = []
    failed_feats: set[str] = set()
    matched: list[RegimeRule] = []
    near: list[tuple[float, int, str]] = []  # (proximity, priority, rule_id)

    for rule in RULE_TABLE:
        rule_missing = [name for name in rule.required_features if name not in fv.features]
        if rule_missing:
            skipped.append(rule.rule_id)
            failed_feats.update(rule_missing)
            continue
        evaluated.append(rule.rule_id)
        if rule.predicate(fv, c):
            matched.append(rule)
        elif rule.margin is not None and rule.regime is not Regime.NEUTRAL:
            prox = near_proximity(fv, c, rule.margin)
            if prox is not None:
                near.append((prox, rule.priority, rule.rule_id))

    # (3) Highest-priority match wins (table is priority-ordered; NEUTRAL guarantees one).
    if not matched:  # unreachable: R11 NEUTRAL is unconditional and never skipped.
        raise AssertionError("taxonomy gap: no rule matched despite the NEUTRAL catch-all")
    winner = matched[0]

    if winner.margin is not None:
        threshold: float | None = winner.margin.threshold(c)
        scale: float | None = winner.margin.scale(c)
        rule_margin = margin_value(fv, c, winner.margin)
        trigger = tuple(sorted(winner.trigger_features))
    else:  # NEUTRAL catch-all: no deciding feature, hence no margin.
        threshold = None
        scale = None
        rule_margin = 0.0
        trigger = ()

    # Secondary matches: other matched signal rules (exclude the NEUTRAL catch-all),
    # ordered by activation margin desc, tiebreak priority asc (NOT by priority).
    secondaries = [r for r in matched[1:] if r.margin is not None and r.regime is not Regime.NEUTRAL]
    secondaries.sort(key=lambda r: (-_secondary_margin(fv, c, r), r.priority))
    secondary_ids = tuple(r.rule_id for r in secondaries)

    # Near matches: ordered by proximity desc, tiebreak priority asc.
    near.sort(key=lambda item: (-item[0], item[1]))
    near_ids = tuple(rule_id for _, _, rule_id in near)

    return RegimeClassification(
        matched_rule_id=winner.rule_id,
        regime=winner.regime,
        rule_priority=winner.priority,
        rule_margin=rule_margin,
        rule_threshold=threshold,
        rule_scale=scale,
        trigger_features=trigger,
        snapshot_id=fv.snapshot_id,
        feature_schema_version=fv.schema_version,
        provenance=_provenance(fv, trigger),
        taxonomy_version=c.taxonomy_version,
        classifier_version=c.classifier_version,
        classification_trace_version=c.classification_trace_version,
        evaluated_rule_ids=tuple(evaluated),
        skipped_rule_ids=tuple(skipped),
        failed_required_features=tuple(sorted(failed_feats)),
        secondary_matching_rules=secondary_ids,
        near_matching_rules=near_ids,
        as_of=as_of,
    )


def _secondary_margin(fv: FeatureVector, c: RegimeConfig, rule: RegimeRule) -> float:
    """Activation margin of a (matched) secondary rule; rule.margin is guaranteed present."""
    assert rule.margin is not None  # guarded by the caller's filter
    return margin_value(fv, c, rule.margin)
