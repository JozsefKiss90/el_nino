"""Execution + fill-model policy config — versioned, fail-closed (ADR-011 §2 / gate b).

``ExecutionPolicyConfig`` carries the v0 *fixed* paper size (sizing is deferred, ADR-011 D2) + the
virtual paper equity the guard validates against. ``FillModelConfig`` carries the deterministic
fill/slippage policy + its ``fill_model_version``. Each exposes a ``fingerprint()`` (SHA-256 over
the policy-defining fields, version excluded) that folds into the execution replay key — a silent
edit without a version bump changes the hash and a CI coherence test fails, exactly mirroring
``runtime_policy_fingerprint`` / ``decision_policy_fingerprint``. Loaders are fail-closed; IO lives
at the boundary so ``execute`` stays pure. Per ADR-003: stdlib frozen dataclasses, zero deps.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any, Mapping

EXECUTION_POLICY_VERSION = "0.1.0"
FILL_MODEL_VERSION = "0.1.0"


class ExecutionPolicyConfigError(ValueError):
    """Raised when an execution / fill-model config is missing or invalid (fail closed)."""


# Fields that define the fill model (version excluded by construction).
_FILL_FIELDS: tuple[str, ...] = ("slippage_bps",)
# Fields that define the execution policy (version excluded by construction).
_EXEC_FIELDS: tuple[str, ...] = ("default_size", "instrument", "paper_equity")


@dataclass(frozen=True)
class FillModelConfig:
    """v0 deterministic fill model: a fixed adverse slippage in bps (no clock/randomness).

    The seeded micro-jitter sketched in ADR-011 gate (b) is a future enhancement; v0 is a flat
    ``slippage_bps`` so a buy fills at ``instrument_price * (1 + slippage_bps / 1e4)``.
    """

    slippage_bps: float = 5.0
    fill_model_version: str = FILL_MODEL_VERSION

    def __post_init__(self) -> None:
        if not self.fill_model_version:
            raise ExecutionPolicyConfigError("fill_model_version must be a non-empty string")
        if self.slippage_bps < 0:
            raise ExecutionPolicyConfigError("slippage_bps must be >= 0")

    def fingerprint(self) -> str:
        items: list[tuple[str, Any]] = [(n, getattr(self, n)) for n in sorted(_FILL_FIELDS)]
        payload = json.dumps(items, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any]) -> "FillModelConfig":
        if not isinstance(mapping, Mapping):
            raise ExecutionPolicyConfigError("fill model config must be a mapping")
        known = {f.name for f in fields(cls)}
        unknown = set(mapping) - known
        if unknown:
            raise ExecutionPolicyConfigError(f"unknown fill model config keys: {sorted(unknown)}")
        if "fill_model_version" not in mapping:
            raise ExecutionPolicyConfigError("config must specify fill_model_version")
        kwargs = {f.name: mapping[f.name] for f in fields(cls) if f.name in mapping}
        try:
            return cls(**kwargs)
        except (TypeError, ValueError) as exc:
            raise ExecutionPolicyConfigError(str(exc)) from exc


@dataclass(frozen=True)
class ExecutionPolicyConfig:
    """v0 execution policy: the fixed paper size + the instrument + the virtual paper equity."""

    default_size: float = 1.0          # the FIXED v0 paper size (ADR-011 D2 — sizing deferred)
    instrument: str = "GLD"            # single instrument (multi-instrument is a Non-Goal)
    paper_equity: float = 100_000.0    # virtual account equity the guard validates against
    execution_policy_version: str = EXECUTION_POLICY_VERSION

    def __post_init__(self) -> None:
        if not self.execution_policy_version:
            raise ExecutionPolicyConfigError("execution_policy_version must be a non-empty string")
        if self.default_size <= 0:
            raise ExecutionPolicyConfigError("default_size must be > 0")
        if self.paper_equity <= 0:
            raise ExecutionPolicyConfigError("paper_equity must be > 0")

    def fingerprint(self) -> str:
        items: list[tuple[str, Any]] = [(n, getattr(self, n)) for n in sorted(_EXEC_FIELDS)]
        payload = json.dumps(items, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any]) -> "ExecutionPolicyConfig":
        if not isinstance(mapping, Mapping):
            raise ExecutionPolicyConfigError("execution policy config must be a mapping")
        known = {f.name for f in fields(cls)}
        unknown = set(mapping) - known
        if unknown:
            raise ExecutionPolicyConfigError(f"unknown execution config keys: {sorted(unknown)}")
        if "execution_policy_version" not in mapping:
            raise ExecutionPolicyConfigError("config must specify execution_policy_version")
        kwargs = {f.name: mapping[f.name] for f in fields(cls) if f.name in mapping}
        try:
            return cls(**kwargs)
        except (TypeError, ValueError) as exc:
            raise ExecutionPolicyConfigError(str(exc)) from exc


def load_config(path: str | Path) -> ExecutionPolicyConfig:
    """Read a JSON execution-policy config file into an ExecutionPolicyConfig, fail-closed."""
    p = Path(path)
    try:
        raw = p.read_text(encoding="utf-8")
    except OSError as exc:
        raise ExecutionPolicyConfigError(f"cannot read execution policy config {p}: {exc}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ExecutionPolicyConfigError(f"invalid execution policy config JSON {p}: {exc}") from exc
    return ExecutionPolicyConfig.from_mapping(data)


# The canonical v0 configurations. execute() / the adapters default to these.
DEFAULT_FILL_MODEL = FillModelConfig()
DEFAULT_EXECUTION_POLICY_CONFIG = ExecutionPolicyConfig()
