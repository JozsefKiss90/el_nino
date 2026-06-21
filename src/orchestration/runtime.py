"""IO shell + replay driver + CLI for the chain orchestrator (MOD-010).

The ONLY IO in the orchestrator lives here (mirrors the MOD-007 / MOD-008 ``runtime.py`` shells): load
the snapshot file + the prior ledger + the prior portfolio, run the pure ``run_chain`` core, then
persist the new ledger + portfolio atomically (temp-file + ``os.replace``, reusing each layer's own
persister). ``run_sequence`` threads the ledger + portfolio in memory over an ordered list of snapshots
— the deterministic replay / BENCH-006 vehicle, with **no IO**.

Crash-consistency: the shell persists the **portfolio first, then the ledger**. A crash between the two
leaves a "redo" state — the ledger lacks the ADMIT, so a re-run re-admits, but the portfolio's
``has_execution`` once-ever guard prevents a double-fill. (Ledger-first could strand an
admitted-but-never-filled snapshot, since ``duplicate_ok`` would then skip it forever.)
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path
from typing import Union

from execution.config import (
    DEFAULT_EXECUTION_POLICY_CONFIG,
    DEFAULT_FILL_MODEL,
    ExecutionPolicyConfig,
    FillModelConfig,
)
from execution.adapters import ExecutionPort, SimulatedBrokerAdapter
from execution.models import PortfolioState
from execution.runtime import load_portfolio, persist_portfolio
from gold.decision_builder.config import DecisionPolicyConfig
from gold.paper_runtime.config import DEFAULT_RUNTIME_POLICY_CONFIG, RuntimePolicyConfig
from gold.paper_runtime.models import OperationalInput, RuntimeLedger
from gold.paper_runtime.runtime import load_ledger, persist_ledger
from regime.regime_classifier.config import RegimeConfig
from risk.guardrail_engine.guardrail_engine import load_config_from_env
from risk.guardrail_engine.models import GuardrailConfig
from snapshot.snapshot_consumer import consume

from .config import DEFAULT_GUARD_CONFIG, DEFAULT_OPERATIONAL_INPUT
from .engine import run_chain
from .models import ChainResult
from .operational_feed import MarketCalendarFeed, OperationalFeed, read_and_capture

PathLike = Union[str, Path]

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_SNAPSHOT = _REPO_ROOT / "snapshot_sources" / "latest_snapshot.json"
_DEFAULT_LEDGER = _REPO_ROOT / "runtime" / "chain" / "runtime_ledger.json"
_DEFAULT_PORTFOLIO = _REPO_ROOT / "runtime" / "chain" / "portfolio_state.json"
_DEFAULT_OP_CAPTURE = _REPO_ROOT / "runtime" / "chain" / "operational_capture.json"
_DEFAULT_PORT: ExecutionPort = SimulatedBrokerAdapter()


def find_latest_snapshot(directory: PathLike) -> Path | None:
    """The lexicographically-latest ``snapshot_<clock_date>__<id8>.json`` in ``directory`` (or None).

    The archive naming (EPOCH_B_CORPUS_RUNBOOK.md §2) sorts by ``clock_date`` lexicographically, so the
    last entry is the most recent banked day. The ``latest_snapshot.json`` *pointer* and the bare
    ``snapshot.json`` are deliberately not matched (only dated archive files).
    """
    candidates = sorted(Path(directory).glob("snapshot_*.json"))
    return candidates[-1] if candidates else None


def run_once(
    snapshot_path: PathLike,
    ledger_path: PathLike,
    portfolio_path: PathLike,
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
    port: ExecutionPort = _DEFAULT_PORT,
) -> ChainResult | None:
    """Single-step operational entrypoint: load state → ``run_chain`` → persist atomically.

    Returns ``None`` when the snapshot is not consumable (the MOD-003 *"Layer-3 outputs nothing"*
    contract — absent / failed-gate / forced / dry-run). A structurally malformed snapshot raises
    ``SnapshotContractError`` via ``consume``; a corrupt ledger / portfolio raises loudly via their
    loaders.

    **Live operational feed (IO path only).** When ``operational_feed`` is given, the venue's
    ``OperationalInput`` is read from the feed at the snapshot's ``clock_ts`` and **captured** to
    ``operational_capture_path`` (the replay source), overriding the passed ``operational_input``. The
    feed read happens **only here** (never in ``run_sequence`` / replay) — the §2 / gate-f quarantine.
    """
    snapshot = consume(snapshot_path)
    if snapshot is None:
        return None
    if operational_feed is not None:
        operational_input = read_and_capture(
            operational_feed, snapshot.clock_ts, operational_capture_path
        )
    prior_ledger = load_ledger(ledger_path)
    prior_portfolio = load_portfolio(portfolio_path)
    result = run_chain(
        snapshot,
        prior_ledger,
        prior_portfolio,
        operational_input=operational_input,
        guard_config=guard_config,
        runtime_config=runtime_config,
        regime_config=regime_config,
        decision_config=decision_config,
        exec_config=exec_config,
        fill_model=fill_model,
        port=port,
    )
    # Portfolio first, then ledger (crash-consistency — see module docstring). Each is atomic.
    persist_portfolio(portfolio_path, result.portfolio)
    persist_ledger(ledger_path, result.ledger)
    return result


def run_sequence(
    snapshots: Sequence[object],
    *,
    operational_input: OperationalInput = DEFAULT_OPERATIONAL_INPUT,
    guard_config: GuardrailConfig = DEFAULT_GUARD_CONFIG,
    runtime_config: RuntimePolicyConfig = DEFAULT_RUNTIME_POLICY_CONFIG,
    regime_config: RegimeConfig | None = None,
    decision_config: DecisionPolicyConfig | None = None,
    exec_config: ExecutionPolicyConfig = DEFAULT_EXECUTION_POLICY_CONFIG,
    fill_model: FillModelConfig = DEFAULT_FILL_MODEL,
    port: ExecutionPort = _DEFAULT_PORT,
    ledger: RuntimeLedger | None = None,
    portfolio: PortfolioState | None = None,
) -> tuple[tuple[ChainResult, ...], RuntimeLedger, PortfolioState]:
    """Thread the ledger + portfolio over an ordered list of (already-loaded) snapshots — pure, no IO.

    Deterministic order = input order. The vehicle for determinism tests + BENCH-006: replaying the
    same snapshot sequence from the same starting ledger + portfolio yields byte-identical records and
    identical ending ledger + portfolio ``state_hash``es. ``snapshots`` are ``Snapshot`` objects (typed
    ``object`` to avoid importing the snapshot model here; ``run_chain`` enforces the real type).
    """
    led = ledger if ledger is not None else RuntimeLedger.empty()
    pf = portfolio if portfolio is not None else PortfolioState.empty()
    results: list[ChainResult] = []
    for snapshot in snapshots:
        result = run_chain(
            snapshot,  # type: ignore[arg-type]  # Snapshot — kept un-imported here (see docstring)
            led,
            pf,
            operational_input=operational_input,
            guard_config=guard_config,
            runtime_config=runtime_config,
            regime_config=regime_config,
            decision_config=decision_config,
            exec_config=exec_config,
            fill_model=fill_model,
            port=port,
        )
        led, pf = result.ledger, result.portfolio
        results.append(result)
    return tuple(results), led, pf


def _summarize(result: ChainResult) -> str:
    """One-line operational summary of a run (deterministic; for the CLI only)."""
    rec = result.runtime_record
    ex = result.execution_record
    fill = "no-fill" if ex is None or ex.fill is None else f"fill@{ex.fill.fill_price:g}"
    exec_part = "no-exec (not ADMIT)" if ex is None else f"{ex.execution_mode.value} {ex.reason} ({fill})"
    return (
        f"snapshot={rec.source_snapshot_id[:12]} regime={result.packet.regime} "
        f"direction={result.packet.direction.value} verdict={rec.verdict.value}"
        f"{'' if rec.triggered_guard is None else ' guard=' + rec.triggered_guard} | {exec_part} | "
        f"ledger={result.ledger.state_hash()[:12]} portfolio={result.portfolio.state_hash()[:12]}"
    )


def main(argv: Sequence[str] | None = None) -> int:
    """CLI: run the latest banked consumable snapshot through ``run_once`` and persist."""
    parser = argparse.ArgumentParser(
        prog="orchestration.runtime",
        description="Run a banked Layer-2 snapshot through the full Layer-3 chain (paper-only).",
    )
    parser.add_argument("--snapshot", default=str(_DEFAULT_SNAPSHOT),
                        help="consumable snapshot file (default: el_nino latest pointer)")
    parser.add_argument("--snapshot-dir", default=None,
                        help="if given, run the latest snapshot_*.json archive in this directory")
    parser.add_argument("--ledger", default=str(_DEFAULT_LEDGER), help="runtime ledger path")
    parser.add_argument("--portfolio", default=str(_DEFAULT_PORTFOLIO), help="portfolio state path")
    parser.add_argument("--guard-from-env", action="store_true",
                        help="load GATE-001 hard limits from env (fail-closed) instead of the captured default")
    parser.add_argument("--operational-feed", action="store_true",
                        help="read operational status from a live operational feed (captured for replay)")
    parser.add_argument("--operational-feed-source", choices=("calendar", "alpaca"), default="calendar",
                        help="feed source when --operational-feed is set: 'calendar' (deterministic, "
                             "default) or 'alpaca' (live paper clock/calendar; default-OFF; env creds; "
                             "fail-closed). Closes the holiday-calendar gap; never reaches replay.")
    parser.add_argument("--operational-capture", default=str(_DEFAULT_OP_CAPTURE),
                        help="where to capture the produced OperationalInput (the replay source)")
    args = parser.parse_args(argv)

    if args.snapshot_dir is not None:
        latest = find_latest_snapshot(args.snapshot_dir)
        if latest is None:
            print(f"no snapshot_*.json found in {args.snapshot_dir}; nothing to do")
            return 0
        snapshot_path: PathLike = latest
    else:
        snapshot_path = args.snapshot

    guard_config = load_config_from_env() if args.guard_from_env else DEFAULT_GUARD_CONFIG
    feed: OperationalFeed | None = None
    capture: PathLike | None = None
    if args.operational_feed:
        if args.operational_feed_source == "alpaca":
            # Live, non-replayable plug — imported only on explicit opt-in (keeps the default graph
            # network-free). Fail-closed: no/non-paper creds ⇒ a feed that yields closed().
            from .alpaca_clock_feed import clock_feed_from_env
            feed = clock_feed_from_env()
        else:
            feed = MarketCalendarFeed()
        capture = args.operational_capture

    result = run_once(
        snapshot_path, args.ledger, args.portfolio, guard_config=guard_config,
        operational_feed=feed, operational_capture_path=capture,
    )
    if result is None:
        print(f"snapshot {snapshot_path} is not consumable; nothing to do (Layer-3 outputs nothing)")
        return 0
    print(_summarize(result))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
