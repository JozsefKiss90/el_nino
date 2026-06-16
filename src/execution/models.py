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
PORTFOLIO_SCHEMA_VERSION = "0.1.0"
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

    def to_dict(self) -> dict[str, Any]:
        return {
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
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ExecutionContractError(f"malformed execution entry: {exc}") from exc


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

    def append(self, position: Position, entry: ExecutionEntry) -> "PortfolioState":
        """Return a NEW portfolio with ``position`` updated and ``entry`` appended (immutable)."""
        return PortfolioState(
            self.portfolio_schema_version,
            _replace_position(self.positions, position),
            (*self.executions, entry),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "executions": [e.to_dict() for e in self.executions],
            "portfolio_schema_version": self.portfolio_schema_version,
            "positions": [
                p.to_dict() for p in sorted(self.positions, key=lambda p: p.instrument)
            ],
        }

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
        if not isinstance(raw_positions, list) or not isinstance(raw_executions, list):
            raise ExecutionContractError("portfolio 'positions'/'executions' must be lists")
        return cls(
            portfolio_schema_version=str(d.get("portfolio_schema_version", PORTFOLIO_SCHEMA_VERSION)),
            positions=tuple(Position.from_dict(p) for p in raw_positions),
            executions=tuple(ExecutionEntry.from_dict(e) for e in raw_executions),
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
            "direction": self.direction.value,
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
            "reason": self.reason,
            "replayable": self.replayable,
            "size": round(self.size, _PRECISION),
            "source_record_id": self.source_record_id,
            "source_snapshot_id": self.source_snapshot_id,
        }
