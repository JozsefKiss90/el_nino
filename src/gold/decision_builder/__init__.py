"""Gold Decision Builder (MOD-006) — deterministic, paper-only Gold DecisionPacket v0.

(FeatureVector SCHEMA-009 + RegimeClassification SCHEMA-010) -> GoldDecisionPacket SCHEMA-011.
Governed by ADR-006 (input boundary / replay) + ADR-008 (confidence semantics). Pure,
snapshot-local, fail-closed; zero runtime dependencies (ADR-003).
"""

from .builder import build_decision
from .config import (
    DECISION_POLICY_VERSION,
    DEFAULT_DECISION_POLICY_CONFIG,
    DEFAULT_DIRECTION_TABLE,
    DecisionPolicyConfig,
    DecisionPolicyConfigError,
    load_config,
)
from .models import (
    PACKET_SCHEMA_VERSION,
    ConfidenceInputs,
    DecisionMode,
    Direction,
    FeatureCitation,
    GoldDecisionPacket,
    GuardRefs,
    SnapshotGuards,
    compute_packet_id,
)
from .policy import direction_for, trust_score

__all__ = [
    "build_decision",
    "GoldDecisionPacket",
    "Direction",
    "DecisionMode",
    "FeatureCitation",
    "ConfidenceInputs",
    "GuardRefs",
    "SnapshotGuards",
    "compute_packet_id",
    "PACKET_SCHEMA_VERSION",
    "DecisionPolicyConfig",
    "DecisionPolicyConfigError",
    "load_config",
    "DEFAULT_DECISION_POLICY_CONFIG",
    "DEFAULT_DIRECTION_TABLE",
    "DECISION_POLICY_VERSION",
    "trust_score",
    "direction_for",
]
