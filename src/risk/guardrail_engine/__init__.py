"""Guardrail Engine (MOD-001) — trade-validation predicate enforcement.

Implements the Risk Check API (INT-003). Public surface:
- GuardrailEngine: evaluate a trade-validation request, return an approve/block decision
- load_config_from_env: fail-closed hard-limit configuration loader
- TradeValidationRequest / TradeValidationDecision: the INT-003 contract (SCHEMA-007 / SCHEMA-008)
"""

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

__all__ = [
    "GuardrailEngine",
    "GuardrailConfigError",
    "load_config_from_env",
    "GuardrailConfig",
    "TradeDirection",
    "TradeValidationRequest",
    "TradeValidationDecision",
]
