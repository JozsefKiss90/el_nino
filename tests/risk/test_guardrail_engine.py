"""Behavioral tests for the Guardrail Engine (covers guardrail_engine.py / MOD-001)."""
from __future__ import annotations

from typing import Any

import pytest

from risk.guardrail_engine.guardrail_engine import (
    GuardrailConfigError,
    GuardrailEngine,
    load_config_from_env,
)
from risk.guardrail_engine.models import (
    GuardrailConfig,
    TradeDirection,
    TradeValidationDecision,
    TradeValidationRequest,
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


def test_approves_when_all_predicates_pass() -> None:
    decision = GuardrailEngine(make_config()).validate(make_request())
    assert decision.approved is True
    assert decision.triggered_predicate is None


def test_blocks_oversized_position_and_names_predicate() -> None:
    decision = GuardrailEngine(make_config()).validate(make_request(size=500.0))
    assert decision.approved is False
    assert decision.triggered_predicate == "position_size_ok"


def test_blocks_malformed_request() -> None:
    decision = GuardrailEngine(make_config()).validate(make_request(size=0.0))
    assert decision.approved is False
    assert decision.triggered_predicate == "request_valid"


def test_short_circuits_on_first_failing_predicate() -> None:
    # position size AND trade count both fail; position_size_ok is evaluated first
    decision = GuardrailEngine(make_config()).validate(
        make_request(size=500.0, trades_today=99)
    )
    assert decision.triggered_predicate == "position_size_ok"


def test_validation_is_deterministic() -> None:
    engine = GuardrailEngine(make_config())
    request = make_request(size=500.0)
    assert engine.validate(request) == engine.validate(request)


def test_load_config_from_env_reads_values() -> None:
    env = {
        "MAX_TRADE_SIZE": "99",
        "MAX_TRADES_PER_DAY": "10",
        "MAX_POSITION_PCT": "0.05",
        "MAX_POSITIONS": "3",
        "DAILY_LOSS_CAP": "50",
    }
    config = load_config_from_env(env)
    assert config.max_trade_size == 99.0
    assert config.allow_withdrawals is False


def test_load_config_fails_closed_on_missing_var() -> None:
    with pytest.raises(GuardrailConfigError):
        load_config_from_env({"MAX_TRADE_SIZE": "99"})


def test_decision_invariant_rejects_blocked_without_predicate() -> None:
    with pytest.raises(ValueError):
        TradeValidationDecision(approved=False, triggered_predicate=None, reason="x")
