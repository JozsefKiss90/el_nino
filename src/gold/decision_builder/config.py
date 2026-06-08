"""DecisionPolicyConfig — versioned, fail-closed gold decision policy (ADR-008 §7).

Holds BOTH the v0 confidence weights AND the regime->direction table, governed by a single
``decision_policy_version``. ``decision_policy_fingerprint`` binds the version to its policy
set — a coherence test fails CI if a weight or a table cell is edited without bumping the
version (mirroring the regime ``decision_fingerprint``). Loaders are fail-closed
(``DecisionPolicyConfigError``); the IO lives at the boundary so ``build_decision`` stays a
pure function of (FeatureVector, RegimeClassification, DecisionPolicyConfig).

The regime->direction table is **decision-policy config, not an ADR** (no separation hazard
comparable to confidence; gold-internal, paper-only). The per-regime gold thesis is
domain-anchored and **provisional** — economic recalibration is a future
``decision_policy_version`` bump, not a rebuild. See GOLD_DECISIONPACKET_V0_BRIEF.md.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any, Mapping

from regime.regime_classifier import Regime

from .models import Direction

DECISION_POLICY_VERSION = "0.1.0"


class DecisionPolicyConfigError(ValueError):
    """Raised when a gold decision policy config is missing or invalid (fail closed)."""


# Canonical v0 regime->direction table. PROVISIONAL / domain-anchored (no corpus to fit to);
# a change is a governed ``decision_policy_version`` bump. Total over all 12 Regime values;
# INDETERMINATE -> WATCH (fail-closed). Gold thesis per cell is in GOLD_DECISIONPACKET_V0_BRIEF.md.
DEFAULT_DIRECTION_TABLE: tuple[tuple[str, str], ...] = (
    ("LIQUIDITY_STRESS", "LONG"),   # funding-stress haven bid
    ("RISK_OFF", "LONG"),           # risk-off haven bid
    ("VOLATILE", "FLAT"),           # elevated vol, direction unclear
    ("RESTRICTIVE_RATES", "AVOID"),  # high real yields are a gold headwind
    ("REFLATION", "LONG"),          # rising inflation expectations + easy real rates
    ("DISINFLATION", "AVOID"),      # falling inflation expectations
    ("CURVE_INVERSION", "WATCH"),   # recession signal, mixed for gold
    ("STRONG_USD", "AVOID"),        # strong USD headwind
    ("RISK_ON", "FLAT"),            # risk appetite competes with gold
    ("LOW_VOL", "FLAT"),            # calm, no edge
    ("NEUTRAL", "FLAT"),            # no signal
    ("INDETERMINATE", "WATCH"),     # fail-closed — no stance
)

# Fields that define the decision policy (confidence weights + floors + direction table +
# instrument). A change to any of these alters a packet's confidence/uncertainty/direction,
# so it MUST be accompanied by a ``decision_policy_version`` bump. The version is excluded.
_DECISION_FIELDS: tuple[str, ...] = (
    "ambiguity_weight",
    "fragility_weight",
    "staleness_weight",
    "staleness_cap",
    "revision_penalty",
    "coverage_weight",
    "coverage_cap",
    "neutral_confidence_floor",
    "indeterminate_confidence",
    "indeterminate_uncertainty",
    "instrument",
    "direction_table",
)


@dataclass(frozen=True)
class DecisionPolicyConfig:
    """v0 confidence weights + regime->direction table + version (decision_policy_version)."""

    # --- confidence weights (ADR-008 ordinal trust score) ---
    ambiguity_weight: float = 0.15      # discount per secondary (ambiguity) match
    fragility_weight: float = 0.10      # discount per near (fragility) match
    staleness_weight: float = 0.02      # discount per cited-feature staleness day
    staleness_cap: float = 0.50         # max staleness discount
    revision_penalty: float = 0.15      # discount if any cited feature is revisable
    coverage_weight: float = 0.05       # discount per unavailable feature
    coverage_cap: float = 0.50          # max coverage discount
    neutral_confidence_floor: float = 0.50   # NEUTRAL confident-quiet floor (not naive-zero)
    indeterminate_confidence: float = 0.0    # INDETERMINATE fail-closed minimum confidence
    indeterminate_uncertainty: float = 1.0   # INDETERMINATE maximum uncertainty
    # --- regime -> direction policy table ---
    direction_table: tuple[tuple[str, str], ...] = DEFAULT_DIRECTION_TABLE
    # --- fixed v0 instrument + version ---
    instrument: str = "GLD"
    decision_policy_version: str = DECISION_POLICY_VERSION

    def __post_init__(self) -> None:
        for name in (
            "ambiguity_weight",
            "fragility_weight",
            "staleness_weight",
            "coverage_weight",
            "revision_penalty",
        ):
            if getattr(self, name) < 0.0:
                raise DecisionPolicyConfigError(f"{name} must be >= 0")
        for name in (
            "staleness_cap",
            "coverage_cap",
            "neutral_confidence_floor",
            "indeterminate_confidence",
            "indeterminate_uncertainty",
        ):
            if not 0.0 <= getattr(self, name) <= 1.0:
                raise DecisionPolicyConfigError(f"{name} must be in [0, 1]")
        # direction table: total over all regimes, valid directions, INDETERMINATE -> WATCH
        table = dict(self.direction_table)
        if len(table) != len(self.direction_table):
            raise DecisionPolicyConfigError("direction_table has duplicate regimes")
        regimes = {r.value for r in Regime}
        if set(table) != regimes:
            missing = sorted(regimes - set(table))
            extra = sorted(set(table) - regimes)
            raise DecisionPolicyConfigError(
                f"direction_table must be total over all regimes (missing={missing}, extra={extra})"
            )
        valid = {d.value for d in Direction}
        for regime_value, direction_value in self.direction_table:
            if direction_value not in valid:
                raise DecisionPolicyConfigError(
                    f"invalid direction {direction_value!r} for regime {regime_value!r}"
                )
        if table["INDETERMINATE"] != Direction.WATCH.value:
            raise DecisionPolicyConfigError("INDETERMINATE must map to WATCH (fail-closed)")
        if not self.decision_policy_version:
            raise DecisionPolicyConfigError("decision_policy_version must be a non-empty string")

    def direction_for(self, regime_value: str) -> Direction:
        """Look up the gold direction for a regime (totality guaranteed by __post_init__)."""
        for regime, direction in self.direction_table:
            if regime == regime_value:
                return Direction(direction)
        raise DecisionPolicyConfigError(f"no direction for regime {regime_value!r}")

    def decision_policy_fingerprint(self) -> str:
        """SHA-256 over the decision-defining fields (weights + floors + table + instrument).

        Binds ``decision_policy_version`` to its policy set: a silent edit to any decision
        field without a version bump changes this hash and fails CI. The version string is
        excluded by construction.
        """
        items: list[tuple[str, Any]] = []
        for name in sorted(_DECISION_FIELDS):
            value = getattr(self, name)
            if name == "direction_table":
                value = [list(pair) for pair in value]
            items.append((name, value))
        payload = json.dumps(items, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any]) -> "DecisionPolicyConfig":
        """Build a config from a mapping, fail-closed. Unknown keys / absent version raise."""
        if not isinstance(mapping, Mapping):
            raise DecisionPolicyConfigError("config must be a mapping")
        known = {f.name for f in fields(cls)}
        unknown = set(mapping) - known
        if unknown:
            raise DecisionPolicyConfigError(f"unknown config keys: {sorted(unknown)}")
        if "decision_policy_version" not in mapping:
            raise DecisionPolicyConfigError("config must specify decision_policy_version")
        kwargs: dict[str, Any] = {}
        for f in fields(cls):
            if f.name not in mapping:
                continue
            value = mapping[f.name]
            if f.name == "direction_table":
                try:
                    value = tuple((str(r), str(d)) for r, d in value)
                except (TypeError, ValueError) as exc:
                    raise DecisionPolicyConfigError(
                        "direction_table must be a list of [regime, direction] pairs"
                    ) from exc
            kwargs[f.name] = value
        try:
            return cls(**kwargs)
        except (TypeError, ValueError) as exc:  # includes DecisionPolicyConfigError
            raise DecisionPolicyConfigError(str(exc)) from exc


def load_config(path: str | Path) -> DecisionPolicyConfig:
    """Read a JSON config file into a DecisionPolicyConfig, fail-closed."""
    p = Path(path)
    try:
        raw = p.read_text(encoding="utf-8")
    except OSError as exc:
        raise DecisionPolicyConfigError(f"cannot read decision policy config {p}: {exc}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise DecisionPolicyConfigError(f"invalid decision policy config JSON {p}: {exc}") from exc
    return DecisionPolicyConfig.from_mapping(data)


# The canonical v0 configuration. build_decision() defaults to this.
DEFAULT_DECISION_POLICY_CONFIG = DecisionPolicyConfig()
