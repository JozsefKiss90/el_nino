"""Tests for the Market Regime Classifier (MOD-005 / SCHEMA-010 / ADR-007).

Grounded against the real Layer-2 artifact (`tests/snapshot/fixtures/latest_snapshot_pass.json`)
and a deterministic synthetic feature grid (no `hypothesis` dependency — property tests are
exhaustive `parametrize` sweeps). Covers: unit per-regime, exhaustive property invariants,
replay/determinism + goldens, schema/serialization invariants, config-driven thresholds,
fail-closed, near/secondary trace metadata, audit fields, trace-version independence,
boundaries, rule-margin interpretability, taxonomy completeness, and provenance.
"""

from __future__ import annotations

import itertools
import json
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest

from features.feature_builder import build_features
from features.feature_builder.models import Feature, FeatureVector
from regime.regime_classifier import (
    DEFAULT_REGIME_CONFIG,
    RULE_TABLE,
    TAXONOMY_VERSION,
    Regime,
    RegimeClassification,
    RegimeConfig,
    RegimeConfigError,
    classify,
    load_config,
)
from regime.regime_classifier import regime_classifier as classifier_mod
from snapshot.snapshot_consumer import consume

# --- Golden anchors (captured from the real PASS fixture) --------------------------------
PASS_FIXTURE = Path(__file__).parent.parent / "snapshot" / "fixtures" / "latest_snapshot_pass.json"
EXPECTED_SNAPSHOT_ID = "952cc83a8f930e27a7c3636cb03cf1c5d9b93a5363fa8d9b1a4891f6af7afaef"
EXPECTED_FINGERPRINT = "8ab0be8d506cbb243db68e7e522bf72f5d6327df80cb3bb7777c52fc3a821837"
GOLDEN_JSON = (
    '{"as_of": null, "feature_schema_version": "0.1.0", "indeterminate_reason": null, '
    '"provenance": [{"inputs": ["DFII10"], "max_staleness_days": 2, "name": "real_yield_10y", '
    '"revision_risk": false, "value": 1.96}], "regime": "RESTRICTIVE_RATES", '
    '"rule": {"id": "R04_restrictive_rates", "margin": 0.46, "priority": 4, '
    '"regime": "RESTRICTIVE_RATES", "scale": 1.0, "threshold": 1.5}, '
    '"snapshot_id": "952cc83a8f930e27a7c3636cb03cf1c5d9b93a5363fa8d9b1a4891f6af7afaef", '
    '"trace": {"classification_trace_version": "0.1.0", "evaluated_rule_ids": '
    '["R01_liquidity_stress", "R02_risk_off", "R03_volatile", "R04_restrictive_rates", '
    '"R05_reflation", "R06_disinflation", "R07_curve_inversion", "R08_strong_usd", '
    '"R09_risk_on", "R10_low_vol", "R11_neutral"], "failed_required_features": [], '
    '"near_matching_rules": ["R08_strong_usd"], "secondary_matching_rules": [], '
    '"skipped_rule_ids": []}, "trigger_features": ["real_yield_10y"], '
    '"versions": {"classifier_version": "0.1.0", "taxonomy_version": "1.0.0"}}'
)

# A calm, mid-band baseline that classifies as NEUTRAL with no near matches (every deciding
# feature is > near_band away from its threshold). Tests override individual features.
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


def make_fv(
    snapshot_id: str = "synthetic",
    schema_version: str = "0.1.0",
    drop: tuple[str, ...] = (),
    **overrides: float | Feature,
) -> FeatureVector:
    """Build a FeatureVector from the baseline. Overrides may be a float or a full Feature."""
    values: dict[str, float | Feature] = dict(_BASELINE)
    values.update(overrides)
    for name in drop:
        values.pop(name, None)
    features: dict[str, Feature] = {}
    for name, val in values.items():
        if isinstance(val, Feature):
            features[name] = val
        else:
            features[name] = Feature(name, float(val), (f"SRC_{name}",), 0, False)
    return FeatureVector(snapshot_id, schema_version, features, tuple(sorted(drop)))


def _valid_kwargs(**over: Any) -> dict[str, Any]:
    """A valid RegimeClassification kwargs set (RESTRICTIVE_RATES) for invariant tests."""
    base: dict[str, Any] = dict(
        matched_rule_id="R04_restrictive_rates",
        regime=Regime.RESTRICTIVE_RATES,
        rule_priority=4,
        rule_margin=0.5,
        rule_threshold=1.5,
        rule_scale=1.0,
        trigger_features=("real_yield_10y",),
        snapshot_id="s",
        feature_schema_version="0.1.0",
        provenance=(),
        taxonomy_version="1.0.0",
        classifier_version="0.1.0",
        classification_trace_version="0.1.0",
    )
    base.update(over)
    return base


# =====================================================================================
# unit — one happy-path FV per regime
# =====================================================================================

def test_liquidity_stress_fires() -> None:
    rc = classify(make_fv(rates_vol=140.0, vol_level=40.0))
    assert rc.regime is Regime.LIQUIDITY_STRESS
    assert rc.matched_rule_id == "R01_liquidity_stress"


def test_risk_off_fires() -> None:
    rc = classify(make_fv(vol_level=40.0))  # rates_vol baseline 72 < 125 -> not stress
    assert rc.regime is Regime.RISK_OFF


def test_volatile_fires() -> None:
    assert classify(make_fv(vol_level=28.0)).regime is Regime.VOLATILE


def test_restrictive_rates_fires() -> None:
    rc = classify(make_fv(real_yield_10y=2.0))
    assert rc.regime is Regime.RESTRICTIVE_RATES


def test_reflation_requires_both_clauses() -> None:
    assert classify(make_fv(breakeven_5y5y_fwd=2.6, real_yield_10y=0.5)).regime is Regime.REFLATION
    # high breakeven but high real yield -> NOT reflation (real_yield >= easy); R04 wins.
    assert classify(make_fv(breakeven_5y5y_fwd=2.6, real_yield_10y=2.0)).regime is Regime.RESTRICTIVE_RATES


def test_disinflation_fires() -> None:
    assert classify(make_fv(breakeven_5y5y_fwd=1.8)).regime is Regime.DISINFLATION


def test_curve_inversion_fires() -> None:
    assert classify(make_fv(curve_2s10s=-0.3)).regime is Regime.CURVE_INVERSION


def test_strong_usd_fires() -> None:
    assert classify(make_fv(usd_level=125.0)).regime is Regime.STRONG_USD


def test_risk_on_fires() -> None:
    rc = classify(make_fv(vol_level=12.0))
    assert rc.regime is Regime.RISK_ON
    assert rc.matched_rule_id == "R09_risk_on"


def test_low_vol_when_equity_absent() -> None:
    rc = classify(make_fv(vol_level=12.0, drop=("equity_level",)))
    assert rc.regime is Regime.LOW_VOL  # R09 skipped (equity missing), R10 covers low vol


def test_neutral_catch_all() -> None:
    rc = classify(make_fv())
    assert rc.regime is Regime.NEUTRAL
    assert rc.matched_rule_id == "R11_neutral"
    assert rc.rule_margin == 0.0
    assert rc.rule_threshold is None and rc.rule_scale is None
    assert rc.near_matching_rules == ()


# =====================================================================================
# property / exhaustive — deterministic grid sweep
# =====================================================================================

_GRID = list(
    itertools.product(
        [10.0, 16.0, 26.0, 36.0],   # vol_level
        [0.5, 1.2, 1.8],            # real_yield_10y
        [1.8, 2.25, 2.6],           # breakeven_5y5y_fwd
        [-0.3, 0.0, 0.5],           # curve_2s10s
        [115.0, 120.0, 125.0],      # usd_level
        [60.0, 130.0],              # rates_vol
    )
)


@pytest.mark.parametrize("cell", _GRID)
def test_grid_exactly_one_valid_label(cell: tuple[float, ...]) -> None:
    vol, ry, be, curve, usd, rv = cell
    rc = classify(
        make_fv(
            vol_level=vol,
            real_yield_10y=ry,
            breakeven_5y5y_fwd=be,
            curve_2s10s=curve,
            usd_level=usd,
            rates_vol=rv,
        )
    )
    table = {r.rule_id: r.regime for r in RULE_TABLE}
    assert rc.regime in set(Regime)
    assert rc.regime is not Regime.INDETERMINATE  # all required features present
    assert rc.regime is table[rc.matched_rule_id]  # regime is a projection of the matched rule
    assert 0.0 <= rc.rule_margin <= 1.0


def test_priority_monotonic_risk_off_beats_volatile() -> None:
    assert classify(make_fv(vol_level=40.0)).matched_rule_id == "R02_risk_off"
    assert classify(make_fv(vol_level=28.0)).matched_rule_id == "R03_volatile"


# =====================================================================================
# replay / determinism + goldens
# =====================================================================================

def test_determinism_same_inputs_same_output() -> None:
    fv = make_fv(real_yield_10y=2.0)
    assert classify(fv) == classify(fv)
    assert classify(fv).to_dict() == classify(fv).to_dict()


def test_golden_real_fixture() -> None:
    snap = consume(PASS_FIXTURE)
    assert snap is not None
    rc = classify(build_features(snap))
    assert rc.regime is Regime.RESTRICTIVE_RATES
    assert rc.matched_rule_id == "R04_restrictive_rates"
    assert rc.rule_margin == pytest.approx(0.46)
    assert rc.rule_threshold == 1.5 and rc.rule_scale == 1.0
    assert rc.trigger_features == ("real_yield_10y",)
    assert rc.snapshot_id == EXPECTED_SNAPSHOT_ID
    assert rc.near_matching_rules == ("R08_strong_usd",)


def test_golden_to_dict_serialization() -> None:
    snap = consume(PASS_FIXTURE)
    assert snap is not None
    rc = classify(build_features(snap))
    assert json.dumps(rc.to_dict(), sort_keys=True) == GOLDEN_JSON


# =====================================================================================
# schema / serialization invariants
# =====================================================================================

def test_to_dict_keys_sorted_and_stable() -> None:
    rc = classify(make_fv(real_yield_10y=2.0))
    d = rc.to_dict()
    assert list(d.keys()) == sorted(d.keys())
    assert rc.to_dict() == rc.to_dict()


def test_to_dict_json_roundtrip() -> None:
    rc = classify(make_fv(real_yield_10y=2.0))
    back = json.loads(json.dumps(rc.to_dict()))
    assert back["regime"] == "RESTRICTIVE_RATES"
    assert back["rule"]["id"] == "R04_restrictive_rates"


def test_indeterminate_nonzero_margin_raises() -> None:
    with pytest.raises(ValueError):
        RegimeClassification(
            **_valid_kwargs(
                matched_rule_id="R00_indeterminate",
                regime=Regime.INDETERMINATE,
                rule_threshold=None,
                rule_scale=None,
                trigger_features=(),
                rule_margin=0.5,
                indeterminate_reason="x",
            )
        )


def test_indeterminate_missing_reason_raises() -> None:
    with pytest.raises(ValueError):
        RegimeClassification(
            **_valid_kwargs(
                matched_rule_id="R00_indeterminate",
                regime=Regime.INDETERMINATE,
                rule_threshold=None,
                rule_scale=None,
                trigger_features=(),
                rule_margin=0.0,
                indeterminate_reason=None,
            )
        )


def test_neutral_with_threshold_raises() -> None:
    with pytest.raises(ValueError):
        RegimeClassification(
            **_valid_kwargs(
                matched_rule_id="R11_neutral",
                regime=Regime.NEUTRAL,
                rule_priority=11,
                rule_margin=0.0,
                rule_threshold=1.0,  # must be None for a terminal regime
                rule_scale=1.0,
                trigger_features=(),
            )
        )


def test_margin_out_of_range_raises() -> None:
    with pytest.raises(ValueError):
        RegimeClassification(**_valid_kwargs(rule_margin=1.5))


def test_matched_rule_in_secondary_raises() -> None:
    with pytest.raises(ValueError):
        RegimeClassification(**_valid_kwargs(secondary_matching_rules=("R04_restrictive_rates",)))


# =====================================================================================
# config-driven thresholds
# =====================================================================================

def test_config_fingerprint_pinned_to_taxonomy_version() -> None:
    assert DEFAULT_REGIME_CONFIG.taxonomy_version == TAXONOMY_VERSION == "1.0.0"
    assert DEFAULT_REGIME_CONFIG.decision_fingerprint() == EXPECTED_FINGERPRINT


def test_near_band_excluded_from_fingerprint() -> None:
    # near_band is trace-only; changing it must NOT change the decision fingerprint.
    assert replace(DEFAULT_REGIME_CONFIG, near_band=0.1).decision_fingerprint() == EXPECTED_FINGERPRINT


def test_from_mapping_roundtrip() -> None:
    cfg = RegimeConfig.from_mapping({"taxonomy_version": "1.0.0"})
    assert cfg.vix_crisis == 35.0


def test_from_mapping_unknown_key_raises() -> None:
    with pytest.raises(RegimeConfigError):
        RegimeConfig.from_mapping({"taxonomy_version": "1.0.0", "bogus": 1})


def test_from_mapping_missing_version_raises() -> None:
    with pytest.raises(RegimeConfigError):
        RegimeConfig.from_mapping({"vix_crisis": 40.0})


def test_from_mapping_bad_required_features_raises() -> None:
    with pytest.raises(RegimeConfigError):
        RegimeConfig.from_mapping({"taxonomy_version": "1.0.0", "required_features": [1, 2]})


def test_invalid_scale_raises() -> None:
    with pytest.raises(RegimeConfigError):
        RegimeConfig.from_mapping({"taxonomy_version": "1.0.0", "scale_volatile": 0.0})


def test_load_config_file(tmp_path: Path) -> None:
    p = tmp_path / "cfg.json"
    p.write_text(json.dumps({"taxonomy_version": "2.0.0", "vix_crisis": 30.0}), encoding="utf-8")
    cfg = load_config(p)
    assert cfg.taxonomy_version == "2.0.0"
    assert cfg.vix_crisis == 30.0


def test_load_config_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(RegimeConfigError):
        load_config(tmp_path / "nope.json")


def test_load_config_bad_json_raises(tmp_path: Path) -> None:
    p = tmp_path / "bad.json"
    p.write_text("{not json", encoding="utf-8")
    with pytest.raises(RegimeConfigError):
        load_config(p)


def test_injected_config_reclassifies() -> None:
    cfg = RegimeConfig.from_mapping({"taxonomy_version": "custom", "vix_elevated": 18.0})
    assert classify(make_fv(), cfg).regime is Regime.VOLATILE  # baseline vol 18.5 >= 18.0
    assert classify(make_fv()).regime is Regime.NEUTRAL  # default unchanged


# =====================================================================================
# fail-closed
# =====================================================================================

@pytest.mark.parametrize("feat", ["vol_level", "real_yield_10y", "curve_2s10s", "usd_level"])
def test_missing_required_feature_is_indeterminate(feat: str) -> None:
    rc = classify(make_fv(drop=(feat,)))
    assert rc.regime is Regime.INDETERMINATE
    assert rc.matched_rule_id == "R00_indeterminate"
    assert rc.rule_margin == 0.0
    assert feat in rc.failed_required_features
    assert rc.indeterminate_reason is not None and feat in rc.indeterminate_reason
    assert rc.provenance == ()
    assert rc.evaluated_rule_ids == ()


# =====================================================================================
# trace: near & secondary matching
# =====================================================================================

def test_near_matching_listed_label_stays_neutral() -> None:
    # real_yield 1.45 -> R04 proximity 0.8; usd 119 -> R08 proximity 0.6 (distinct, robust order).
    rc = classify(make_fv(real_yield_10y=1.45, usd_level=119.0))
    assert rc.regime is Regime.NEUTRAL  # neither crossed -> no MIXED_SIGNAL, just NEUTRAL
    assert rc.near_matching_rules == ("R04_restrictive_rates", "R08_strong_usd")


def test_secondary_matching_listed() -> None:
    rc = classify(make_fv(real_yield_10y=2.0, usd_level=125.0))
    assert rc.matched_rule_id == "R04_restrictive_rates"
    assert "R08_strong_usd" in rc.secondary_matching_rules


def test_secondary_ordered_by_margin_not_priority() -> None:
    # R08 (priority 8) margin 0.8 > R07 (priority 7) margin 0.1 -> R08 listed first.
    rc = classify(make_fv(real_yield_10y=2.0, usd_level=128.0, curve_2s10s=-0.05))
    assert rc.matched_rule_id == "R04_restrictive_rates"
    assert rc.secondary_matching_rules == ("R08_strong_usd", "R07_curve_inversion")


# =====================================================================================
# audit fields
# =====================================================================================

def test_evaluated_skipped_partition_when_full() -> None:
    rc = classify(make_fv(real_yield_10y=2.0))
    all_ids = {r.rule_id for r in RULE_TABLE}
    assert set(rc.evaluated_rule_ids) | set(rc.skipped_rule_ids) == all_ids
    assert rc.skipped_rule_ids == ()
    assert len(rc.evaluated_rule_ids) == len(RULE_TABLE)


def test_skipped_on_missing_per_rule_feature() -> None:
    rc = classify(make_fv(vol_level=40.0, drop=("rates_vol",)))
    assert rc.regime is Regime.RISK_OFF  # R01 skipped, R02 fires (degradation, not INDETERMINATE)
    assert "R01_liquidity_stress" in rc.skipped_rule_ids
    assert "R01_liquidity_stress" not in rc.evaluated_rule_ids
    assert "rates_vol" in rc.failed_required_features


def test_matched_not_in_secondary() -> None:
    rc = classify(make_fv(real_yield_10y=2.0, usd_level=125.0))
    assert rc.matched_rule_id not in rc.secondary_matching_rules


# =====================================================================================
# trace-version independence
# =====================================================================================

def test_trace_version_independent_of_decision() -> None:
    cfg2 = replace(DEFAULT_REGIME_CONFIG, classification_trace_version="9.9.9", near_band=0.1)
    fv = make_fv(real_yield_10y=2.0, usd_level=119.0)
    a = classify(fv)
    b = classify(fv, cfg2)

    def decision(r: RegimeClassification) -> tuple[Any, ...]:
        return (
            r.matched_rule_id, r.regime, r.rule_margin,
            r.rule_threshold, r.rule_scale, r.trigger_features,
        )

    assert decision(a) == decision(b)
    assert b.classification_trace_version == "9.9.9"


# =====================================================================================
# boundary (inclusive/exclusive conventions)
# =====================================================================================

def test_vix_exactly_crisis_is_risk_off() -> None:
    assert classify(make_fv(vol_level=35.0)).matched_rule_id == "R02_risk_off"  # >= inclusive


def test_real_yield_exactly_threshold_is_restrictive() -> None:
    assert classify(make_fv(real_yield_10y=1.5)).regime is Regime.RESTRICTIVE_RATES  # >= inclusive


def test_curve_exactly_zero_not_inverted() -> None:
    assert classify(make_fv(curve_2s10s=0.0)).regime is not Regime.CURVE_INVERSION  # < exclusive


def test_be_exactly_two_not_disinflation() -> None:
    assert classify(make_fv(breakeven_5y5y_fwd=2.0)).regime is not Regime.DISINFLATION  # < exclusive


# =====================================================================================
# rule-margin interpretability
# =====================================================================================

def test_rule_margin_reconstructs_deciding_feature() -> None:
    rc = classify(make_fv(real_yield_10y=1.96))
    assert rc.rule_threshold == 1.5 and rc.rule_scale == 1.0
    # x = threshold + direction * margin * scale ; direction +1 for RESTRICTIVE_RATES.
    assert rc.rule_threshold + rc.rule_margin * rc.rule_scale == pytest.approx(1.96)


def test_terminals_have_none_threshold_and_scale() -> None:
    neutral = classify(make_fv())
    assert neutral.rule_threshold is None and neutral.rule_scale is None
    indeterminate = classify(make_fv(drop=("usd_level",)))
    assert indeterminate.rule_threshold is None and indeterminate.rule_scale is None


# =====================================================================================
# taxonomy completeness
# =====================================================================================

_REACHABILITY: list[tuple[str, dict[str, float], tuple[str, ...]]] = [
    ("R01_liquidity_stress", dict(rates_vol=140.0, vol_level=40.0), ()),
    ("R02_risk_off", dict(vol_level=40.0), ()),
    ("R03_volatile", dict(vol_level=28.0), ()),
    ("R04_restrictive_rates", dict(real_yield_10y=2.0), ()),
    ("R05_reflation", dict(breakeven_5y5y_fwd=2.6, real_yield_10y=0.5), ()),
    ("R06_disinflation", dict(breakeven_5y5y_fwd=1.8), ()),
    ("R07_curve_inversion", dict(curve_2s10s=-0.3), ()),
    ("R08_strong_usd", dict(usd_level=125.0), ()),
    ("R09_risk_on", dict(vol_level=12.0), ()),
    ("R10_low_vol", dict(vol_level=12.0), ("equity_level",)),
    ("R11_neutral", {}, ()),
]


@pytest.mark.parametrize("rule_id,over,drop", _REACHABILITY)
def test_every_rule_reachable(rule_id: str, over: dict[str, float], drop: tuple[str, ...]) -> None:
    # `over` only ever holds feature-name keys (never the reserved str params of make_fv).
    rc = classify(make_fv(drop=drop, **over))  # type: ignore[arg-type]
    assert rc.matched_rule_id == rule_id


def test_rule_ids_unique_and_priorities_contiguous() -> None:
    ids = [r.rule_id for r in RULE_TABLE]
    assert len(ids) == len(set(ids))
    assert [r.priority for r in RULE_TABLE] == list(range(1, len(RULE_TABLE) + 1))


def test_every_signal_regime_in_table_once() -> None:
    table_regimes = [r.regime for r in RULE_TABLE]
    for regime in Regime:
        if regime is Regime.INDETERMINATE:
            continue
        assert table_regimes.count(regime) == 1


def test_neutral_is_last_and_unconditional() -> None:
    last = RULE_TABLE[-1]
    assert last.regime is Regime.NEUTRAL
    assert last.required_features == ()
    assert last.margin is None


def test_no_rule_match_raises_when_neutral_removed(monkeypatch: pytest.MonkeyPatch) -> None:
    trimmed = tuple(r for r in RULE_TABLE if r.regime is not Regime.NEUTRAL)
    monkeypatch.setattr(classifier_mod, "RULE_TABLE", trimmed)
    with pytest.raises(AssertionError):
        classify(make_fv())


# =====================================================================================
# provenance
# =====================================================================================

def test_provenance_propagates_revision_and_staleness() -> None:
    rich = Feature("real_yield_10y", 2.0, ("DFII10",), 5, True)
    rc = classify(make_fv(real_yield_10y=rich))
    assert rc.regime is Regime.RESTRICTIVE_RATES
    assert len(rc.provenance) == 1
    prov = rc.provenance[0]
    assert prov.name == "real_yield_10y"
    assert prov.inputs == ("DFII10",)
    assert prov.max_staleness_days == 5
    assert prov.revision_risk is True
