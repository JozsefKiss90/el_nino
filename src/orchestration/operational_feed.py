"""Live operational-status feed adapter (MOD-010 seam) — lifts ADR-009's deferred "live operational feed".

The pure cores (``evaluate`` / ``run_chain``) keep taking ``OperationalInput`` as an **explicit value**
(unchanged contract — this module never touches it). This is the IO adapter that **reads** operational
status and **produces** that ``OperationalInput`` on the live ``run_once`` path **only**. The produced
value is **captured** (persisted as a JSON artifact in the existing ``load_operational`` format), so any
``run_sequence`` replay threads the captured value (via ``load_operational``) and **never** re-reads the
feed — exactly the ADR-011 §2 / gate-f **non-replayable-adapter quarantine** (live runs logged, not
replayed; no clock / network on the replay path).

**Fail-closed:** an unavailable / ambiguous source ⇒ ``OperationalInput.closed()`` (not tradeable, no
admission) — never fail-open.

v0 source: a **deterministic** US-equity trading-calendar computation for the GLD venue (no credentials,
no network) — itself replay-safe. The live **Alpaca clock/calendar** feed is the pluggable, non-replayable
plug behind the same ``OperationalFeed`` port; its credentials live in **env / git-ignored ``.secrets``
only** ([[Agent Safety Principles]] KA-008), never in the repo, a memory file, or a dev_graph node. It is
**deferred** (not built here) — the seam is ready for it.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Protocol, Union

from gold.paper_runtime.models import OperationalInput

PathLike = Union[str, Path]

# Approximate v0 US-market fixed-date holidays (no observed-date shifting / movable feasts like Good
# Friday / Thanksgiving). A complete, correct NYSE calendar is the live Alpaca-calendar feed's job
# (deferred); this v0 set is a deterministic, fail-closed approximation, not an exchange calendar.
_DEFAULT_HOLIDAYS: frozenset[str] = frozenset({"01-01", "06-19", "07-04", "12-25"})


def _parse(value: str | None) -> datetime | None:
    """Deterministic ISO-8601 parse (never wall-clock). ``None`` if absent/unparseable."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


class OperationalFeed(Protocol):
    """The operational-status port: read venue readiness as of a timestamp ⇒ an ``OperationalInput``.

    Both the deterministic ``MarketCalendarFeed`` and a future live ``AlpacaClockFeed`` implement this
    one method; the orchestrator captures the result so the choice of plug never reaches the replay path.
    """

    def read(self, as_of: str | None) -> OperationalInput:
        """Produce the venue's ``OperationalInput`` as of ``as_of`` (fail-closed on ambiguity)."""
        ...


@dataclass(frozen=True)
class MarketCalendarFeed:
    """Deterministic US-equity trading-calendar feed for the GLD venue (the replay-safe v0 source).

    A pure function of the given ``as_of`` — **no network, no wall-clock, no credentials**, so it is
    itself replay-safe (the capture step below makes even a *non*-deterministic feed replayable). A
    trading day is a weekday that is not a listed holiday; ``halt``/``degraded`` are not modelled by a
    calendar (a live feed would). **Fail-closed:** weekend / listed holiday / unparseable ``as_of`` ⇒
    not tradeable.
    """

    instrument: str = "GLD"
    holidays: frozenset[str] = field(default=_DEFAULT_HOLIDAYS)

    def read(self, as_of: str | None) -> OperationalInput:
        when = _parse(as_of)
        if when is None:
            return OperationalInput.closed(instrument=self.instrument, as_of=as_of)
        is_weekend = when.weekday() >= 5  # Sat=5, Sun=6
        is_holiday = when.strftime("%m-%d") in self.holidays
        if is_weekend or is_holiday:
            return OperationalInput.closed(instrument=self.instrument, as_of=as_of)
        return OperationalInput(
            instrument=self.instrument,
            tradeable=True,
            venue_open=True,
            halt=False,
            degraded=False,
            as_of=as_of,
        )


def operator_halt_active(path: PathLike) -> bool:
    """True iff the operator kill switch is engaged (ADR-014 §6.6). Absent marker ⇒ NOT halted (run).

    The marker is a persisted ``OperationalInput`` (written by the ADR-013 gated Tier-2 halt action). A
    **present** marker with ``halt: true`` is engaged; an **absent** marker means "no kill switch set" →
    run (the default is to run, never to halt-by-default); a present-but-unreadable marker fails
    **closed** (halted) — the safe direction. This is a pure read; it never writes.
    """
    p = Path(path)
    if not p.exists():
        return False  # no kill switch set → run (do NOT default-halt on absence)
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return True  # a present-but-unreadable kill switch is honored as HALTED (fail-closed)
    return bool(data.get("halt", False)) if isinstance(data, dict) else True


@dataclass(frozen=True)
class OperatorHaltFeed:
    """An ``OperationalFeed`` decorator that honors the operator kill switch (ADR-014 §6.6).

    It delegates to ``inner`` and, when :func:`operator_halt_active` reports the kill switch engaged,
    **forces ``halt=True``** (and not-tradeable) on the produced ``OperationalInput`` — so the **existing**
    ``operational_ok`` predicate (PRED-007) REJECTs the next cycle. No new honor path / no new predicate:
    the feed simply *produces* a halted input, which the runtime already refuses. The forced value is
    captured by ``read_and_capture`` like any other, so the honored halt stays replay-safe.
    """

    inner: OperationalFeed
    halt_path: PathLike

    def read(self, as_of: str | None) -> OperationalInput:
        op = self.inner.read(as_of)
        if not operator_halt_active(self.halt_path):
            return op
        # Force the kill: keep the venue/instrument provenance, flip halt + tradeable. operational_ok
        # blocks on halt regardless of the other flags (a single governed kill mechanism).
        return OperationalInput(
            instrument=op.instrument,
            tradeable=False,
            venue_open=op.venue_open,
            halt=True,
            degraded=op.degraded,
            as_of=op.as_of,
        )


def persist_operational(path: PathLike, op: OperationalInput) -> None:
    """Atomically capture an ``OperationalInput`` as canonical JSON (temp + ``os.replace``).

    The captured artifact is the **replay source**: it is exactly what ``paper_runtime.load_operational``
    reads, so a later replay reconstructs the operational decision byte-identically without the feed.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(op.to_dict(), sort_keys=True, indent=2) + "\n"
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_text(payload, encoding="utf-8")
    os.replace(tmp, p)


def read_and_capture(
    feed: OperationalFeed,
    as_of: str | None,
    capture_path: PathLike | None,
) -> OperationalInput:
    """Read the feed **once** (the only live IO) and capture the produced ``OperationalInput`` for replay.

    The returned value is what the live ``run_once`` uses; the captured artifact at ``capture_path`` is
    what a later replay threads (via ``load_operational``) — the feed is **never** re-read on the replay
    path (the §2 / gate-f quarantine). ``capture_path=None`` reads without capturing (the value still
    flows into that single live run, but is not made replayable).
    """
    op = feed.read(as_of)
    if capture_path is not None:
        persist_operational(capture_path, op)
    return op
