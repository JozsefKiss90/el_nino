"""Snapshot Consumer (MOD-003) — the Layer-3 ingestion boundary.

Reads the Layer-2 Snapshot (SCHEMA-001) via the Snapshot API (INT-001) and
enforces the Layer-3 consumption contract: no snapshot, a failed quality gate,
a forced bypass, or a dry-run preview all yield *nothing* downstream.
"""

from .consumer import consume, is_consumable, load_snapshot
from .models import Guards, QualitySummary, SeriesValue, Snapshot, SnapshotContractError

__all__ = [
    "consume",
    "is_consumable",
    "load_snapshot",
    "Guards",
    "QualitySummary",
    "SeriesValue",
    "Snapshot",
    "SnapshotContractError",
]
