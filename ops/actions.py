"""Safe (non-destructive) console actions — ADR-013 Tier 2 (Step 2).

Each action REUSES an existing governed function, writes an append-only audit entry, and returns a
structured ``ActionResult``. **Actions never raise** — a failure is caught, audited (ok=False), and
returned, so the console stays fail-closed. No extra confirm modal (Tier 2); the safety guarantee is
**structural**, not a UI prompt:

- ``run_chain_now`` is hardwired to the deterministic ``SimulatedBrokerAdapter`` (the ``run_once`` default
  port) + the credential-free, network-free ``MarketCalendarFeed`` — there is NO parameter by which a live
  Alpaca port/feed could be reached here (that is the Step-3 gated-live tier). ``run_once`` enforces
  paper-only + GATE-001 internally; writes are atomic and idempotent on ``source_snapshot_id``.
- ``rerun_calibration_readiness`` re-runs the MOD-009 labeler (which never bumps a ``*_version``) and
  re-reads the committed golden.
- ``resync_neo4j`` runs ``sync_to_neo4j.py --clear`` — an idempotent, read-only re-projection of the
  canonical dev_graph markdown.

Headless + testable: subprocess actions take an injectable ``runner`` (tests never spawn a real process)
and the clock is injectable (deterministic audit timestamps). This module imports no Textual.
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from dataclasses import dataclass

from orchestration.operational_feed import MarketCalendarFeed
from orchestration.runtime import run_once

from ops import audit, core
from ops.audit import AuditEntry, Clock
from ops.core import OpsPaths
from ops.proc import ProcResult, Runner, default_runner, redact, tail

__all__ = [
    "ActionResult", "ProcResult", "Runner", "run_chain_now",
    "rerun_calibration_readiness", "resync_neo4j", "SAFE_ACTIONS",
]


@dataclass(frozen=True)
class ActionResult:
    action: str
    ok: bool
    summary: str            # one-line, safe -> audit result + status surfacing
    detail: tuple[str, ...]  # multi-line -> Log pane (e.g. a subprocess output tail)
    audit: AuditEntry


def _finish(
    paths: OpsPaths, action: str, args_summary: str, ok: bool, summary: str,
    detail: tuple[str, ...], clock: Clock | None,
) -> ActionResult:
    """Build the audit entry, attempt the write (guarded), and return — an action NEVER raises."""
    # Redact the FULL audit surface (not just detail) so no env-secret can reach any persisted field.
    detail = redact(detail)
    args_summary = redact((args_summary,))[0]
    summary = redact((summary,))[0]
    entry = audit.make_entry(action, args_summary, summary, ok, clock=clock)
    try:
        audit.write_entry(paths.audit_log_path, entry)
    except OSError as exc:  # the audit write itself failed — surface loudly, never raise
        detail = (*detail, f"[AUDIT-WRITE-FAILED: {exc}]")
    return ActionResult(action=action, ok=ok, summary=summary, detail=detail, audit=entry)


def run_chain_now(paths: OpsPaths, *, clock: Clock | None = None) -> ActionResult:
    """Run the latest banked snapshot through the chain on the deterministic simulator (paper-only).

    Mutates the canonical ledger + portfolio (idempotent on ``source_snapshot_id``). Reuses the governed
    ``orchestration.run_once`` with the default ``SimulatedBrokerAdapter`` port + ``MarketCalendarFeed`` —
    no live broker / live feed is reachable from this action.
    """
    action = "run-chain-now"
    snap_path, source = core.resolve_run_snapshot(paths)
    args_summary = (
        f"port=simulated feed=calendar ledger={paths.ledger_path.name} "
        f"portfolio={paths.portfolio_path.name} snapshot={source or 'none'}"
    )
    if snap_path is None:
        return _finish(paths, action, args_summary, True, "nothing to do (no banked snapshot)", (), clock)
    try:
        result = run_once(
            snap_path, paths.ledger_path, paths.portfolio_path,
            operational_feed=MarketCalendarFeed(),
            operational_capture_path=paths.operational_capture_path,
        )
    except Exception as exc:  # fail-closed: audit + return, never raise
        return _finish(paths, action, args_summary, False, f"error: {exc}", (str(exc),), clock)
    if result is None:
        return _finish(
            paths, action, args_summary, True, "nothing to do (snapshot not consumable)", (), clock,
        )
    rec = result.runtime_record
    ex = result.execution_record
    fill = "no-fill" if ex is None or ex.fill is None else f"fill@{ex.fill.fill_price:g}"
    summary = (
        f"verdict={rec.verdict.value} direction={result.packet.direction.value} "
        f"regime={result.packet.regime} {fill}"
    )
    detail = (
        f"snapshot={rec.source_snapshot_id}",
        f"ledger_hash={result.ledger.state_hash()[:12]} "
        f"portfolio_hash={result.portfolio.state_hash()[:12]}",
    )
    return _finish(paths, action, args_summary, True, summary, detail, clock)


def rerun_calibration_readiness(
    paths: OpsPaths, *, runner: Runner | None = None, clock: Clock | None = None,
) -> ActionResult:
    """Re-run the MOD-009 forward-return labeler (regenerates the committed golden) and re-read readiness.

    The labeler is measurement-only — it NEVER calibrates or bumps a ``*_version`` (ADR-012); on an
    unchanged corpus the golden is byte-identical (idempotent).
    """
    action = "rerun-calibration"
    run = runner or default_runner
    script = paths.repo_root / "benchmarks" / "calibration" / "run_forward_return_labels.py"
    args_summary = f"script={script.name} (MOD-009 labeler; measurement-only, never bumps a *_version)"
    proc = run([sys.executable, str(script)], paths)
    ok = proc.returncode == 0
    cal = core.calibration_readiness(paths)
    if ok:
        summary = (
            f"exit=0 calibration={cal.overall} N={cal.n_committed} realized={cal.realized_count}"
        )
    else:
        summary = f"exit={proc.returncode} (failed)"
    detail = tail(proc.stdout if ok else (proc.stderr or proc.stdout))
    return _finish(paths, action, args_summary, ok, summary, detail, clock)


def resync_neo4j(
    paths: OpsPaths, *, runner: Runner | None = None, clock: Clock | None = None,
) -> ActionResult:
    """Re-project the canonical dev_graph markdown into Neo4j via ``sync_to_neo4j.py --clear`` (idempotent).

    The Neo4j graph is read-only; the markdown is canonical. Requires ``NEO4J_PASSWORD`` in the
    environment / the DB to be up — a failure is audited (ok=False) and surfaced, never raised.
    """
    action = "resync-neo4j"
    run = runner or default_runner
    script = paths.repo_root / "sync_to_neo4j.py"
    args_summary = f"script={script.name} --clear (idempotent read-only re-projection)"
    proc = run([sys.executable, str(script), "--clear"], paths)
    ok = proc.returncode == 0
    summary = f"exit={proc.returncode}" + (" (synced)" if ok else " (failed)")
    detail = tail(proc.stdout if ok else (proc.stderr or proc.stdout))
    return _finish(paths, action, args_summary, ok, summary, detail, clock)


# The Step-2 safe action registry (name -> callable). The TUI dispatches through this.
SAFE_ACTIONS: dict[str, Callable[[OpsPaths], ActionResult]] = {
    "run-chain-now": run_chain_now,
    "rerun-calibration": rerun_calibration_readiness,
    "resync-neo4j": resync_neo4j,
}
