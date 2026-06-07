"""Tests for the Layer-2 Snapshot contract models (SCHEMA-001).

Grounded against the real Ripley artifact copied verbatim into
``fixtures/latest_snapshot_pass.json``. The identity-recomputation test is the
contract anchor: if our model captures the wrong identity-determining fields,
the recomputed hash diverges from the published one.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from snapshot.snapshot_consumer.models import Snapshot, SnapshotContractError

FIXTURES = Path(__file__).parent / "fixtures"
PASS_FIXTURE = FIXTURES / "latest_snapshot_pass.json"

EXPECTED_ID = "952cc83a8f930e27a7c3636cb03cf1c5d9b93a5363fa8d9b1a4891f6af7afaef"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_parses_real_artifact_top_level() -> None:
    snap = Snapshot.from_dict(_load("latest_snapshot_pass.json"))
    assert snap.snapshot_id == EXPECTED_ID
    assert snap.engine_version == "gold-v3.3.0"
    assert snap.config_version == "1.1.0"
    assert snap.verdict == "PASS"
    assert snap.forced is False
    assert snap.dry_run is False
    assert snap.series_count == 21
    assert len(snap.values) == 21


def test_recomputed_id_matches_published() -> None:
    # The contract anchor: identity is reproducible from modelled content alone.
    snap = Snapshot.from_dict(_load("latest_snapshot_pass.json"))
    assert snap.recompute_id() == EXPECTED_ID
    assert snap.id_matches is True


def test_series_value_full_fidelity() -> None:
    snap = Snapshot.from_dict(_load("latest_snapshot_pass.json"))
    gold = snap.values["gold_price_proxy"]
    assert gold.value == 4624.5
    assert gold.tier == 1
    assert gold.group == "gold"
    assert gold.source == "goldapi_com"
    assert gold.staleness_days == 1
    assert gold.revision_risk is False
    # A Tier-2 revision-risk series round-trips its flag.
    cpi = snap.values["CPILFESL"]
    assert cpi.tier == 2
    assert cpi.revision_risk is True


def test_guards_parsed() -> None:
    snap = Snapshot.from_dict(_load("latest_snapshot_pass.json"))
    assert snap.guards.snapshot_ok is True
    assert snap.guards.data_ok is True
    assert snap.guards.freshness_ok is True
    assert snap.guards.missing_tier1 is False
    assert snap.guards.reason_code == "DATA_OK"
    # Layer-3 stubs default-present in the Layer-2 output.
    assert snap.guards.supervisor_veto is False
    assert snap.guards.risk_ok is True


def test_quality_summary_parsed() -> None:
    snap = Snapshot.from_dict(_load("latest_snapshot_pass.json"))
    assert snap.quality_summary.tier1_total == 16
    assert snap.quality_summary.tier1_pass == 16
    assert snap.quality_summary.tier1_fail == 0
    assert snap.quality_summary.tier2_warn == 3
    assert "CPILFESL" in snap.quality_summary.revision_risk_series


def test_missing_required_key_raises() -> None:
    payload = _load("latest_snapshot_pass.json")
    del payload["snapshot_id"]
    with pytest.raises(SnapshotContractError, match="snapshot_id"):
        Snapshot.from_dict(payload)


def test_missing_values_by_group_raises() -> None:
    payload = _load("latest_snapshot_pass.json")
    del payload["values_by_group"]
    with pytest.raises(SnapshotContractError, match="values_by_group"):
        Snapshot.from_dict(payload)


def test_non_object_payload_raises() -> None:
    with pytest.raises(SnapshotContractError):
        Snapshot.from_dict([])  # type: ignore[arg-type]
