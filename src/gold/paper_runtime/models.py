"""Paper-Trading Runtime contracts (SCHEMA-012 + SCHEMA-013) — the runtime's output models.

The runtime **wraps** the pure ``GoldDecisionPacket`` (SCHEMA-011): it never mutates, re-hashes,
or re-emits the packet (ADR-009 §2). ``evaluate()`` consumes the packet + explicit runtime state
and produces a ``RuntimeDecisionRecord`` (SCHEMA-012 — the admission verdict + the evaluated
six-guard block) plus a new ``RuntimeLedger`` (SCHEMA-013). The packet stays pure; all runtime
state lives here, keyed by ``source_snapshot_id``.

Determinism (ADR-009 §4/§5): state is an explicit value; the ledger is **self-describing** and
**append-only**; ``record_id`` binds everything that can change a record's content — including the
prior ledger's ``state_hash()``. Per ADR-003: stdlib frozen dataclasses, zero runtime dependencies.
The six-guard ordering is reused from the packet module (``_GUARD_NAMES``) — a single source of
truth, never a parallel list.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

from gold.decision_builder.models import (  # the single guard-name ordering (ADR-009 §6 / plan)
    DecisionMode,
    GoldDecisionPacket,
    SnapshotGuards,
    _GUARD_NAMES,
)

RECORD_SCHEMA_VERSION = "0.1.0"
LEDGER_SCHEMA_VERSION = "0.1.0"


class RuntimeContractError(ValueError):
    """A runtime artifact (record / ledger / operational input) violates its contract."""


# --- verdict + guard outcome ----------------------------------------------------------------


class Verdict(str, Enum):
    """The runtime's admission decision over a gold packet."""

    ADMIT = "ADMIT"    # all required guards passed and the packet carries an actionable stance
    HOLD = "HOLD"      # no actionable stance (WATCH/INDETERMINATE) — nothing to admit
    REJECT = "REJECT"  # a required guard blocked admission (duplicate / operational / data)


@dataclass(frozen=True)
class GuardOutcome:
    """One guard's evaluated outcome — the single (name, passed, reason) source of truth.

    ``passed`` is ``True``/``False`` for an evaluated guard, or ``None`` for an explicit stub
    (``supervisor_ok`` — no supervisor exists in v0).
    """

    name: str
    passed: bool | None
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "passed": self.passed, "reason": self.reason}


# --- operational readiness input ------------------------------------------------------------


@dataclass(frozen=True)
class OperationalInput:
    """Explicit, versioned operational-readiness artifact (ADR-009 §3, PRED-007).

    NOT a live venue probe (Non-Goal): a deterministic, caller/file-supplied snapshot of venue
    state so ``operational_ok`` replays byte-identically. Default-closed: an absent or malformed
    input resolves to ``closed()`` (not tradeable) at the IO boundary.
    """

    instrument: str
    tradeable: bool
    venue_open: bool
    halt: bool
    degraded: bool
    as_of: str | None = None
    source_version: str = "0.1.0"

    def to_dict(self) -> dict[str, Any]:
        return {
            "as_of": self.as_of,
            "degraded": self.degraded,
            "halt": self.halt,
            "instrument": self.instrument,
            "source_version": self.source_version,
            "tradeable": self.tradeable,
            "venue_open": self.venue_open,
        }

    def fingerprint(self) -> str:
        """Deterministic content digest — threads into ``record_id`` and the ledger entry."""
        payload = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @classmethod
    def closed(cls, instrument: str = "GLD", as_of: str | None = None) -> "OperationalInput":
        """The fail-closed (not-tradeable) state — the default on absent/malformed input."""
        return cls(
            instrument=instrument,
            tradeable=False,
            venue_open=False,
            halt=True,
            degraded=True,
            as_of=as_of,
        )

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any]) -> "OperationalInput":
        """Strict, fail-closed construction (unknown keys / missing required field raise)."""
        if not isinstance(mapping, Mapping):
            raise RuntimeContractError("operational input must be a mapping")
        required = ("instrument", "tradeable", "venue_open", "halt", "degraded")
        known = {*required, "as_of", "source_version"}
        unknown = set(mapping) - known
        if unknown:
            raise RuntimeContractError(f"unknown operational input keys: {sorted(unknown)}")
        missing = [k for k in required if k not in mapping]
        if missing:
            raise RuntimeContractError(f"missing operational input keys: {missing}")
        return cls(
            instrument=str(mapping["instrument"]),
            tradeable=bool(mapping["tradeable"]),
            venue_open=bool(mapping["venue_open"]),
            halt=bool(mapping["halt"]),
            degraded=bool(mapping["degraded"]),
            as_of=(str(mapping["as_of"]) if mapping.get("as_of") is not None else None),
            source_version=str(mapping.get("source_version", "0.1.0")),
        )


# --- ledger (SCHEMA-013) --------------------------------------------------------------------


@dataclass(frozen=True)
class LedgerEntry:
    """A self-describing record of one evaluation (ADR-009 §5).

    Carries everything needed to reproduce its own decision: the snapshot-guards digest, the
    operational fingerprint, ``as_of``, the verdict + triggering guard, and a length-derived
    ``seq``. The ledger of these entries is sufficient replay state on its own.
    """

    source_snapshot_id: str
    source_packet_id: str
    as_of: str | None
    verdict: str
    triggered_guard: str | None
    snapshot_guards_digest: str
    operational_fingerprint: str
    seq: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "as_of": self.as_of,
            "operational_fingerprint": self.operational_fingerprint,
            "seq": self.seq,
            "snapshot_guards_digest": self.snapshot_guards_digest,
            "source_packet_id": self.source_packet_id,
            "source_snapshot_id": self.source_snapshot_id,
            "triggered_guard": self.triggered_guard,
            "verdict": self.verdict,
        }

    @classmethod
    def from_dict(cls, d: Mapping[str, Any]) -> "LedgerEntry":
        if not isinstance(d, Mapping):
            raise RuntimeContractError("ledger entry must be a mapping")
        try:
            return cls(
                source_snapshot_id=str(d["source_snapshot_id"]),
                source_packet_id=str(d["source_packet_id"]),
                as_of=(str(d["as_of"]) if d.get("as_of") is not None else None),
                verdict=str(d["verdict"]),
                triggered_guard=(
                    str(d["triggered_guard"]) if d.get("triggered_guard") is not None else None
                ),
                snapshot_guards_digest=str(d["snapshot_guards_digest"]),
                operational_fingerprint=str(d["operational_fingerprint"]),
                seq=int(d["seq"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise RuntimeContractError(f"malformed ledger entry: {exc}") from exc


@dataclass(frozen=True)
class RuntimeLedger:
    """Append-only, deterministically-serialized dedup/admission state (SCHEMA-013)."""

    ledger_schema_version: str
    entries: tuple[LedgerEntry, ...]

    @classmethod
    def empty(cls) -> "RuntimeLedger":
        return cls(ledger_schema_version=LEDGER_SCHEMA_VERSION, entries=())

    def has_admit(self, snapshot_id: str) -> bool:
        """True iff a prior entry ADMITted this ``snapshot_id`` (the once-ever dedup key).

        Only prior ADMITs count — a prior HOLD/REJECT did NOT "produce a packet", so it does
        not block a later genuine admission (PRED-006).
        """
        return any(
            e.source_snapshot_id == snapshot_id and e.verdict == Verdict.ADMIT.value
            for e in self.entries
        )

    def last_admit_as_of(self, exclude_snapshot_id: str | None = None) -> str | None:
        """The ``as_of`` of the most recent ADMIT entry (by append order), excluding one snapshot_id.

        Reads only existing entry fields (no schema change) — the time source for the computed
        cooldown guard (PRED-008). ``exclude_snapshot_id`` is the current snapshot, so an exact
        re-presentation does not cool down against its own prior ADMIT (that is ``duplicate_ok``'s
        job). Returns ``None`` when there is no qualifying prior ADMIT.
        """
        for entry in reversed(self.entries):
            if entry.verdict == Verdict.ADMIT.value and entry.source_snapshot_id != exclude_snapshot_id:
                return entry.as_of
        return None

    def next_seq(self) -> int:
        """Length-derived insertion index — stable across load/persist/reload cycles."""
        return len(self.entries)

    def append(self, entry: LedgerEntry) -> "RuntimeLedger":
        """Return a NEW ledger with ``entry`` appended (immutability — never mutate in place)."""
        return RuntimeLedger(self.ledger_schema_version, (*self.entries, entry))

    def to_dict(self) -> dict[str, Any]:
        return {
            "entries": [e.to_dict() for e in self.entries],
            "ledger_schema_version": self.ledger_schema_version,
        }

    def state_hash(self) -> str:
        """SHA-256 over the canonical JSON — the ledger's identity (threads into record_id)."""
        payload = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @classmethod
    def from_dict(cls, d: Mapping[str, Any]) -> "RuntimeLedger":
        if not isinstance(d, Mapping):
            raise RuntimeContractError("ledger must be a mapping")
        raw_entries = d.get("entries", [])
        if not isinstance(raw_entries, list):
            raise RuntimeContractError("ledger 'entries' must be a list")
        entries = tuple(LedgerEntry.from_dict(e) for e in raw_entries)
        return cls(
            ledger_schema_version=str(d.get("ledger_schema_version", LEDGER_SCHEMA_VERSION)),
            entries=entries,
        )


# --- decision record (SCHEMA-012) -----------------------------------------------------------


def digest_snapshot_guards(packet: GoldDecisionPacket) -> str:
    """Deterministic digest of the packet's forwarded L1 snapshot-guard provenance (or null)."""
    sg: SnapshotGuards | None = packet.snapshot_guards
    payload = json.dumps(
        sg.to_dict() if sg is not None else None, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def compute_record_id(
    source_packet_id: str,
    runtime_policy_fingerprint: str,
    as_of: str | None,
    operational_fingerprint: str,
    snapshot_guards_digest: str,
    prior_ledger_state_hash: str,
) -> str:
    """``paper-v0:`` + 16 hex of SHA-256 over everything that can change a record's content.

    Mirrors ``compute_packet_id``. Binding the prior ledger ``state_hash`` makes the record a
    per-evaluation identity (distinct from the snapshot/idempotency key, which is
    ``source_snapshot_id``) — the runtime analogue of the packet-id collision the wrap closes.
    """
    lines = [
        f"source_packet_id={source_packet_id}",
        f"runtime_policy_fingerprint={runtime_policy_fingerprint}",
        f"as_of={as_of or ''}",
        f"operational_fingerprint={operational_fingerprint}",
        f"snapshot_guards_digest={snapshot_guards_digest}",
        f"prior_ledger_state_hash={prior_ledger_state_hash}",
    ]
    payload = "\n".join(lines) + "\n"
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return f"paper-v0:{digest[:16]}"


@dataclass(frozen=True)
class RuntimeDecisionRecord:
    """The runtime's admission decision over one gold packet (SCHEMA-012).

    Wraps the pure packet by reference (``source_packet_id``) — never embeds or mutates it. Carries
    the full six-guard evaluation block plus a fail-closed ADMIT/HOLD/REJECT verdict.
    """

    record_id: str
    record_schema_version: str
    source_packet_id: str
    source_snapshot_id: str
    decision_mode: DecisionMode
    verdict: Verdict
    triggered_guard: str | None
    reason: str
    guard_outcomes: tuple[GuardOutcome, ...]
    runtime_policy_version: str
    as_of: str | None
    prior_ledger_state_hash: str
    new_ledger_state_hash: str
    non_execution_notice: str
    constraints: tuple[str, ...]

    def __post_init__(self) -> None:
        # fail-closed verdict invariant (mirrors TradeValidationDecision, by pattern not import)
        if self.verdict is Verdict.ADMIT and self.triggered_guard is not None:
            raise RuntimeContractError("an ADMIT record must not name a triggered guard")
        if self.verdict is not Verdict.ADMIT and self.triggered_guard is None:
            raise RuntimeContractError("a non-ADMIT record must name its triggering guard")
        if self.decision_mode is not DecisionMode.PAPER_ONLY:
            raise RuntimeContractError("runtime record decision_mode must be paper_only")

    def to_dict(self) -> dict[str, Any]:
        """Deterministic, JSON-stable dict (alphabetical keys; guard_outcomes ordered list)."""
        return {
            "as_of": self.as_of,
            "constraints": list(self.constraints),
            "decision_mode": self.decision_mode.value,
            "guard_outcomes": [g.to_dict() for g in self.guard_outcomes],
            "new_ledger_state_hash": self.new_ledger_state_hash,
            "non_execution_notice": self.non_execution_notice,
            "prior_ledger_state_hash": self.prior_ledger_state_hash,
            "reason": self.reason,
            "record_id": self.record_id,
            "record_schema_version": self.record_schema_version,
            "runtime_policy_version": self.runtime_policy_version,
            "source_packet_id": self.source_packet_id,
            "source_snapshot_id": self.source_snapshot_id,
            "triggered_guard": self.triggered_guard,
            "verdict": self.verdict.value,
        }


# Re-exported for callers that want the canonical guard ordering without reaching into the packet.
GUARD_NAMES: tuple[str, ...] = _GUARD_NAMES
