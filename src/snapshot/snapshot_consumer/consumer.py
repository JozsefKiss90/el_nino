"""Snapshot Consumer (MOD-003) — Layer-3 ingestion of the Layer-2 truth snapshot.

Implements the Layer-3 side of the Snapshot API (INT-001). The Layer-2 publisher
contract is explicit:

    Layer-3 MUST NOT read observations directly.
    Layer-3 reads latest_snapshot.json or queries snapshots by snapshot_id.
    If no snapshot exists or the quality gate failed -> Layer-3 outputs nothing.

This module realises that contract as a fail-closed gate. ``consume()`` is the
single entry point downstream stages (Feature Builder, Decision) should call:
it returns a snapshot ONLY when it is safe to act on, and ``None`` otherwise.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Union

from .models import Snapshot

PathLike = Union[str, Path]


def load_snapshot(path: PathLike) -> Snapshot | None:
    """Load and parse a snapshot JSON file.

    Returns ``None`` when the file is absent (a legitimate "no snapshot yet"
    state). Raises ``SnapshotContractError`` when the file exists but violates
    the contract — an upstream truth-layer fault must be loud, not silently
    swallowed as absence. JSON that is not even parseable raises
    ``json.JSONDecodeError`` for the same reason.
    """
    p = Path(path)
    if not p.exists():
        return None
    payload = json.loads(p.read_text(encoding="utf-8"))
    return Snapshot.from_dict(payload)


def is_consumable(snapshot: Snapshot) -> bool:
    """Whether Layer-3 may act on this snapshot.

    Fail-closed: a snapshot is consumable ONLY if the quality gate passed
    (``verdict == "PASS"`` and ``guards.snapshot_ok``) and it is neither a
    forced bypass nor a dry-run preview. A ``forced`` snapshot deliberately
    bypassed the gate (testing only); consuming it would let known-bad data
    into a decision, so it is rejected here.
    """
    return (
        snapshot.verdict == "PASS"
        and snapshot.guards.snapshot_ok
        and not snapshot.forced
        and not snapshot.dry_run
    )


def consume(path: PathLike) -> Snapshot | None:
    """Layer-3 entry point: return a consumable snapshot, or ``None``.

    ``None`` means "Layer-3 outputs nothing" — there is no snapshot, or the
    snapshot's quality gate did not pass (or it was forced / dry-run). A
    structurally malformed snapshot still raises ``SnapshotContractError`` via
    ``load_snapshot`` rather than being masked as ``None``.
    """
    snapshot = load_snapshot(path)
    if snapshot is None:
        return None
    if not is_consumable(snapshot):
        return None
    return snapshot
