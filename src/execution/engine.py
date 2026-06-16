"""Pure execution engine (MOD-008) — ``execute`` over an ADMIT record + portfolio state.

``execute(admit, direction, instrument_price, prior_portfolio, guard_result, port, fill_model,
config) -> (ExecutionRecord, new PortfolioState)``. No IO, clock, randomness, or ``src/risk`` import
(ADR-009 §3, ADR-011 §2): state is an explicit argument and return value; the GATE-001 outcome
arrives as a forwarded ``GuardResult`` (gate c), never recomputed here. ``direction`` and
``instrument_price`` are forwarded from the lineage the orchestrator holds (the ADMIT record omits
direction; the price is re-derived from ``source_snapshot_id``, ADR-011 D1).

Total + fail-closed, mirroring the runtime ``evaluate``: a non-ADMIT input is a caller error; a
blocked guard, a non-LONG stance, or an already-executed snapshot yields a **no-fill** record
(portfolio unchanged); only an approved LONG on a fresh snapshot fills. Idempotent on
``source_snapshot_id`` (the once-ever discipline). ``paper_only`` always (ADR-011 §3).
"""

from __future__ import annotations

from gold.decision_builder.models import Direction
from gold.paper_runtime.models import RuntimeDecisionRecord, Verdict

from .adapters import ExecutionPort, SimulatedBrokerAdapter
from .config import (
    DEFAULT_EXECUTION_POLICY_CONFIG,
    DEFAULT_FILL_MODEL,
    ExecutionPolicyConfig,
    FillModelConfig,
)
from .models import (
    EXECUTION_SCHEMA_VERSION,
    ExecutionContractError,
    ExecutionEntry,
    ExecutionRecord,
    Fill,
    GuardResult,
    PortfolioState,
    Position,
    compute_execution_id,
)

_DEFAULT_PORT: ExecutionPort = SimulatedBrokerAdapter()


def _apply_buy(
    prior: Position | None,
    instrument: str,
    size: float,
    fill_price: float,
    mark_price: float,
) -> Position:
    """Fold a LONG buy into the position; ``unrealized_pnl`` is marked at ``mark_price`` (D1)."""
    q0 = prior.quantity if prior is not None else 0.0
    c0 = prior.avg_cost if prior is not None else 0.0
    r0 = prior.realized_pnl if prior is not None else 0.0
    quantity = q0 + size
    avg_cost = (q0 * c0 + size * fill_price) / quantity  # quantity > 0 (size > 0, q0 >= 0)
    unrealized = quantity * (mark_price - avg_cost)
    return Position(
        instrument=instrument,
        quantity=quantity,
        avg_cost=avg_cost,
        realized_pnl=r0,
        unrealized_pnl=unrealized,
    )


def execute(
    admit: RuntimeDecisionRecord,
    direction: Direction,
    instrument_price: float,
    prior_portfolio: PortfolioState,
    guard_result: GuardResult,
    port: ExecutionPort = _DEFAULT_PORT,
    fill_model: FillModelConfig = DEFAULT_FILL_MODEL,
    config: ExecutionPolicyConfig = DEFAULT_EXECUTION_POLICY_CONFIG,
) -> tuple[ExecutionRecord, PortfolioState]:
    """Execute an ADMITted paper decision against explicit portfolio state. Pure; no IO."""
    if admit.verdict is not Verdict.ADMIT:
        raise ExecutionContractError(
            f"execute() requires an ADMIT record, got {admit.verdict.value}"
        )

    prior_hash = prior_portfolio.state_hash()
    instrument = config.instrument
    size = config.default_size

    # Decide whether a fill occurs (fail-closed). Order: guard block -> idempotency -> stance.
    fill: Fill | None
    new_portfolio: PortfolioState
    if not guard_result.approved:
        fill, new_portfolio, reason = None, prior_portfolio, f"blocked by {guard_result.blocked_by}"
    elif prior_portfolio.has_execution(admit.source_snapshot_id):
        fill, new_portfolio, reason = None, prior_portfolio, "already executed (idempotent — once-ever)"
    elif direction is not Direction.LONG:
        fill, new_portfolio, reason = (
            None,
            prior_portfolio,
            f"non-LONG stance {direction.value} — no paper fill in v0",
        )
    else:
        f = port.fill(instrument, direction, size, instrument_price, fill_model)
        position = _apply_buy(prior_portfolio.position(instrument), instrument, size, f.fill_price, instrument_price)
        entry = ExecutionEntry(
            source_snapshot_id=admit.source_snapshot_id,
            source_record_id=admit.record_id,
            instrument=instrument,
            fill_price=f.fill_price,
            quantity=f.quantity,
            fill_model_version=fill_model.fill_model_version,
            prior_portfolio_state_hash=prior_hash,
            seq=prior_portfolio.next_seq(),
        )
        fill, new_portfolio, reason = f, prior_portfolio.append(position, entry), "filled"

    record = ExecutionRecord(
        execution_id=compute_execution_id(
            source_record_id=admit.record_id,
            fill_model_version=fill_model.fill_model_version,
            execution_policy_fingerprint=config.fingerprint(),
            instrument_price=instrument_price,
            prior_portfolio_state_hash=prior_hash,
        ),
        execution_schema_version=EXECUTION_SCHEMA_VERSION,
        source_record_id=admit.record_id,
        source_snapshot_id=admit.source_snapshot_id,
        instrument=instrument,
        direction=direction,
        size=size,
        instrument_price=instrument_price,
        fill=fill,
        guard_result=guard_result,
        execution_mode=port.mode,
        replayable=port.replayable,
        fill_model_version=fill_model.fill_model_version,
        prior_portfolio_state_hash=prior_hash,
        new_portfolio_state_hash=new_portfolio.state_hash(),
        reason=reason,
    )
    return record, new_portfolio
