"""Feature Builder (MOD-004) — Layer-2 Snapshot -> deterministic feature vector.

Governed by ADR-005 (Feature Layer Contract): pure, stateless, snapshot-local
features only; replay-safe (same snapshot_id + schema_version => identical
output); consumes only validated Snapshot objects from the Snapshot Consumer
(MOD-003), never raw JSON.
"""

from .feature_builder import FEATURE_REGISTRY, FeatureSpec, build_features
from .models import FEATURE_SCHEMA_VERSION, Feature, FeatureVector

__all__ = [
    "build_features",
    "FEATURE_REGISTRY",
    "FeatureSpec",
    "Feature",
    "FeatureVector",
    "FEATURE_SCHEMA_VERSION",
]
