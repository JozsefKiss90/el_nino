"""RegimeConfig — config-driven, versioned, fail-closed regime thresholds (ADR-007 / R2).

Every numeric *decision threshold* and every *rule-margin scale* lives here, not as a
free-floating constant in ``taxonomy.py``; predicates and margin functions read them from
the passed config. ``taxonomy_version`` versions the decision-threshold set — a fingerprint
coherence check (``decision_fingerprint``) lets a test fail CI if a threshold/scale is
edited without bumping the version. ``near_band`` is a *trace* parameter (governed by
``classification_trace_version``) and is deliberately excluded from the fingerprint.

``load_config`` / ``from_mapping`` are fail-closed (raise ``RegimeConfigError``), mirroring
the Guardrail Engine's ``GuardrailConfigError`` policy (ADR-003): the I/O lives at the
boundary so ``classify()`` stays a pure function of (FeatureVector, RegimeConfig).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any, Mapping

from .models import (
    CLASSIFICATION_TRACE_VERSION,
    CLASSIFIER_VERSION,
    TAXONOMY_VERSION,
)


class RegimeConfigError(ValueError):
    """Raised when a regime configuration is missing or invalid (fail closed)."""


# Fields that define a *decision-group* output (regime selection thresholds + margin scales
# + the required-feature gate). A change to any of these alters `regime`/`matched_rule_id`
# and/or `rule_margin`, so it MUST be accompanied by a `taxonomy_version` bump. `near_band`
# and the version strings are intentionally excluded.
_DECISION_FIELDS: tuple[str, ...] = (
    "vix_calm",
    "vix_elevated",
    "vix_crisis",
    "vix_liquidity_gate",
    "move_stress",
    "real_yield_restrictive",
    "real_yield_easy",
    "be5y5y_reflation",
    "be5y5y_disinflation",
    "curve_inversion",
    "usd_strong",
    "scale_liquidity_stress",
    "scale_risk_off",
    "scale_volatile",
    "scale_restrictive_rates",
    "scale_reflation",
    "scale_disinflation",
    "scale_curve_inversion",
    "scale_strong_usd",
    "scale_risk_on",
    "scale_low_vol",
    "required_features",
)


@dataclass(frozen=True)
class RegimeConfig:
    """Domain-anchored thresholds + margin scales + versions for the regime taxonomy.

    Defaults are the canonical v1.0.0 anchor set (``DEFAULT_REGIME_CONFIG``). Anchors are
    standard macro bands (VIX 15/25/35, MOVE 125, real-yield +1.5%, 5y5y breakeven 2.0/2.5,
    curve inversion at 0, broad-USD 120) — not data-fitted (no corpus exists to fit to).
    """

    # vol (VIX-like) bands
    vix_calm: float = 15.0
    vix_elevated: float = 25.0
    vix_crisis: float = 35.0
    vix_liquidity_gate: float = 30.0
    # rates vol (MOVE-like) stress line
    move_stress: float = 125.0
    # real yields
    real_yield_restrictive: float = 1.50
    real_yield_easy: float = 1.00
    # 5y5y forward breakeven
    be5y5y_reflation: float = 2.50
    be5y5y_disinflation: float = 2.00
    # yield curve (2s10s) inversion anchor
    curve_inversion: float = 0.0
    # trade-weighted broad USD strong band
    usd_strong: float = 120.0
    # per-rule margin scales (the "full-margin" band width of each deciding feature)
    scale_liquidity_stress: float = 50.0
    scale_risk_off: float = 15.0
    scale_volatile: float = 10.0
    scale_restrictive_rates: float = 1.0
    scale_reflation: float = 0.5
    scale_disinflation: float = 0.5
    scale_curve_inversion: float = 0.5
    scale_strong_usd: float = 10.0
    scale_risk_on: float = 5.0
    scale_low_vol: float = 5.0
    # trace-only: near-activation band, as a fraction of each rule's scale
    near_band: float = 0.25
    # the global required-feature gate (absent => INDETERMINATE)
    required_features: tuple[str, ...] = (
        "vol_level",
        "real_yield_10y",
        "curve_2s10s",
        "usd_level",
    )
    # versions
    taxonomy_version: str = TAXONOMY_VERSION
    classifier_version: str = CLASSIFIER_VERSION
    classification_trace_version: str = CLASSIFICATION_TRACE_VERSION

    def __post_init__(self) -> None:
        scales = (
            self.scale_liquidity_stress,
            self.scale_risk_off,
            self.scale_volatile,
            self.scale_restrictive_rates,
            self.scale_reflation,
            self.scale_disinflation,
            self.scale_curve_inversion,
            self.scale_strong_usd,
            self.scale_risk_on,
            self.scale_low_vol,
        )
        if any(s <= 0.0 for s in scales):
            raise RegimeConfigError("all margin scales must be > 0")
        if self.near_band <= 0.0:
            raise RegimeConfigError("near_band must be > 0")
        if not (self.vix_calm < self.vix_elevated < self.vix_crisis):
            raise RegimeConfigError("VIX bands must satisfy calm < elevated < crisis")
        if self.be5y5y_disinflation > self.be5y5y_reflation:
            raise RegimeConfigError("be5y5y_disinflation must not exceed be5y5y_reflation")
        if not self.required_features:
            raise RegimeConfigError("required_features must be non-empty")
        for name in ("taxonomy_version", "classifier_version", "classification_trace_version"):
            if not getattr(self, name):
                raise RegimeConfigError(f"{name} must be a non-empty string")

    def decision_fingerprint(self) -> str:
        """SHA-256 over the decision-defining fields (thresholds, scales, required gate).

        Used by a coherence test to bind ``taxonomy_version`` to its threshold set: a silent
        edit to any decision field without a version bump changes this hash and fails CI.
        ``near_band`` and version strings are excluded by construction.
        """
        items: list[tuple[str, Any]] = []
        for name in sorted(_DECISION_FIELDS):
            value = getattr(self, name)
            if isinstance(value, tuple):
                value = list(value)
            items.append((name, value))
        payload = json.dumps(items, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any]) -> "RegimeConfig":
        """Build a config from a mapping, fail-closed. Unknown keys / absent version raise."""
        if not isinstance(mapping, Mapping):
            raise RegimeConfigError("config must be a mapping")
        known = {f.name for f in fields(cls)}
        unknown = set(mapping) - known
        if unknown:
            raise RegimeConfigError(f"unknown config keys: {sorted(unknown)}")
        if "taxonomy_version" not in mapping:
            raise RegimeConfigError("config must specify taxonomy_version")
        kwargs: dict[str, Any] = {}
        for f in fields(cls):
            if f.name not in mapping:
                continue
            value = mapping[f.name]
            if f.name == "required_features":
                if not isinstance(value, (list, tuple)) or not all(isinstance(x, str) for x in value):
                    raise RegimeConfigError("required_features must be a list of strings")
                value = tuple(value)
            kwargs[f.name] = value
        try:
            return cls(**kwargs)
        except (TypeError, ValueError) as exc:  # includes RegimeConfigError from __post_init__
            raise RegimeConfigError(str(exc)) from exc


def load_config(path: str | Path) -> RegimeConfig:
    """Read a JSON config file into a RegimeConfig, fail-closed (RegimeConfigError)."""
    p = Path(path)
    try:
        raw = p.read_text(encoding="utf-8")
    except OSError as exc:
        raise RegimeConfigError(f"cannot read regime config {p}: {exc}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RegimeConfigError(f"invalid regime config JSON {p}: {exc}") from exc
    return RegimeConfig.from_mapping(data)


# The canonical v1.0.0 configuration. classify() defaults to this.
DEFAULT_REGIME_CONFIG = RegimeConfig()
