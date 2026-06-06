"""Data models for the Decision Engine (MOD-002).

Realizes:
- EvaluationScorecard           -> SCHEMA-005 (input contract)
- DecisionPacket / RankedOption -> SCHEMA-004 (output contract)

Plus internal Supervisor Office value objects (UpgradeOption, TreasuryState, DecisionConfig).
Dependency-free stdlib dataclasses (ADR-003).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationScorecard:
    """Realizes SCHEMA-005 — performance evidence consumed by the Decision API."""

    realized_pnl: float
    calibration: float
    drawdown: float
    disagreement: float


@dataclass(frozen=True)
class UpgradeOption:
    """A candidate upgrade in the catalog (internal Supervisor Office value object)."""

    upgrade_id: str
    cost: float
    target_dimension: str
    expected_improvement: float


@dataclass(frozen=True)
class TreasuryState:
    """Runtime treasury snapshot (internal). ``available = budget - deployed``."""

    budget: float
    deployed: float

    @property
    def available(self) -> float:
        return self.budget - self.deployed

    def after_spend(self, amount: float) -> "TreasuryState":
        return TreasuryState(budget=self.budget, deployed=self.deployed + amount)


@dataclass(frozen=True)
class RankedOption:
    """One scored option within a decision packet (part of SCHEMA-004).

    Invariant: a blocked option must carry a reason; an allowed option must not.
    """

    upgrade_id: str
    score: float
    allowed: bool
    blocked_reason: str | None

    def __post_init__(self) -> None:
        if not self.allowed and self.blocked_reason is None:
            raise ValueError("a blocked option must carry a blocked_reason")
        if self.allowed and self.blocked_reason is not None:
            raise ValueError("an allowed option must not carry a blocked_reason")


@dataclass(frozen=True)
class DecisionPacket:
    """Realizes SCHEMA-004 — the deterministic decision output.

    Invariant: a non-null selected_upgrade_id must reference an allowed ranked option.
    """

    selected_upgrade_id: str | None
    ranked_options: tuple[RankedOption, ...]
    rationale: str
    treasury_state_after: TreasuryState

    def __post_init__(self) -> None:
        if self.selected_upgrade_id is not None:
            match = [r for r in self.ranked_options if r.upgrade_id == self.selected_upgrade_id]
            if not match or not match[0].allowed:
                raise ValueError("selected_upgrade_id must reference an allowed ranked option")


@dataclass(frozen=True)
class DecisionConfig:
    """Early-exit thresholds (from the Supervisor Decision Engine spec)."""

    promotable_pnl_threshold: float = 0.0
    promotable_calibration_threshold: float = 0.65
