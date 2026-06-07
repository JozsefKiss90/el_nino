"""Feature Vector contract (SCHEMA-009) — the Feature Builder's output models.

Frozen, snapshot-local feature vector derived purely from a single Layer-2
Snapshot (SCHEMA-001). Each feature carries its provenance (input series ids,
max staleness, revision risk). Per ADR-003: stdlib frozen dataclasses, zero
runtime dependencies. Per ADR-005: determinism is keyed on
(snapshot_id, schema_version).
"""

from __future__ import annotations

from dataclasses import dataclass

# Bumping this version is the ONLY sanctioned way to change feature semantics;
# it is part of the determinism key (same snapshot_id + same version => same vector).
FEATURE_SCHEMA_VERSION = "0.1.0"


@dataclass(frozen=True)
class Feature:
    """A single derived feature with full provenance back to SCHEMA-001 series."""

    name: str
    value: float
    inputs: tuple[str, ...]
    max_staleness_days: int
    revision_risk: bool


@dataclass(frozen=True)
class FeatureVector:
    """The deterministic output of the Feature Builder for one snapshot.

    Logically immutable. ``features`` is name-sorted at construction so iteration
    order is stable. ``unavailable_features`` lists features skipped because an
    input series was absent from the snapshot (no partial/invented values).
    """

    snapshot_id: str
    schema_version: str
    features: dict[str, Feature]
    unavailable_features: tuple[str, ...]

    @property
    def names(self) -> tuple[str, ...]:
        """Feature names present in this vector, in deterministic (sorted) order."""
        return tuple(self.features.keys())

    def value(self, name: str) -> float:
        """Convenience accessor for a feature's value (KeyError if unavailable)."""
        return self.features[name].value
