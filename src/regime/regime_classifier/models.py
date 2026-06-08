"""Regime Classification contract (SCHEMA-010) — the Regime Classifier's output models.

A deterministic, snapshot-local regime classification derived purely from a single
``FeatureVector`` (SCHEMA-009). The classifier is a *rule-selection engine*: its primary
output is ``matched_rule_id``; ``regime`` is a pure projection of the matched rule
(``RULE_TABLE[matched].regime``).

``rule_margin`` is a *rule-local activation margin* — how far the winning rule's deciding
feature sits past its own threshold, normalized by that rule's scale. It is explicitly
**not** epistemic confidence and **not** comparable across rules; ``rule_threshold`` and
``rule_scale`` are carried alongside so the margin is self-describing (a consumer can
recover the deciding value as ``x = rule_threshold + dir * rule_margin * rule_scale``).

Per ADR-003: stdlib frozen dataclasses, zero runtime dependencies.
Per ADR-007 determinism:
- Decision replay key:        (snapshot_id, taxonomy_version, classifier_version)
                              => identical (matched_rule_id, regime, rule_margin, trigger_features)
- Full-serialization key:     + classification_trace_version => byte-identical ``to_dict()``.
The explainability/trace block is versioned independently so it can evolve without
disturbing decision replay.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

# --- Version triple (see ADR-007 / dev_graph CLAUDE.md bump discipline) ---------------
# Bumping any of these is the ONLY sanctioned way to change the corresponding behaviour.
TAXONOMY_VERSION = "1.0.0"  # the regime set + decision thresholds (the values live in RegimeConfig)
CLASSIFIER_VERSION = "0.1.0"  # the classify/selection/rule-margin logic
CLASSIFICATION_TRACE_VERSION = "0.1.0"  # the explainability/trace metadata shape + near_band

# Margin is rounded at serialization to neutralize platform float-format drift, mirroring
# the codebase's existing ``:.6f`` provenance/score convention.
_MARGIN_PRECISION = 6


class Regime(str, Enum):
    """The canonical, enumerated macro-financial-conditions regimes (ADR-007).

    All but the last two are signal regimes. ``NEUTRAL`` is the sole catch-all for a
    successfully-classified-but-quiet snapshot; ``INDETERMINATE`` is the fail-closed
    terminal emitted when a globally-required feature is absent (never guessed).
    """

    LIQUIDITY_STRESS = "LIQUIDITY_STRESS"
    RISK_OFF = "RISK_OFF"
    VOLATILE = "VOLATILE"
    RESTRICTIVE_RATES = "RESTRICTIVE_RATES"
    REFLATION = "REFLATION"
    DISINFLATION = "DISINFLATION"
    CURVE_INVERSION = "CURVE_INVERSION"
    STRONG_USD = "STRONG_USD"
    RISK_ON = "RISK_ON"
    LOW_VOL = "LOW_VOL"
    NEUTRAL = "NEUTRAL"
    INDETERMINATE = "INDETERMINATE"


# Regimes that carry no deciding feature, hence no margin/threshold/scale.
_TERMINAL_NO_MARGIN = (Regime.NEUTRAL, Regime.INDETERMINATE)

# The canonical id of the fail-closed terminal rule.
INDETERMINATE_RULE_ID = "R00_indeterminate"


@dataclass(frozen=True)
class FeatureProvenance:
    """One cited feature's provenance, read verbatim from the FeatureVector (no inference)."""

    name: str
    value: float
    inputs: tuple[str, ...]
    max_staleness_days: int
    revision_risk: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "inputs": list(self.inputs),
            "max_staleness_days": self.max_staleness_days,
            "name": self.name,
            "revision_risk": self.revision_risk,
            "value": self.value,
        }


@dataclass(frozen=True)
class RegimeClassification:
    """Deterministic regime classification for one snapshot (SCHEMA-010).

    Rule-selection-first. Field groups: decision, provenance/identity, versions, and
    explainability/trace. ``__post_init__`` enforces the cross-field invariants; the
    fields default to empty so the frozen dataclass stays ergonomic to construct.
    """

    # --- decision (keyed by taxonomy_version + classifier_version) --------------------
    matched_rule_id: str
    regime: Regime
    rule_priority: int
    rule_margin: float
    rule_threshold: float | None
    rule_scale: float | None
    trigger_features: tuple[str, ...]
    # --- provenance / identity -------------------------------------------------------
    snapshot_id: str
    feature_schema_version: str
    provenance: tuple[FeatureProvenance, ...]
    # --- versions --------------------------------------------------------------------
    taxonomy_version: str
    classifier_version: str
    classification_trace_version: str
    # --- explainability / trace (keyed by classification_trace_version) --------------
    evaluated_rule_ids: tuple[str, ...] = ()
    skipped_rule_ids: tuple[str, ...] = ()
    failed_required_features: tuple[str, ...] = ()
    secondary_matching_rules: tuple[str, ...] = ()
    near_matching_rules: tuple[str, ...] = ()
    # --- deterministic, caller-supplied (never wall-clock) ---------------------------
    as_of: str | None = None
    indeterminate_reason: str | None = None

    def __post_init__(self) -> None:
        if not 0.0 <= self.rule_margin <= 1.0:
            raise ValueError("rule_margin must be in [0, 1]")
        if self.regime is Regime.INDETERMINATE:
            if self.rule_margin != 0.0:
                raise ValueError("INDETERMINATE rule_margin must be 0.0")
            if self.indeterminate_reason is None:
                raise ValueError("INDETERMINATE must carry an indeterminate_reason")
        if self.regime in _TERMINAL_NO_MARGIN:
            if self.rule_threshold is not None or self.rule_scale is not None:
                raise ValueError("NEUTRAL/INDETERMINATE must have rule_threshold/rule_scale = None")
            if self.trigger_features:
                raise ValueError("NEUTRAL/INDETERMINATE must have no trigger_features")
        else:
            if self.rule_threshold is None or self.rule_scale is None:
                raise ValueError("a deciding-rule classification must set rule_threshold and rule_scale")
        if self.matched_rule_id in self.secondary_matching_rules:
            raise ValueError("matched_rule_id must not appear in secondary_matching_rules")

    def to_dict(self) -> dict[str, Any]:
        """Deterministic, JSON-stable dict (alphabetical keys, margin rounded).

        ``json.dumps(c.to_dict(), sort_keys=True)`` is byte-identical across replays for a
        fixed (snapshot, taxonomy_version, classifier_version, classification_trace_version).
        """
        return {
            "as_of": self.as_of,
            "feature_schema_version": self.feature_schema_version,
            "indeterminate_reason": self.indeterminate_reason,
            "provenance": [p.to_dict() for p in self.provenance],
            "regime": self.regime.value,
            "rule": {
                "id": self.matched_rule_id,
                "margin": round(self.rule_margin, _MARGIN_PRECISION),
                "priority": self.rule_priority,
                "regime": self.regime.value,
                "scale": self.rule_scale,
                "threshold": self.rule_threshold,
            },
            "snapshot_id": self.snapshot_id,
            "trace": {
                "classification_trace_version": self.classification_trace_version,
                "evaluated_rule_ids": list(self.evaluated_rule_ids),
                "failed_required_features": list(self.failed_required_features),
                "near_matching_rules": list(self.near_matching_rules),
                "secondary_matching_rules": list(self.secondary_matching_rules),
                "skipped_rule_ids": list(self.skipped_rule_ids),
            },
            "trigger_features": list(self.trigger_features),
            "versions": {
                "classifier_version": self.classifier_version,
                "taxonomy_version": self.taxonomy_version,
            },
        }
