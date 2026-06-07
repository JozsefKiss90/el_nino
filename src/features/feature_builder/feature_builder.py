"""Feature Builder (MOD-004) — deterministic SCHEMA-001 -> Feature Vector transform.

`build_features(snapshot)` is a total, pure function: it reads only the snapshot's
series values and a fixed feature registry, and returns a `FeatureVector`. No IO,
no clock, no randomness, no history. Same `snapshot_id` + `FEATURE_SCHEMA_VERSION`
always yield an identical vector (ADR-005 determinism rule).

Allowed feature classes (ADR-005): levels, spreads, ratios, arithmetic transforms.
Forbidden: anything needing history (moving averages, momentum, z-scores,
percentiles, rolling windows, smoothing, inferred regimes, learned embeddings).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping

from snapshot.snapshot_consumer.models import SeriesValue, Snapshot

from .models import FEATURE_SCHEMA_VERSION, Feature, FeatureVector

# A feature's pure compute function: snapshot series-map -> value.
ComputeFn = Callable[[Mapping[str, SeriesValue]], float]


@dataclass(frozen=True)
class FeatureSpec:
    """Declarative definition of one feature: its inputs and a pure compute fn.

    `inputs` must list every SCHEMA-001 series_id the value depends on, so
    provenance (max staleness, revision risk) can be derived mechanically.
    """

    name: str
    inputs: tuple[str, ...]
    fn: ComputeFn


def _level(name: str, series_id: str) -> FeatureSpec:
    """A level feature — the direct value of one series."""
    return FeatureSpec(name, (series_id,), lambda v, _s=series_id: v[_s].value)


def _spread(name: str, minuend: str, subtrahend: str) -> FeatureSpec:
    """A spread feature — `minuend - subtrahend`."""
    return FeatureSpec(
        name,
        (minuend, subtrahend),
        lambda v, _a=minuend, _b=subtrahend: v[_a].value - v[_b].value,
    )


# v0.1.0 feature set. Levels and spreads only — every input is a real SCHEMA-001
# series. No history-dependent feature appears here (ADR-005).
FEATURE_REGISTRY: tuple[FeatureSpec, ...] = (
    _level("real_yield_10y", "DFII10"),
    _level("real_yield_5y", "DFII5"),
    _level("breakeven_10y", "T10YIE"),
    _level("breakeven_5y", "T5YIE"),
    _level("breakeven_5y5y_fwd", "T5YIFR"),
    _spread("curve_2s10s", "DGS10", "DGS2"),
    _spread("curve_5s10s", "DGS10", "DGS5"),
    _spread("policy_spread", "EFFR", "DFF"),
    _level("usd_level", "DTWEXBGS"),
    _level("vol_level", "VIXCLS"),
    _level("rates_vol", "rates_vol_stress_move"),
    _level("equity_level", "SP500"),
    _level("gold_price", "gold_price_proxy"),
    _level("gold_flow", "gld_holdings_flow_confirm"),
)


def build_features(snapshot: Snapshot) -> FeatureVector:
    """Transform a validated snapshot into a deterministic, provenance-tagged vector.

    The snapshot is assumed already consumed/gated by MOD-003 (verdict PASS). This
    function only transforms; it does not re-gate, read files, or touch IO.

    A feature whose input series are not all present in the snapshot is omitted and
    its name recorded in ``unavailable_features`` — never emitted with a partial or
    invented value. Features are name-sorted for deterministic ordering.
    """
    values = snapshot.values
    features: dict[str, Feature] = {}
    unavailable: list[str] = []

    for spec in sorted(FEATURE_REGISTRY, key=lambda s: s.name):
        if any(series_id not in values for series_id in spec.inputs):
            unavailable.append(spec.name)
            continue
        features[spec.name] = Feature(
            name=spec.name,
            value=spec.fn(values),
            inputs=spec.inputs,
            max_staleness_days=max(values[s].staleness_days for s in spec.inputs),
            revision_risk=any(values[s].revision_risk for s in spec.inputs),
        )

    return FeatureVector(
        snapshot_id=snapshot.snapshot_id,
        schema_version=FEATURE_SCHEMA_VERSION,
        features=features,
        unavailable_features=tuple(unavailable),
    )
