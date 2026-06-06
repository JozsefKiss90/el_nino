"""Unit tests for the hard-limit guardrail predicates (covers predicates.py)."""
from __future__ import annotations

from typing import Any

from risk.guardrail_engine.models import (
    GuardrailConfig,
    TradeDirection,
    TradeValidationRequest,
)
from risk.guardrail_engine.predicates import (
    daily_loss_cap_ok,
    max_positions_ok,
    max_trades_ok,
    position_size_ok,
    withdrawal_disabled,
)


def make_config(**overrides: Any) -> GuardrailConfig:
    base: dict[str, Any] = dict(
        max_trade_size=99.0,
        max_trades_per_day=10,
        max_position_pct=0.05,
        max_positions=3,
        daily_loss_cap=50.0,
        allow_withdrawals=False,
    )
    base.update(overrides)
    return GuardrailConfig(**base)


def make_request(**overrides: Any) -> TradeValidationRequest:
    base: dict[str, Any] = dict(
        symbol="AAPL",
        direction=TradeDirection.BUY,
        size=10.0,
        strategy_id="vwap",
        current_equity=1000.0,
        daily_pnl=0.0,
        trades_today=0,
        open_positions=0,
    )
    base.update(overrides)
    return TradeValidationRequest(**base)


def test_position_size_ok_passes_at_pct_limit() -> None:
    # limit = min(1000 * 0.05, 99) = 50
    assert position_size_ok(make_request(size=50.0), make_config())[0] is True


def test_position_size_ok_blocks_above_pct_limit() -> None:
    passed, reason = position_size_ok(make_request(size=50.01), make_config())
    assert passed is False
    assert "exceeds limit" in reason


def test_position_size_ok_uses_absolute_cap_when_smaller() -> None:
    # huge equity -> pct limit large, so the absolute cap (99) binds
    passed, _ = position_size_ok(
        make_request(size=100.0, current_equity=1_000_000.0), make_config()
    )
    assert passed is False


def test_daily_loss_cap_ok_blocks_at_cap() -> None:
    assert daily_loss_cap_ok(make_request(daily_pnl=-50.0), make_config())[0] is False
    assert daily_loss_cap_ok(make_request(daily_pnl=-49.99), make_config())[0] is True


def test_max_trades_ok_blocks_at_limit() -> None:
    assert max_trades_ok(make_request(trades_today=10), make_config())[0] is False
    assert max_trades_ok(make_request(trades_today=9), make_config())[0] is True


def test_max_positions_ok_blocks_at_limit() -> None:
    assert max_positions_ok(make_request(open_positions=3), make_config())[0] is False
    assert max_positions_ok(make_request(open_positions=2), make_config())[0] is True


def test_withdrawal_disabled_blocks_when_enabled() -> None:
    assert withdrawal_disabled(make_request(), make_config(allow_withdrawals=True))[0] is False
    assert withdrawal_disabled(make_request(), make_config())[0] is True
