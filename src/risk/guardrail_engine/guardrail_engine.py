"""Guardrail Engine (MOD-001) — Risk Control's trade-validation boundary.

Implements the Risk Check API (INT-003): given a ``TradeValidationRequest``,
evaluate the hard-limit predicates as a short-circuit conjunction and return a
``TradeValidationDecision``. Stateless, synchronous, and deterministic — identical
inputs always yield identical decisions.
"""
from __future__ import annotations

import os
from collections.abc import Callable, Mapping, Sequence

from risk.guardrail_engine.models import (
    GuardrailConfig,
    TradeValidationDecision,
    TradeValidationRequest,
)
from risk.guardrail_engine.predicates import ALL_PREDICATES, PredicateResult

Predicate = Callable[[TradeValidationRequest, GuardrailConfig], PredicateResult]

_REQUIRED_ENV = (
    "MAX_TRADE_SIZE",
    "MAX_TRADES_PER_DAY",
    "MAX_POSITION_PCT",
    "MAX_POSITIONS",
    "DAILY_LOSS_CAP",
)


class GuardrailConfigError(RuntimeError):
    """Raised when hard-limit configuration is missing or invalid (fail closed)."""


def load_config_from_env(env: Mapping[str, str] | None = None) -> GuardrailConfig:
    """Build a GuardrailConfig from environment variables, failing closed.

    A missing required hard-limit variable raises ``GuardrailConfigError`` so the
    engine cannot be constructed and the system will not trade. The only default is
    ``ALLOW_WITHDRAWALS=false`` (the safe state).
    """
    source = os.environ if env is None else env
    missing = [name for name in _REQUIRED_ENV if name not in source]
    if missing:
        raise GuardrailConfigError(
            f"missing hard-limit config: {', '.join(sorted(missing))}"
        )
    try:
        return GuardrailConfig(
            max_trade_size=float(source["MAX_TRADE_SIZE"]),
            max_trades_per_day=int(source["MAX_TRADES_PER_DAY"]),
            max_position_pct=float(source["MAX_POSITION_PCT"]),
            max_positions=int(source["MAX_POSITIONS"]),
            daily_loss_cap=float(source["DAILY_LOSS_CAP"]),
            allow_withdrawals=source.get("ALLOW_WITHDRAWALS", "false").lower() == "true",
        )
    except ValueError as exc:
        raise GuardrailConfigError(f"invalid hard-limit config value: {exc}") from exc


class GuardrailEngine:
    """Evaluate trade-validation predicates and return an approve/block decision."""

    def __init__(
        self,
        config: GuardrailConfig,
        predicates: Sequence[Predicate] = ALL_PREDICATES,
    ) -> None:
        self._config = config
        self._predicates: tuple[Predicate, ...] = tuple(predicates)

    def validate(self, request: TradeValidationRequest) -> TradeValidationDecision:
        """Return APPROVE only if the request is well-formed and every predicate passes."""
        if request.size <= 0:
            return TradeValidationDecision(
                approved=False,
                triggered_predicate="request_valid",
                reason="invalid request: size must be > 0",
            )
        for predicate in self._predicates:
            passed, reason = predicate(request, self._config)
            if not passed:
                return TradeValidationDecision(
                    approved=False,
                    triggered_predicate=predicate.__name__,
                    reason=reason,
                )
        return TradeValidationDecision(
            approved=True,
            triggered_predicate=None,
            reason="all guardrails passed",
        )
