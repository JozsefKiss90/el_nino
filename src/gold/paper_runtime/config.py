"""RuntimePolicyConfig — versioned, fail-closed paper-runtime admission policy (ADR-009 §7/§8).

Governs which guards are *required* to ADMIT. ``runtime_policy_fingerprint`` binds the version to
its policy set: a silent edit to a policy field without a ``runtime_policy_version`` bump changes
the hash and fails a CI coherence test (TEST-015), exactly mirroring ``decision_policy_fingerprint``.
Loaders are fail-closed (``RuntimePolicyConfigError``); IO lives at the boundary so ``evaluate``
stays a pure function of (packet, ledger, operational input, config).

v0.2.0 (ADR-009 amendment, 2026-06-18) lifts the deferred **computed cooldown**: the L3 ``cooldown_ok``
guard is now *computed* from runtime state — the gap between the current snapshot's ``as_of`` and the
last ADMIT's recorded ``as_of`` must be ``>= cooldown_window_hours`` — instead of echoing the snapshot's
``cooldown_ok`` flag. The sole time source is the snapshot ``as_of`` (never wall-clock). ``duplicate_ok``
is still always required (once-ever idempotency) and is evaluated FIRST, so an exact re-presentation
always attributes to idempotency, not cooldown. The prior ``v0.1.0`` (echo) behavior is preserved at its
version — this is a replay-key axis change, hence the ``runtime_policy_version`` bump.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any, Mapping

RUNTIME_POLICY_VERSION = "0.2.0"


class RuntimePolicyConfigError(ValueError):
    """Raised when a runtime policy config is missing or invalid (fail closed)."""


# Fields that define the admission policy (require-flags + the cooldown window). The version is
# excluded by construction; a change to any of these alters which packets ADMIT, so it MUST be
# accompanied by a version bump.
_RUNTIME_FIELDS: tuple[str, ...] = (
    "cooldown_window_hours",
    "require_cooldown",
    "require_operational",
    "require_snapshot_guards",
)


@dataclass(frozen=True)
class RuntimePolicyConfig:
    """v0.2.0 admission policy: which guards gate ADMIT (incl. the computed cooldown), plus the version."""

    require_operational: bool = True       # operational_ok must pass to ADMIT
    require_snapshot_guards: bool = True    # data_ok and freshness_ok must pass to ADMIT
    require_cooldown: bool = True           # the computed cooldown_ok must pass to ADMIT (v0.2.0)
    cooldown_window_hours: float = 20.0     # min gap (hours) since the last ADMIT of a DIFFERENT snapshot
    runtime_policy_version: str = RUNTIME_POLICY_VERSION

    def __post_init__(self) -> None:
        if not self.runtime_policy_version:
            raise RuntimePolicyConfigError("runtime_policy_version must be a non-empty string")
        if self.cooldown_window_hours < 0:
            raise RuntimePolicyConfigError("cooldown_window_hours must be >= 0")

    def runtime_policy_fingerprint(self) -> str:
        """SHA-256 over the policy-defining fields (version excluded) — same idiom as the gold config."""
        items: list[tuple[str, Any]] = [(name, getattr(self, name)) for name in sorted(_RUNTIME_FIELDS)]
        payload = json.dumps(items, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any]) -> "RuntimePolicyConfig":
        """Build a config from a mapping, fail-closed. Unknown keys / absent version raise."""
        if not isinstance(mapping, Mapping):
            raise RuntimePolicyConfigError("config must be a mapping")
        known = {f.name for f in fields(cls)}
        unknown = set(mapping) - known
        if unknown:
            raise RuntimePolicyConfigError(f"unknown config keys: {sorted(unknown)}")
        if "runtime_policy_version" not in mapping:
            raise RuntimePolicyConfigError("config must specify runtime_policy_version")
        kwargs: dict[str, Any] = {f.name: mapping[f.name] for f in fields(cls) if f.name in mapping}
        try:
            return cls(**kwargs)
        except (TypeError, ValueError) as exc:  # includes RuntimePolicyConfigError
            raise RuntimePolicyConfigError(str(exc)) from exc


def load_config(path: str | Path) -> RuntimePolicyConfig:
    """Read a JSON config file into a RuntimePolicyConfig, fail-closed."""
    p = Path(path)
    try:
        raw = p.read_text(encoding="utf-8")
    except OSError as exc:
        raise RuntimePolicyConfigError(f"cannot read runtime policy config {p}: {exc}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimePolicyConfigError(f"invalid runtime policy config JSON {p}: {exc}") from exc
    return RuntimePolicyConfig.from_mapping(data)


# The canonical v0 runtime configuration. evaluate() defaults to this.
DEFAULT_RUNTIME_POLICY_CONFIG = RuntimePolicyConfig()
