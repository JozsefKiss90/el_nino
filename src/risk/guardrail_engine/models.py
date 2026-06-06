"""Data models for the Guardrail Engine.

Realizes the Risk Check API data contract:
- TradeValidationRequest  -> SCHEMA-007 (input)
- TradeValidationDecision -> SCHEMA-008 (output)

Dependency-free stdlib dataclasses (ADR-003).
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TradeDirection(str, Enum):
    """Side of a proposed trade."""

    BUY = "buy"
    SELL = "sell"


@dataclass(frozen=True)
class TradeValidationRequest:
    """Input contract for the Risk Check API (realizes SCHEMA-007).

    Carries the proposed-trade parameters plus the portfolio context required to
    evaluate the hard-limit guardrail predicates.
    """

    symbol: str
    direction: TradeDirection
    size: float
    strategy_id: str
    current_equity: float
    daily_pnl: float
    trades_today: int
    open_positions: int


@dataclass(frozen=True)
class TradeValidationDecision:
    """Output contract for the Risk Check API (realizes SCHEMA-008).

    Invariant (SCHEMA-008): a BLOCK must name the triggering predicate; an APPROVE
    must not name one. Enforced at construction (fail closed).
    """

    approved: bool
    triggered_predicate: str | None
    reason: str

    def __post_init__(self) -> None:
        if not self.approved and self.triggered_predicate is None:
            raise ValueError("a blocked decision must name the triggered predicate")
        if self.approved and self.triggered_predicate is not None:
            raise ValueError("an approved decision must not name a triggered predicate")


@dataclass(frozen=True)
class GuardrailConfig:
    """Hard-limit configuration. These limits are non-negotiable at runtime.

    `daily_loss_cap` is a positive magnitude; a trade is blocked once realized
    daily P&L has fallen to -daily_loss_cap or below. `allow_withdrawals` is
    false in the only safe state.
    """

    max_trade_size: float
    max_trades_per_day: int
    max_position_pct: float
    max_positions: int
    daily_loss_cap: float
    allow_withdrawals: bool = False
