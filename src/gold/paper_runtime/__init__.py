"""Paper-Trading Runtime (MOD-007) — stateful L3 admission over the pure Gold DecisionPacket.

Wrap-not-enrich (ADR-009 §2): consumes SCHEMA-011 + explicit runtime state (a self-describing,
append-only ledger + a versioned operational input) and emits a ``RuntimeDecisionRecord``
(SCHEMA-012) + a new ``RuntimeLedger`` (SCHEMA-013). The pure ``evaluate()`` core never mutates the
packet; all IO is confined to ``runtime.py``. Computes the two stateful L3 guards — ``duplicate_ok``
(PRED-006) and ``operational_ok`` (PRED-007) — and echoes the snapshot-derived guards.
"""

from .config import (
    DEFAULT_RUNTIME_POLICY_CONFIG,
    RUNTIME_POLICY_VERSION,
    RuntimePolicyConfig,
    RuntimePolicyConfigError,
    load_config,
)
from .engine import evaluate
from .models import (
    LEDGER_SCHEMA_VERSION,
    RECORD_SCHEMA_VERSION,
    GuardOutcome,
    LedgerEntry,
    OperationalInput,
    RuntimeContractError,
    RuntimeDecisionRecord,
    RuntimeLedger,
    Verdict,
    compute_record_id,
)
from .predicates import cooldown_ok, data_ok, duplicate_ok, freshness_ok, operational_ok
from .runtime import (
    load_ledger,
    load_operational,
    persist_ledger,
    run_once,
    run_sequence,
)

__all__ = [
    "evaluate",
    "run_once",
    "run_sequence",
    "RuntimeDecisionRecord",
    "RuntimeLedger",
    "LedgerEntry",
    "OperationalInput",
    "Verdict",
    "GuardOutcome",
    "RuntimePolicyConfig",
    "RuntimePolicyConfigError",
    "RuntimeContractError",
    "DEFAULT_RUNTIME_POLICY_CONFIG",
    "RUNTIME_POLICY_VERSION",
    "RECORD_SCHEMA_VERSION",
    "LEDGER_SCHEMA_VERSION",
    "load_config",
    "load_ledger",
    "persist_ledger",
    "load_operational",
    "compute_record_id",
    "duplicate_ok",
    "operational_ok",
    "data_ok",
    "freshness_ok",
    "cooldown_ok",
]
