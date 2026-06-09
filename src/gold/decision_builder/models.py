"""Gold DecisionPacket v0 contract (SCHEMA-011) — the Gold Decision Builder's output models.

A deterministic, snapshot-local paper-trading decision derived purely from a single
``FeatureVector`` (SCHEMA-009) + ``RegimeClassification`` (SCHEMA-010). ``decision_mode`` is
always ``paper_only`` — this is a planning artifact, never a live order, broker instruction,
or execution command (ADR-006 §1, Non-Goals).

``confidence`` is the ADR-008 ordinal trust score (anchor = within-rule ``rule_margin``, four
structural discounts, NEUTRAL/INDETERMINATE floors) — explicitly **not** a calibrated
probability. ``uncertainty`` is a structural-penalty aggregate (ADR-008 §5), **not**
``1 - confidence``. ``direction`` is a versioned regime->direction policy table
(``decision_policy_version``).

Per ADR-003: stdlib frozen dataclasses, zero runtime dependencies.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import Enum
from typing import Any

PACKET_SCHEMA_VERSION = "0.2.0"
# Confidence/uncertainty are rounded at serialization to neutralize float-format drift,
# mirroring the regime layer's 6-dp margin convention.
_FLOAT_PRECISION = 6


class Direction(str, Enum):
    """The v0 gold stance enum (regime->direction policy output)."""

    LONG = "LONG"      # the regime supports (paper) gold exposure
    FLAT = "FLAT"      # no directional edge
    AVOID = "AVOID"    # the regime is a gold headwind — stay out
    WATCH = "WATCH"    # insufficient/ambiguous basis (fail-closed default)


class DecisionMode(str, Enum):
    """v0 is paper-only — explicit non-execution."""

    PAPER_ONLY = "paper_only"


@dataclass(frozen=True)
class FeatureCitation:
    """A MOD-004 feature the decision cites, read verbatim from the FeatureVector."""

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
class ConfidenceInputs:
    """The deterministic signals feeding the trust score (auditability of the scalar)."""

    anchor: float  # within-rule rule_margin (or the NEUTRAL floor)
    secondary_count: int
    near_count: int
    max_staleness_days: int
    revision_risk: bool
    unavailable_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "anchor": round(self.anchor, _FLOAT_PRECISION),
            "max_staleness_days": self.max_staleness_days,
            "near_count": self.near_count,
            "revision_risk": self.revision_risk,
            "secondary_count": self.secondary_count,
            "unavailable_count": self.unavailable_count,
        }


# The six-guard taxonomy (ADR-004 / ADR-006 §6). The packet CITES these outcomes; it never
# computes them as features. data_ok/freshness_ok are snapshot-derived; supervisor_ok/
# cooldown_ok are L3 stubs; duplicate_ok/operational_ok are net-new L3 guards (PRED-006/007).
_GUARD_NAMES: tuple[str, ...] = (
    "cooldown_ok",
    "data_ok",
    "duplicate_ok",
    "freshness_ok",
    "operational_ok",
    "supervisor_ok",
)


@dataclass(frozen=True)
class GuardRefs:
    """The six-guard taxonomy outcomes the packet honored — each ``bool | None``.

    ``None`` = not-yet-evaluated; the stateful L3 guards (``duplicate_ok``/``operational_ok``)
    need the deferred paper-trading runtime (ADR-006 Non-Goals), so v0 carries ``None``.
    """

    data_ok: bool | None = None
    freshness_ok: bool | None = None
    supervisor_ok: bool | None = None
    cooldown_ok: bool | None = None
    duplicate_ok: bool | None = None
    operational_ok: bool | None = None

    def to_dict(self) -> dict[str, bool | None]:
        return {name: getattr(self, name) for name in _GUARD_NAMES}


@dataclass(frozen=True)
class SnapshotGuards:
    """Snapshot-derived L1 guard provenance forwarded onto the packet (ADR-009 §3).

    The data-quality / freshness / cooldown flags the Layer-2 snapshot published
    (``Snapshot.guards``), copied verbatim by the chain orchestrator at build time so a
    downstream consumer (the paper-trading runtime) reads them from the packet and never
    re-reads the raw SCHEMA-001 snapshot. **Distinct from** ``GuardRefs`` — that is the
    L3-outcome block (computed by the runtime); this is upstream L1 provenance. ``None`` on
    the packet means the orchestrator did not forward a snapshot block (a pre-runtime caller).
    """

    data_ok: bool
    freshness_ok: bool
    cooldown_ok: bool

    def to_dict(self) -> dict[str, bool]:
        return {
            "cooldown_ok": self.cooldown_ok,
            "data_ok": self.data_ok,
            "freshness_ok": self.freshness_ok,
        }


@dataclass(frozen=True)
class GoldDecisionPacket:
    """Deterministic, paper-only gold decision for one snapshot (SCHEMA-011)."""

    # --- decision ---
    packet_id: str
    packet_schema_version: str
    instrument: str
    decision_mode: DecisionMode
    regime: str  # Regime.value, echoed
    direction: Direction
    confidence: float
    uncertainty: float
    rationale: str
    # --- provenance / identity ---
    source_snapshot_id: str
    source_feature_schema_version: str
    regime_taxonomy_version: str
    regime_classifier_version: str
    regime_classification_trace_version: str
    matched_rule_id: str
    cited_features: tuple[FeatureCitation, ...]
    # --- versions ---
    decision_policy_version: str
    # --- trust trace ---
    confidence_inputs: ConfidenceInputs
    # --- guards ---
    guard_refs: GuardRefs
    # --- safety ---
    non_execution_notice: str
    constraints: tuple[str, ...]
    # --- deterministic, caller-supplied (never wall-clock) ---
    as_of: str | None = None
    # --- snapshot-derived L1 guard provenance (ADR-009 §3; forwarded by the orchestrator) ---
    snapshot_guards: SnapshotGuards | None = None

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be in [0, 1]")
        if not 0.0 <= self.uncertainty <= 1.0:
            raise ValueError("uncertainty must be in [0, 1]")
        if self.decision_mode is not DecisionMode.PAPER_ONLY:
            raise ValueError("v0 decision_mode must be paper_only")
        if self.regime == "INDETERMINATE" and self.direction is not Direction.WATCH:
            raise ValueError("INDETERMINATE must map to direction WATCH (fail-closed)")

    def to_dict(self) -> dict[str, Any]:
        """Deterministic, JSON-stable dict (alphabetical keys, rounded scalars).

        ``json.dumps(p.to_dict(), sort_keys=True)`` is byte-identical across replays for a
        fixed (snapshot, regime versions, decision_policy_version, configuration).
        """
        return {
            "as_of": self.as_of,
            "cited_features": [c.to_dict() for c in self.cited_features],
            "confidence": round(self.confidence, _FLOAT_PRECISION),
            "confidence_inputs": self.confidence_inputs.to_dict(),
            "constraints": list(self.constraints),
            "decision": {
                "direction": self.direction.value,
                "instrument": self.instrument,
                "mode": self.decision_mode.value,
                "regime": self.regime,
            },
            "decision_policy_version": self.decision_policy_version,
            "guard_refs": self.guard_refs.to_dict(),
            "matched_rule_id": self.matched_rule_id,
            "non_execution_notice": self.non_execution_notice,
            "packet_id": self.packet_id,
            "packet_schema_version": self.packet_schema_version,
            "provenance": {
                "regime_classification_trace_version": self.regime_classification_trace_version,
                "regime_classifier_version": self.regime_classifier_version,
                "regime_taxonomy_version": self.regime_taxonomy_version,
                "source_feature_schema_version": self.source_feature_schema_version,
                "source_snapshot_id": self.source_snapshot_id,
            },
            "rationale": self.rationale,
            "snapshot_guards": (
                self.snapshot_guards.to_dict() if self.snapshot_guards is not None else None
            ),
            "uncertainty": round(self.uncertainty, _FLOAT_PRECISION),
        }


def compute_packet_id(
    source_snapshot_id: str,
    source_feature_schema_version: str,
    regime_taxonomy_version: str,
    regime_classifier_version: str,
    decision_policy_version: str,
    decision_policy_fingerprint: str,
) -> str:
    """Deterministic packet identity over the FULL identity tuple.

    ``gold-v0:`` + the first 16 hex of a SHA-256 over a newline-joined ``key=value`` block,
    mirroring ``Snapshot.recompute_id``'s hashing. Including the feature/regime versions and
    the ``decision_policy_fingerprint`` (not just snapshot_id + policy_version) closes an
    id-collision hazard across version/config bumps.
    """
    lines = [
        f"source_snapshot_id={source_snapshot_id}",
        f"source_feature_schema_version={source_feature_schema_version}",
        f"regime_taxonomy_version={regime_taxonomy_version}",
        f"regime_classifier_version={regime_classifier_version}",
        f"decision_policy_version={decision_policy_version}",
        f"decision_policy_fingerprint={decision_policy_fingerprint}",
    ]
    payload = "\n".join(lines) + "\n"
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return f"gold-v0:{digest[:16]}"
