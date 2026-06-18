"""Captured orchestration inputs (MOD-010) — the operational + guard seams, explicit and replay-safe.

The chain orchestrator forwards two cross-cutting inputs into the chain that are **explicit captured
values**, never read live on the replay path:

- ``DEFAULT_OPERATIONAL_INPUT`` — the v0 *configured default* operational-readiness artifact (ADR-009
  §3 / PRED-007). It is a **configured assumption** ("for paper-trading v0, assume the venue is open"),
  passed as a parameter and fingerprinted into the ledger — **distinct from**
  ``paper_runtime.load_operational``'s default-**closed** fallback for an *absent/malformed file*
  (unknown status → fail closed). This is the seam a future live-feed adapter plugs into (the live feed
  is an ADR-009 Non-Goal, deferred). Safety is preserved independently: paper-only / virtual-money, the
  GATE-001 hard limits still enforced, ``withdrawal_disabled`` (PRED-005) always on.

- ``DEFAULT_GUARD_CONFIG`` — the v0 *captured* GATE-001 hard-limit config (ADR-011 gate c.4). It is an
  explicit value (never ``os.environ`` on the replay path), so a replayed APPROVE/BLOCK is independent
  of ambient env. The operational CLI may instead load real env limits (``--guard-from-env``); the
  replay/benchmark path always uses a captured config.

These are **captured instances of existing types** — no new contract, schema, or ``*_version``.
"""

from __future__ import annotations

from gold.paper_runtime.models import OperationalInput
from risk.guardrail_engine.models import GuardrailConfig

# v0 configured-default operational input: GLD, venue open / tradeable. as_of is left None — it is a
# snapshot-agnostic configured assumption, not tied to any one snapshot's clock. Fingerprinted into the
# ledger for audit; replaced (not bypassed) when a live operational feed lands.
DEFAULT_OPERATIONAL_INPUT = OperationalInput(
    instrument="GLD",
    tradeable=True,
    venue_open=True,
    halt=False,
    degraded=False,
    as_of=None,
)

# v0 captured GATE-001 guard config (mirrors the BENCH-004 ``_GUARD_OK`` paper limits): generous enough
# that the guard APPROVES a v0 paper trade, so a non-fill on the real corpus is attributable to the
# AVOID stance, not the guard. Explicit + captured (never read from env on the replay path).
DEFAULT_GUARD_CONFIG = GuardrailConfig(
    max_trade_size=10_000.0,
    max_trades_per_day=10,
    max_position_pct=0.05,
    max_positions=5,
    daily_loss_cap=5_000.0,
    allow_withdrawals=False,
)
