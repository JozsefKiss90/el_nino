"""Layer-2 Snapshot contract (SCHEMA-001) — read-only models for Layer-3.

These dataclasses mirror the JSON payload published by the Layer-2 engine
(Mr. Ripley) `snapshot_publisher.py` (`write_snapshot_json`). They are the
Layer-3 *consumer's* view of the contract: only the fields the consumer needs
to enforce the consumption gate and to expose the per-series truth are modelled.
Fields present in the payload but not yet needed downstream (revision_policy,
tier1_series/tier2_series convenience maps, values_by_group, layer1_events,
run_ts/published_at) are intentionally not modelled in this minimal slice; they
remain available in the raw payload and can be promoted to typed fields when a
consumer needs them.

Grounded against the real artifact `snapshot_sources/latest_snapshot.json`.
Per ADR-003: stdlib frozen dataclasses, zero runtime dependencies, fail-closed.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Mapping


class SnapshotContractError(ValueError):
    """A payload violates the Layer-2 Snapshot contract (SCHEMA-001).

    Raised for *structural* breaches (missing required key, wrong shape) — an
    upstream truth-layer fault that Layer-3 must surface loudly, NOT silently
    treat as "no snapshot". Legitimate absence (no file) and a failed/forced
    quality gate are handled by the consumer returning ``None`` instead.
    """


def _require(payload: Mapping[str, Any], key: str) -> Any:
    if key not in payload:
        raise SnapshotContractError(f"missing required key: {key!r}")
    return payload[key]


@dataclass(frozen=True)
class SeriesValue:
    """A single point-in-time series observation inside a snapshot."""

    series_id: str
    tier: int
    group: str
    obs_ts: str
    value: float
    staleness_days: int
    source: str
    as_of_ts: str | None
    revision_seq: int
    revision_risk: bool

    @classmethod
    def from_grouped_entry(cls, entry: Mapping[str, Any]) -> "SeriesValue":
        """Parse one entry from the payload's ``values_by_group`` lists.

        That representation carries full fidelity (series_id + group + tier +
        as_of_ts + revision_seq), unlike the ``values`` / ``tierN_series`` maps
        which each drop one of those fields.
        """
        try:
            return cls(
                series_id=str(_require(entry, "series_id")),
                tier=int(_require(entry, "tier")),
                group=str(_require(entry, "group")),
                obs_ts=str(_require(entry, "obs_ts")),
                value=float(_require(entry, "value")),
                staleness_days=int(_require(entry, "staleness_days")),
                source=str(_require(entry, "source")),
                as_of_ts=(entry.get("as_of_ts") if entry.get("as_of_ts") else None),
                revision_seq=int(entry.get("revision_seq", 0)),
                revision_risk=bool(entry.get("revision_risk", False)),
            )
        except (TypeError, ValueError) as exc:
            if isinstance(exc, SnapshotContractError):
                raise
            raise SnapshotContractError(
                f"malformed series entry {entry.get('series_id', '?')!r}: {exc}"
            ) from exc

    def _id_line(self) -> str:
        """The series' contribution to the deterministic snapshot identity hash.

        Mirrors `compute_snapshot_id` in the Layer-2 publisher exactly:
        ``<series_id>=<obs_ts>:<value:.6f>:<as_of_ts>:<revision_seq>``.
        """
        as_of = self.as_of_ts or ""
        return f"{self.series_id}={self.obs_ts}:{float(self.value):.6f}:{as_of}:{self.revision_seq}"


@dataclass(frozen=True)
class Guards:
    """The snapshot's gate flags. ``snapshot_ok`` is the binding quality verdict.

    ``risk_ok``, ``supervisor_veto`` and ``cooldown_ok`` are Layer-3 stubs in the
    Layer-2 output (defaults) — they are filled by the Risk Desk / Supervisor
    downstream, not by the truth layer. Read tolerantly so an evolving guard
    block (new keys) does not break ingestion.
    """

    snapshot_ok: bool
    data_ok: bool
    freshness_ok: bool
    missing_tier1: bool
    forced: bool
    revision_risk_present: bool
    idempotent_ok: bool
    reason_code: str
    cooldown_ok: bool
    risk_ok: bool
    supervisor_veto: bool

    @classmethod
    def from_dict(cls, d: Mapping[str, Any]) -> "Guards":
        if not isinstance(d, Mapping):
            raise SnapshotContractError("'guards' must be an object")
        return cls(
            snapshot_ok=bool(_require(d, "snapshot_ok")),
            data_ok=bool(d.get("data_ok", False)),
            freshness_ok=bool(d.get("freshness_ok", False)),
            missing_tier1=bool(d.get("missing_tier1", False)),
            forced=bool(d.get("forced", False)),
            revision_risk_present=bool(d.get("revision_risk_present", False)),
            idempotent_ok=bool(d.get("idempotent_ok", False)),
            reason_code=str(d.get("reason_code", "")),
            cooldown_ok=bool(d.get("cooldown_ok", False)),
            risk_ok=bool(d.get("risk_ok", False)),
            supervisor_veto=bool(d.get("supervisor_veto", False)),
        )


@dataclass(frozen=True)
class QualitySummary:
    """Tier pass/warn counts from the Layer-2 quality gate."""

    tier1_total: int
    tier1_pass: int
    tier1_fail: int
    tier2_total: int
    tier2_warn: int
    revision_risk_series_count: int
    revision_risk_series: tuple[str, ...]

    @classmethod
    def from_dict(cls, d: Mapping[str, Any]) -> "QualitySummary":
        if not isinstance(d, Mapping):
            raise SnapshotContractError("'quality_summary' must be an object")
        return cls(
            tier1_total=int(d.get("tier1_total", 0)),
            tier1_pass=int(d.get("tier1_pass", 0)),
            tier1_fail=int(d.get("tier1_fail", 0)),
            tier2_total=int(d.get("tier2_total", 0)),
            tier2_warn=int(d.get("tier2_warn", 0)),
            revision_risk_series_count=int(d.get("revision_risk_series_count", 0)),
            revision_risk_series=tuple(str(s) for s in d.get("revision_risk_series", [])),
        )


@dataclass(frozen=True)
class Snapshot:
    """A Layer-2 truth snapshot as seen by Layer-3 (SCHEMA-001).

    Immutable and self-contained: a snapshot makes no reference to any prior
    snapshot (temporal independence is a Layer-2 invariant).
    """

    snapshot_id: str
    engine_version: str
    config_version: str
    clock_ts: str
    clock_date: str
    verdict: str
    forced: bool
    dry_run: bool
    guards: Guards
    quality_summary: QualitySummary
    missing_series: tuple[str, ...]
    series_count: int
    values: dict[str, SeriesValue]

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "Snapshot":
        if not isinstance(payload, Mapping):
            raise SnapshotContractError("snapshot payload must be a JSON object")

        grouped = _require(payload, "values_by_group")
        if not isinstance(grouped, Mapping):
            raise SnapshotContractError("'values_by_group' must be an object")

        values: dict[str, SeriesValue] = {}
        for group_name, entries in grouped.items():
            if not isinstance(entries, list):
                raise SnapshotContractError(
                    f"'values_by_group[{group_name}]' must be a list"
                )
            for entry in entries:
                sv = SeriesValue.from_grouped_entry(entry)
                if sv.series_id in values:
                    raise SnapshotContractError(
                        f"duplicate series_id in snapshot: {sv.series_id!r}"
                    )
                values[sv.series_id] = sv

        return cls(
            snapshot_id=str(_require(payload, "snapshot_id")),
            engine_version=str(_require(payload, "engine_version")),
            config_version=str(_require(payload, "config_version")),
            clock_ts=str(_require(payload, "clock_ts")),
            clock_date=str(_require(payload, "clock_date")),
            verdict=str(_require(payload, "verdict")),
            forced=bool(payload.get("forced", False)),
            dry_run=bool(payload.get("dry_run", False)),
            guards=Guards.from_dict(_require(payload, "guards")),
            quality_summary=QualitySummary.from_dict(payload.get("quality_summary", {})),
            missing_series=tuple(str(s) for s in payload.get("missing_series", [])),
            series_count=int(payload.get("series_count", len(values))),
            values=values,
        )

    def recompute_id(self) -> str:
        """Re-derive the deterministic SHA-256 snapshot identity from content.

        Mirrors the Layer-2 publisher's `compute_snapshot_id`. Equality with
        ``snapshot_id`` proves the payload was not tampered with between
        publication and consumption (a Layer-3 integrity check).
        """
        lines = [
            f"clock_ts={self.clock_ts}",
            f"engine_version={self.engine_version}",
            f"config_version={self.config_version}",
        ]
        for sv in sorted(self.values.values(), key=lambda s: s.series_id):
            lines.append(sv._id_line())
        payload = "\n".join(lines) + "\n"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @property
    def id_matches(self) -> bool:
        """True iff the recomputed identity equals the published ``snapshot_id``."""
        return self.recompute_id() == self.snapshot_id
