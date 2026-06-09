"""Gold Decision Builder (MOD-006) tests — units, determinism, fail-closed, golden, fingerprint.

Grounded against the real PASS fixture (the sole consumable real snapshot) and synthetic
FeatureVectors built the same way as the regime benchmark. Pins the golden packet for
RESTRICTIVE_RATES -> AVOID / confidence 0.39744 and the full-key packet_id.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from features.feature_builder import build_features
from features.feature_builder.models import Feature, FeatureVector
from gold.decision_builder import (
    DEFAULT_DECISION_POLICY_CONFIG,
    DEFAULT_DIRECTION_TABLE,
    DecisionMode,
    DecisionPolicyConfig,
    DecisionPolicyConfigError,
    Direction,
    GuardRefs,
    SnapshotGuards,
    build_decision,
)
from regime.regime_classifier import DEFAULT_REGIME_CONFIG, Regime, classify
from snapshot.snapshot_consumer import consume

_REPO_ROOT = Path(__file__).resolve().parents[2]
_REAL_PASS = _REPO_ROOT / "tests" / "snapshot" / "fixtures" / "latest_snapshot_pass.json"

# A calm, mid-band NEUTRAL baseline (same point the regime benchmark uses).
_BASELINE: dict[str, float] = {
    "real_yield_10y": 0.9,
    "real_yield_5y": 0.8,
    "breakeven_10y": 2.3,
    "breakeven_5y": 2.3,
    "breakeven_5y5y_fwd": 2.25,
    "curve_2s10s": 0.5,
    "curve_5s10s": 0.4,
    "policy_spread": 0.0,
    "usd_level": 110.0,
    "vol_level": 18.5,
    "rates_vol": 72.0,
    "equity_level": 5000.0,
    "gold_price": 4000.0,
    "gold_flow": 1_000_000.0,
}


def _make_fv(
    overrides: dict[str, float] | None = None,
    drop: tuple[str, ...] = (),
    snapshot_id: str = "synthetic",
) -> FeatureVector:
    values = dict(_BASELINE)
    if overrides:
        values.update(overrides)
    for name in drop:
        values.pop(name, None)
    features = {
        name: Feature(name, float(val), (f"SRC_{name}",), 0, False)
        for name, val in values.items()
    }
    return FeatureVector(snapshot_id, "0.1.0", features, tuple(sorted(drop)))


def _real_packet():
    snap = consume(_REAL_PASS)
    assert snap is not None
    fv = build_features(snap)
    rc = classify(fv)
    return fv, rc, build_decision(fv, rc)


# --- golden (real snapshot) ----------------------------------------------------------------

def test_real_snapshot_golden() -> None:
    fv, rc, pkt = _real_packet()
    assert rc.regime is Regime.RESTRICTIVE_RATES
    assert pkt.regime == "RESTRICTIVE_RATES"
    assert pkt.direction is Direction.AVOID
    assert pkt.decision_mode is DecisionMode.PAPER_ONLY
    assert pkt.instrument == "GLD"
    assert round(pkt.confidence, 6) == 0.39744
    assert round(pkt.confidence, 2) == 0.40  # the brief's "confidence ≈ 0.40"
    assert round(pkt.uncertainty, 6) == 0.136
    # the full-key packet_id (digest over the whole identity tuple)
    assert pkt.packet_id == "gold-v0:5653d07a0b3949d5"
    # cited features come verbatim from the regime provenance (real_yield_10y / DFII10)
    assert [c.name for c in pkt.cited_features] == ["real_yield_10y"]
    assert pkt.cited_features[0].value == 1.96
    assert pkt.cited_features[0].inputs == ("DFII10",)


def test_byte_identical_replay() -> None:
    fv, rc, _ = _real_packet()
    first = json.dumps(build_decision(fv, rc).to_dict(), sort_keys=True)
    second = json.dumps(build_decision(fv, rc).to_dict(), sort_keys=True)
    assert first == second


def test_confidence_inputs_recorded() -> None:
    _, _, pkt = _real_packet()
    ci = pkt.confidence_inputs.to_dict()
    assert ci == {
        "anchor": 0.46,
        "max_staleness_days": 2,
        "near_count": 1,
        "revision_risk": False,
        "secondary_count": 0,
        "unavailable_count": 0,
    }


# --- floors ---------------------------------------------------------------------------------

def test_indeterminate_fail_closed_floor() -> None:
    fv = _make_fv(drop=("usd_level",))  # drop a globally-required feature
    rc = classify(fv)
    assert rc.regime is Regime.INDETERMINATE
    pkt = build_decision(fv, rc)
    assert pkt.direction is Direction.WATCH
    assert pkt.confidence == 0.0
    assert pkt.uncertainty == 1.0
    assert pkt.cited_features == ()


def test_neutral_confident_quiet_floor() -> None:
    fv = _make_fv()
    rc = classify(fv)
    assert rc.regime is Regime.NEUTRAL
    pkt = build_decision(fv, rc)
    assert pkt.direction is Direction.FLAT
    # NEUTRAL is floored above zero (not naive-zero from rule_margin=0.0)
    assert pkt.confidence > 0.0
    assert pkt.confidence <= 0.5
    assert pkt.confidence_inputs.anchor == 0.5


# --- direction table totality ---------------------------------------------------------------

def test_direction_table_total_over_all_regimes() -> None:
    table = dict(DEFAULT_DIRECTION_TABLE)
    assert set(table) == {r.value for r in Regime}
    assert table["INDETERMINATE"] == "WATCH"
    cfg = DEFAULT_DECISION_POLICY_CONFIG
    for regime in Regime:
        assert isinstance(cfg.direction_for(regime.value), Direction)


# --- fingerprint coherence ------------------------------------------------------------------

def test_decision_policy_fingerprint_pinned() -> None:
    # Pins the v0 policy set; an un-versioned edit to a weight or a table cell changes this.
    assert (
        DEFAULT_DECISION_POLICY_CONFIG.decision_policy_fingerprint()
        == "be7e3192889ebe5deb100a9510fe2adc0fb676eb2eca199de3ffa1df9369a8a5"
    )


def test_fingerprint_changes_on_weight_drift() -> None:
    drifted = DecisionPolicyConfig(ambiguity_weight=0.20)
    assert (
        drifted.decision_policy_fingerprint()
        != DEFAULT_DECISION_POLICY_CONFIG.decision_policy_fingerprint()
    )


def test_fingerprint_excludes_version() -> None:
    # Bumping only the version must NOT change the fingerprint (it digests the policy set).
    bumped = DecisionPolicyConfig(decision_policy_version="9.9.9")
    assert (
        bumped.decision_policy_fingerprint()
        == DEFAULT_DECISION_POLICY_CONFIG.decision_policy_fingerprint()
    )


# --- packet_id identity-tuple coverage (the step-0 collision fix) ---------------------------

def test_packet_id_changes_with_policy_version() -> None:
    fv, rc, pkt = _real_packet()
    other = build_decision(fv, rc, config=DecisionPolicyConfig(decision_policy_version="0.2.0"))
    assert other.packet_id != pkt.packet_id


def test_packet_id_changes_with_config_fingerprint() -> None:
    # Same version, different weights => different fingerprint => different packet_id.
    fv, rc, pkt = _real_packet()
    other = build_decision(fv, rc, config=DecisionPolicyConfig(coverage_weight=0.10))
    assert other.packet_id != pkt.packet_id


# --- fail-closed input boundary -------------------------------------------------------------

def test_snapshot_id_mismatch_fail_closed() -> None:
    fv_a = _make_fv(snapshot_id="A")
    rc_a = classify(fv_a)
    fv_b = _make_fv(snapshot_id="B")
    with pytest.raises(ValueError, match="snapshot_id mismatch"):
        build_decision(fv_b, rc_a)


# --- guard refs -----------------------------------------------------------------------------

def test_guard_refs_default_null() -> None:
    _, _, pkt = _real_packet()
    assert pkt.guard_refs.to_dict() == {
        "cooldown_ok": None,
        "data_ok": None,
        "duplicate_ok": None,
        "freshness_ok": None,
        "operational_ok": None,
        "supervisor_ok": None,
    }


def test_guard_refs_passthrough() -> None:
    fv, rc, _ = _real_packet()
    pkt = build_decision(fv, rc, guards=GuardRefs(duplicate_ok=True, operational_ok=False))
    assert pkt.guard_refs.duplicate_ok is True
    assert pkt.guard_refs.operational_ok is False
    assert pkt.guard_refs.data_ok is None


# --- snapshot_guards provenance (ADR-009 §3 additive block) ---------------------------------

def test_snapshot_guards_forwarded_without_moving_packet_id() -> None:
    fv, rc, base = _real_packet()  # base built without snapshot_guards/as_of
    sg = SnapshotGuards(data_ok=True, freshness_ok=True, cooldown_ok=False)
    pkt = build_decision(fv, rc, snapshot_guards=sg, as_of="2026-05-01T22:00:00+00:00")
    assert pkt.snapshot_guards == sg
    assert pkt.to_dict()["snapshot_guards"] == {
        "cooldown_ok": False,
        "data_ok": True,
        "freshness_ok": True,
    }
    assert pkt.as_of == "2026-05-01T22:00:00+00:00"
    assert pkt.packet_schema_version == "0.2.0"
    # the additive provenance + as_of are excluded from packet_id (no collision hazard)
    assert pkt.packet_id == base.packet_id
    # and absent on a pre-runtime caller (default None, serialized as null)
    assert base.snapshot_guards is None
    assert base.to_dict()["snapshot_guards"] is None


# --- config fail-closed ---------------------------------------------------------------------

def test_config_unknown_key_raises() -> None:
    with pytest.raises(DecisionPolicyConfigError, match="unknown config keys"):
        DecisionPolicyConfig.from_mapping({"decision_policy_version": "0.1.0", "bogus": 1})


def test_config_missing_version_raises() -> None:
    with pytest.raises(DecisionPolicyConfigError, match="decision_policy_version"):
        DecisionPolicyConfig.from_mapping({"ambiguity_weight": 0.2})


def test_config_non_total_table_raises() -> None:
    with pytest.raises(DecisionPolicyConfigError, match="total over all regimes"):
        DecisionPolicyConfig(direction_table=(("NEUTRAL", "FLAT"),))


def test_config_indeterminate_must_be_watch() -> None:
    bad = tuple(
        (r, "LONG" if r == "INDETERMINATE" else d) for r, d in DEFAULT_DIRECTION_TABLE
    )
    with pytest.raises(DecisionPolicyConfigError, match="INDETERMINATE must map to WATCH"):
        DecisionPolicyConfig(direction_table=bad)


def test_config_invalid_direction_raises() -> None:
    bad = tuple(
        (r, "BUY" if r == "RISK_ON" else d) for r, d in DEFAULT_DIRECTION_TABLE
    )
    with pytest.raises(DecisionPolicyConfigError, match="invalid direction"):
        DecisionPolicyConfig(direction_table=bad)


def test_default_regime_config_unused_but_importable() -> None:
    # sanity: the regime default config is the one classify() uses under the hood
    assert DEFAULT_REGIME_CONFIG.taxonomy_version == "1.0.0"
