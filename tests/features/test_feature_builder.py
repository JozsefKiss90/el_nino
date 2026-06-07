"""Tests for the Feature Builder (MOD-004 / SCHEMA-009 / ADR-005).

Grounded against the real Layer-2 artifact already used by the Snapshot Consumer
slice (`tests/snapshot/fixtures/latest_snapshot_pass.json`). Covers exact
arithmetic, replay determinism, provenance propagation, and the
unavailable-feature path. The snapshot is consumed through MOD-003's `consume()`
so the real data path (ingest+gate -> transform) is exercised end to end.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from features.feature_builder import (
    FEATURE_REGISTRY,
    FEATURE_SCHEMA_VERSION,
    FeatureVector,
    build_features,
)
from snapshot.snapshot_consumer import consume
from snapshot.snapshot_consumer.models import Snapshot

SNAPSHOT_FIXTURES = Path(__file__).parent.parent / "snapshot" / "fixtures"
PASS_FIXTURE = SNAPSHOT_FIXTURES / "latest_snapshot_pass.json"

EXPECTED_SNAPSHOT_ID = "952cc83a8f930e27a7c3636cb03cf1c5d9b93a5363fa8d9b1a4891f6af7afaef"


@pytest.fixture
def snapshot() -> Snapshot:
    snap = consume(PASS_FIXTURE)
    assert snap is not None  # PASS fixture must be consumable
    return snap


def _payload() -> dict:
    return json.loads(PASS_FIXTURE.read_text(encoding="utf-8"))


def test_builds_full_v0_feature_set(snapshot: Snapshot) -> None:
    fv = build_features(snapshot)
    assert isinstance(fv, FeatureVector)
    assert len(fv.features) == len(FEATURE_REGISTRY) == 14
    assert fv.unavailable_features == ()


def test_anchored_to_snapshot_and_version(snapshot: Snapshot) -> None:
    fv = build_features(snapshot)
    assert fv.snapshot_id == EXPECTED_SNAPSHOT_ID
    assert fv.schema_version == FEATURE_SCHEMA_VERSION == "0.1.0"


def test_exact_level_values(snapshot: Snapshot) -> None:
    fv = build_features(snapshot)
    # Levels are direct reads — exact, no float arithmetic.
    assert fv.value("real_yield_10y") == 1.96
    assert fv.value("real_yield_5y") == 1.38
    assert fv.value("breakeven_10y") == 2.46
    assert fv.value("breakeven_5y") == 2.67
    assert fv.value("breakeven_5y5y_fwd") == 2.25
    assert fv.value("usd_level") == 118.7294
    assert fv.value("vol_level") == 16.89
    assert fv.value("rates_vol") == 72.06999969482422
    assert fv.value("equity_level") == 7209.01
    assert fv.value("gold_price") == 4624.5
    assert fv.value("gold_flow") == 24949755.0


def test_exact_spread_values(snapshot: Snapshot) -> None:
    fv = build_features(snapshot)
    assert fv.value("curve_2s10s") == pytest.approx(0.50)   # DGS10 4.42 - DGS2 3.92
    assert fv.value("curve_5s10s") == pytest.approx(0.37)   # DGS10 4.42 - DGS5 4.05
    assert fv.value("policy_spread") == 0.0                  # EFFR 3.64 - DFF 3.64


def test_provenance_propagation(snapshot: Snapshot) -> None:
    fv = build_features(snapshot)

    ry = fv.features["real_yield_10y"]
    assert ry.inputs == ("DFII10",)
    assert ry.max_staleness_days == 2          # DFII10 staleness_days
    assert ry.revision_risk is False

    # Spread takes the MAX staleness over its two inputs (EFFR=1, DFF=2).
    ps = fv.features["policy_spread"]
    assert ps.inputs == ("EFFR", "DFF")
    assert ps.max_staleness_days == 2
    assert ps.revision_risk is False


def test_determinism_same_inputs_same_output(snapshot: Snapshot) -> None:
    # Same snapshot_id + same schema_version => identical vector (ADR-005).
    a = build_features(snapshot)
    b = build_features(snapshot)
    assert a == b
    assert a.features == b.features
    assert a.names == b.names


def test_feature_names_sorted(snapshot: Snapshot) -> None:
    fv = build_features(snapshot)
    assert list(fv.names) == sorted(fv.names)


def test_revision_risk_propagates_from_input_series() -> None:
    # Flip a real_yields input to carry revision risk; the feature must inherit it.
    payload = _payload()
    for entry in payload["values_by_group"]["real_yields"]:
        if entry["series_id"] == "DFII10":
            entry["revision_risk"] = True
    snap = Snapshot.from_dict(payload)
    fv = build_features(snap)
    assert fv.features["real_yield_10y"].revision_risk is True
    # An unaffected feature stays clean.
    assert fv.features["real_yield_5y"].revision_risk is False


def test_missing_input_series_marks_feature_unavailable() -> None:
    # Drop DGS5 entirely; curve_5s10s must become unavailable, others unaffected.
    payload = _payload()
    payload["values_by_group"]["nominal_yields"] = [
        e for e in payload["values_by_group"]["nominal_yields"] if e["series_id"] != "DGS5"
    ]
    snap = Snapshot.from_dict(payload)
    fv = build_features(snap)
    assert "curve_5s10s" in fv.unavailable_features
    assert "curve_5s10s" not in fv.features
    assert len(fv.features) == 13
    # curve_2s10s (DGS10-DGS2) is unaffected and still present.
    assert "curve_2s10s" in fv.features


def test_consumes_snapshot_object_not_raw_json(snapshot: Snapshot) -> None:
    # build_features takes a Snapshot, not a path/dict — guards the input boundary.
    with pytest.raises(AttributeError):
        build_features(str(PASS_FIXTURE))  # type: ignore[arg-type]
