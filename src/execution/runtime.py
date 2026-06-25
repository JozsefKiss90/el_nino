"""IO boundary shell + guard-wiring orchestrator for the execution layer (MOD-008).

The ONLY IO in the execution layer lives here (load/persist the portfolio — mirrors the runtime
``runtime.py``). This is also the **composition root** that wires the Risk Control guard
(GATE-001 / ``GuardrailEngine``) into the trade pipeline (ADR-011 gate c): it builds a
``TradeValidationRequest`` from the ADMIT decision + portfolio context, runs
``GuardrailEngine.validate()`` **before** ``execute()``, and forwards the outcome as a
``GuardResult``. Bounded-context hygiene (ADR-009 §3): **only this orchestrator imports
``src/risk``**; the pure ``execute()`` core never does.

``run_sequence`` is the deterministic replay / BENCH-004 vehicle (no IO). For replay the
``GuardrailConfig`` is an explicit **captured** value (ADR-011 gate c.4) — never read from the
environment on the replay path, so a replayed APPROVE/BLOCK is independent of ambient env.
"""

from __future__ import annotations

import json
import os
from collections.abc import Sequence
from datetime import datetime
from pathlib import Path
from typing import Union

from gold.decision_builder.models import Direction
from gold.paper_runtime.models import RuntimeDecisionRecord
from risk.guardrail_engine.guardrail_engine import GuardrailEngine
from risk.guardrail_engine.models import (
    GuardrailConfig,
    TradeDirection,
    TradeValidationRequest,
)

from .adapters import ExecutionPort, SimulatedBrokerAdapter
from .config import (
    DEFAULT_EXECUTION_POLICY_CONFIG,
    DEFAULT_FILL_MODEL,
    ExecutionPolicyConfig,
    FillModelConfig,
)
from .engine import execute
from .models import ExecutionContractError, ExecutionRecord, GuardResult, PortfolioState

PathLike = Union[str, Path]
_DEFAULT_PORT: ExecutionPort = SimulatedBrokerAdapter()
_STRATEGY_ID = "execution-v0"

# An ordered (admit, direction, instrument_price) item — the orchestrator forwards `direction` and
# the D1 re-derived `instrument_price` from the lineage it holds; the ADMIT record carries neither.
ExecutionItem = tuple[RuntimeDecisionRecord, Direction, float]


def load_portfolio(path: PathLike) -> PortfolioState:
    """Load a portfolio JSON, or an empty portfolio if the file is absent (mirrors ``consume()``).

    A *missing* file is a legitimate "no prior state"; a present but *malformed* portfolio raises
    ``ExecutionContractError`` — a corrupt state file must be loud, not silently treated as empty.
    """
    p = Path(path)
    if not p.exists():
        return PortfolioState.empty()
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ExecutionContractError(f"cannot read portfolio {p}: {exc}") from exc
    return PortfolioState.from_dict(data)


def persist_portfolio(path: PathLike, portfolio: PortfolioState) -> None:
    """Atomically write the portfolio as canonical JSON (temp file + ``os.replace``)."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(portfolio.to_dict(), sort_keys=True, indent=2) + "\n"
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_text(payload, encoding="utf-8")
    os.replace(tmp, p)


def _as_of_date(value: str | None) -> str | None:
    """The calendar date (``YYYY-MM-DD``) of an ISO-8601 ``as_of``, or ``None`` if absent/unparseable.

    Deterministic — parses the snapshot clock, never the wall-clock — mirroring the runtime cooldown
    discipline's ``_parse_as_of``. Day-scoping keys off this date so a daily cap resets per trading day.
    """
    if not value:
        return None
    try:
        return datetime.fromisoformat(value).date().isoformat()
    except ValueError:
        return None


def build_guard_request(
    direction: Direction,
    portfolio: PortfolioState,
    config: ExecutionPolicyConfig = DEFAULT_EXECUTION_POLICY_CONFIG,
    *,
    as_of: str | None = None,
) -> TradeValidationRequest:
    """Build the SCHEMA-007 guard request from the (fixed) trade params + deterministic portfolio context.

    Day-scoping (ADR-014 §5.2 — mirrors the runtime cooldown discipline that keys off the snapshot
    ``as_of``, never wall-clock): ``trades_today`` counts only executions whose entry ``as_of`` falls on
    the SAME trading day as the request ``as_of``, so ``max_trades_per_day`` is a genuine daily cap, not
    a lifetime cap that blocks forever. ``daily_pnl`` is realized P&L; on the accumulate-only sim/replay
    path it is 0.0 (no sells), so its day-scoped value equals its lifetime value — genuine per-day
    realized-P&L scoping arrives with the live SELL-fold (ADR-014 bucket ii). ``open_positions`` = count
    of non-zero positions; size is the fixed ``default_size`` (ADR-011 D2). NO live broker read enters
    this shared deterministic request (it would contaminate the replay key).
    """
    open_positions = sum(1 for pos in portfolio.positions if pos.quantity != 0.0)
    daily_pnl = sum((pos.realized_pnl for pos in portfolio.positions), 0.0)
    today = _as_of_date(as_of)
    trades_today = sum(1 for e in portfolio.executions if _as_of_date(e.as_of) == today)
    return TradeValidationRequest(
        symbol=config.instrument,
        direction=TradeDirection.BUY,
        size=config.default_size,
        strategy_id=_STRATEGY_ID,
        current_equity=config.paper_equity,
        daily_pnl=daily_pnl,
        trades_today=trades_today,
        open_positions=open_positions,
    )


def run_guard(
    direction: Direction,
    portfolio: PortfolioState,
    guard_config: GuardrailConfig,
    config: ExecutionPolicyConfig = DEFAULT_EXECUTION_POLICY_CONFIG,
    *,
    as_of: str | None = None,
) -> GuardResult:
    """Run GATE-001 (``GuardrailEngine``) and map its decision to a forwarded ``GuardResult``.

    The only place ``src/risk`` is touched. ``guard_config`` is an explicit captured value
    (deterministic replay, gate c.4) — not read from the environment here. ``as_of`` (the snapshot
    clock) day-scopes the request's daily inputs (ADR-014 §5.2).
    """
    request = build_guard_request(direction, portfolio, config, as_of=as_of)
    decision = GuardrailEngine(guard_config).validate(request)
    return GuardResult(
        approved=decision.approved,
        blocked_by=decision.triggered_predicate,
        reason=decision.reason,
    )


def run_once(
    admit: RuntimeDecisionRecord,
    direction: Direction,
    instrument_price: float,
    portfolio_path: PathLike,
    guard_config: GuardrailConfig,
    port: ExecutionPort = _DEFAULT_PORT,
    fill_model: FillModelConfig = DEFAULT_FILL_MODEL,
    config: ExecutionPolicyConfig = DEFAULT_EXECUTION_POLICY_CONFIG,
) -> ExecutionRecord:
    """Single-step operational entrypoint: load state → guard → ``execute`` → persist atomically."""
    # ADR-014 §5.3 fence: the canonical execution entrypoint refuses a non-replayable port (the live
    # plug is reachable only via the orchestration live entrypoint, never this replay shell).
    assert port.replayable, (
        "execution.run_once is a replayable entrypoint; a non-replayable port is barred (ADR-014 §5.3)"
    )
    prior = load_portfolio(portfolio_path)
    guard_result = run_guard(direction, prior, guard_config, config, as_of=admit.as_of)
    record, new_portfolio = execute(
        admit, direction, instrument_price, prior, guard_result, port, fill_model, config
    )
    persist_portfolio(portfolio_path, new_portfolio)
    return record


def run_sequence(
    items: Sequence[ExecutionItem],
    guard_config: GuardrailConfig,
    port: ExecutionPort = _DEFAULT_PORT,
    fill_model: FillModelConfig = DEFAULT_FILL_MODEL,
    config: ExecutionPolicyConfig = DEFAULT_EXECUTION_POLICY_CONFIG,
    portfolio: PortfolioState | None = None,
) -> tuple[tuple[ExecutionRecord, ...], PortfolioState]:
    """Thread the portfolio over an ordered ``(admit, direction, instrument_price)`` list — no IO.

    Deterministic order = input order. The vehicle for determinism tests + BENCH-004: replaying the
    same sequence from the same starting portfolio (and the same captured ``guard_config``) yields
    identical records and an identical ending portfolio ``state_hash``.
    """
    # ADR-014 §5.3 fence: the BENCH-004 / determinism replay vehicle refuses a non-replayable port.
    assert port.replayable, (
        "execution.run_sequence is the deterministic replay vehicle; a non-replayable port is barred "
        "(ADR-014 §5.3)"
    )
    pf = portfolio if portfolio is not None else PortfolioState.empty()
    records: list[ExecutionRecord] = []
    for admit, direction, instrument_price in items:
        guard_result = run_guard(direction, pf, guard_config, config, as_of=admit.as_of)
        record, pf = execute(
            admit, direction, instrument_price, pf, guard_result, port, fill_model, config
        )
        records.append(record)
    return tuple(records), pf
