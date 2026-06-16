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


def build_guard_request(
    direction: Direction,
    portfolio: PortfolioState,
    config: ExecutionPolicyConfig = DEFAULT_EXECUTION_POLICY_CONFIG,
) -> TradeValidationRequest:
    """Build the SCHEMA-007 guard request from the (fixed) trade params + deterministic portfolio context.

    v0 derivations (deterministic from explicit state — no clock/day boundary): ``daily_pnl`` =
    summed realized P&L; ``trades_today`` = prior fill count (a monotonic proxy capped by
    ``max_trades_per_day``); ``open_positions`` = count of non-zero positions. Size is the fixed
    ``default_size`` (ADR-011 D2 — the guard *validates* it; it does not compute it).
    """
    open_positions = sum(1 for pos in portfolio.positions if pos.quantity != 0.0)
    daily_pnl = sum((pos.realized_pnl for pos in portfolio.positions), 0.0)
    return TradeValidationRequest(
        symbol=config.instrument,
        direction=TradeDirection.BUY,
        size=config.default_size,
        strategy_id=_STRATEGY_ID,
        current_equity=config.paper_equity,
        daily_pnl=daily_pnl,
        trades_today=portfolio.next_seq(),
        open_positions=open_positions,
    )


def run_guard(
    direction: Direction,
    portfolio: PortfolioState,
    guard_config: GuardrailConfig,
    config: ExecutionPolicyConfig = DEFAULT_EXECUTION_POLICY_CONFIG,
) -> GuardResult:
    """Run GATE-001 (``GuardrailEngine``) and map its decision to a forwarded ``GuardResult``.

    The only place ``src/risk`` is touched. ``guard_config`` is an explicit captured value
    (deterministic replay, gate c.4) — not read from the environment here.
    """
    request = build_guard_request(direction, portfolio, config)
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
    prior = load_portfolio(portfolio_path)
    guard_result = run_guard(direction, prior, guard_config, config)
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
    pf = portfolio if portfolio is not None else PortfolioState.empty()
    records: list[ExecutionRecord] = []
    for admit, direction, instrument_price in items:
        guard_result = run_guard(direction, pf, guard_config, config)
        record, pf = execute(
            admit, direction, instrument_price, pf, guard_result, port, fill_model, config
        )
        records.append(record)
    return tuple(records), pf
