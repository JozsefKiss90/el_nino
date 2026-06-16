"""Execution layer (MOD-008) — acts on an ADMIT decision to produce a (paper) fill + portfolio state.

The first money-shaped layer (ADR-011): a deterministic, replay-safe simulated-broker core behind the
``ExecutionPort`` (INT-011), consuming an ADMIT ``RuntimeDecisionRecord`` (SCHEMA-012) + explicit
portfolio state and producing an ``ExecutionRecord`` (SCHEMA-014) + a new ``PortfolioState``
(SCHEMA-015). ``execute()`` is pure (no IO / clock / randomness / ``src/risk`` import); the IO shell +
the GATE-001 guard-wiring orchestrator live in ``runtime.py``. ``paper_only`` / virtual-money; the
Alpaca-paper adapter (non-replayable, gate f) is deferred.
"""

from .adapters import ExecutionPort, SimulatedBrokerAdapter
from .config import (
    DEFAULT_EXECUTION_POLICY_CONFIG,
    DEFAULT_FILL_MODEL,
    EXECUTION_POLICY_VERSION,
    FILL_MODEL_VERSION,
    ExecutionPolicyConfig,
    ExecutionPolicyConfigError,
    FillModelConfig,
    load_config,
)
from .engine import execute
from .models import (
    EXECUTION_SCHEMA_VERSION,
    PORTFOLIO_SCHEMA_VERSION,
    ExecutionContractError,
    ExecutionEntry,
    ExecutionMode,
    ExecutionRecord,
    Fill,
    GuardResult,
    PortfolioState,
    Position,
    compute_execution_id,
)
from .runtime import (
    ExecutionItem,
    build_guard_request,
    load_portfolio,
    persist_portfolio,
    run_guard,
    run_once,
    run_sequence,
)

__all__ = [
    "execute",
    "run_once",
    "run_sequence",
    "run_guard",
    "build_guard_request",
    "load_portfolio",
    "persist_portfolio",
    "ExecutionPort",
    "SimulatedBrokerAdapter",
    "ExecutionRecord",
    "PortfolioState",
    "Position",
    "ExecutionEntry",
    "Fill",
    "GuardResult",
    "ExecutionMode",
    "ExecutionContractError",
    "ExecutionItem",
    "ExecutionPolicyConfig",
    "FillModelConfig",
    "ExecutionPolicyConfigError",
    "DEFAULT_EXECUTION_POLICY_CONFIG",
    "DEFAULT_FILL_MODEL",
    "EXECUTION_POLICY_VERSION",
    "FILL_MODEL_VERSION",
    "EXECUTION_SCHEMA_VERSION",
    "PORTFOLIO_SCHEMA_VERSION",
    "compute_execution_id",
    "load_config",
]
