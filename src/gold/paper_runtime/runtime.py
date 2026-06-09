"""IO boundary shell + replay driver for the paper-trading runtime (MOD-007).

The ONLY IO in the runtime lives here (mirrors ``consume()`` / ``load_config``): load/persist the
ledger and load the operational input. ``run_once`` is the single-step operational entrypoint;
``run_sequence`` threads the ledger in memory over an ordered ``(packet, operational_input)`` list —
the deterministic replay / benchmark vehicle, with **no IO**. The pure core (``evaluate``) never
touches the filesystem, clock, or environment.
"""

from __future__ import annotations

import json
import os
from collections.abc import Sequence
from pathlib import Path
from typing import Union

from gold.decision_builder.models import GoldDecisionPacket

from .config import DEFAULT_RUNTIME_POLICY_CONFIG, RuntimePolicyConfig
from .engine import evaluate
from .models import (
    OperationalInput,
    RuntimeContractError,
    RuntimeDecisionRecord,
    RuntimeLedger,
)

PathLike = Union[str, Path]


def load_ledger(path: PathLike) -> RuntimeLedger:
    """Load a ledger JSON, or an empty ledger if the file is absent (mirrors ``consume()``).

    A *missing* file is a legitimate "no prior state" (returns ``RuntimeLedger.empty()``); a present
    but *malformed* ledger raises ``RuntimeContractError`` — a corrupt state file must be loud, not
    silently treated as "no state".
    """
    p = Path(path)
    if not p.exists():
        return RuntimeLedger.empty()
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeContractError(f"cannot read runtime ledger {p}: {exc}") from exc
    return RuntimeLedger.from_dict(data)


def persist_ledger(path: PathLike, ledger: RuntimeLedger) -> None:
    """Atomically write the ledger as canonical JSON (temp file + ``os.replace``)."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(ledger.to_dict(), sort_keys=True, indent=2) + "\n"
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_text(payload, encoding="utf-8")
    os.replace(tmp, p)


def load_operational(path: PathLike, instrument: str = "GLD") -> OperationalInput:
    """Load operational input, **default-closed** on absence or malformation (ADR-009 §3).

    Absent file or any parse/contract error resolves to ``OperationalInput.closed()`` (not
    tradeable) — the safe direction, which fails ``operational_ok`` and blocks ADMIT.
    """
    p = Path(path)
    if not p.exists():
        return OperationalInput.closed(instrument=instrument)
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return OperationalInput.from_mapping(data)
    except (OSError, json.JSONDecodeError, RuntimeContractError):
        return OperationalInput.closed(instrument=instrument)


def run_once(
    packet: GoldDecisionPacket,
    ledger_path: PathLike,
    operational_path: PathLike,
    config: RuntimePolicyConfig = DEFAULT_RUNTIME_POLICY_CONFIG,
) -> RuntimeDecisionRecord:
    """Single-step operational entrypoint: load state → ``evaluate`` → persist atomically."""
    prior = load_ledger(ledger_path)
    operational = load_operational(operational_path, instrument=packet.instrument)
    record, new_ledger = evaluate(packet, prior, operational, config)
    persist_ledger(ledger_path, new_ledger)
    return record


def run_sequence(
    items: Sequence[tuple[GoldDecisionPacket, OperationalInput]],
    config: RuntimePolicyConfig = DEFAULT_RUNTIME_POLICY_CONFIG,
    ledger: RuntimeLedger | None = None,
) -> tuple[tuple[RuntimeDecisionRecord, ...], RuntimeLedger]:
    """Thread the ledger over an ordered ``(packet, operational_input)`` list — pure, no IO.

    Deterministic order = input order. The vehicle for determinism tests + BENCH-003: replaying the
    same sequence from the same starting ledger yields identical records and an identical ending
    ledger ``state_hash``.
    """
    led = ledger if ledger is not None else RuntimeLedger.empty()
    records: list[RuntimeDecisionRecord] = []
    for packet, operational in items:
        record, led = evaluate(packet, led, operational, config)
        records.append(record)
    return tuple(records), led
