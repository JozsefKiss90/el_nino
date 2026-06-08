"""Regime taxonomy (ADR-007) — the ordered, declarative rule table + pure helpers.

Mirrors the Feature Builder's declarative ``FEATURE_REGISTRY`` (MOD-004) and the Guardrail
Engine's pure predicate tuple (MOD-001): a frozen, priority-ordered ``RULE_TABLE`` of
``RegimeRule`` entries, each a pure function of a ``FeatureVector`` and a ``RegimeConfig``.

Selection is first-match-wins by priority (lowest number = highest priority). The single
unconditional catch-all is ``R11_neutral``; the fail-closed terminal is handled in the
driver, not the table. No history, no clock, no randomness, no I/O — replay-safe (ADR-005).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from features.feature_builder.models import FeatureVector

from .config import RegimeConfig
from .models import Regime

Predicate = Callable[[FeatureVector, RegimeConfig], bool]
Number = Callable[[RegimeConfig], float]


@dataclass(frozen=True)
class MarginSpec:
    """How to compute a rule's deciding-feature margin: feature, threshold, scale, direction.

    ``direction`` is +1 for ``>=``/``>`` rules and -1 for ``<``/``<=`` rules. ``threshold``
    and ``scale`` are read from the (versioned) ``RegimeConfig`` so no numeric constant is
    hard-coded here.
    """

    feature: str
    threshold: Number
    scale: Number
    direction: int


@dataclass(frozen=True)
class RegimeRule:
    """One entry in the priority-ordered taxonomy. ``regime`` is what a match projects to."""

    rule_id: str
    regime: Regime
    priority: int
    required_features: tuple[str, ...]
    trigger_features: tuple[str, ...]
    predicate: Predicate
    margin: MarginSpec | None


def clamp01(value: float) -> float:
    """Clamp to the unit interval."""
    return max(0.0, min(1.0, value))


def margin_value(fv: FeatureVector, c: RegimeConfig, spec: MarginSpec) -> float:
    """Normalized activation margin of the deciding feature past its threshold, in [0, 1].

    ``clamp(direction * (x - t) / s, 0, 1)``. Pure; raises ``KeyError`` only if the deciding
    feature is absent (the driver guarantees presence before calling).
    """
    x = fv.value(spec.feature)
    return clamp01(spec.direction * (x - spec.threshold(c)) / spec.scale(c))


def near_proximity(fv: FeatureVector, c: RegimeConfig, spec: MarginSpec) -> float | None:
    """Proximity in [0, 1] if the (non-matching) deciding feature is within ``near_band``.

    Distance to the threshold, in scale units, on the non-firing side:
    ``distance = -direction * (x - t) / s``. Returns ``1 - distance/near_band`` when
    ``0 <= distance <= near_band``, else ``None`` (not near). Pure.
    """
    x = fv.value(spec.feature)
    distance = -spec.direction * (x - spec.threshold(c)) / spec.scale(c)
    if distance < 0.0 or distance > c.near_band:
        return None
    return clamp01(1.0 - distance / c.near_band)


# Feature usage (ADR-007 / KA-011). The v1.0.0 taxonomy decides on 7 of the 14 SCHEMA-009
# features: vol_level, rates_vol, real_yield_10y, breakeven_5y5y_fwd, curve_2s10s, usd_level,
# equity_level. The other 7 are intentionally RESERVED for a future taxonomy_version, not used
# here: real_yield_5y / breakeven_10y / breakeven_5y / curve_5s10s are redundant with the chosen
# tenor (10y real, 5y5y breakeven, 2s10s curve); policy_spread adds no distinct snapshot-local
# regime signal in v0; gold_price / gold_flow have no defensible absolute-level anchor (only
# forbidden momentum/history would apply). Reserved features are never invented or fabricated —
# they are promoted only via a governed version bump.

# --- Predicates (pure; only read features guaranteed present by each rule's required set) --

def _p_liquidity_stress(fv: FeatureVector, c: RegimeConfig) -> bool:
    return fv.value("rates_vol") >= c.move_stress and fv.value("vol_level") >= c.vix_liquidity_gate


def _p_risk_off(fv: FeatureVector, c: RegimeConfig) -> bool:
    return fv.value("vol_level") >= c.vix_crisis


def _p_volatile(fv: FeatureVector, c: RegimeConfig) -> bool:
    return fv.value("vol_level") >= c.vix_elevated


def _p_restrictive_rates(fv: FeatureVector, c: RegimeConfig) -> bool:
    return fv.value("real_yield_10y") >= c.real_yield_restrictive


def _p_reflation(fv: FeatureVector, c: RegimeConfig) -> bool:
    return (
        fv.value("breakeven_5y5y_fwd") >= c.be5y5y_reflation
        and fv.value("real_yield_10y") < c.real_yield_easy
    )


def _p_disinflation(fv: FeatureVector, c: RegimeConfig) -> bool:
    return fv.value("breakeven_5y5y_fwd") < c.be5y5y_disinflation


def _p_curve_inversion(fv: FeatureVector, c: RegimeConfig) -> bool:
    return fv.value("curve_2s10s") < c.curve_inversion


def _p_strong_usd(fv: FeatureVector, c: RegimeConfig) -> bool:
    return fv.value("usd_level") >= c.usd_strong


def _p_risk_on(fv: FeatureVector, c: RegimeConfig) -> bool:
    return fv.value("vol_level") < c.vix_calm and fv.value("equity_level") > 0.0


def _p_low_vol(fv: FeatureVector, c: RegimeConfig) -> bool:
    return fv.value("vol_level") < c.vix_calm


def _p_neutral(fv: FeatureVector, c: RegimeConfig) -> bool:
    return True


# --- The canonical priority-ordered rule table (first match wins) -------------------------
RULE_TABLE: tuple[RegimeRule, ...] = (
    RegimeRule(
        "R01_liquidity_stress", Regime.LIQUIDITY_STRESS, 1,
        ("rates_vol", "vol_level"), ("rates_vol", "vol_level"),
        _p_liquidity_stress,
        MarginSpec("rates_vol", lambda c: c.move_stress, lambda c: c.scale_liquidity_stress, 1),
    ),
    RegimeRule(
        "R02_risk_off", Regime.RISK_OFF, 2,
        ("vol_level",), ("vol_level",),
        _p_risk_off,
        MarginSpec("vol_level", lambda c: c.vix_crisis, lambda c: c.scale_risk_off, 1),
    ),
    RegimeRule(
        "R03_volatile", Regime.VOLATILE, 3,
        ("vol_level",), ("vol_level",),
        _p_volatile,
        MarginSpec("vol_level", lambda c: c.vix_elevated, lambda c: c.scale_volatile, 1),
    ),
    RegimeRule(
        "R04_restrictive_rates", Regime.RESTRICTIVE_RATES, 4,
        ("real_yield_10y",), ("real_yield_10y",),
        _p_restrictive_rates,
        MarginSpec("real_yield_10y", lambda c: c.real_yield_restrictive, lambda c: c.scale_restrictive_rates, 1),
    ),
    RegimeRule(
        "R05_reflation", Regime.REFLATION, 5,
        ("breakeven_5y5y_fwd", "real_yield_10y"), ("breakeven_5y5y_fwd", "real_yield_10y"),
        _p_reflation,
        MarginSpec("breakeven_5y5y_fwd", lambda c: c.be5y5y_reflation, lambda c: c.scale_reflation, 1),
    ),
    RegimeRule(
        "R06_disinflation", Regime.DISINFLATION, 6,
        ("breakeven_5y5y_fwd",), ("breakeven_5y5y_fwd",),
        _p_disinflation,
        MarginSpec("breakeven_5y5y_fwd", lambda c: c.be5y5y_disinflation, lambda c: c.scale_disinflation, -1),
    ),
    RegimeRule(
        "R07_curve_inversion", Regime.CURVE_INVERSION, 7,
        ("curve_2s10s",), ("curve_2s10s",),
        _p_curve_inversion,
        MarginSpec("curve_2s10s", lambda c: c.curve_inversion, lambda c: c.scale_curve_inversion, -1),
    ),
    RegimeRule(
        "R08_strong_usd", Regime.STRONG_USD, 8,
        ("usd_level",), ("usd_level",),
        _p_strong_usd,
        MarginSpec("usd_level", lambda c: c.usd_strong, lambda c: c.scale_strong_usd, 1),
    ),
    RegimeRule(
        "R09_risk_on", Regime.RISK_ON, 9,
        ("vol_level", "equity_level"), ("vol_level", "equity_level"),
        _p_risk_on,
        MarginSpec("vol_level", lambda c: c.vix_calm, lambda c: c.scale_risk_on, -1),
    ),
    RegimeRule(
        "R10_low_vol", Regime.LOW_VOL, 10,
        ("vol_level",), ("vol_level",),
        _p_low_vol,
        MarginSpec("vol_level", lambda c: c.vix_calm, lambda c: c.scale_low_vol, -1),
    ),
    RegimeRule(
        "R11_neutral", Regime.NEUTRAL, 11,
        (), (),
        _p_neutral,
        None,
    ),
)
