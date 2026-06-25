"""Chain Orchestrator (MOD-010) — the end-to-end Layer-3 composition root.

Threads a banked Layer-2 snapshot through every already-governed Layer-3 stage in one deterministic
call:

    consume → build_features → classify → build_decision → evaluate → [GATE-001 guard] → execute → persist

It **changes no layer's logic, no contract, and no ``*_version``** — it only *threads* the existing
pure cores and confines IO to its shell. It forwards ``packet.direction`` and the in-hand
GLD-share execution reference (``resolve_sim_exec_ref(fv.value("gold_price"), …)`` — ADR-014 bucket i,
not gold spot) into ``execute`` (the ADR-011 D1 in-hand path), and runs
the GATE-001 guard **in the orchestrator** before ``execute`` (ADR-009 §3 / ADR-011 gate c — the
orchestrator is the only cross-context importer, incl. ``src/risk``; the per-layer pure cores stay
clean). ``paper_only`` (ADR-009 / ADR-011).

- ``run_chain`` — the pure full-chain core (no IO / clock / randomness).
- ``run_once`` — the thin IO shell (load snapshot + ledger + portfolio → core → persist atomically).
- ``run_sequence`` — the pure in-memory replay / BENCH-006 vehicle (threads ledger + portfolio).
"""

from .config import DEFAULT_GUARD_CONFIG, DEFAULT_OPERATIONAL_INPUT
from .engine import run_chain
from .models import ChainContractError, ChainResult
from .operational_feed import (
    MarketCalendarFeed,
    OperationalFeed,
    OperatorHaltFeed,
    operator_halt_active,
    persist_operational,
    read_and_capture,
)
from .runtime import (
    find_latest_snapshot,
    run_once,
    run_sequence,
)

__all__ = [
    "run_chain",
    "run_once",
    "run_sequence",
    "find_latest_snapshot",
    "ChainResult",
    "ChainContractError",
    "DEFAULT_OPERATIONAL_INPUT",
    "DEFAULT_GUARD_CONFIG",
    "OperationalFeed",
    "MarketCalendarFeed",
    "OperatorHaltFeed",
    "operator_halt_active",
    "read_and_capture",
    "persist_operational",
]
