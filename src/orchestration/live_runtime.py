"""Non-replayable LIVE execution entrypoint (ADR-014 bucket ii) — ``operate_live`` reconcile-then-act.

The **only** door to a non-replayable broker port. It mirrors the chain ``run_once`` IO shell but
threads a **separate** ``(ledger, portfolio)`` pair physically distinct from the canonical replay
files, so live broker state never contaminates the deterministic ledger/portfolio the benchmarks +
replay depend on. It is deliberately quarantined off ``run_once`` / ``run_sequence`` — which now
``assert port.replayable`` (ADR-014 §5.3) and so structurally refuse a live port.

**Reuse, not reimplementation (ADR-014 §6.1).** ``operate_live`` re-threads the *same deterministic
pure cores* the chain uses for the decision + idempotency + GATE-001 guard
(``build_features → classify → build_decision → evaluate → run_guard``) — ``run_chain`` and the
``SimulatedBrokerAdapter`` stay **structurally unchanged**. Only the act is different: instead of the
LONG-only ``execute()`` / ``fill()`` simulator path, the live path does **reconcile-then-act** with the
side/order-based :class:`~execution.live_adapter.LiveExecutionAdapter` (ADR-014 §6):

* **Mandatory startup reconcile before any new action** — read the account (status gate), positions, and
  open orders; never blind-buy.
* **Authority split** — the broker is the authority for *position truth*; the local SCHEMA-015 portfolio
  is the authority for *decision lineage + idempotency*.
* **Reconcile delta drives a side-based order** — LONG → cash-capped notional buy, FLAT → sell-to-close,
  AVOID/WATCH → NO_ACTION (resolved *before* the adapter, no broker call).
* **Open-orders-aware netting** — a queued ours-lineage order that already covers the target nets to
  NO_ACTION (the cross-snapshot queue window); an **unexpected** open order (foreign ``client_order_id``
  or wrong side) or an unexplained FLAT-time position is a **discrepancy** → **terminal-refuse execution
  only** (no auto-flatten) + an append-only **reconcile-heal** entry. The decision/observation/labeling
  chain keeps advancing so the calibration corpus never stalls.
* **Live SELL-fold realizes P&L** (``realized_pnl += qty × (exit_fill − avg_cost); position → 0``) — on
  the live path *only*; the simulator portfolio stays accumulate-only (``realized_pnl == 0.0``).
* **Idempotency bifurcation** — ``has_execution(snapshot_id)`` on the live portfolio + the decision
  chain's ``duplicate_ok`` + reconcile-delta + open-orders awareness + the adapter's ``client_order_id``
  422 dedup. The sim path's once-ever guard is unchanged.

**Live execution reference (ADR-014 §5.1).** The live path marks/slips against the **real live GLD share
mark**, read from the broker's market-data host inside the startup reconcile
(:meth:`~execution.live_adapter.LiveExecutionAdapter.live_submit_mark`, basis
:data:`~execution.price_reference.BASIS_LIVE_SUBMIT`, pinned timestamp). A FILLED order records the
broker's real ``filled_avg_price`` in the :class:`~execution.models.Fill` with slippage GLD-vs-GLD
**against that real mark** — never against the sim derived proxy (``gold_price_proxy × OZ_PER_SHARE``),
which stays sim/replay-only. Reading the real mark fail-closed (a missing / non-positive mark refuses
execution) is the Q2/§5.1 correctness gate that removes the "plausible-but-wrong slippage" defect.

**Fill resolution scope.** Fills resolve from the broker positions/orders read (never the POST echo).
The within-cycle path resolves immediately (submit → resolve from the order read). A genuinely-async
order (broker still ``accepted``/``new`` at resolve) yields a **QUEUED** record and is recorded as a
live-only :class:`~execution.models.PendingOrder` on the portfolio (the durable order↔snapshot lineage).
The **next startup reconcile folds the now-filled cross-run order exactly once** (:func:`_fold_pending_fills`)
— booking the buy/sell-fold + an :class:`~execution.models.ExecutionEntry` and dropping the pending order —
so a LONG run sees the position locally (already-long NO_ACTION) and a FLAT run can sell it instead of
mis-flagging it as an unexplained position. ``client_order_id`` 422 dedup + open-orders netting keep the
async case double-order-safe across the queue window (ADR-014 §6.3).

**default-OFF:** nothing wires to this by default — it is imported explicitly by the ADR-013 gated-live
console action, never from the ``orchestration`` package ``__init__`` (mirrors the alpaca clock-feed
opt-in; keeps the default graph free of any live plug).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence, Union

from execution import (
    EXECUTION_SCHEMA_VERSION,
    ExecutionEntry,
    ExecutionMode,
    ExecutionRecord,
    ExecutionStatus,
    Fill,
    GuardResult,
    PendingOrder,
    PortfolioState,
    Position,
    ReconcileEntry,
    compute_execution_id,
    run_guard,
)
from execution.config import (
    DEFAULT_EXECUTION_POLICY_CONFIG,
    DEFAULT_FILL_MODEL,
    ExecutionPolicyConfig,
    FillModelConfig,
)
from execution.live_adapter import (
    _COID_PREFIX,
    LiveExecutionAdapter,
    LiveOrderOutcome,
    make_client_order_id,
)
from execution.price_reference import BASIS_LIVE_SUBMIT, ExecPriceRef
from execution.runtime import load_portfolio, persist_portfolio
from features.feature_builder import build_features
from gold.decision_builder import SnapshotGuards, build_decision
from gold.decision_builder.config import DecisionPolicyConfig
from gold.decision_builder.models import Direction
from gold.paper_runtime import evaluate
from gold.paper_runtime.config import DEFAULT_RUNTIME_POLICY_CONFIG, RuntimePolicyConfig
from gold.paper_runtime.models import OperationalInput, RuntimeDecisionRecord, Verdict
from gold.paper_runtime.runtime import load_ledger, persist_ledger
from regime.regime_classifier import classify
from regime.regime_classifier.config import RegimeConfig
from risk.guardrail_engine.models import GuardrailConfig
from snapshot.snapshot_consumer import consume

from .config import DEFAULT_GUARD_CONFIG, DEFAULT_OPERATIONAL_INPUT
from .models import ChainContractError, ChainResult
from .operational_feed import OperationalFeed, read_and_capture

PathLike = Union[str, Path]

_PRICE_FEATURE = "gold_price"
_EPS = 1e-9

# Reconcile plan actions (the side-based drive surface).
_BUY = "buy"
_SELL = "sell"
_NO_ACTION = "no_action"
_DISCREPANCY = "discrepancy"


# --- live sizing config (live-plug-only; never on the deterministic replay key) ------------------


@dataclass(frozen=True)
class LiveExecutionConfig:
    """Live-plug-only sizing config (ADR-014 §6.4).

    The sim/replay path keeps fixed-*qty* ``ExecutionPolicyConfig.default_size`` (a notional there would
    change ``state_hash`` and break BENCH). The live path sizes a fixed *notional*, cash-capped against
    the literal settled-cash field. This config lives entirely off the sim path — it never folds into the
    deterministic replay key.
    """

    target_notional: float = 1000.0  # the fixed live notional per LONG (cash-capped at act time)
    instrument: str = "GLD"


DEFAULT_LIVE_CONFIG = LiveExecutionConfig()


# --- the reconcile plan (pure: broker reads + decision direction → a side-based action) ----------


@dataclass(frozen=True)
class ReconcilePlan:
    """The reconcile decision: which side-based action the delta implies (or a discrepancy)."""

    action: str  # _BUY | _SELL | _NO_ACTION | _DISCREPANCY
    reason: str
    sell_qty: float = 0.0  # for _SELL: the broker position quantity to close
    observed_qty: float = 0.0  # broker position quantity (for a reconcile-heal record)
    observed_avg_price: float = 0.0
    marker: str = ""  # discrepancy marker (recorded on the reconcile-heal entry)


def _broker_position(positions: Sequence[Mapping[str, Any]], instrument: str) -> tuple[float, float]:
    """``(qty, avg_entry_price)`` for ``instrument`` from the broker positions read (``(0,0)`` if flat)."""
    for p in positions:
        if str(p.get("symbol")) == instrument:
            return float(p.get("qty") or 0.0), float(p.get("avg_entry_price") or 0.0)
    return 0.0, 0.0


def _orders_for(orders: Sequence[Mapping[str, Any]], instrument: str) -> list[Mapping[str, Any]]:
    return [o for o in orders if str(o.get("symbol")) == instrument]


def _is_ours(order: Mapping[str, Any], coid_prefix: str) -> bool:
    """True iff the order carries one of *our* deterministic ``client_order_id``s (expected lineage)."""
    return str(order.get("client_order_id") or "").startswith(coid_prefix)


def _side(order: Mapping[str, Any]) -> str:
    return str(order.get("side") or "").lower()


def plan_reconcile(
    direction: Direction,
    instrument: str,
    positions: Sequence[Mapping[str, Any]],
    open_orders: Sequence[Mapping[str, Any]],
    local_position: Position | None,
    *,
    coid_prefix: str = _COID_PREFIX,
) -> ReconcilePlan:
    """Compute the reconcile delta → a side-based action (ADR-014 §6.2/§6.3). Pure; no IO.

    Discrepancy (→ terminal-refuse + reconcile-heal, never auto-flatten):
      * a **foreign** open order on the instrument (a ``client_order_id`` that is not ours);
      * an ours **wrong-side** open order (an open SELL under LONG, or an open BUY under FLAT);
      * a **FLAT-time standing position with no local lineage** (a position we have no record of buying —
        adopting it is a separate governed action, so we refuse the exit rather than sell blind).

    Otherwise the delta nets to a side-based action:
      * LONG → ``_NO_ACTION`` if already long *or* an ours BUY is in flight (the queue nets to zero), else
        ``_BUY`` (cash-capped notional);
      * FLAT → ``_NO_ACTION`` if an ours SELL is already in flight or there is nothing to close, else
        ``_SELL`` the broker position to close;
      * AVOID/WATCH → ``_NO_ACTION`` (resolved before the adapter by the caller; never reaches here).
    """
    broker_qty, broker_avg = _broker_position(positions, instrument)
    local_qty = local_position.quantity if local_position is not None else 0.0
    orders = _orders_for(open_orders, instrument)
    foreign = [o for o in orders if not _is_ours(o, coid_prefix)]
    ours = [o for o in orders if _is_ours(o, coid_prefix)]
    ours_buys = [o for o in ours if _side(o) == "buy"]
    ours_sells = [o for o in ours if _side(o) == "sell"]

    heal = ReconcilePlan(
        _DISCREPANCY, reason="", observed_qty=broker_qty, observed_avg_price=broker_avg,
    )

    # --- discrepancy detection (account-state truth, independent of the sizing arithmetic) ---
    if foreign:
        coids = ", ".join(str(o.get("client_order_id")) for o in foreign)
        return _replace_plan(
            heal, reason=f"unexpected open order(s) not ours ({coids}) — refuse execution, heal-record",
            marker="unexpected_open_order",
        )
    if direction is Direction.LONG and ours_sells:
        return _replace_plan(
            heal, reason="open SELL in flight under a LONG decision (wrong side) — refuse, heal-record",
            marker="wrong_side_open_order",
        )
    if direction is Direction.FLAT and ours_buys:
        return _replace_plan(
            heal, reason="open BUY in flight under a FLAT decision (wrong side) — refuse, heal-record",
            marker="wrong_side_open_order",
        )

    # --- side-based action on the netted delta ---
    if direction is Direction.LONG:
        if broker_qty > _EPS or ours_buys:
            return ReconcilePlan(
                _NO_ACTION,
                reason="already long / buy in flight — delta nets to zero (NO_ACTION)",
            )
        return ReconcilePlan(_BUY, reason="flat — submit a cash-capped notional buy")

    if direction is Direction.FLAT:
        if ours_sells:
            return ReconcilePlan(_NO_ACTION, reason="exit already in flight — delta nets to zero (NO_ACTION)")
        if broker_qty <= _EPS:
            return ReconcilePlan(_NO_ACTION, reason="already flat — nothing to close (NO_ACTION)")
        if local_qty <= _EPS:
            # The broker shows a position we have no local lineage for: an unexplained standing position.
            # Do NOT auto-flatten (it imports a real-money instinct and destroys evidence) — refuse + heal;
            # adopting it is a separate ops-console governed action (ADR-014 §6.2).
            return _replace_plan(
                heal,
                reason="FLAT but broker holds a position with no local lineage — refuse exit, heal-record "
                       "(governed adopt required)",
                marker="unexplained_position",
            )
        return ReconcilePlan(
            _SELL, reason="exit — sell the broker position to close",
            sell_qty=broker_qty, observed_qty=broker_qty, observed_avg_price=broker_avg,
        )

    # AVOID / WATCH never reach here (the caller resolves them before the adapter), but stay total.
    return ReconcilePlan(_NO_ACTION, reason=f"{direction.value} — no target (NO_ACTION)")


def _replace_plan(plan: ReconcilePlan, *, reason: str, marker: str) -> ReconcilePlan:
    return ReconcilePlan(
        plan.action, reason=reason, sell_qty=plan.sell_qty,
        observed_qty=plan.observed_qty, observed_avg_price=plan.observed_avg_price, marker=marker,
    )


# --- live position folds (live_runtime only — NEVER the pure execute() core, ADR-014 §6.5) -------


def _apply_live_buy(
    prior: Position | None, instrument: str, qty: float, fill_price: float, mark: float,
) -> Position:
    """Fold a FILLED live BUY into the position (mirrors the sim ``_apply_buy``; ``unrealized`` at mark)."""
    q0 = prior.quantity if prior is not None else 0.0
    c0 = prior.avg_cost if prior is not None else 0.0
    r0 = prior.realized_pnl if prior is not None else 0.0
    quantity = q0 + qty
    avg_cost = (q0 * c0 + qty * fill_price) / quantity if quantity > _EPS else 0.0
    unrealized = quantity * (mark - avg_cost)
    return Position(instrument, quantity, avg_cost, r0, unrealized)


def _apply_live_sell(prior: Position, instrument: str, qty: float, exit_fill: float) -> Position:
    """Live SELL-fold (ADR-014 §6.5): ``realized_pnl += qty × (exit_fill − avg_cost); position → 0``.

    Live-path-only — the simulator never sells (teaching it to would break BENCH). The cost basis is the
    local ``avg_cost`` (set by the prior live buy-fold); a full exit zeroes the position.
    """
    remaining = prior.quantity - qty
    realized = prior.realized_pnl + qty * (exit_fill - prior.avg_cost)
    flat = remaining <= _EPS
    return Position(
        instrument,
        0.0 if flat else remaining,
        0.0 if flat else prior.avg_cost,
        realized,
        0.0 if flat else remaining * (exit_fill - prior.avg_cost),
    )


# --- the reconcile-then-act core (testable with an injected stub adapter; no IO) -----------------


def reconcile_and_act(
    admit: RuntimeDecisionRecord,
    direction: Direction,
    prior_portfolio: PortfolioState,
    guard_result: GuardResult,
    adapter: LiveExecutionAdapter,
    exec_ref: ExecPriceRef | None = None,
    *,
    fill_model: FillModelConfig = DEFAULT_FILL_MODEL,
    exec_config: ExecutionPolicyConfig = DEFAULT_EXECUTION_POLICY_CONFIG,
    live_config: LiveExecutionConfig = DEFAULT_LIVE_CONFIG,
) -> tuple[ExecutionRecord, PortfolioState]:
    """Reconcile-then-act for one ADMITted decision on the LIVE path (ADR-014 §6). Pure of file IO.

    Order of fail-closed gates mirrors the sim ``execute()`` (guard → idempotency → stance), then the live
    reconcile-then-act replaces the sim fill. Returns ``(record, new_portfolio)``; on any execution
    refusal the portfolio advances only by an append-only reconcile-heal entry (or is unchanged), so the
    decision/observation/labeling chain is never blocked by a broker problem.

    ``exec_ref`` is the GLD-share execution reference. **Live path:** pass ``None`` — the **real broker
    GLD mark** is read inside the startup reconcile (ADR-014 §5.1, fail-closed; never the sim proxy). An
    explicit ``exec_ref`` (a test fixture or a pre-captured mark) is used as-is and skips the live read.
    The startup reconcile also **folds any cross-run async fills** that completed since the last run
    (ADR-014 §6.3) before planning, so the plan acts on the true post-fold local position.
    """
    instrument = exec_config.instrument
    snapshot_id = admit.source_snapshot_id

    # A pre-mark placeholder reference for any refusal that occurs *before* the live mark is read (no
    # order, no slippage — the mark is genuinely unread). An injected exec_ref is used verbatim instead.
    ref = exec_ref if exec_ref is not None else ExecPriceRef(0.0, admit.as_of, BASIS_LIVE_SUBMIT)

    # 1. Guard block (fail-closed) — no broker contact.
    if not guard_result.approved:
        return _no_fill(admit, direction, ref, prior_portfolio, guard_result,
                        ExecutionStatus.NO_ACTION, f"blocked by {guard_result.blocked_by}",
                        exec_config, fill_model)
    # 2. Once-ever idempotency on the LIVE portfolio (bifurcated, not demoted) — no broker contact.
    if prior_portfolio.has_execution(snapshot_id):
        return _no_fill(admit, direction, ref, prior_portfolio, guard_result,
                        ExecutionStatus.NO_ACTION, "already executed (idempotent — once-ever)",
                        exec_config, fill_model)
    # 3. Non-actionable stance resolved BEFORE the adapter (AVOID/WATCH never reach the broker).
    if direction not in (Direction.LONG, Direction.FLAT):
        return _no_fill(admit, direction, ref, prior_portfolio, guard_result,
                        ExecutionStatus.NO_ACTION,
                        f"non-actionable stance {direction.value} — no live order", exec_config, fill_model)

    # 4. Mandatory startup reconcile (account gate + positions ∪ open orders + the REAL live GLD mark)
    #    BEFORE any new action. The mark read (when exec_ref is None) is the §5.1 Q2 correctness gate —
    #    live slippage is recorded fill-vs-real-mark, never against the sim derived proxy.
    try:
        account = adapter.assert_account_tradeable()
        positions = list(adapter.client.get_positions()) if adapter.client is not None else []
        open_orders = list(adapter.client.get_open_orders()) if adapter.client is not None else []
        if exec_ref is None:  # live path: read the REAL broker GLD mark (ADR-014 §5.1), fail-closed
            ref = adapter.live_submit_mark(instrument, as_of=admit.as_of)
        # 4b. Cross-run fold (ADR-014 §6.3): book any async order from a prior run that has since filled,
        #     exactly once, BEFORE planning — so the plan sees the true post-fold local position. Inside the
        #     reconcile try so a fold failure refuses safely (pending preserved), never crashes the run.
        working = _fold_pending_fills(adapter, prior_portfolio, instrument, ref, fill_model)
    except Exception as exc:  # noqa: BLE001 — any broker/read failure refuses execution safely (fail-closed)
        return _no_fill(admit, direction, ref, prior_portfolio, guard_result,
                        ExecutionStatus.EXECUTION_UNCERTAIN,
                        f"startup reconcile failed ({exc}) — refuse execution, halt", exec_config, fill_model,
                        halt=True)

    plan = plan_reconcile(
        direction, instrument, positions, open_orders, working.position(instrument),
    )

    # 5a. Discrepancy → terminal-refuse execution + append-only reconcile-heal (no auto-flatten). The
    #     record's prior hash is the TRUE pre-heal state; the new hash includes the heal observation.
    if plan.action == _DISCREPANCY:
        healed = working.append_reconcile(ReconcileEntry(
            source_snapshot_id=snapshot_id,
            instrument=instrument,
            observed_qty=plan.observed_qty,
            observed_avg_price=plan.observed_avg_price,
            marker=f"discrepancy:{plan.marker}",
            seq=working.next_reconcile_seq(),
            as_of=admit.as_of,
        ))
        record = _record(admit, direction, ref, working, healed, None, guard_result,
                         ExecutionStatus.EXECUTION_UNCERTAIN, plan.reason, exec_config, fill_model, None)
        return record, healed

    # 5b. Delta nets to zero → NO_ACTION (no broker order). ``working`` carries any cross-run fold.
    if plan.action == _NO_ACTION:
        return _no_fill(admit, direction, ref, working, guard_result,
                        ExecutionStatus.NO_ACTION, plan.reason, exec_config, fill_model)

    # 5c. Act on the delta via the side-based adapter.
    if plan.action == _BUY:
        return _act_buy(admit, direction, working, guard_result, adapter, ref,
                        account, exec_config, fill_model, live_config)
    return _act_sell(admit, direction, working, guard_result, adapter, ref,
                     plan.sell_qty, exec_config, fill_model)


def _fold_pending_fills(
    adapter: LiveExecutionAdapter,
    portfolio: PortfolioState,
    instrument: str,
    exec_ref: ExecPriceRef,
    fill_model: FillModelConfig,
) -> PortfolioState:
    """Fold any cross-run async fills that completed since the last run — exactly once (ADR-014 §6.3).

    For each in-flight :class:`~execution.models.PendingOrder` on the LIVE portfolio, resolve its fill
    from the broker ORDER read (the authority, never the POST echo). A now-FILLED order is **booked** —
    a buy-fold or the realizing sell-fold, plus an :class:`~execution.models.ExecutionEntry` carrying the
    original snapshot/record lineage — and the pending order is dropped. So the *next* decision sees the
    position locally: a LONG run nets to already-long NO_ACTION, and a FLAT run sells the lineaged
    position instead of mis-flagging it as an unexplained discrepancy. **Exactly once:** a folded order
    leaves an ``ExecutionEntry`` (``has_execution`` true) and is removed from ``pending``. **Fail-closed:**
    a still-open / partial / unresolvable order (or a sell with no local position to fold) is **kept**
    pending — never silently dropped, so a real fill is never lost. Live-path-only; the sim portfolio
    never has a pending order, so this is a no-op there.
    """
    if not any(p.instrument == instrument for p in portfolio.pending):
        return portfolio
    working = portfolio
    survivors: list[PendingOrder] = []
    for pend in portfolio.pending:
        if pend.instrument != instrument:
            survivors.append(pend)  # not ours to resolve on this instrument's reconcile — keep
            continue
        if working.has_execution(pend.source_snapshot_id):
            continue  # already booked (defensive idempotency) — drop the now-stale pending order
        outcome = adapter.resolve_fill(pend.client_order_id, pend.requested_qty)
        if outcome.status is not ExecutionStatus.FILLED:
            survivors.append(pend)  # still open / partial / unresolvable — keep (fail-closed)
            continue
        prior_pos = working.position(instrument)
        if pend.side == _SELL:
            if prior_pos is None:
                survivors.append(pend)  # nothing to fold a sell into — keep, surface on the next cycle
                continue
            position = _apply_live_sell(
                prior_pos, instrument, outcome.filled_qty, outcome.filled_avg_price
            )
        else:
            position = _apply_live_buy(
                prior_pos, instrument, outcome.filled_qty, outcome.filled_avg_price, exec_ref.price
            )
        entry = ExecutionEntry(
            source_snapshot_id=pend.source_snapshot_id,
            source_record_id=pend.source_record_id,
            instrument=instrument,
            fill_price=outcome.filled_avg_price,
            quantity=outcome.filled_qty,
            fill_model_version=fill_model.fill_model_version,
            prior_portfolio_state_hash=working.state_hash(),
            seq=working.next_seq(),
            as_of=pend.as_of,
        )
        working = working.append(position, entry)  # pending re-set to survivors below (overrides this)
    return working.with_pending(tuple(survivors))


def _act_buy(
    admit: RuntimeDecisionRecord, direction: Direction, prior_portfolio: PortfolioState,
    guard_result: GuardResult, adapter: LiveExecutionAdapter, exec_ref: ExecPriceRef,
    account: Mapping[str, Any], exec_config: ExecutionPolicyConfig, fill_model: FillModelConfig,
    live_config: LiveExecutionConfig,
) -> tuple[ExecutionRecord, PortfolioState]:
    instrument = exec_config.instrument
    try:
        settled = adapter.settled_cash(account)
        asset = adapter.client.get_asset(instrument) if adapter.client is not None else {}
        fractionable = bool(asset.get("fractionable", False))
        qty, notional = adapter.resolve_order_qty(
            live_config.target_notional, settled, fractionable=fractionable, mark=exec_ref.price,
        )
    except Exception as exc:  # noqa: BLE001 — sizing / asset-read failure refuses execution safely
        return _no_fill(admit, direction, exec_ref, prior_portfolio, guard_result,
                        ExecutionStatus.EXECUTION_UNCERTAIN, f"buy sizing failed ({exc}) — refuse, halt",
                        exec_config, fill_model, halt=True)
    if qty is None and notional is None:
        return _no_fill(admit, direction, exec_ref, prior_portfolio, guard_result,
                        ExecutionStatus.NO_ACTION, "nothing affordable at the cash-cap — NO_ACTION",
                        exec_config, fill_model)

    coid = make_client_order_id(admit.source_snapshot_id, "buy")
    submit = adapter.submit_buy(instrument, coid, qty=qty, notional=notional)
    # For a fractionable NOTIONAL order the share qty is unknown at submit; resolve with requested_qty=0.0
    # so a broker 'filled' status is taken at the broker's filled_qty (a notional order is not "partial"
    # in our model — the broker either fills the notional or it does not). Integer-share orders pass qty.
    requested_qty = qty if qty is not None else 0.0
    outcome = _resolve_if_queued(adapter, coid, submit, requested_qty)

    if outcome.status is ExecutionStatus.FILLED:
        position = _apply_live_buy(
            prior_portfolio.position(instrument), instrument, outcome.filled_qty,
            outcome.filled_avg_price, exec_ref.price,
        )
        fill = _live_fill(outcome.filled_avg_price, outcome.filled_qty, exec_ref.price)
        new_portfolio = prior_portfolio.append(position, _entry(
            admit, instrument, outcome.filled_qty, outcome.filled_avg_price, fill_model, prior_portfolio,
        ))
        return _record(admit, direction, exec_ref, prior_portfolio, new_portfolio, fill, guard_result,
                       ExecutionStatus.FILLED, outcome.reason, exec_config, fill_model, outcome), new_portfolio
    # QUEUED / PARTIAL → record a PendingOrder for the cross-run fold (§6.3); UNCERTAIN / 422-dup → no fold.
    return _no_fill_or_queue(admit, direction, exec_ref, prior_portfolio, guard_result, outcome,
                             _BUY, requested_qty, exec_config, fill_model)


def _act_sell(
    admit: RuntimeDecisionRecord, direction: Direction, prior_portfolio: PortfolioState,
    guard_result: GuardResult, adapter: LiveExecutionAdapter, exec_ref: ExecPriceRef,
    sell_qty: float, exec_config: ExecutionPolicyConfig, fill_model: FillModelConfig,
) -> tuple[ExecutionRecord, PortfolioState]:
    instrument = exec_config.instrument
    coid = make_client_order_id(admit.source_snapshot_id, "sell")
    submit = adapter.submit_sell(instrument, coid, qty=sell_qty)
    outcome = _resolve_if_queued(adapter, coid, submit, sell_qty)

    if outcome.status is ExecutionStatus.FILLED:
        prior_pos = prior_portfolio.position(instrument)
        if prior_pos is None:  # defensive: the plan only emits _SELL with local lineage present
            return _no_fill(admit, direction, exec_ref, prior_portfolio, guard_result,
                            ExecutionStatus.EXECUTION_UNCERTAIN,
                            "sell filled but no local position to fold — refuse, halt", exec_config,
                            fill_model, halt=True, outcome=outcome)
        position = _apply_live_sell(prior_pos, instrument, outcome.filled_qty, outcome.filled_avg_price)
        fill = _live_fill(outcome.filled_avg_price, outcome.filled_qty, exec_ref.price)
        new_portfolio = prior_portfolio.append(position, _entry(
            admit, instrument, outcome.filled_qty, outcome.filled_avg_price, fill_model, prior_portfolio,
        ))
        return _record(admit, direction, exec_ref, prior_portfolio, new_portfolio, fill, guard_result,
                       ExecutionStatus.FILLED, f"exit filled — {outcome.reason}", exec_config, fill_model,
                       outcome), new_portfolio
    # QUEUED / PARTIAL → record a PendingOrder for the cross-run fold (§6.3); UNCERTAIN / 422-dup → no fold.
    return _no_fill_or_queue(admit, direction, exec_ref, prior_portfolio, guard_result, outcome,
                             _SELL, sell_qty, exec_config, fill_model)


def _resolve_if_queued(
    adapter: LiveExecutionAdapter, coid: str, submit: LiveOrderOutcome, requested_qty: float,
) -> LiveOrderOutcome:
    """If the submit was accepted (QUEUED), resolve the fill from the broker ORDER read (never the echo)."""
    if submit.status is ExecutionStatus.QUEUED:
        return adapter.resolve_fill(coid, requested_qty)
    return submit  # NO_ACTION (422 dup) / EXECUTION_UNCERTAIN (reject/timeout/auth/429) — order resolved


def _live_fill(fill_price: float, quantity: float, mark: float) -> Fill:
    """A live Fill: the broker fill price + slippage recorded GLD-vs-GLD against the orchestrator mark."""
    slippage_bps = (fill_price - mark) / mark * 10_000.0 if mark else 0.0
    return Fill(fill_price=fill_price, quantity=quantity, slippage_bps=slippage_bps)


def _entry(
    admit: RuntimeDecisionRecord, instrument: str, qty: float, fill_price: float,
    fill_model: FillModelConfig, prior_portfolio: PortfolioState,
) -> ExecutionEntry:
    return ExecutionEntry(
        source_snapshot_id=admit.source_snapshot_id,
        source_record_id=admit.record_id,
        instrument=instrument,
        fill_price=fill_price,
        quantity=qty,
        fill_model_version=fill_model.fill_model_version,
        prior_portfolio_state_hash=prior_portfolio.state_hash(),
        seq=prior_portfolio.next_seq(),
        as_of=admit.as_of,
    )


def _no_fill(
    admit: RuntimeDecisionRecord, direction: Direction, exec_ref: ExecPriceRef,
    portfolio: PortfolioState, guard_result: GuardResult, status: ExecutionStatus, reason: str,
    exec_config: ExecutionPolicyConfig, fill_model: FillModelConfig, *, halt: bool = False,
    outcome: LiveOrderOutcome | None = None,
) -> tuple[ExecutionRecord, PortfolioState]:
    """A no-fill live record + the (possibly heal-appended) portfolio. ``portfolio`` is the new state."""
    return _record(admit, direction, exec_ref, portfolio, portfolio, None, guard_result, status, reason,
                   exec_config, fill_model, outcome), portfolio


def _no_fill_or_queue(
    admit: RuntimeDecisionRecord, direction: Direction, exec_ref: ExecPriceRef,
    working: PortfolioState, guard_result: GuardResult, outcome: LiveOrderOutcome, side: str,
    requested_qty: float, exec_config: ExecutionPolicyConfig, fill_model: FillModelConfig,
) -> tuple[ExecutionRecord, PortfolioState]:
    """A non-fill live result; a QUEUED/PARTIAL order is recorded as a PendingOrder (ADR-014 §6.3).

    An ``accepted`` order whose fill did not resolve within this cycle (QUEUED) — or a PARTIAL whose
    remainder is still open — leaves a live broker order that may complete **after** this run. It is
    recorded as a live-only :class:`~execution.models.PendingOrder` (the durable order↔snapshot lineage),
    so the next startup reconcile folds the completed fill exactly once (:func:`_fold_pending_fills`).
    Every other non-fill status (EXECUTION_UNCERTAIN; a 422-duplicate NO_ACTION) changes no local state.
    """
    if (
        outcome.status in (ExecutionStatus.QUEUED, ExecutionStatus.PARTIAL)
        and outcome.client_order_id is not None
    ):
        queued = working.append_pending(PendingOrder(
            source_snapshot_id=admit.source_snapshot_id,
            source_record_id=admit.record_id,
            instrument=exec_config.instrument,
            side=side,
            requested_qty=requested_qty,
            client_order_id=outcome.client_order_id,
            seq=working.next_pending_seq(),
            as_of=admit.as_of,
        ))
        record = _record(admit, direction, exec_ref, working, queued, None, guard_result,
                         outcome.status, outcome.reason, exec_config, fill_model, outcome)
        return record, queued
    return _no_fill(admit, direction, exec_ref, working, guard_result, outcome.status, outcome.reason,
                    exec_config, fill_model, halt=outcome.halt, outcome=outcome)


def _record(
    admit: RuntimeDecisionRecord, direction: Direction, exec_ref: ExecPriceRef,
    prior_portfolio: PortfolioState, new_portfolio: PortfolioState, fill: Fill | None,
    guard_result: GuardResult, status: ExecutionStatus, reason: str,
    exec_config: ExecutionPolicyConfig, fill_model: FillModelConfig,
    outcome: LiveOrderOutcome | None,
) -> ExecutionRecord:
    """Build the live SCHEMA-014 ExecutionRecord (status + broker traceability; non-replayable)."""
    prior_hash = prior_portfolio.state_hash()
    return ExecutionRecord(
        execution_id=compute_execution_id(
            source_record_id=admit.record_id,
            fill_model_version=fill_model.fill_model_version,
            execution_policy_fingerprint=exec_config.fingerprint(),
            instrument_price=exec_ref.price,
            prior_portfolio_state_hash=prior_hash,
        ),
        execution_schema_version=EXECUTION_SCHEMA_VERSION,
        source_record_id=admit.record_id,
        source_snapshot_id=admit.source_snapshot_id,
        instrument=exec_config.instrument,
        direction=direction,
        size=exec_config.default_size,
        instrument_price=exec_ref.price,
        fill=fill,
        guard_result=guard_result,
        execution_mode=ExecutionMode.ALPACA_PAPER,
        replayable=False,
        fill_model_version=fill_model.fill_model_version,
        prior_portfolio_state_hash=prior_hash,
        new_portfolio_state_hash=new_portfolio.state_hash(),
        reason=reason,
        exec_ref_gld_price=exec_ref.price,
        exec_ref_gld_price_ts=exec_ref.ts,
        exec_ref_gld_price_basis=exec_ref.basis,
        status=status,
        client_order_id=outcome.client_order_id if outcome is not None else None,
        alpaca_order_id=outcome.alpaca_order_id if outcome is not None else None,
        raw_payload=outcome.raw_payload if outcome is not None else None,
    )


# --- the non-replayable live IO shell ------------------------------------------------------------


def operate_live(
    snapshot_path: PathLike,
    live_ledger_path: PathLike,
    live_portfolio_path: PathLike,
    adapter: LiveExecutionAdapter,
    *,
    operational_input: OperationalInput = DEFAULT_OPERATIONAL_INPUT,
    operational_feed: OperationalFeed | None = None,
    operational_capture_path: PathLike | None = None,
    guard_config: GuardrailConfig = DEFAULT_GUARD_CONFIG,
    runtime_config: RuntimePolicyConfig = DEFAULT_RUNTIME_POLICY_CONFIG,
    regime_config: RegimeConfig | None = None,
    decision_config: DecisionPolicyConfig | None = None,
    exec_config: ExecutionPolicyConfig = DEFAULT_EXECUTION_POLICY_CONFIG,
    fill_model: FillModelConfig = DEFAULT_FILL_MODEL,
    live_config: LiveExecutionConfig = DEFAULT_LIVE_CONFIG,
) -> ChainResult | None:
    """Run the chain once on the LIVE path: load SEPARATE live state → decide → reconcile-act → persist.

    The non-replayable counterpart to ``run_once``. ``adapter`` is the side/order-based
    :class:`~execution.live_adapter.LiveExecutionAdapter` (required — no simulator default; this is the
    live door) and is **not** subject to the ``run_once`` / ``run_sequence`` ``replayable`` fence. State
    threads through the **separate** ``(live_ledger_path, live_portfolio_path)`` pair so a live run never
    writes the canonical replay files. Returns ``None`` when the snapshot is not consumable (the MOD-003
    *"Layer-3 outputs nothing"* contract).
    """
    snapshot = consume(snapshot_path)
    if snapshot is None:
        return None
    if operational_feed is not None:
        operational_input = read_and_capture(
            operational_feed, snapshot.clock_ts, operational_capture_path
        )
    prior_ledger = load_ledger(live_ledger_path)
    prior_portfolio = load_portfolio(live_portfolio_path)

    # Decision composition — the SAME pure cores the chain uses (run_chain is left unchanged, ADR-014 §6.1).
    fv = build_features(snapshot)
    rc = classify(fv, regime_config)
    snapshot_guards = SnapshotGuards(
        data_ok=snapshot.guards.data_ok,
        freshness_ok=snapshot.guards.freshness_ok,
        cooldown_ok=snapshot.guards.cooldown_ok,
    )
    packet = build_decision(
        fv, rc, guards=None, snapshot_guards=snapshot_guards, config=decision_config,
        as_of=snapshot.clock_ts,
    )
    runtime_record, new_ledger = evaluate(packet, prior_ledger, operational_input, runtime_config)

    execution_record: ExecutionRecord | None
    new_portfolio: PortfolioState
    if runtime_record.verdict is Verdict.ADMIT:
        # ADR-011 D1 contract invariant (retained): an ADMIT packet carries the in-hand price feature.
        # On the LIVE path this is NOT the execution mark — the real GLD submit mark is read live from the
        # broker inside reconcile_and_act (ADR-014 §5.1); the derived proxy (gold_price_proxy × OZ_PER_SHARE)
        # is sim/replay-only. (Severing gold_price from the live mark is the Blocker-1 / §5.1 fix.)
        if _PRICE_FEATURE not in fv.features:
            raise ChainContractError(
                f"ADMIT packet has no in-hand {_PRICE_FEATURE} to forward (ADR-011 D1): "
                f"snapshot {snapshot.snapshot_id} lacks the {_PRICE_FEATURE} feature"
            )
        guard_result = run_guard(
            packet.direction, prior_portfolio, guard_config, exec_config, as_of=packet.as_of
        )
        # exec_ref omitted (=None) → reconcile_and_act reads the REAL broker GLD mark inside the startup
        # reconcile, fail-closed (never the proxy): recorded slippage is fill-vs-real-mark (ADR-014 §5.1).
        execution_record, new_portfolio = reconcile_and_act(
            runtime_record, packet.direction, prior_portfolio, guard_result, adapter,
            fill_model=fill_model, exec_config=exec_config, live_config=live_config,
        )
    else:
        execution_record, new_portfolio = None, prior_portfolio

    result = ChainResult(
        feature_vector=fv,
        regime=rc,
        packet=packet,
        runtime_record=runtime_record,
        execution_record=execution_record,
        ledger=new_ledger,
        portfolio=new_portfolio,
    )
    # Persist to the SEPARATE live files (portfolio first, then ledger — the run_once crash-consistency
    # discipline). The canonical replay files are never touched on the live path.
    persist_portfolio(live_portfolio_path, result.portfolio)
    persist_ledger(live_ledger_path, result.ledger)
    return result
