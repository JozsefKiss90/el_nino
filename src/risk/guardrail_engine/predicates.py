"""Hard-limit guardrail predicates (realizes the Guardrail Pattern, PAT-002).

Each predicate is a pure function ``(request, config) -> (passed, reason)``. The
Guardrail Engine evaluates them as a short-circuit conjunction — ALL must pass to
approve a trade. Pure functions keep every predicate independently unit-testable.
"""
from __future__ import annotations

from risk.guardrail_engine.models import GuardrailConfig, TradeValidationRequest

PredicateResult = tuple[bool, str]


def position_size_ok(
    request: TradeValidationRequest, config: GuardrailConfig
) -> PredicateResult:
    """Position must not exceed the lesser of the %-of-equity and absolute caps."""
    limit = min(request.current_equity * config.max_position_pct, config.max_trade_size)
    if request.size <= limit:
        return True, "position size within limit"
    return False, f"position size {request.size} exceeds limit {limit}"


def daily_loss_cap_ok(
    request: TradeValidationRequest, config: GuardrailConfig
) -> PredicateResult:
    """No new trades once the daily loss cap has been reached."""
    if request.daily_pnl > -config.daily_loss_cap:
        return True, "daily loss within cap"
    return False, (
        f"daily loss cap reached: pnl {request.daily_pnl} <= -{config.daily_loss_cap}"
    )


def max_trades_ok(
    request: TradeValidationRequest, config: GuardrailConfig
) -> PredicateResult:
    """Trade count for the day must be below the configured maximum."""
    if request.trades_today < config.max_trades_per_day:
        return True, "trade count within daily limit"
    return False, (
        f"max trades per day reached: {request.trades_today} >= {config.max_trades_per_day}"
    )


def max_positions_ok(
    request: TradeValidationRequest, config: GuardrailConfig
) -> PredicateResult:
    """Open position count must be below the configured maximum."""
    if request.open_positions < config.max_positions:
        return True, "open positions within limit"
    return False, (
        f"max concurrent positions reached: {request.open_positions} >= {config.max_positions}"
    )


def withdrawal_disabled(
    request: TradeValidationRequest, config: GuardrailConfig
) -> PredicateResult:
    """Withdrawals must be disabled — a system invariant, fail closed if enabled."""
    if not config.allow_withdrawals:
        return True, "withdrawals disabled"
    return False, "withdrawals must be disabled"


ALL_PREDICATES = (
    position_size_ok,
    daily_loss_cap_ok,
    max_trades_ok,
    max_positions_ok,
    withdrawal_disabled,
)
