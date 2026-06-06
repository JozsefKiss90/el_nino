"""Decision Engine (MOD-002) — deterministic upgrade selection under treasury constraints.

Implements the Decision API (INT-006). Public surface:
- DecisionEngine: score upgrade options and emit a decision packet
- EvaluationScorecard (SCHEMA-005), DecisionPacket / RankedOption (SCHEMA-004)
- UpgradeOption, TreasuryState, DecisionConfig (value objects)
"""

from supervisor.decision_engine.decision_engine import DecisionEngine
from supervisor.decision_engine.models import (
    DecisionConfig,
    DecisionPacket,
    EvaluationScorecard,
    RankedOption,
    TreasuryState,
    UpgradeOption,
)

__all__ = [
    "DecisionEngine",
    "DecisionConfig",
    "DecisionPacket",
    "EvaluationScorecard",
    "RankedOption",
    "TreasuryState",
    "UpgradeOption",
]
