"""L3 guard predicates for the paper-trading runtime (PRED-006 / PRED-007 + snapshot echoes).

Each guard is a pure function returning ``(passed, reason)`` — mirroring the Risk Control predicate
shape ``(...) -> (passed, reason)``. **Pattern only; never imported** — coupling ``gold`` to
``risk`` would breach the Risk Control ↔ Trading Engine boundary (Context Map / ARCH-001;
re-implemented here, ADR-009 §3). The engine evaluates the *required* subset as a short-circuit
conjunction in the canonical ``_GUARD_NAMES`` order to attribute a verdict.

- ``duplicate_ok`` (PRED-006): once-ever idempotency — fails iff this snapshot already ADMITted.
- ``operational_ok`` (PRED-007): right instrument, venue tradeable + open, not halted/degraded.
- ``data_ok`` / ``freshness_ok`` / ``cooldown_ok``: echo the packet's forwarded ``snapshot_guards``.
- ``supervisor_ok``: an explicit ``None`` stub (no supervisor) — added by the engine, not here.
"""

from __future__ import annotations

from gold.decision_builder.models import GoldDecisionPacket

from .models import OperationalInput, RuntimeLedger

GuardResult = tuple[bool | None, str]

_ABSENT_PROVENANCE = "snapshot_guards provenance absent on packet (default-closed)"


def duplicate_ok(packet: GoldDecisionPacket, prior_ledger: RuntimeLedger) -> GuardResult:
    """PRED-006: pass iff this snapshot has not already produced an ADMITted packet (once-ever)."""
    if prior_ledger.has_admit(packet.source_snapshot_id):
        return False, f"snapshot {packet.source_snapshot_id} already admitted (duplicate)"
    return True, "snapshot not previously admitted"


def operational_ok(packet: GoldDecisionPacket, op: OperationalInput) -> GuardResult:
    """PRED-007: pass iff operational preconditions hold for the packet's instrument."""
    if op.instrument != packet.instrument:
        return False, f"operational instrument {op.instrument!r} != packet {packet.instrument!r}"
    if not (op.tradeable and op.venue_open and not op.halt and not op.degraded):
        return False, (
            f"operational preconditions not met "
            f"(tradeable={op.tradeable}, venue_open={op.venue_open}, "
            f"halt={op.halt}, degraded={op.degraded})"
        )
    return True, "operational preconditions met"


def _echo(packet: GoldDecisionPacket, attr: str, label: str) -> GuardResult:
    sg = packet.snapshot_guards
    if sg is None:
        return False, _ABSENT_PROVENANCE
    value = bool(getattr(sg, attr))
    return value, f"snapshot {label}={value}"


def data_ok(packet: GoldDecisionPacket) -> GuardResult:
    """Echo the snapshot's data-quality flag from the packet's forwarded provenance."""
    return _echo(packet, "data_ok", "data_ok")


def freshness_ok(packet: GoldDecisionPacket) -> GuardResult:
    """Echo the snapshot's freshness flag from the packet's forwarded provenance."""
    return _echo(packet, "freshness_ok", "freshness_ok")


def cooldown_ok(packet: GoldDecisionPacket) -> GuardResult:
    """Echo the snapshot's cooldown flag (computed cooldown deferred — ADR-009 §6)."""
    return _echo(packet, "cooldown_ok", "cooldown_ok")
