"""Market Regime Classifier (MOD-005) — FeatureVector -> deterministic RegimeClassification.

Governed by ADR-007 (Deterministic Regime Taxonomy): a pure, snapshot-local, fail-closed
rule-selection engine over the SCHEMA-009 Feature Vector. Replay-safe (same snapshot_id +
taxonomy_version + classifier_version => identical decision); thresholds are config-driven
and versioned; explainability metadata is carried separately under classification_trace_version.
"""

from .config import (
    DEFAULT_REGIME_CONFIG,
    RegimeConfig,
    RegimeConfigError,
    load_config,
)
from .models import (
    CLASSIFICATION_TRACE_VERSION,
    CLASSIFIER_VERSION,
    INDETERMINATE_RULE_ID,
    TAXONOMY_VERSION,
    FeatureProvenance,
    Regime,
    RegimeClassification,
)
from .regime_classifier import classify
from .taxonomy import RULE_TABLE, MarginSpec, RegimeRule, margin_value, near_proximity

__all__ = [
    "classify",
    "Regime",
    "RegimeClassification",
    "FeatureProvenance",
    "RegimeConfig",
    "RegimeConfigError",
    "load_config",
    "DEFAULT_REGIME_CONFIG",
    "RegimeRule",
    "MarginSpec",
    "RULE_TABLE",
    "margin_value",
    "near_proximity",
    "TAXONOMY_VERSION",
    "CLASSIFIER_VERSION",
    "CLASSIFICATION_TRACE_VERSION",
    "INDETERMINATE_RULE_ID",
]
