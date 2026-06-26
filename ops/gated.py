"""Gated-live console actions — ADR-013 Tier 3 (Step 3).

The most privileged surface. Each action, in the TUI, sits behind THREE things: an in-console **confirm
modal**, an append-only **audit entry**, and a **server-side precondition** enforced HERE (not by the UI).
Like the safe tier, gated actions **never raise** — failures/refusals are caught, audited, and returned.

The four gated actions:
- ``run_chain_now_alpaca_paper`` — runs the chain ONCE routing execution through the LIVE Alpaca **paper**
  adapter (``paper_adapter_from_env``) via the non-replayable ``live_runtime.operate_live`` entrypoint,
  threading the **separate** live ledger/portfolio files (ADR-014 §5.3) so live state never contaminates
  the canonical replay files. Server-side precondition: the factory must return a non-dormant client
  (paper creds present AND the parsed paper host) — else the action REFUSES (executed=False), never
  placing an order. Paper-only / virtual-money always; built-but-dormant (no LONG emitted pre-calibration,
  so today this is a safe no-fill live round-trip). No persisted 'always-live' state (the one-shot model).
- ``register_daily_schedule`` / ``unregister_daily_schedule`` — reuse ``register_daily_chain_task.ps1`` /
  ``Unregister-ScheduledTask`` (reversible). The scheduled run uses the deterministic simulator + calendar.
- ``commit_calibration_bump`` — gate-respecting: returns **DEFER** unless the ADR-012 readiness gate passes,
  and even when 'ELIGIBLE' it does NOT auto-bump (a bump is a human-review-required config-version
  amendment, ADR-012 sec.6). This action NEVER mutates a ``*_version`` on any branch.

Headless + testable: the Alpaca adapter factory and the subprocess runner are injectable (tests never hit
the network / spawn PowerShell), and the clock is injectable. Imports no Textual.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Callable
from dataclasses import dataclass

from execution import Position, ReconcileEntry, load_portfolio, persist_portfolio
from execution.live_adapter import LiveExecutionAdapter, live_adapter_from_env
from gold.paper_runtime.models import OperationalInput
from orchestration.live_runtime import operate_live
from orchestration.operational_feed import (
    MarketCalendarFeed,
    OperatorHaltFeed,
    operator_halt_active,
    persist_operational,
)

from ops import audit, core
from ops.audit import AuditEntry, Clock
from ops.core import OpsPaths
from ops.proc import Runner, default_runner, redact, tail

_TASK_NAME = "ElNino-Chain-DailyRun"
AdapterFactory = Callable[[], LiveExecutionAdapter]


@dataclass(frozen=True)
class GatedResult:
    action: str
    ok: bool
    executed: bool            # whether the governed mutation actually RAN (vs refused by the precondition)
    summary: str
    detail: tuple[str, ...]
    audit: AuditEntry


def _finish(
    paths: OpsPaths, action: str, args_summary: str, ok: bool, executed: bool, summary: str,
    detail: tuple[str, ...], clock: Clock | None,
) -> GatedResult:
    """Build the audit entry, attempt the write (guarded), and return — a gated action NEVER raises."""
    # Redact the FULL audit surface (not just detail) so no env-secret can reach any persisted field.
    detail = redact(detail)
    args_summary = redact((args_summary,))[0]
    summary = redact((summary,))[0]
    entry = audit.make_entry(action, args_summary, summary, ok, clock=clock)
    try:
        audit.write_entry(paths.audit_log_path, entry)
    except OSError as exc:  # the audit write itself failed — surface loudly, never raise
        detail = (*detail, f"[AUDIT-WRITE-FAILED: {exc}]")
    return GatedResult(action=action, ok=ok, executed=executed, summary=summary, detail=detail, audit=entry)


# ====================================================================================== alpaca paper
def run_chain_now_alpaca_paper(
    paths: OpsPaths, *, adapter_factory: AdapterFactory = live_adapter_from_env,
    clock: Clock | None = None,
) -> GatedResult:
    """Run the chain once routing execution through the LIVE Alpaca paper adapter (gated).

    Routes through the reconcile-then-act ``live_runtime.operate_live`` (ADR-014 §6) with the
    side/order-based :class:`~execution.live_adapter.LiveExecutionAdapter`, threading the **separate**
    live ledger/portfolio files (§5.3). Server-side precondition: the factory must return a non-dormant
    client (paper creds + parsed paper host) — else REFUSE, no order. Operator-halt aware: a set kill
    switch forces the operational feed to ``halt`` so the run REJECTs before any order (ADR-014 §6.6).
    """
    action = "run-chain-now-ALPACA-PAPER"
    args_summary = (
        f"port=alpaca_paper(LIVE) feed=calendar ledger={paths.live_ledger_path.name} "
        f"portfolio={paths.live_portfolio_path.name}"
    )
    # Outer guard: ANY unexpected error in the pre/post-order work still audits (executed=False),
    # so the action structurally never raises — it does not rely on each sub-call being perfect.
    try:
        adapter = adapter_factory()
        # SERVER-SIDE PRECONDITION: paper creds present AND parsed paper host (else client is None).
        if adapter.client is None:
            return _finish(
                paths, action, args_summary, ok=False, executed=False,
                summary="REFUSED (fail-closed): no paper creds / non-paper host - no order placed",
                detail=("the governed paper_adapter_from_env() returned a dormant client; nothing sent",),
                clock=clock,
            )
        snap_path, source = core.resolve_run_snapshot(paths)
        args_summary = f"{args_summary} snapshot={source or 'none'}"
        if snap_path is None:
            return _finish(
                paths, action, args_summary, True, False, "nothing to do (no banked snapshot)", (), clock,
            )
        try:
            result = operate_live(
                snap_path, paths.live_ledger_path, paths.live_portfolio_path, adapter,
                # Operator-halt-aware: a set kill switch forces the feed to halt → operational_ok REJECTs
                # before any order is reconciled (ADR-014 §6.6 — one governed kill mechanism).
                operational_feed=OperatorHaltFeed(MarketCalendarFeed(), paths.operator_halt_path),
                operational_capture_path=paths.live_operational_capture_path,
            )
        except Exception as exc:  # the live order attempt failed (e.g. AlpacaExecutionError) -> executed
            return _finish(paths, action, args_summary, False, True, f"error: {exc}", (str(exc),), clock)
    except Exception as exc:  # unexpected pre/post-order error -> never raise, audit as not-executed
        return _finish(
            paths, action, args_summary, False, False, f"unexpected error: {exc}", (str(exc),), clock,
        )
    if result is None:
        return _finish(
            paths, action, args_summary, True, True, "nothing to do (snapshot not consumable)", (), clock,
        )
    rec = result.runtime_record
    ex = result.execution_record
    mode = ex.execution_mode.value if ex is not None else "no-exec"
    fill = "no-fill" if ex is None or ex.fill is None else f"fill@{ex.fill.fill_price:g}"
    summary = (
        f"LIVE-PAPER verdict={rec.verdict.value} direction={result.packet.direction.value} "
        f"mode={mode} {fill}"
    )
    detail = (
        f"snapshot={rec.source_snapshot_id}",
        f"ledger_hash={result.ledger.state_hash()[:12]} "
        f"portfolio_hash={result.portfolio.state_hash()[:12]}",
    )
    return _finish(paths, action, args_summary, True, True, summary, detail, clock)


# ====================================================================================== schedule
def register_daily_schedule(
    paths: OpsPaths, *, runner: Runner | None = None, clock: Clock | None = None,
) -> GatedResult:
    """Register the recurring daily scheduled task via the existing governed script (reversible)."""
    action = "register-daily-schedule"
    run = runner or default_runner
    script = paths.repo_root / "scripts" / "register_daily_chain_task.ps1"
    args_summary = f"script={script.name} task={_TASK_NAME} (reversible via unregister)"
    try:
        if not script.exists():
            return _finish(
                paths, action, args_summary, False, False,
                f"REFUSED: missing script {script.name}", (), clock,
            )
        proc = run(
            ["powershell", "-NonInteractive", "-NoProfile", "-ExecutionPolicy", "Bypass",
             "-File", str(script)],
            paths,
        )
    except Exception as exc:  # structural never-raise: any unexpected error still audits
        return _finish(
            paths, action, args_summary, False, False, f"unexpected error: {exc}", (str(exc),), clock,
        )
    ok = proc.returncode == 0
    summary = f"exit={proc.returncode}" + (" (registered)" if ok else " (failed)")
    detail = tail(proc.stdout if ok else (proc.stderr or proc.stdout))
    return _finish(paths, action, args_summary, ok, True, summary, detail, clock)


def unregister_daily_schedule(
    paths: OpsPaths, *, runner: Runner | None = None, clock: Clock | None = None,
) -> GatedResult:
    """Unregister the recurring daily scheduled task (the reversal of register)."""
    action = "unregister-daily-schedule"
    run = runner or default_runner
    args_summary = f"task={_TASK_NAME} (Unregister-ScheduledTask)"
    try:
        proc = run(
            ["powershell", "-NonInteractive", "-NoProfile", "-Command",
             f"Unregister-ScheduledTask -TaskName '{_TASK_NAME}' -Confirm:$false"],
            paths,
        )
    except Exception as exc:  # structural never-raise: any unexpected error still audits
        return _finish(
            paths, action, args_summary, False, False, f"unexpected error: {exc}", (str(exc),), clock,
        )
    ok = proc.returncode == 0
    summary = f"exit={proc.returncode}" + (" (unregistered)" if ok else " (failed)")
    detail = tail(proc.stdout if ok else (proc.stderr or proc.stdout))
    return _finish(paths, action, args_summary, ok, True, summary, detail, clock)


# ====================================================================================== operator halt
def set_operator_halt(
    paths: OpsPaths, *, halt: bool = True, clock: Clock | None = None,
) -> GatedResult:
    """Audited Tier-2 kill switch (ADR-014 §6.6): write (engage) or clear (resume) the operator halt.

    Persists an ``OperationalInput`` with ``halt=True`` (engage) / ``halt=False`` (resume) to the
    operator-halt marker. The live operational feed (:class:`OperatorHaltFeed`) honors it through the
    **existing** ``operational_ok`` predicate, so the next live cycle REJECTs before any order is placed —
    the single chosen governed kill mechanism (no second mechanism, no standalone rate limiter, no new
    read path). Writing the marker is the governed mutation (``executed=True``); a failed write is
    audited, never raised.
    """
    action = "operator-halt" if halt else "operator-resume"
    args_summary = f"halt={halt} marker={paths.operator_halt_path.name}"
    try:
        marker = OperationalInput(
            instrument="GLD", tradeable=not halt, venue_open=True, halt=halt, degraded=False,
        )
        persist_operational(paths.operator_halt_path, marker)
    except Exception as exc:  # structural never-raise: any unexpected error still audits
        return _finish(
            paths, action, args_summary, False, False, f"unexpected error: {exc}", (str(exc),), clock,
        )
    state = "ENGAGED — execution halted" if halt else "CLEARED — execution resumes"
    summary = f"operator halt {state}"
    detail = (
        f"marker: {paths.operator_halt_path}",
        "honored via operational_ok (REJECT) on the next live cycle — the single governed kill mechanism",
    )
    return _finish(paths, action, args_summary, True, True, summary, detail, clock)


def resume_operator_halt(paths: OpsPaths, *, clock: Clock | None = None) -> GatedResult:
    """Clear the operator kill switch (the reversal of :func:`set_operator_halt`)."""
    return set_operator_halt(paths, halt=False, clock=clock)


# ====================================================================================== calibration bump
def commit_calibration_bump(paths: OpsPaths, *, clock: Clock | None = None) -> GatedResult:
    """Gate-respecting calibration bump: DEFER unless the ADR-012 gate passes. NEVER mutates a *_version.

    There is no callable that performs a bump (it is a human-review-required config-version amendment,
    ADR-012 sec.6). So this action only evaluates the gate and audits the outcome; ``executed`` is always
    False — the console can never force a bump.
    """
    action = "commit-calibration-bump"
    args_summary = "calibration gate check (console never bumps)"
    try:
        cal = core.calibration_readiness(paths)
        args_summary = (
            f"eligible={cal.eligible} N={cal.n_committed} realized={cal.realized_count} "
            "(console never bumps)"
        )
        # Branch on the DISCRETE gate verdict, not a prose prefix. executed is False on BOTH branches —
        # the console never mutates a *_version under any circumstance.
        if not cal.eligible:
            summary = "DEFER: ADR-012 gate not passed; NO bump (the console never mutates a *_version)"
            return _finish(paths, action, args_summary, True, False, summary, (cal.note,), clock)
        summary = (
            "ELIGIBLE but NOT auto-applied: a bump is a human-review-required config-version amendment "
            "(ADR-012 sec.6); the console does NOT bump"
        )
        return _finish(paths, action, args_summary, True, False, summary, (cal.note,), clock)
    except Exception as exc:  # structural never-raise: any unexpected error still audits
        return _finish(
            paths, action, args_summary, False, False, f"unexpected error: {exc}", (str(exc),), clock,
        )


# ====================================================================================== adopt broker position
def adopt_broker_position(paths: OpsPaths, *, clock: Clock | None = None) -> GatedResult:
    """Adopt the observed broker position into the LIVE portfolio, clearing a terminal-refuse (ADR-014 §6.2).

    A live FLAT-time reconcile that finds a broker position with **no local lineage** records a
    ``discrepancy:unexplained_position`` reconcile observation and **terminal-refuses live execution**
    (no auto-flatten — selling blind would import a real-money instinct and destroy evidence). The only
    governed way out is THIS action: it adopts the observed broker position (quantity + average entry
    price) into the local position so the next FLAT cycle can sell to close instead of refusing — **never
    automatic** (ADR-014 §6.2 / ADR-013 Tier-3).

    **Append-only / reuse-only.** It records an append-only ``adopt:reconcile-adopt`` :class:`ReconcileEntry`
    in the live portfolio's existing reconcile history and sets the local position from the OBSERVED broker
    quantity/avg-cost using the **existing** immutable :class:`PortfolioState` value type
    (``append_reconcile`` + ``dataclasses.replace``), then persists via the existing ``persist_portfolio``
    onto the **separate** live file (§5.3). No ``src/`` method, schema, or ``*_version`` is added/changed,
    and the canonical (sim/replay) portfolio is never touched.

    **Server-side precondition** (enforced HERE, not by the UI): an unhealed
    ``discrepancy:unexplained_position`` with a positive observed quantity and no current local open
    position must exist — else REFUSE (``executed=False``), nothing written. Re-running after an adopt is a
    no-op refusal (the discrepancy is healed). Like every gated action it NEVER raises.
    """
    action = "adopt-broker-position"
    args_summary = f"live_portfolio={paths.live_portfolio_path.name} (append-only reconcile-adopt; never auto)"
    try:
        disc = core.adoptable_discrepancy(paths)
        # SERVER-SIDE PRECONDITION: no unhealed unexplained-position discrepancy ⇒ nothing to adopt → REFUSE.
        if disc is None:
            return _finish(
                paths, action, args_summary, ok=True, executed=False,
                summary="no-op: no unhealed broker-position discrepancy to adopt (nothing refused)",
                detail=("adopt is only valid against a discrepancy:unexplained_position observation",),
                clock=clock,
            )
        args_summary = (
            f"{args_summary} instrument={disc.instrument} observed_qty={disc.observed_qty:g} "
            f"observed_avg={disc.observed_avg_price:g}"
        )
        pf = load_portfolio(paths.live_portfolio_path)
        # Append-only adopt observation into the live reconcile history (records WHY the position appeared).
        healed = pf.append_reconcile(ReconcileEntry(
            source_snapshot_id=disc.source_snapshot_id,
            instrument=disc.instrument,
            observed_qty=disc.observed_qty,
            observed_avg_price=disc.observed_avg_price,
            marker="adopt:reconcile-adopt",
            seq=pf.next_reconcile_seq(),
            as_of=disc.as_of,
        ))
        # Set the local position from the OBSERVED broker truth. Only the per-lot cost basis resets to the
        # observed broker avg (the newly adopted shares); the portfolio-level realized-P&L ACCUMULATOR of any
        # prior (flat) position for this instrument MUST carry forward — a live SELL-fold leaves the residue
        # Position(instr, qty=0, avg=0, realized=X, 0), and dropping it would silently wipe the LIVE real
        # paper-P&L track record (mirrors _apply_live_buy's r0 carry). Uses only the existing immutable type.
        prior = healed.position(disc.instrument)
        realized = prior.realized_pnl if prior is not None else 0.0
        adopted = Position(disc.instrument, disc.observed_qty, disc.observed_avg_price, realized, 0.0)
        others = tuple(p for p in healed.positions if p.instrument != disc.instrument)
        new_positions = tuple(sorted((*others, adopted), key=lambda p: p.instrument))
        new_portfolio = dataclasses.replace(healed, positions=new_positions)
        persist_portfolio(paths.live_portfolio_path, new_portfolio)
        summary = (
            f"ADOPTED {disc.instrument} qty={disc.observed_qty:g} @ {disc.observed_avg_price:g} "
            "- refuse cleared; next cycle can act"
        )
        detail = (
            f"appended adopt:reconcile-adopt seq={pf.next_reconcile_seq()} (append-only); "
            f"realized_pnl carried fwd={realized:g}",
            f"live_portfolio_hash={new_portfolio.state_hash()[:12]}",
        )
    except Exception as exc:  # structural never-raise: any unexpected error still audits (not-executed)
        return _finish(
            paths, action, args_summary, False, False, f"unexpected error: {exc}", (str(exc),), clock,
        )
    return _finish(paths, action, args_summary, True, True, summary, detail, clock)


# The Step-3 gated-live action registry (name -> callable). The TUI dispatches through this AFTER a
# confirm modal; each callable enforces its own server-side precondition.
GATED_ACTIONS: dict[str, Callable[[OpsPaths], GatedResult]] = {
    "run-chain-now-ALPACA-PAPER": run_chain_now_alpaca_paper,
    "register-daily-schedule": register_daily_schedule,
    "unregister-daily-schedule": unregister_daily_schedule,
    "commit-calibration-bump": commit_calibration_bump,
    "operator-halt": set_operator_halt,          # engage the kill switch (halt=True default)
    "operator-resume": resume_operator_halt,      # clear it (the reversal)
    "adopt-broker-position": adopt_broker_position,  # heal an unexplained-position discrepancy (append-only)
}


def precondition_line(paths: OpsPaths, name: str) -> str:
    """A one-line, read-only precondition status shown in the confirm modal (no secrets, never a key)."""
    if name == "run-chain-now-ALPACA-PAPER":
        plug = next((p for p in core.plug_statuses() if p.name == "alpaca_paper_execution"), None)
        status = plug.status if plug is not None else "unknown"
        if status == "creds-present":
            return "precondition OK: paper creds + paper host present -> execution routes LIVE (paper money)"
        return "precondition FAILS: plug dormant (no paper creds / non-paper host) -> will REFUSE, no order"
    if name == "register-daily-schedule":
        return "registers the daily Windows scheduled task (simulator + calendar feed); reversible"
    if name == "unregister-daily-schedule":
        return "removes the daily scheduled task (reversal of register)"
    if name == "commit-calibration-bump":
        cal = core.calibration_readiness(paths)
        return f"ADR-012 gate = {cal.overall} -> {'no bump (DEFER)' if cal.overall.startswith('DEFER') else 'manual review only'}"
    if name == "operator-halt":
        engaged = operator_halt_active(paths.operator_halt_path)
        return (
            "kill switch ALREADY engaged -> live execution already halts (operational_ok REJECT)"
            if engaged
            else "engages the kill switch -> live execution halts on the next cycle (operational_ok REJECT)"
        )
    if name == "operator-resume":
        engaged = operator_halt_active(paths.operator_halt_path)
        return (
            "clears the kill switch -> live execution resumes on the next cycle"
            if engaged
            else "kill switch not engaged -> resume is a no-op"
        )
    if name == "adopt-broker-position":
        disc = core.adoptable_discrepancy(paths)
        if disc is None:
            return "precondition FAILS: no unhealed broker-position discrepancy -> will REFUSE (nothing to adopt)"
        return (
            f"precondition OK: adopt {disc.instrument} qty={disc.observed_qty:g} @ {disc.observed_avg_price:g} "
            "(append-only) -> clears the terminal-refuse"
        )
    return "unknown action"
