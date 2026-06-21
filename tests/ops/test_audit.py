"""Headless tests for the append-only audit log (ADR-013 sec.7)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from ops import audit


def _fixed_clock() -> datetime:
    return datetime(2026, 6, 18, 12, 0, 0, tzinfo=timezone.utc)


def test_append_then_read_roundtrip(tmp_path: Path) -> None:
    log = tmp_path / "ops" / "audit_log.jsonl"
    e1 = audit.append_audit(log, "run-chain-now", "port=simulated", "verdict=ADMIT", True, clock=_fixed_clock)
    audit.append_audit(log, "resync-neo4j", "--clear", "exit=1 (failed)", False, clock=_fixed_clock)
    assert e1.timestamp == "2026-06-18T12:00:00Z"
    entries = audit.read_audit(log)
    assert len(entries) == 2
    assert entries[0].action == "run-chain-now" and entries[0].ok is True
    assert entries[1].action == "resync-neo4j" and entries[1].ok is False


def test_append_only_never_truncates(tmp_path: Path) -> None:
    log = tmp_path / "audit.jsonl"
    for i in range(5):
        audit.append_audit(log, f"act-{i}", "args", "ok", True, clock=_fixed_clock)
    assert len(audit.read_audit(log, limit=100)) == 5


def test_read_limit_tails(tmp_path: Path) -> None:
    log = tmp_path / "audit.jsonl"
    for i in range(10):
        audit.append_audit(log, f"act-{i}", "args", "ok", True, clock=_fixed_clock)
    tail = audit.read_audit(log, limit=3)
    assert [e.action for e in tail] == ["act-7", "act-8", "act-9"]


def test_file_is_ascii_even_with_unicode_result(tmp_path: Path) -> None:
    log = tmp_path / "audit.jsonl"
    audit.append_audit(log, "act", "args", "regime=RESTRICTIVE_RATES section-6 ≥ floor", True,
                       clock=_fixed_clock)
    raw = log.read_bytes()
    assert all(b < 128 for b in raw)  # ensure_ascii=True escaped the non-ASCII char


def test_read_absent_returns_empty(tmp_path: Path) -> None:
    assert audit.read_audit(tmp_path / "nope.jsonl") == ()


def test_read_skips_malformed_lines(tmp_path: Path) -> None:
    log = tmp_path / "audit.jsonl"
    audit.append_audit(log, "good", "args", "ok", True, clock=_fixed_clock)
    with log.open("a", encoding="utf-8") as fh:
        fh.write("{not json\n")
        fh.write("\n")
    entries = audit.read_audit(log)
    assert len(entries) == 1 and entries[0].action == "good"


def test_line_format() -> None:
    e = audit.AuditEntry("2026-06-18T12:00:00Z", "run-chain-now", "port=simulated", "verdict=ADMIT", True)
    line = e.line()
    assert "run-chain-now" in line and "verdict=ADMIT" in line and "[OK " in line
