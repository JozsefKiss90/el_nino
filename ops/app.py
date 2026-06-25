"""Textual TUI for the Operations Control Plane (ADR-013, Step 1 — READ-ONLY).

A local terminal operator console over the El Niño Layer-3 runtime. It renders the governed read-model
in ``ops.core`` and performs **no mutation** in this step (no actions are wired — Step 2 adds the safe
tier behind an audit log; Step 3 the gated-live tier behind confirm + audit + a server-side precondition,
after an operator HARD PAUSE). There is **no network listener** — it reads artefacts and calls in-process
governed functions only (ADR-013 §2).

Run:  python -m ops.app            # the interactive TUI
      python -m ops.app --once     # a one-shot headless text dump (no TTY needed)

The header shows pipeline health + the always-on ``paper-only`` badge; tabs cover Overview, Gates,
Calibration, Artefacts, Processes, Plugs, and a Log pane. The view auto-refreshes on an interval and on
demand (``r``); the scheduled-task query is run on mount / manual refresh only (it spawns PowerShell).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Make the trading engine importable when launched as a plain script (mirrors the calibration harness /
# daily_chain_run.ps1 convention). A proper ``pip install -e ".[ops]"`` exposes src/* as top-level
# packages and makes this a no-op. This runs BEFORE importing ops.core (which imports src/).
_SRC = Path(__file__).resolve().parents[1] / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from rich.text import Text  # noqa: E402  (after the src bootstrap)
from textual import work  # noqa: E402
from textual.app import App, ComposeResult  # noqa: E402
from textual.containers import Container, Horizontal, VerticalScroll  # noqa: E402
from textual.screen import ModalScreen  # noqa: E402
from textual.widgets import (  # noqa: E402
    Button,
    DataTable,
    Footer,
    Header,
    Label,
    RichLog,
    Static,
    TabbedContent,
    TabPane,
)

from ops import actions, gated  # noqa: E402
from ops.core import (  # noqa: E402
    Dashboard,
    OpsPaths,
    assemble_dashboard,
    query_scheduled_task,
    render_text_dashboard,
)


class ConfirmModal(ModalScreen[bool]):
    """A blocking confirm dialog for a gated-live (Tier 3) action — shows its server-side precondition."""

    BINDINGS = [
        ("y", "confirm", "Confirm"),
        ("n", "cancel", "Cancel"),
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(self, action_name: str, description: str, precondition: str) -> None:
        super().__init__()
        self._action_name = action_name
        self._description = description
        self._precondition = precondition

    def compose(self) -> ComposeResult:
        with Container(id="confirm-box"):
            yield Label(f"GATED-LIVE: {self._action_name}", id="confirm-title")
            yield Label(self._description, id="confirm-desc")
            yield Label(self._precondition, id="confirm-pre")
            yield Label("Confirm this live/mutating action?  [y] yes   [n] no", id="confirm-hint")
            with Horizontal(id="confirm-buttons"):
                yield Button("Confirm", variant="error", id="confirm-yes")
                yield Button("Cancel", variant="primary", id="confirm-no")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "confirm-yes")

    def action_confirm(self) -> None:
        self.dismiss(True)

    def action_cancel(self) -> None:
        self.dismiss(False)

REFRESH_SECONDS = 5.0

_HEALTH_STYLE = {
    "ok": "bold green",
    "degraded": "bold yellow",
    "no-state": "bold cyan",
    "error": "bold red",
}


class OpsConsole(App[None]):
    """The read-only operations console."""

    TITLE = "El Nino - Operations Control Plane"
    SUB_TITLE = "paper-only - read-only (ADR-013 Step 1)"

    CSS = """
    #statusbar { height: 1; padding: 0 1; background: $panel; }
    #overview-body { padding: 1; }
    DataTable { height: auto; }
    ConfirmModal { align: center middle; }
    #confirm-box { width: 78; height: auto; border: thick $error; background: $surface; padding: 1 2; }
    #confirm-title { text-style: bold; color: $error; }
    #confirm-pre { color: $warning; }
    #confirm-buttons { height: auto; padding-top: 1; }
    """

    BINDINGS = [
        ("r", "refresh", "Refresh"),
        ("c", "run_chain", "Run chain"),
        ("k", "calibration", "Re-run calib"),
        ("s", "resync_neo4j", "Re-sync graph"),
        # Gated-live (Tier 3) — each opens a confirm modal first.
        ("a", "alpaca_run", "Alpaca run"),
        ("g", "reg_sched", "Reg sched"),
        ("u", "unreg_sched", "Unreg sched"),
        ("b", "calib_bump", "Calib bump"),
        ("h", "operator_halt", "HALT"),
        ("j", "operator_resume", "Resume"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, paths: OpsPaths | None = None) -> None:
        super().__init__()
        self._paths = paths if paths is not None else OpsPaths.default()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(id="statusbar")
        with TabbedContent(initial="overview-tab"):
            with TabPane("Overview", id="overview-tab"):
                with VerticalScroll():
                    yield Static(id="overview-body")
            with TabPane("Gates", id="gates-tab"):
                with VerticalScroll():
                    yield Static("ADR-011 Execution Creation Gates (a-f)", classes="hdr")
                    yield DataTable(id="adr011-table")
                    yield Static("ADR-012 Calibration Readiness (G0-G3, advisory)", classes="hdr")
                    yield DataTable(id="adr012-table")
            with TabPane("Calibration", id="calibration-tab"):
                with VerticalScroll():
                    yield Static(id="calibration-body")
            with TabPane("Artefacts", id="artefacts-tab"):
                with VerticalScroll():
                    yield DataTable(id="artefacts-table")
            with TabPane("Processes", id="processes-tab"):
                with VerticalScroll():
                    yield DataTable(id="processes-table")
            with TabPane("Plugs", id="plugs-tab"):
                with VerticalScroll():
                    yield DataTable(id="plugs-table")
            with TabPane("Log", id="log-tab"):
                yield RichLog(id="logpane", highlight=False, markup=False, wrap=True)
        yield Footer()

    def on_mount(self) -> None:
        for table_id, cols in (
            ("#adr011-table", ("gate", "title", "status", "closing artifact")),
            ("#adr012-table", ("gate", "title", "status", "detail")),
            ("#artefacts-table", ("artefact", "status", "detail")),
            ("#processes-table", ("process", "status", "detail")),
            ("#plugs-table", ("plug", "status", "detail")),
        ):
            self.query_one(table_id, DataTable).add_columns(*cols)
        # First paint queries the scheduled task; the interval refresh does not (it spawns PowerShell).
        self.refresh_dashboard(query_tasks=True)
        self.set_interval(REFRESH_SECONDS, self.refresh_dashboard)

    def action_refresh(self) -> None:
        """Manual refresh (also re-queries the scheduled task)."""
        self.refresh_dashboard(query_tasks=True)

    # --- Step-2 safe actions (Tier 2: no confirm modal; audit-logged; result in the Log pane) ----
    def action_run_chain(self) -> None:
        self._begin_action("run-chain-now")

    def action_calibration(self) -> None:
        self._begin_action("rerun-calibration")

    def action_resync_neo4j(self) -> None:
        self._begin_action("resync-neo4j")

    def _begin_action(self, name: str) -> None:
        """Surface the action immediately, switch to the Log tab, then run it off the UI thread."""
        self.query_one("TabbedContent", TabbedContent).active = "log-tab"
        self.query_one("#logpane", RichLog).write(f"[running] {name} ...")
        self._run_action(name)

    @work(thread=True)
    def _run_action(self, name: str) -> None:
        """Run a safe action in a worker thread (subprocess actions must not block the event loop).

        Defense in depth: actions are designed never to raise, but the worker still catches everything
        and marshals a result back — so the UI never sticks on '[running]' and the app never exits on a
        worker error (Textual's default exit_on_error).
        """
        try:
            result = actions.SAFE_ACTIONS[name](self._paths)
        except Exception as exc:  # noqa: BLE001 — worker must never let an exception escape
            self.call_from_thread(self._on_action_failed, name, exc)
            return
        self.call_from_thread(self._on_action_done, result)

    def _on_action_failed(self, name: str, exc: Exception) -> None:
        self.query_one("#logpane", RichLog).write(f"[FAILED] {name}: unexpected error: {exc}")
        self.refresh_dashboard(query_tasks=False)

    def _on_action_done(self, result: actions.ActionResult) -> None:
        log = self.query_one("#logpane", RichLog)
        status = "OK" if result.ok else "FAILED"
        log.write(f"[{status}] {result.action}: {result.summary}")
        for line in result.detail:
            log.write(f"    {line}")
        # Refresh re-renders every pane (the action mutated ledger/portfolio/calibration state) +
        # re-reads the audit tail; query_tasks=False keeps this fast (no PowerShell spawn).
        self.refresh_dashboard(query_tasks=False)

    # --- Step-3 gated-live actions (Tier 3: confirm modal + audit + server-side precondition) ----
    def action_alpaca_run(self) -> None:
        self._confirm_gated(
            "run-chain-now-ALPACA-PAPER",
            "Route THIS run's execution to the LIVE Alpaca PAPER adapter (virtual money, paper-only).",
        )

    def action_reg_sched(self) -> None:
        self._confirm_gated(
            "register-daily-schedule", "Register the recurring daily chain scheduled task (reversible).",
        )

    def action_unreg_sched(self) -> None:
        self._confirm_gated(
            "unregister-daily-schedule", "Unregister the daily chain scheduled task.",
        )

    def action_calib_bump(self) -> None:
        self._confirm_gated(
            "commit-calibration-bump",
            "Commit a calibration bump (gate-checked: DEFER unless ADR-012 passes; never bumps a *_version).",
        )

    def action_operator_halt(self) -> None:
        self._confirm_gated(
            "operator-halt",
            "ENGAGE the operator kill switch: the next live cycle REJECTs (operational_ok) before any order.",
        )

    def action_operator_resume(self) -> None:
        self._confirm_gated(
            "operator-resume", "CLEAR the operator kill switch: live execution resumes on the next cycle.",
        )

    def _confirm_gated(self, name: str, description: str) -> None:
        precondition = gated.precondition_line(self._paths, name)

        def on_result(confirmed: bool | None) -> None:
            if confirmed:
                self._begin_gated(name)
            else:
                self.query_one("#logpane", RichLog).write(f"[cancelled] {name}")

        self.push_screen(ConfirmModal(name, description, precondition), on_result)

    def _begin_gated(self, name: str) -> None:
        self.query_one("TabbedContent", TabbedContent).active = "log-tab"
        self.query_one("#logpane", RichLog).write(f"[running] {name} ...")
        self._run_gated(name)

    @work(thread=True)
    def _run_gated(self, name: str) -> None:
        """Run a gated action in a worker thread; crash-proof (the worker never lets an exception escape)."""
        try:
            result = gated.GATED_ACTIONS[name](self._paths)
        except Exception as exc:  # noqa: BLE001 — defense in depth; gated actions are designed not to raise
            self.call_from_thread(self._on_gated_failed, name, exc)
            return
        self.call_from_thread(self._on_gated_done, result)

    def _on_gated_failed(self, name: str, exc: Exception) -> None:
        self.query_one("#logpane", RichLog).write(f"[FAILED] {name}: unexpected error: {exc}")
        self.refresh_dashboard(query_tasks=False)

    def _on_gated_done(self, result: gated.GatedResult) -> None:
        log = self.query_one("#logpane", RichLog)
        status = "OK" if result.ok else "FAILED"
        verb = "executed" if result.executed else "no-op/refused"
        log.write(f"[{status}/{verb}] {result.action}: {result.summary}")
        for line in result.detail:
            log.write(f"    {line}")
        self.refresh_dashboard(query_tasks=False)

    def refresh_dashboard(self, query_tasks: bool = False) -> None:
        fetcher = query_scheduled_task if query_tasks else None
        try:
            dash = assemble_dashboard(self._paths, task_fetcher=fetcher)
        except Exception as exc:  # the read-model is defensive, but never let a refresh kill the app
            self.query_one("#statusbar", Static).update(Text(f"read-model error: {exc}", style="bold red"))
            return
        self._render_statusbar(dash)
        self._render_overview(dash)
        self._render_gates(dash)
        self._render_calibration(dash)
        self._render_artefacts(dash)
        self._render_processes(dash)
        self._render_plugs(dash)
        self._render_log(dash)

    # --- per-pane renderers ---------------------------------------------------------------
    def _render_statusbar(self, dash: Dashboard) -> None:
        p = dash.pipeline
        bar = Text()
        bar.append(" PAPER-ONLY ", style="bold white on dark_green")
        bar.append("  health=", style="dim")
        bar.append(p.health, style=_HEALTH_STYLE.get(p.health, "white"))
        bar.append(f"  ledger={p.ledger_entries}", style="dim")
        bar.append(f"  verdict={p.latest_verdict or '-'}", style="dim")
        bar.append(f"  positions={p.open_positions}", style="dim")
        bar.append(f"  calib={dash.calibration.overall}", style="dim")
        if p.errors:
            bar.append(f"  errors={len(p.errors)}", style="bold red")
        self.query_one("#statusbar", Static).update(bar)

    def _render_overview(self, dash: Dashboard) -> None:
        pv = dash.preview
        body = Text()
        body.append("Pipeline\n", style="bold underline")
        body.append(f"  {dash.pipeline.headline}\n")
        for err in dash.pipeline.errors:
            body.append(f"  ! {err}\n", style="red")
        body.append("\nLatest-decision preview ", style="bold underline")
        body.append("(pure, no persistence)\n", style="dim italic")
        if not pv.consumable:
            body.append(f"  {pv.note}{' - ' + pv.error if pv.error else ''}\n", style="yellow")
        else:
            body.append(f"  snapshot={pv.snapshot_id} [{pv.snapshot_source}]\n", style="dim")
            body.append(f"  regime={pv.regime}  direction={pv.direction}  ")
            body.append(f"verdict={pv.verdict}", style=self._verdict_style(pv.verdict))
            body.append(f"  fill={pv.fill}\n")
            body.append("  guards:\n", style="dim")
            for g in pv.guards:
                mark = {True: "PASS", False: "FAIL", None: "n/a "}[g.passed]
                style = {True: "green", False: "red", None: "dim"}[g.passed]
                body.append(f"    [{mark}] {g.name}: {g.reason}\n", style=style)
        body.append("\nPolicy versions\n", style="bold underline")
        pol = dash.policy
        body.append(
            f"  runtime={pol.runtime_policy_version} ({pol.runtime_policy_fingerprint})  "
            f"exec={pol.execution_policy_version} ({pol.execution_policy_fingerprint})  "
            f"fill={pol.fill_model_version} ({pol.fill_model_fingerprint})\n",
            style="dim",
        )
        self.query_one("#overview-body", Static).update(body)

    def _render_gates(self, dash: Dashboard) -> None:
        t11 = self.query_one("#adr011-table", DataTable)
        t11.clear()
        for g in dash.gates.adr011:
            t11.add_row(g.gate_id, g.title, g.status, g.detail)
        t12 = self.query_one("#adr012-table", DataTable)
        t12.clear()
        for g in dash.gates.adr012:
            t12.add_row(g.gate_id, g.title, g.status, g.detail)

    def _render_calibration(self, dash: Dashboard) -> None:
        c = dash.calibration
        body = Text()
        body.append("Calibration readiness ", style="bold underline")
        body.append(f"= {c.overall}\n", style="bold yellow" if c.overall == "DEFER" else "bold green")
        body.append(f"  committed N={c.n_committed} (G0 floor {c.g0_floor})\n", style="dim")
        body.append(f"  regimes={list(c.regimes)}\n  directions={list(c.directions)}\n", style="dim")
        body.append(
            f"  labels={c.label_count}  realized={c.realized_count}\n", style="dim"
        )
        body.append(f"  decision versions: {c.decision_versions}\n", style="dim")
        for g in c.per_gate:
            style = "green" if g.status == "pass" else "red"
            body.append(f"  {g.gate_id} {g.title}: ", style="bold")
            body.append(f"{g.status}", style=style)
            body.append(f" - {g.detail}\n", style="dim")
        body.append(f"\n  {c.note}\n", style="italic dim")
        if c.error:
            body.append(f"  ! {c.error}\n", style="red")
        self.query_one("#calibration-body", Static).update(body)

    def _render_artefacts(self, dash: Dashboard) -> None:
        table = self.query_one("#artefacts-table", DataTable)
        table.clear()
        led = dash.ledger
        table.add_row(
            "runtime_ledger", _exists(led.exists, led.error),
            f"entries={led.entry_count} verdicts={led.verdict_counts} hash={_short(led.state_hash)}",
        )
        pf = dash.portfolio
        table.add_row(
            "portfolio_state", _exists(pf.exists, pf.error),
            f"positions={pf.position_count} open={pf.open_position_count} "
            f"realized_pnl={pf.realized_pnl} fills={pf.execution_count} hash={_short(pf.state_hash)}",
        )
        op = dash.operational
        table.add_row(
            "operational_capture", op.source,
            f"tradeable={op.tradeable} venue_open={op.venue_open} halt={op.halt} "
            f"degraded={op.degraded} as_of={op.as_of}",
        )
        cal = dash.calibration
        table.add_row(
            "calibration_golden", "ok" if cal.available else "absent/error",
            f"N={cal.n_committed} realized={cal.realized_count} versions={cal.decision_versions}",
        )

    def _render_processes(self, dash: Dashboard) -> None:
        table = self.query_one("#processes-table", DataTable)
        table.clear()
        for proc in dash.processes:
            table.add_row(proc.name, proc.status, proc.detail)

    def _render_plugs(self, dash: Dashboard) -> None:
        table = self.query_one("#plugs-table", DataTable)
        table.clear()
        for plug in dash.plugs:
            table.add_row(plug.name, plug.status, plug.detail)

    def _render_log(self, dash: Dashboard) -> None:
        log = self.query_one("#logpane", RichLog)
        log.clear()
        log.write("=== AUDIT (console actions) ===")
        if dash.audit_tail:
            for line in dash.audit_tail:
                log.write(line)
        else:
            log.write("(no console actions audited yet)")
        log.write("")
        log.write("=== RUN LOGS (daily chain) ===")
        if dash.events:
            for line in dash.events:
                log.write(line)
        else:
            log.write("(no daily-run logs found)")

    @staticmethod
    def _verdict_style(verdict: str | None) -> str:
        return {"ADMIT": "bold green", "HOLD": "bold yellow", "REJECT": "bold red"}.get(
            verdict or "", "white"
        )


def _exists(exists: bool, error: str | None) -> str:
    if error:
        return "ERROR"
    return "ok" if exists else "absent"


def _short(value: str | None) -> str:
    return value[:12] if value else "-"


def _print_once(paths: OpsPaths) -> None:
    """One-shot headless dump (no Textual). stdout is made UTF-8 / replace-safe for Windows consoles."""
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
    except (AttributeError, ValueError):
        pass
    try:
        dash = assemble_dashboard(paths, task_fetcher=query_scheduled_task)
        lines = render_text_dashboard(dash)
    except Exception as exc:  # the read-model is fail-closed, but never traceback on --once
        print(f"ops console read-model error (fail-closed): {exc}")
        return
    for line in lines:
        print(line)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ops.app",
        description="El Nino Operations Control Plane (ADR-013, Step 1: read-only TUI).",
    )
    parser.add_argument(
        "--once", action="store_true",
        help="print a one-shot headless text dashboard and exit (no TTY needed)",
    )
    args = parser.parse_args(argv)
    paths = OpsPaths.default()
    if args.once:
        _print_once(paths)
        return 0
    OpsConsole(paths).run()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
