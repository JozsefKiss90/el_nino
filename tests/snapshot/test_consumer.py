"""Tests for the Snapshot Consumer fail-closed gate (MOD-003 / INT-001).

Verifies the Layer-3 consumption contract: a clean PASS snapshot is returned;
a failed gate, a forced bypass, a dry-run, or an absent file all yield nothing;
a structurally malformed snapshot raises rather than masquerading as absence.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from snapshot.snapshot_consumer import (
    Snapshot,
    SnapshotContractError,
    consume,
    is_consumable,
    load_snapshot,
)

FIXTURES = Path(__file__).parent / "fixtures"
PASS = FIXTURES / "latest_snapshot_pass.json"
FAIL = FIXTURES / "snapshot_fail.json"
FORCED = FIXTURES / "snapshot_forced.json"


def test_consume_returns_pass_snapshot() -> None:
    snap = consume(PASS)
    assert isinstance(snap, Snapshot)
    assert snap.verdict == "PASS"
    assert snap.id_matches is True


def test_is_consumable_true_for_pass() -> None:
    assert is_consumable(load_snapshot(PASS)) is True  # type: ignore[arg-type]


def test_failed_gate_outputs_nothing() -> None:
    assert is_consumable(load_snapshot(FAIL)) is False  # type: ignore[arg-type]
    assert consume(FAIL) is None


def test_forced_snapshot_rejected_fail_closed() -> None:
    # Gate was bypassed (forced); fail-closed means Layer-3 still acts on nothing.
    snap = load_snapshot(FORCED)
    assert snap is not None
    assert snap.forced is True
    assert is_consumable(snap) is False
    assert consume(FORCED) is None


def test_dry_run_snapshot_rejected(tmp_path: Path) -> None:
    payload = json.loads(PASS.read_text(encoding="utf-8"))
    payload["dry_run"] = True
    p = tmp_path / "dry.json"
    p.write_text(json.dumps(payload), encoding="utf-8")
    assert consume(p) is None


def test_absent_file_outputs_nothing(tmp_path: Path) -> None:
    assert load_snapshot(tmp_path / "nope.json") is None
    assert consume(tmp_path / "nope.json") is None


def test_malformed_snapshot_raises_not_silently_none(tmp_path: Path) -> None:
    payload = json.loads(PASS.read_text(encoding="utf-8"))
    del payload["guards"]
    p = tmp_path / "broken.json"
    p.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(SnapshotContractError):
        consume(p)


def test_consume_accepts_str_path() -> None:
    assert consume(str(PASS)) is not None
