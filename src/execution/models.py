"""Execution layer contracts (SCHEMA-014 + SCHEMA-015) — the execution layer's output models.

The execution layer *acts on* an ADMIT ``RuntimeDecisionRecord`` (SCHEMA-012): it produces a (paper)
``ExecutionRecord`` (SCHEMA-014) + a new ``PortfolioState`` (SCHEMA-015). It **wraps** the ADMIT
record by reference (``source_record_id``) — never mutates it (the ADR-009 §2 wrap discipline).

Determinism (ADR-011 §2): state is an explicit value; the portfolio is **self-describing** +
**append-only**; ``execution_id`` binds the prior portfolio ``state_hash()``. ``instrument_price`` is
re-derived from ``source_snapshot_id`` by the orchestrator (ADR-011 D1) and persisted here, so the
record reproduces without touching the frozen pure chain. ``paper_only`` (ADR-011 §3): a
simulated/virtual-money fill, never a live order. Per ADR-003: stdlib frozen dataclasses, zero
runtime dependencies.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

from gold.decision_builder.models import Direction

EXECUTION_SCHEMA_VERSION = "0.1.0"
# 0.2.0 (ADR-014 §5.2): additive ``as_of`` on ExecutionEntry (day-scopes the guard's daily inputs).
# Additive + versioned — older portfolios load via from_dict (as_of defaults None); the version string
# folds into state_hash + the replay key, so the execution + chain benchmarks re-pin for this change.
PORTFOLIO_SCHEMA_VERSION = "0.2.0"
# Prices / sizes / P&L are rounded at serialization to neutralize float-format drift (the gold
# layer's 6-dp convention) so state_hash() and to_dict() are byte-stable across replays.
_PRECISION = 6

NON_EXECUTION_NOTICE = (
    "PAPER EXECUTION — a simulated / virtual-money fill, never a live order, "
    "broker instruction, or execution command (ADR-011)."
)


class ExecutionContractError(ValueError):
    """An execution artifact (record / portfolio / fill) violates its contract."""


class ExecutionMode(str, Enum):
    """Which adapter produced a record — the determinism boundary (ADR-011 §2)."""

    SIMULATED = "simulated"        # deterministic, replay-safe (the canonical core path)
    ALPACA_PAPER = "alpaca_paper"  # live virtual-money adapter — non-replayable (deferred, gate f)


class ExecutionStatus(str, Enum):
    """Live execution state-machine status (SCHEMA-014 additive, ADR-014 §6).

    The live (non-replayable) Alpaca path's async order lifecycle, representable on the record. The
    deterministic sim/replay path leaves ``status`` None (it expresses outcome via ``fill`` / ``reason``)
    so its records + benchmark goldens stay byte-identical.
    """

    QUEUED = "queued"                            # accepted/pending_new/new — async; fill resolved on reconcile
    PARTIAL = "partial"                          # filled_qty < requested — corrected on the next reconcile
    FILLED = "filled"                            # fully filled — resolved from positions/orders, not the POST echo
    EXECUTION_UNCERTAIN = "execution_uncertain"  # timeout/reject/429/auth — halt the instrument, no blind retry
    NO_ACTION = "no_action"                      # nothing to do (delta nets to zero / idempotent duplicate)


# --- guard provenance (forwarded from GATE-001) ---------------------------------------------


@dataclass(frozen=True)
class GuardResult:
    """The GATE-001 outcome, forwarded onto the execution layer as provenance (ADR-011 gate c).

    A plain DTO: the execution core never imports ``src/risk``; the orchestrator maps the risk
    engine's ``TradeValidationDecision`` into this. Fail-closed invariant mirrors that decision —
    ``approved`` ⇔ no blocking predicate.
    """

    approved: bool
    blocked_by: str | None
    reason: str

    def __post_init__(self) -> None:
        if self.approved and self.blocked_by is not None:
            raise ExecutionContractError("an approved guard_result must not name a blocking predicate")
        if not self.approved and self.blocked_by is None:
            raise ExecutionContractError("a blocked guard_result must name its blocking predicate")

    def to_dict(self) -> dict[str, Any]:
        return {"approved": self.approved, "blocked_by": self.blocked_by, "reason": self.reason}


# --- fill -----------------------------------------------------------------------------------


@dataclass(frozen=True)
class Fill:
    """A (paper) fill — deterministically simulated, or echoed from the paper broker (logging)."""

    fill_price: float
    quantity: float
    slippage_bps: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "fill_price": round(self.fill_price, _PRECISION),
            "quantity": round(self.quantity, _PRECISION),
            "slippage_bps": round(self.slippage_bps, _PRECISION),
        }


# --- portfolio / position state (SCHEMA-015) ------------------------------------------------


@dataclass(frozen=True)
class Position:
    """Per-instrument paper position; ``unrealized_pnl`` is mark-to-snapshot (ADR-011 D1)."""

    instrument: str
    quantity: float
    avg_cost: float
    realized_pnl: float
    unrealized_pnl: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "avg_cost": round(self.avg_cost, _PRECISION),
            "instrument": self.instrument,
            "quantity": round(self.quantity, _PRECISION),
            "realized_pnl": round(self.realized_pnl, _PRECISION),
            "unrealized_pnl": round(self.unrealized_pnl, _PRECISION),
        }

    @classmethod
    def from_dict(cls, d: Mapping[str, Any]) -> "Position":
        if not isinstance(d, Mapping):
            raise ExecutionContractError("position must be a mapping")
        try:
            return cls(
                instrument=str(d["instrument"]),
                quantity=float(d["quantity"]),
                avg_cost=float(d["avg_cost"]),
                realized_pnl=float(d["realized_pnl"]),
                unrealized_pnl=float(d["unrealized_pnl"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ExecutionContractError(f"malformed position: {exc}") from exc


@dataclass(frozen=True)
class ExecutionEntry:
    """A self-describing record of one applied execution (the ADR-009 §5 ledger idiom)."""

    source_snapshot_id: str
    source_record_id: str
    instrument: str
    fill_price: float
    quantity: float
    fill_model_version: str
    prior_portfolio_state_hash: str
    seq: int
    # Snapshot clock of the admitting decision (SCHEMA-015 additive, ADR-014 §5.2). Day-scopes the
    # guard's ``trades_today`` so ``max_trades_per_day`` resets per trading day. Defaults None so older
    # persisted entries load unchanged.
    as_of: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "as_of": self.as_of,
            "fill_model_version": self.fill_model_version,
            "fill_price": round(self.fill_price, _PRECISION),
            "instrument": self.instrument,
            "prior_portfolio_state_hash": self.prior_portfolio_state_hash,
            "quantity": round(self.quantity, _PRECISION),
            "seq": self.seq,
            "source_record_id": self.source_record_id,
            "source_snapshot_id": self.source_snapshot_id,
        }

    @classmethod
    def from_dict(cls, d: Mapping[str, Any]) -> "ExecutionEntry":
        if not isinstance(d, Mapping):
            raise ExecutionContractError("execution entry must be a mapping")
        try:
            return cls(
                source_snapshot_id=str(d["source_snapshot_id"]),
                source_record_id=str(d["source_record_id"]),
                instrument=str(d["instrument"]),
                fill_price=float(d["fill_price"]),
                quantity=float(d["quantity"]),
                fill_model_version=str(d["fill_model_version"]),
                prior_portfolio_state_hash=str(d["prior_portfolio_state_hash"]),
                seq=int(d["seq"]),
                as_of=(str(d["as_of"]) if d.get("as_of") is not None else None),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ExecutionContractError(f"malformed execution entry: {exc}") from exc


@dataclass(frozen=True)
class ReconcileEntry:
    """A LIVE-path append-only reconcile observation (SCHEMA-015 new kind, ADR-014 §6.2).

    Distinct from :class:`ExecutionEntry`: a reconcile observation records what the *broker* shows
    (the authority for position truth) — the observed quantity + average entry price + a ``marker``
    saying why it was recorded — and is **not** a fill the system placed, so it carries **no**
    ``source_record_id`` and **no** ``guard_result``. It heals a broker↔local divergence into the
    append-only history *without faking an execution record*; adopting the observed position into the
    local position is a separate ops-console **governed adopt**, never automatic (ADR-014 §6.2).

    **Live-path-only / determinism trick.** The deterministic sim/replay portfolio never produces a
    reconcile entry, and :meth:`PortfolioState.to_dict` **omits an empty** ``reconciles`` list, so the
    sim/replay portfolio's ``to_dict`` / ``state_hash`` stay byte-identical — no
    ``PORTFOLIO_SCHEMA_VERSION`` bump, no BENCH-004/006 re-pin.
    """

    source_snapshot_id: str    # the snapshot during whose reconcile this was observed (run lineage)
    instrument: str
    observed_qty: float        # the broker position quantity (authority for position truth)
    observed_avg_price: float  # the broker position average entry price
    marker: str                # why this was recorded (e.g. "discrepancy:unexpected_open_order")
    seq: int
    # Snapshot clock of the reconcile (mirrors ``ExecutionEntry.as_of``). Defaults None so a hand-built
    # or older entry loads unchanged.
    as_of: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "as_of": self.as_of,
            "instrument": self.instrument,
            "marker": self.marker,
            "observed_avg_price": round(self.observed_avg_price, _PRECISION),
            "observed_qty": round(self.observed_qty, _PRECISION),
            "seq": self.seq,
            "source_snapshot_id": self.source_snapshot_id,
        }

    @classmethod
    def from_dict(cls, d: Mapping[str, Any]) -> "ReconcileEntry":
        if not isinstance(d, Mapping):
            raise ExecutionContractError("reconcile entry must be a mapping")
        try:
            return cls(
                source_snapshot_id=str(d["source_snapshot_id"]),
                instrument=str(d["instrument"]),
                observed_qty=float(d["observed_qty"]),
                observed_avg_price=float(d["observed_avg_price"]),
                marker=str(d["marker"]),
                seq=int(d["seq"]),
                as_of=(str(d["as_of"]) if d.get("as_of") is not None else None),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ExecutionContractError(f"malformed reconcile entry: {exc}") from exc


@dataclass(frozen=True)
class PendingOrder:
    """A LIVE-path in-flight order awaiting a cross-run async fill (SCHEMA-015 new kind, ADR-014 §6.3).

    A market+day order submitted in run *N* can be ``accepted``/``new`` (QUEUED) at submit and fill
    **after** the run ends (queue-to-next-open, or a slow paper fill). The synchronous QUEUED record
    carries the order↔snapshot lineage, but the per-run :class:`ExecutionRecord` is not itself persisted,
    so this entry is the **durable order↔snapshot lineage** the next startup reconcile needs to fold the
    fill back into the local position **exactly once** (the docstring follow-up the v1 entrypoint deferred
    is closed by this kind). It carries the deterministic ``client_order_id`` (so ``resolve_fill`` can
    find the broker order), the submitting ``side``, the ``requested_qty`` (0.0 for a notional order), and
    the originating snapshot/record ids + ``as_of`` (so the folded :class:`ExecutionEntry` keeps full
    lineage). Removed when the fill is folded (or the order is found terminally gone).

    **Live-path-only / determinism trick** (identical to :class:`ReconcileEntry`): the deterministic
    sim/replay portfolio never queues an async order, and :meth:`PortfolioState.to_dict` **omits an empty**
    ``pending`` list, so the sim/replay portfolio's ``to_dict`` / ``state_hash`` stay byte-identical — no
    ``PORTFOLIO_SCHEMA_VERSION`` bump, no BENCH-004/006 re-pin.
    """

    source_snapshot_id: str
    source_record_id: str
    instrument: str
    side: str            # "buy" | "sell" — which fold the fill resolves to
    requested_qty: float  # the submitted share qty (0.0 for a fractionable notional order)
    client_order_id: str  # the deterministic id the broker order carries (the reconcile lookup key)
    seq: int
    # Snapshot clock of the submitting decision (mirrors ``ExecutionEntry.as_of``). Defaults None.
    as_of: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "as_of": self.as_of,
            "client_order_id": self.client_order_id,
            "instrument": self.instrument,
            "requested_qty": round(self.requested_qty, _PRECISION),
            "seq": self.seq,
            "side": self.side,
            "source_record_id": self.source_record_id,
            "source_snapshot_id": self.source_snapshot_id,
        }

    @classmethod
    def from_dict(cls, d: Mapping[str, Any]) -> "PendingOrder":
        if not isinstance(d, Mapping):
            raise ExecutionContractError("pending order must be a mapping")
        try:
            return cls(
                source_snapshot_id=str(d["source_snapshot_id"]),
                source_record_id=str(d["source_record_id"]),
                instrument=str(d["instrument"]),
                side=str(d["side"]),
                requested_qty=float(d["requested_qty"]),
                client_order_id=str(d["client_order_id"]),
                seq=int(d["seq"]),
                as_of=(str(d["as_of"]) if d.get("as_of") is not None else None),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ExecutionContractError(f"malformed pending order: {exc}") from exc


def _replace_position(positions: tuple[Position, ...], new: Position) -> tuple[Position, ...]:
    """Return the positions with ``new`` replacing any prior position for its instrument."""
    others = tuple(p for p in positions if p.instrument != new.instrument)
    return tuple(sorted((*others, new), key=lambda p: p.instrument))


@dataclass(frozen=True)
class PortfolioState:
    """Append-only, deterministically-serialized portfolio/position state (SCHEMA-015).

    Both an input and an output of ``execute()`` (the layer threads ``prior -> new``), making the
    stateful execution layer a pure function of explicit values. The ``executions`` history is
    keyed by ``source_snapshot_id`` (the once-ever idempotency key).
    """

    portfolio_schema_version: str
    positions: tuple[Position, ...]
    executions: tuple[ExecutionEntry, ...]
    # LIVE-path-only reconcile observations (ADR-014 §6.2). Defaults empty so every existing positional
    # construction stays valid, and ``to_dict`` omits it while empty — the sim/replay portfolio stays
    # byte-identical (no schema bump / no benchmark re-pin). See :class:`ReconcileEntry`.
    reconciles: tuple[ReconcileEntry, ...] = ()
    # LIVE-path-only in-flight orders awaiting a cross-run async fill (ADR-014 §6.3). Same determinism
    # trick as ``reconciles``: defaults empty (every positional construction stays valid) and ``to_dict``
    # omits it while empty, so the sim/replay portfolio stays byte-identical. See :class:`PendingOrder`.
    pending: tuple[PendingOrder, ...] = ()

    @classmethod
    def empty(cls) -> "PortfolioState":
        return cls(portfolio_schema_version=PORTFOLIO_SCHEMA_VERSION, positions=(), executions=())

    def position(self, instrument: str) -> Position | None:
        return next((p for p in self.positions if p.instrument == instrument), None)

    def has_execution(self, snapshot_id: str) -> bool:
        """True iff a prior execution already filled this ``snapshot_id`` (once-ever idempotency)."""
        return any(e.source_snapshot_id == snapshot_id for e in self.executions)

    def next_seq(self) -> int:
        """Length-derived insertion index — stable across load/persist/reload cycles."""
        return len(self.executions)

    def next_reconcile_seq(self) -> int:
        """Length-derived insertion index for reconcile entries (the live-path append-only history)."""
        return len(self.reconciles)

    def next_pending_seq(self) -> int:
        """Length-derived insertion index for pending (in-flight) orders (the live-path queue lineage)."""
        return len(self.pending)

    def append(self, position: Position, entry: ExecutionEntry) -> "PortfolioState":
        """Return a NEW portfolio with ``position`` updated and ``entry`` appended (immutable)."""
        return PortfolioState(
            self.portfolio_schema_version,
            _replace_position(self.positions, position),
            (*self.executions, entry),
            self.reconciles,
            self.pending,
        )

    def append_reconcile(self, entry: ReconcileEntry) -> "PortfolioState":
        """Return a NEW portfolio with a reconcile observation appended (LIVE-path-only, ADR-014 §6.2).

        Positions and executions are left **unchanged** — a reconcile records the broker's observed
        state but never auto-adopts it into the local position (adoption is a separate governed action).
        """
        return PortfolioState(
            self.portfolio_schema_version,
            self.positions,
            self.executions,
            (*self.reconciles, entry),
            self.pending,
        )

    def append_pending(self, order: PendingOrder) -> "PortfolioState":
        """Return a NEW portfolio with an in-flight (QUEUED) order recorded (LIVE-path-only, ADR-014 §6.3).

        Positions and executions are unchanged — the order has not filled yet; the next startup reconcile
        folds the fill (and removes the pending order) via :meth:`with_pending`. See :class:`PendingOrder`.
        """
        return PortfolioState(
            self.portfolio_schema_version,
            self.positions,
            self.executions,
            self.reconciles,
            (*self.pending, order),
        )

    def with_pending(self, pending: tuple[PendingOrder, ...]) -> "PortfolioState":
        """Return a NEW portfolio with the in-flight-order list replaced (LIVE-path-only, ADR-014 §6.3).

        Used by the cross-run fold to drop a now-resolved order (compose with :meth:`append` to book the
        folded fill in one immutable step). Positions/executions/reconciles are otherwise unchanged.
        """
        return PortfolioState(
            self.portfolio_schema_version,
            self.positions,
            self.executions,
            self.reconciles,
            pending,
        )

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "executions": [e.to_dict() for e in self.executions],
            "portfolio_schema_version": self.portfolio_schema_version,
            "positions": [
                p.to_dict() for p in sorted(self.positions, key=lambda p: p.instrument)
            ],
        }
        # Omit the live-path reconcile history when empty so the sim/replay portfolio's serialization +
        # ``state_hash`` stay byte-identical to the pre-ADR-014 form (the determinism trick, §6.2).
        if self.reconciles:
            d["reconciles"] = [r.to_dict() for r in self.reconciles]
        # Same trick for the live-path in-flight orders (§6.3): omitted while empty (always on the sim
        # path), so a portfolio that never queues an async order serializes byte-identically.
        if self.pending:
            d["pending"] = [p.to_dict() for p in self.pending]
        return d

    def state_hash(self) -> str:
        """SHA-256 over canonical JSON — the portfolio identity (threads into execution_id)."""
        payload = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @classmethod
    def from_dict(cls, d: Mapping[str, Any]) -> "PortfolioState":
        if not isinstance(d, Mapping):
            raise ExecutionContractError("portfolio must be a mapping")
        raw_positions = d.get("positions", [])
        raw_executions = d.get("executions", [])
        raw_reconciles = d.get("reconciles", [])  # absent on every sim/replay portfolio (live-path-only)
        raw_pending = d.get("pending", [])        # absent on every sim/replay portfolio (live-path-only)
        if (
            not isinstance(raw_positions, list)
            or not isinstance(raw_executions, list)
            or not isinstance(raw_reconciles, list)
            or not isinstance(raw_pending, list)
        ):
            raise ExecutionContractError(
                "portfolio 'positions'/'executions'/'reconciles'/'pending' must be lists"
            )
        return cls(
            portfolio_schema_version=str(d.get("portfolio_schema_version", PORTFOLIO_SCHEMA_VERSION)),
            positions=tuple(Position.from_dict(p) for p in raw_positions),
            executions=tuple(ExecutionEntry.from_dict(e) for e in raw_executions),
            reconciles=tuple(ReconcileEntry.from_dict(r) for r in raw_reconciles),
            pending=tuple(PendingOrder.from_dict(p) for p in raw_pending),
        )


# --- execution record (SCHEMA-014) ----------------------------------------------------------


def compute_execution_id(
    source_record_id: str,
    fill_model_version: str,
    execution_policy_fingerprint: str,
    instrument_price: float,
    prior_portfolio_state_hash: str,
) -> str:
    """``exec-v0:`` + 16 hex of SHA-256 over everything that can change a record's content.

    Mirrors ``compute_record_id``. Binds the prior portfolio ``state_hash`` so the id is a
    per-execution identity (distinct from the snapshot/idempotency key, ``source_snapshot_id``).
    """
    lines = [
        f"source_record_id={source_record_id}",
        f"fill_model_version={fill_model_version}",
        f"execution_policy_fingerprint={execution_policy_fingerprint}",
        f"instrument_price={instrument_price:.{_PRECISION}f}",
        f"prior_portfolio_state_hash={prior_portfolio_state_hash}",
    ]
    payload = "\n".join(lines) + "\n"
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return f"exec-v0:{digest[:16]}"


@dataclass(frozen=True)
class ExecutionRecord:
    """The execution layer's output over one ADMIT record (SCHEMA-014).

    Wraps the ADMIT record by reference (``source_record_id``); carries the (paper) fill (or
    ``None`` when fail-closed) + the forwarded guard provenance + the determinism boundary flags.
    """

    execution_id: str
    execution_schema_version: str
    source_record_id: str
    source_snapshot_id: str
    instrument: str
    direction: Direction
    size: float
    instrument_price: float
    fill: Fill | None
    guard_result: GuardResult
    execution_mode: ExecutionMode
    replayable: bool
    fill_model_version: str
    prior_portfolio_state_hash: str
    new_portfolio_state_hash: str
    reason: str
    # exec_ref_gld_price triple (SCHEMA-014 additive, ADR-014 bucket i): the GLD *share* price the
    # record marks/slips against + its provenance. ``price`` == ``instrument_price``; ts/basis label
    # the mark (sim: snapshot clock + derived proxy; live: pinned submit/open mark). Defaults keep
    # older direct constructions valid (this is an output-only record — there is no from_dict).
    exec_ref_gld_price: float = 0.0
    exec_ref_gld_price_ts: str | None = None
    exec_ref_gld_price_basis: str = ""
    # Live state-machine status + broker traceability (SCHEMA-014 additive, ADR-014 §6). Set ONLY on
    # the live (non-replayable) path; the sim/replay path leaves them None so its records + goldens are
    # unchanged. ``raw_payload`` is the raw broker response/reject body (never silently dropped).
    status: ExecutionStatus | None = None
    client_order_id: str | None = None
    alpaca_order_id: str | None = None
    raw_payload: str | None = None
    paper_only: bool = True
    non_execution_notice: str = NON_EXECUTION_NOTICE

    def __post_init__(self) -> None:
        if not self.paper_only:
            raise ExecutionContractError("execution record must be paper_only")
        # a fill can only exist on an approved guard_result (fail-closed)
        if self.fill is not None and not self.guard_result.approved:
            raise ExecutionContractError("a fill requires an approved guard_result")

    def to_dict(self) -> dict[str, Any]:
        """Deterministic, JSON-stable dict (alphabetical keys)."""
        return {
            "alpaca_order_id": self.alpaca_order_id,
            "client_order_id": self.client_order_id,
            "direction": self.direction.value,
            "exec_ref_gld_price": round(self.exec_ref_gld_price, _PRECISION),
            "exec_ref_gld_price_basis": self.exec_ref_gld_price_basis,
            "exec_ref_gld_price_ts": self.exec_ref_gld_price_ts,
            "execution_id": self.execution_id,
            "execution_mode": self.execution_mode.value,
            "execution_schema_version": self.execution_schema_version,
            "fill": self.fill.to_dict() if self.fill is not None else None,
            "fill_model_version": self.fill_model_version,
            "guard_result": self.guard_result.to_dict(),
            "instrument": self.instrument,
            "instrument_price": round(self.instrument_price, _PRECISION),
            "new_portfolio_state_hash": self.new_portfolio_state_hash,
            "non_execution_notice": self.non_execution_notice,
            "paper_only": self.paper_only,
            "prior_portfolio_state_hash": self.prior_portfolio_state_hash,
            "raw_payload": self.raw_payload,
            "reason": self.reason,
            "replayable": self.replayable,
            "size": round(self.size, _PRECISION),
            "source_record_id": self.source_record_id,
            "source_snapshot_id": self.source_snapshot_id,
            "status": (self.status.value if self.status is not None else None),
        }
