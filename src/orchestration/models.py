"""Chain Orchestrator output model (MOD-010) — the full-chain record bundle.

``ChainResult`` aggregates the five typed records one end-to-end run produces plus the two new state
artifacts. It is **not** a new contract / schema / ``*_version`` — it introduces no persisted format
(the persisted artifacts are the existing ``RuntimeLedger`` (SCHEMA-013) + ``PortfolioState``
(SCHEMA-015)); it is an in-memory bundle of already-governed records. ``to_dict()`` is a deterministic,
JSON-stable projection over all five records + the two state hashes — the byte-identical replay vehicle
for BENCH-006 and the determinism tests.

Per ADR-003: stdlib frozen dataclass, zero runtime dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from execution.models import ExecutionRecord, PortfolioState
from features.feature_builder.models import FeatureVector
from gold.decision_builder.models import GoldDecisionPacket
from gold.paper_runtime.models import RuntimeDecisionRecord, RuntimeLedger
from regime.regime_classifier.models import RegimeClassification

# Feature values are rounded at projection to neutralize float-format drift (the codebase's 6-dp
# convention), so ``to_dict()`` is byte-stable across replays.
_FV_PRECISION = 6


class ChainContractError(ValueError):
    """The end-to-end chain reached an inconsistent state (e.g. an ADMIT with no in-hand price)."""


@dataclass(frozen=True)
class ChainResult:
    """One end-to-end run's full record set + the two new state artifacts.

    ``execution_record`` is ``None`` when the runtime verdict is not ADMIT (``execute`` requires an
    ADMIT record), in which case ``portfolio`` is the prior portfolio unchanged. ``ledger`` always
    advances by exactly one self-describing entry per evaluation (ADMIT / HOLD / REJECT).
    """

    feature_vector: FeatureVector
    regime: RegimeClassification
    packet: GoldDecisionPacket
    runtime_record: RuntimeDecisionRecord
    execution_record: ExecutionRecord | None
    ledger: RuntimeLedger
    portfolio: PortfolioState

    def _feature_vector_dict(self) -> dict[str, Any]:
        """Deterministic projection of the FeatureVector (it has no ``to_dict`` of its own)."""
        fv = self.feature_vector
        return {
            "features": [
                {
                    "inputs": list(feat.inputs),
                    "max_staleness_days": feat.max_staleness_days,
                    "name": feat.name,
                    "revision_risk": feat.revision_risk,
                    "value": round(feat.value, _FV_PRECISION),
                }
                for feat in sorted(fv.features.values(), key=lambda f: f.name)
            ],
            "schema_version": fv.schema_version,
            "snapshot_id": fv.snapshot_id,
            "unavailable_features": list(fv.unavailable_features),
        }

    def to_dict(self) -> dict[str, Any]:
        """Deterministic, JSON-stable dict over all five records + the two ending state hashes.

        ``json.dumps(r.to_dict(), sort_keys=True)`` is byte-identical across replays for a fixed
        full replay key (the union of every composed layer's version axis + the captured guard /
        operational fingerprints + the prior ledger / portfolio state).
        """
        return {
            "execution_record": (
                self.execution_record.to_dict() if self.execution_record is not None else None
            ),
            "feature_vector": self._feature_vector_dict(),
            "ledger_state_hash": self.ledger.state_hash(),
            "packet": self.packet.to_dict(),
            "portfolio_state_hash": self.portfolio.state_hash(),
            "regime": self.regime.to_dict(),
            "runtime_record": self.runtime_record.to_dict(),
        }
