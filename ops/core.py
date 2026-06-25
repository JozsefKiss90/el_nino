"""Governed, headless read-model for the Operations Control Plane (ADR-013, Step 1).

This module is **read-only** and imports **no Textual** — it is the testable core the TUI (``ops.app``)
renders. Every surface is assembled by **reusing** an existing ``src/`` governed function (ADR-013 §4);
nothing here reimplements safety, paper-only, gate, or persistence logic, and nothing here mutates state:

- ledger / portfolio / operational status — via the fail-closed loaders ``load_ledger`` /
  ``load_portfolio`` / ``load_operational`` (a missing file is empty/closed; a malformed file raises,
  which we catch and surface as a fail-closed ``error`` field rather than crashing the console);
- the latest-decision preview (regime / direction / verdict / the full six-guard block / fill-or-no-fill)
  — via the **pure** ``run_sequence`` over the latest banked snapshot against the current state. This does
  **no IO, no persistence, no live feed, no network** (default ``SimulatedBrokerAdapter`` port, captured
  ``DEFAULT_OPERATIONAL_INPUT``); it is a deterministic "what running now would produce" projection;
- calibration readiness — by **reading the committed golden** ``forward_return_labels.json`` (the MOD-009
  output) and comparing its counts to the ADR-012 floors in this display layer (advisory; the
  authoritative gate + any bump are human-review-required per ADR-012 §6 — the console never bumps);
- live-plug status — by calling the governed ``paper_adapter_from_env`` / ``clock_feed_from_env``
  factories and inspecting **only** ``client is None``. Credentials are never read, stored, or displayed
  (ADR-013 §6 / KA-008): the badge is ``dormant`` / ``creds-present`` and nothing else.

Per ADR-003 the only third-party dependency the console adds (Textual / Rich) lives in ``ops.app``; this
module is stdlib-only and depends solely on the ``src/`` governed functions.
"""

from __future__ import annotations

import dataclasses
import json
import subprocess
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from execution.alpaca_adapter import paper_adapter_from_env
from execution.config import (
    DEFAULT_EXECUTION_POLICY_CONFIG,
    DEFAULT_FILL_MODEL,
)
from execution.runtime import load_portfolio
from gold.paper_runtime.config import DEFAULT_RUNTIME_POLICY_CONFIG
from gold.paper_runtime.models import Verdict
from gold.paper_runtime.runtime import load_ledger, load_operational
from orchestration.alpaca_clock_feed import clock_feed_from_env
from orchestration.models import ChainResult
from orchestration.runtime import find_latest_snapshot, run_sequence
from snapshot.snapshot_consumer import consume

from ops.audit import read_audit

# The Mr-Ripley Layer-2 producer (a SEPARATE repo) banks one immutable consumable snapshot per day here;
# el_nino READS this directory and never writes it. Overridable via OpsPaths for tests / other hosts.
DEFAULT_PRODUCER_SNAPSHOT_DIR = Path(r"C:\Code\Mr-Ripley\runtime\snapshots")
# The recurring daily-run scheduled task (registered by scripts/register_daily_chain_task.ps1, a Step-3
# gated-live action — NOT registered by the console here).
DAILY_TASK_NAME = "ElNino-Chain-DailyRun"
# ADR-012 gate G0 corpus-size floor, MIRRORED from the ADR-012 document (no governed constant exists to
# import). Advisory only: this display layer compares the committed golden's counts to this floor; it is
# NOT the authoritative gate and never bumps a *_version (a bump is human-review-required, ADR-012 sec.6).
# G1/G2/G3 below are advisory diversity/realized proxies, NOT ADR-012's exact per-target coverage criteria.
G0_CORPUS_FLOOR = 60


# ======================================================================================
# Paths
# ======================================================================================
@dataclass(frozen=True)
class OpsPaths:
    """The artefact paths the read-model reads (mirrors the orchestration runtime defaults).

    All paths are explicit so the read-model is fully testable against fixtures — no hidden reliance
    on the live ``runtime/`` directory.
    """

    repo_root: Path
    ledger_path: Path
    portfolio_path: Path
    operational_capture_path: Path
    el_nino_snapshot: Path
    producer_snapshot_dir: Path
    calibration_artifact: Path
    daily_log_dir: Path
    audit_log_path: Path

    def _live_sibling(self, path: Path) -> Path:
        """A ``.live`` sibling of a canonical artefact path (e.g. ``portfolio_state.live.json``)."""
        return path.with_name(f"{path.stem}.live{path.suffix}")

    @property
    def live_ledger_path(self) -> Path:
        """Physically-separate LIVE ledger (ADR-014 §5.3) — the live path never writes the canonical ledger."""
        return self._live_sibling(self.ledger_path)

    @property
    def live_portfolio_path(self) -> Path:
        """Physically-separate LIVE portfolio (ADR-014 §5.3) — distinct from the deterministic replay file."""
        return self._live_sibling(self.portfolio_path)

    @property
    def live_operational_capture_path(self) -> Path:
        """Physically-separate LIVE operational capture (keeps the canonical capture replay-clean)."""
        return self._live_sibling(self.operational_capture_path)

    @property
    def operator_halt_path(self) -> Path:
        """Operator kill-switch marker (ADR-014 §6.6). A set halt forces the operational feed to ``halt``
        (the existing ``operational_ok`` honor path) so the next live cycle REJECTs before any order."""
        return self.operational_capture_path.with_name("operator_halt.json")

    @classmethod
    def default(cls, repo_root: Path | None = None) -> "OpsPaths":
        root = repo_root if repo_root is not None else Path(__file__).resolve().parents[1]
        chain = root / "runtime" / "chain"
        return cls(
            repo_root=root,
            ledger_path=chain / "runtime_ledger.json",
            portfolio_path=chain / "portfolio_state.json",
            operational_capture_path=chain / "operational_capture.json",
            el_nino_snapshot=root / "snapshot_sources" / "latest_snapshot.json",
            producer_snapshot_dir=DEFAULT_PRODUCER_SNAPSHOT_DIR,
            calibration_artifact=(
                root / "benchmarks" / "calibration" / "artifacts" / "forward_return_labels.json"
            ),
            daily_log_dir=root / "runtime" / "logs",
            audit_log_path=root / "runtime" / "ops" / "audit_log.jsonl",
        )


# ======================================================================================
# View models (frozen, JSON-friendly — the TUI renders these; tests assert on them)
# ======================================================================================
@dataclass(frozen=True)
class LedgerView:
    exists: bool
    entry_count: int
    latest_verdict: str | None
    latest_triggered_guard: str | None
    latest_snapshot_id: str | None
    latest_as_of: str | None
    verdict_counts: dict[str, int]
    state_hash: str | None
    error: str | None


@dataclass(frozen=True)
class PositionView:
    instrument: str
    quantity: float
    avg_cost: float
    realized_pnl: float
    unrealized_pnl: float


@dataclass(frozen=True)
class PortfolioView:
    exists: bool
    position_count: int
    open_position_count: int
    realized_pnl: float
    execution_count: int
    state_hash: str | None
    positions: tuple[PositionView, ...]
    error: str | None


@dataclass(frozen=True)
class OperationalView:
    source: str  # "captured file" | "default-closed (absent)" | "error"
    instrument: str
    tradeable: bool
    venue_open: bool
    halt: bool
    degraded: bool
    as_of: str | None
    error: str | None


@dataclass(frozen=True)
class GuardOutcomeView:
    name: str
    passed: bool | None
    reason: str


@dataclass(frozen=True)
class DecisionPreview:
    """A PURE preview of running the latest banked snapshot against the current state (no persistence).

    ``run_sequence`` is the deterministic replay vehicle: no IO, no live feed, no network. This is a
    "what running now would produce" projection — the only place the full six-guard block exists (the
    persisted ledger stores only the verdict + triggering guard per entry).
    """

    available: bool
    snapshot_source: str | None
    snapshot_id: str | None
    consumable: bool
    regime: str | None
    direction: str | None
    verdict: str | None
    triggered_guard: str | None
    guards: tuple[GuardOutcomeView, ...]
    fill: str | None
    note: str
    error: str | None


@dataclass(frozen=True)
class GateRow:
    gate_id: str
    title: str
    status: str  # "closed" | "pass" | "fail" | "open"
    detail: str


@dataclass(frozen=True)
class GateBoard:
    adr011: tuple[GateRow, ...]
    adr012: tuple[GateRow, ...]
    source: str


@dataclass(frozen=True)
class CalibrationReadiness:
    available: bool
    n_committed: int
    g0_floor: int
    regimes: tuple[str, ...]
    directions: tuple[str, ...]
    label_count: int
    realized_count: int
    decision_versions: dict[str, str]
    per_gate: tuple[GateRow, ...]
    eligible: bool  # the discrete gate verdict (all G0-G3 pass) — consumers branch on THIS, not `overall`
    overall: str    # display string: "DEFER" | "ELIGIBLE (advisory) - operator review (ADR-012 sec.6)"
    note: str
    error: str | None


@dataclass(frozen=True)
class PlugStatus:
    name: str
    status: str  # "dormant" | "creds-present"  (never "enabled" in the read-only tier; never a key)
    detail: str


@dataclass(frozen=True)
class ProcessInfo:
    name: str
    status: str
    detail: str


@dataclass(frozen=True)
class PolicyVersions:
    runtime_policy_version: str
    runtime_policy_fingerprint: str
    execution_policy_version: str
    execution_policy_fingerprint: str
    fill_model_version: str
    fill_model_fingerprint: str


@dataclass(frozen=True)
class PipelineStatus:
    paper_only: bool  # ALWAYS True (ADR-013 §5) — surfaced, never weakened
    health: str  # "ok" | "degraded" | "no-state" | "error"
    headline: str
    ledger_entries: int
    open_positions: int
    latest_verdict: str | None
    errors: tuple[str, ...]


@dataclass(frozen=True)
class Dashboard:
    pipeline: PipelineStatus
    ledger: LedgerView
    portfolio: PortfolioView
    operational: OperationalView
    preview: DecisionPreview
    gates: GateBoard
    calibration: CalibrationReadiness
    plugs: tuple[PlugStatus, ...]
    processes: tuple[ProcessInfo, ...]
    policy: PolicyVersions
    events: tuple[str, ...]
    audit_tail: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Deterministic, fully-serializable projection (used by the no-secret-leak test + the TUI)."""
        return dataclasses.asdict(self)


# A scheduled-task fetcher returns Get-ScheduledTaskInfo-style fields (or None). Injectable so the
# read-model is testable without spawning PowerShell.
TaskInfoFetcher = Callable[[str], Mapping[str, Any] | None]


# ======================================================================================
# Read-model assemblers (each pure; each catches loud loader errors into an ``error`` field)
# ======================================================================================
def ledger_view(paths: OpsPaths) -> LedgerView:
    """Read the runtime ledger (SCHEMA-013) purely via ``load_ledger`` (missing ⇒ empty; malformed ⇒ error)."""
    if not paths.ledger_path.exists():
        return LedgerView(False, 0, None, None, None, None, {}, None, None)
    try:
        ledger = load_ledger(paths.ledger_path)
    except Exception as exc:  # RuntimeContractError on a corrupt ledger — surface, don't crash
        return LedgerView(True, 0, None, None, None, None, {}, None, str(exc))
    counts = {v.value: 0 for v in Verdict}
    for entry in ledger.entries:
        counts[entry.verdict] = counts.get(entry.verdict, 0) + 1
    latest = ledger.entries[-1] if ledger.entries else None
    return LedgerView(
        exists=True,
        entry_count=len(ledger.entries),
        latest_verdict=latest.verdict if latest else None,
        latest_triggered_guard=latest.triggered_guard if latest else None,
        latest_snapshot_id=latest.source_snapshot_id if latest else None,
        latest_as_of=latest.as_of if latest else None,
        verdict_counts=counts,
        state_hash=ledger.state_hash(),
        error=None,
    )


def portfolio_view(paths: OpsPaths) -> PortfolioView:
    """Read the portfolio state (SCHEMA-015) purely via ``load_portfolio`` (missing ⇒ empty; malformed ⇒ error)."""
    if not paths.portfolio_path.exists():
        return PortfolioView(False, 0, 0, 0.0, 0, None, (), None)
    try:
        pf = load_portfolio(paths.portfolio_path)
    except Exception as exc:  # ExecutionContractError on a corrupt portfolio — surface, don't crash
        return PortfolioView(True, 0, 0, 0.0, 0, None, (), str(exc))
    positions = tuple(
        PositionView(p.instrument, p.quantity, p.avg_cost, p.realized_pnl, p.unrealized_pnl)
        for p in sorted(pf.positions, key=lambda p: p.instrument)
    )
    return PortfolioView(
        exists=True,
        position_count=len(pf.positions),
        open_position_count=sum(1 for p in pf.positions if p.quantity != 0.0),
        realized_pnl=round(sum(p.realized_pnl for p in pf.positions), 6),
        execution_count=pf.next_seq(),
        state_hash=pf.state_hash(),
        positions=positions,
        error=None,
    )


def operational_view(paths: OpsPaths) -> OperationalView:
    """Read the captured operational input (default-closed) via the governed ``load_operational``."""
    exists = paths.operational_capture_path.exists()
    try:
        op = load_operational(paths.operational_capture_path)
    except Exception as exc:  # load_operational is itself fail-closed, but stay defensive
        return OperationalView(
            source="error", instrument="GLD", tradeable=False, venue_open=False,
            halt=True, degraded=True, as_of=None, error=str(exc),
        )
    source = "captured file" if exists else "default-closed (absent)"
    return OperationalView(
        source=source,
        instrument=op.instrument,
        tradeable=op.tradeable,
        venue_open=op.venue_open,
        halt=op.halt,
        degraded=op.degraded,
        as_of=op.as_of,
        error=None,
    )


def resolve_run_snapshot(paths: OpsPaths) -> tuple[Path | None, str | None]:
    """The snapshot a run would consume: the latest producer archive, else the el_nino pointer.

    Shared by the read-only preview and the Step-2 'run chain now' action (so both pick the same
    snapshot the daily job would). Fail-closed to the next candidate (and ultimately ``(None, None)``)
    on any ``OSError`` — e.g. an exists-but-unreadable producer directory — so the read-model never raises.
    """
    latest: Path | None = None
    try:
        if paths.producer_snapshot_dir.exists():
            latest = find_latest_snapshot(paths.producer_snapshot_dir)
    except OSError:
        latest = None
    if latest is not None:
        return latest, f"producer:{paths.producer_snapshot_dir.name}"
    try:
        if paths.el_nino_snapshot.exists():
            return paths.el_nino_snapshot, "el_nino:latest_snapshot.json"
    except OSError:
        pass
    return None, None


def _empty_preview(
    available: bool, source: str | None, note: str, error: str | None
) -> DecisionPreview:
    """A preview carrying no decision (no snapshot / not consumable / read error)."""
    return DecisionPreview(
        available=available,
        snapshot_source=source,
        snapshot_id=None,
        consumable=False,
        regime=None,
        direction=None,
        verdict=None,
        triggered_guard=None,
        guards=(),
        fill=None,
        note=note,
        error=error,
    )


def decision_preview(paths: OpsPaths) -> DecisionPreview:
    """Pure preview of the latest snapshot against the current state (no IO/persist/feed/network)."""
    note = (
        "pure preview via run_sequence (no persistence, simulated port, configured-default operational "
        "input: venue-open ADR-009 v0 assumption, NOT the captured file) - what a default run would produce"
    )
    snap_path, source = resolve_run_snapshot(paths)
    if snap_path is None:
        return _empty_preview(False, None, "no banked snapshot found", None)
    try:
        snapshot = consume(snap_path)
        if snapshot is None:
            return _empty_preview(
                True, source, "latest snapshot is not consumable (Layer-3 outputs nothing)", None
            )
        prior_ledger = load_ledger(paths.ledger_path)
        prior_portfolio = load_portfolio(paths.portfolio_path)
        results, _, _ = run_sequence(
            [snapshot], ledger=prior_ledger, portfolio=prior_portfolio
        )
        result: ChainResult = results[0]
    except Exception as exc:  # any contract error — surface as a fail-closed read, never crash
        return _empty_preview(True, source, note, str(exc))
    rec = result.runtime_record
    guards = tuple(GuardOutcomeView(g.name, g.passed, g.reason) for g in rec.guard_outcomes)
    return DecisionPreview(
        available=True,
        snapshot_source=source,
        snapshot_id=rec.source_snapshot_id,
        consumable=True,
        regime=str(result.packet.regime),
        direction=result.packet.direction.value,
        verdict=rec.verdict.value,
        triggered_guard=rec.triggered_guard,
        guards=guards,
        fill=_fill_label(result),
        note=note,
        error=None,
    )


def _fill_label(result: ChainResult) -> str:
    ex = result.execution_record
    if ex is None:
        return "no-exec (verdict not ADMIT)"
    if ex.fill is None:
        return "no-fill (guard-blocked or non-LONG)"
    return f"fill@{ex.fill.fill_price:g} x{ex.fill.quantity:g}"


# The ADR-011 §7 execution-layer Creation Gates (a–f) — all CLOSED per the ADR of record
# (reconciled 2026-06-18). A static, read-only governance board, not a runtime computation.
_ADR011_GATES: tuple[tuple[str, str, str], ...] = (
    ("a", "Execution interface contract (INT-011 ExecutionPort)", "Execution API node (STEP 1)"),
    ("b", "Fill-simulation model replay-keyed", "FillModelConfig fill_model_version (STEP 2)"),
    ("c", "Guard-wiring GATE-001 specified", "run_guard before execute, captured config (STEP 2)"),
    ("d", "Execution-determinism replay benchmark", "BENCH-004 byte-identical replay (STEP 4)"),
    ("e", "Portfolio/position state model", "SCHEMA-015 PortfolioState (STEP 1/2)"),
    ("f", "Alpaca-adapter boundary (default-OFF, fail-closed)", "FILE-037/038 (STEP 5)"),
)


def gate_board(calibration: CalibrationReadiness) -> GateBoard:
    """The ADR-011 a–f board (static, all closed) + the ADR-012 G0–G3 readiness (derived, advisory)."""
    adr011 = tuple(GateRow(g, title, "closed", detail) for g, title, detail in _ADR011_GATES)
    return GateBoard(
        adr011=adr011,
        adr012=calibration.per_gate,
        source="ADR-011 sec.7 (a-f, all closed) + ADR-012 sec.3 readiness (advisory, derived)",
    )


def calibration_readiness(paths: OpsPaths) -> CalibrationReadiness:
    """Read the committed MOD-009 golden and derive ADR-012 readiness signals (advisory; never bumps)."""
    note = (
        "Advisory readiness derived from the committed golden; the authoritative ADR-012 gate and any "
        "*_version bump are human-review-required (ADR-012 sec.3/sec.6). The console never bumps."
    )
    empty: tuple[GateRow, ...] = ()
    if not paths.calibration_artifact.exists():
        return CalibrationReadiness(
            False, 0, G0_CORPUS_FLOOR, (), (), 0, 0, {}, empty, False, "DEFER",
            note, "calibration artifact absent — run the labeler (Step-2 action)",
        )
    try:
        data = json.loads(paths.calibration_artifact.read_text(encoding="utf-8"))
    except Exception as exc:
        return CalibrationReadiness(
            False, 0, G0_CORPUS_FLOOR, (), (), 0, 0, {}, empty, False, "DEFER", note, str(exc)
        )
    committed = data.get("committed_real", {}) if isinstance(data, Mapping) else {}
    cov = committed.get("coverage", {}) if isinstance(committed, Mapping) else {}
    regimes = tuple(str(r) for r in cov.get("regimes", []))
    directions = tuple(str(d) for d in cov.get("directions", []))
    label_count = int(cov.get("label_count", 0) or 0)
    realized = int(cov.get("realized_count", 0) or 0)
    n_committed = int(committed.get("distinct_snapshots", 0) or 0)
    versions = {
        str(k): str(v) for k, v in (data.get("decision_versions", {}) or {}).items()
    }
    g0 = n_committed >= G0_CORPUS_FLOOR
    g1 = len(regimes) >= 2
    g2 = len(directions) >= 2
    g3 = realized > 0
    per_gate = (
        GateRow("G0", "corpus size N>=60", _pf(g0), f"N={n_committed} (committed scope)"),
        GateRow("G1", "regime diversity >=2 (proxy)", _pf(g1), f"{len(regimes)} distinct: {list(regimes)}"),
        GateRow("G2", "direction diversity >=2 (proxy)", _pf(g2), f"{len(directions)} distinct: {list(directions)}"),
        GateRow("G3", "realized forward labels >0", _pf(g3), f"realized={realized} of {label_count}"),
    )
    eligible = all((g0, g1, g2, g3))
    overall = "ELIGIBLE (advisory) - operator review (ADR-012 sec.6)" if eligible else "DEFER"
    return CalibrationReadiness(
        available=True,
        n_committed=n_committed,
        g0_floor=G0_CORPUS_FLOOR,
        regimes=regimes,
        directions=directions,
        label_count=label_count,
        realized_count=realized,
        decision_versions=versions,
        per_gate=per_gate,
        eligible=eligible,
        overall=overall,
        note=note,
        error=None,
    )


def _pf(passed: bool) -> str:
    return "pass" if passed else "fail"


def plug_statuses() -> tuple[PlugStatus, ...]:
    """Derive live-plug status from the governed factories — only ``client is None``, never a key (§6).

    ``creds-present`` ⇒ the factory built a live client (creds present AND the paper host passed the
    parsed-hostname check); ``dormant`` ⇒ fail-closed (no creds, or a non-paper base URL). The factories
    read the environment internally; this function reads neither the environment nor any credential value.
    """
    exec_dormant = paper_adapter_from_env().client is None
    feed_dormant = clock_feed_from_env().client is None
    detail = "default-OFF; paper-host-only; fail-closed; never live-money (ADR-011 sec.3 / KA-008)"
    return (
        PlugStatus(
            "alpaca_paper_execution",
            "dormant" if exec_dormant else "creds-present",
            detail,
        ),
        PlugStatus(
            "alpaca_clock_feed",
            "dormant" if feed_dormant else "creds-present",
            detail,
        ),
    )


def query_scheduled_task(task_name: str) -> Mapping[str, Any] | None:
    """Default fetcher: read Windows Task Scheduler state (read-only) via Get-ScheduledTaskInfo.

    Returns the parsed JSON fields (LastRunTime / NextRunTime / LastTaskResult / …) or ``None`` if the
    task is absent or the query is unavailable (non-Windows host, no PowerShell). This is a pure read —
    Get-ScheduledTaskInfo never mutates the task. Injectable, so tests never spawn PowerShell.
    """
    if not task_name.replace("-", "").replace("_", "").isalnum():
        return None
    cmd = [
        "powershell", "-NonInteractive", "-NoProfile", "-Command",
        f"Get-ScheduledTaskInfo -TaskName '{task_name}' -ErrorAction Stop | ConvertTo-Json -Compress",
    ]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0 or not out.stdout.strip():
        return None
    try:
        data = json.loads(out.stdout)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def process_infos(paths: OpsPaths, task_fetcher: TaskInfoFetcher | None = None) -> tuple[ProcessInfo, ...]:
    """Read process status: the daily scheduled task, producer corpus freshness, and the Neo4j note."""
    infos: list[ProcessInfo] = []

    # 1. Daily chain scheduled task (registering it is a Step-3 gated-live action; here we only observe).
    if task_fetcher is None:
        infos.append(ProcessInfo(
            "daily-chain-task", "not-queried",
            f"task '{DAILY_TASK_NAME}' (pass a task fetcher / manual refresh to query)",
        ))
    else:
        info = task_fetcher(DAILY_TASK_NAME)
        if info is None:
            infos.append(ProcessInfo(
                "daily-chain-task", "not-registered",
                f"'{DAILY_TASK_NAME}' not registered (register is a gated-live action)",
            ))
        else:
            last = info.get("LastRunTime")
            result = info.get("LastTaskResult")
            nxt = info.get("NextRunTime")
            infos.append(ProcessInfo(
                "daily-chain-task", "registered",
                f"last={last} next={nxt} last_result={result}",
            ))

    # 2. Producer corpus freshness (read-only over the separate Mr-Ripley snapshot dir).
    if not paths.producer_snapshot_dir.exists():
        infos.append(ProcessInfo(
            "producer-freshness", "absent",
            f"producer dir not found: {paths.producer_snapshot_dir}",
        ))
    else:
        latest = None
        read_error: str | None = None
        try:
            latest = find_latest_snapshot(paths.producer_snapshot_dir)
        except OSError as exc:  # exists-but-unreadable dir — degrade, never propagate
            read_error = str(exc)
        if read_error is not None:
            infos.append(ProcessInfo(
                "producer-freshness", "error", f"cannot read producer dir: {read_error}",
            ))
        elif latest is None:
            infos.append(ProcessInfo("producer-freshness", "empty", "no snapshot_*.json banked yet"))
        else:
            mtime = _safe_mtime(latest)
            infos.append(ProcessInfo(
                "producer-freshness", "ok", f"latest={latest.name} banked={mtime}",
            ))

    # 3. Neo4j sync — no timestamp is tracked; re-sync is a Step-2 safe action.
    sync_script = paths.repo_root / "sync_to_neo4j.py"
    infos.append(ProcessInfo(
        "neo4j-sync",
        "available" if sync_script.exists() else "missing",
        "read-only projection of dev_graph; last-sync time not tracked (re-sync is a safe action)",
    ))
    return tuple(infos)


def _safe_mtime(path: Path) -> str:
    try:
        return _iso_utc(path.stat().st_mtime)
    except OSError:
        return "unknown"


def _iso_utc(epoch: float) -> str:
    from datetime import datetime, timezone

    return datetime.fromtimestamp(epoch, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def policy_versions() -> PolicyVersions:
    """The active captured policy versions + fingerprints (pure reads of the DEFAULT_* configs)."""
    rc = DEFAULT_RUNTIME_POLICY_CONFIG
    ec = DEFAULT_EXECUTION_POLICY_CONFIG
    fm = DEFAULT_FILL_MODEL
    return PolicyVersions(
        runtime_policy_version=rc.runtime_policy_version,
        runtime_policy_fingerprint=rc.runtime_policy_fingerprint()[:16],
        execution_policy_version=ec.execution_policy_version,
        execution_policy_fingerprint=ec.fingerprint()[:16],
        fill_model_version=fm.fill_model_version,
        fill_model_fingerprint=fm.fingerprint()[:16],
    )


def recent_events(paths: OpsPaths, limit: int = 30) -> tuple[str, ...]:
    """Tail the newest daily-run log (run output + fail-closed events). Pure file read; empty if none."""
    if not paths.daily_log_dir.exists():
        return ()
    logs = sorted(paths.daily_log_dir.glob("daily_chain_run_*.log"))
    if not logs:
        return ()
    try:
        lines = logs[-1].read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        return (f"[error reading {logs[-1].name}: {exc}]",)
    header = f"--- {logs[-1].name} (last {min(limit, len(lines))} of {len(lines)}) ---"
    return (header, *tuple(line.rstrip() for line in lines[-limit:]))


def pipeline_status(
    ledger: LedgerView,
    portfolio: PortfolioView,
    operational: OperationalView,
) -> PipelineStatus:
    """Aggregate overall health from the sub-views. ``paper_only`` is ALWAYS True (ADR-013 §5)."""
    errors = tuple(
        e for e in (ledger.error, portfolio.error, operational.error) if e is not None
    )
    if errors:
        health = "error"
    elif not ledger.exists and not portfolio.exists:
        health = "no-state"
    elif not operational.tradeable:
        health = "degraded"
    else:
        health = "ok"
    headline = (
        f"paper-only | {health} | ledger={ledger.entry_count} "
        f"verdict={ledger.latest_verdict or '-'} positions={portfolio.open_position_count}"
    )
    return PipelineStatus(
        paper_only=True,
        health=health,
        headline=headline,
        ledger_entries=ledger.entry_count,
        open_positions=portfolio.open_position_count,
        latest_verdict=ledger.latest_verdict,
        errors=errors,
    )


def assemble_dashboard(
    paths: OpsPaths | None = None,
    *,
    task_fetcher: TaskInfoFetcher | None = None,
    event_limit: int = 30,
) -> Dashboard:
    """Assemble the full read-only dashboard in one pass (the TUI calls this per refresh).

    Pure: reads artefacts + runs the pure preview; never mutates state, never opens a network connection.
    ``task_fetcher`` is injectable so the scheduled-task read is testable without spawning PowerShell;
    when ``None`` the daily-task row is reported ``not-queried`` (the cheap auto-refresh path).
    """
    p = paths if paths is not None else OpsPaths.default()
    ledger = ledger_view(p)
    portfolio = portfolio_view(p)
    operational = operational_view(p)
    calibration = calibration_readiness(p)
    return Dashboard(
        pipeline=pipeline_status(ledger, portfolio, operational),
        ledger=ledger,
        portfolio=portfolio,
        operational=operational,
        preview=decision_preview(p),
        gates=gate_board(calibration),
        calibration=calibration,
        plugs=plug_statuses(),
        processes=process_infos(p, task_fetcher),
        policy=policy_versions(),
        events=recent_events(p, event_limit),
        audit_tail=tuple(e.line() for e in read_audit(p.audit_log_path, event_limit)),
    )


def render_text_dashboard(dash: Dashboard) -> Sequence[str]:
    """A plain-text rendering of the dashboard — used by tests and a ``--once`` headless dump.

    Kept here (not in ``ops.app``) so it is importable and testable without Textual.
    """
    lines: list[str] = []
    lines.append(f"PIPELINE: {dash.pipeline.headline}")
    if dash.pipeline.errors:
        lines.append(f"  errors: {' | '.join(dash.pipeline.errors)}")
    lines.append("")
    lines.append(
        f"PREVIEW (latest snapshot): regime={dash.preview.regime} "
        f"direction={dash.preview.direction} verdict={dash.preview.verdict} fill={dash.preview.fill}"
    )
    for go in dash.preview.guards:
        lines.append(f"  guard {go.name}: passed={go.passed} ({go.reason})")
    lines.append("")
    lines.append(f"CALIBRATION: {dash.calibration.overall}  (N={dash.calibration.n_committed})")
    for gr in dash.calibration.per_gate:
        lines.append(f"  {gr.gate_id} {gr.title}: {gr.status} - {gr.detail}")
    lines.append("")
    lines.append("PLUGS:")
    for plug in dash.plugs:
        lines.append(f"  {plug.name}: {plug.status}")
    lines.append("")
    lines.append("PROCESSES:")
    for proc in dash.processes:
        lines.append(f"  {proc.name}: {proc.status} - {proc.detail}")
    return tuple(lines)
