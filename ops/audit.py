"""Append-only audit log for the Operations Control Plane (ADR-013 sec.7).

Every mutating / live console action writes ONE append-only entry: timestamp, action, args-summary,
result, ok. Entries are ASCII JSON lines (``json.dumps`` default ``ensure_ascii=True``) and MUST NOT
contain credentials — callers pass only safe summaries (paths / outcomes), and the live-plug factories
never expose keys (ADR-013 sec.6). The log is a read surface for the console's Log pane; it is an
operational journal of console ACTIONS, never a second source of truth for pipeline state (ADR-013 sec.11).

Stdlib-only (no third-party dependency, no Textual). The clock is injectable so audit timestamps are
deterministic in tests.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

Clock = Callable[[], datetime]


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class AuditEntry:
    timestamp: str
    action: str
    args_summary: str
    result: str
    ok: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "args_summary": self.args_summary,
            "ok": self.ok,
            "result": self.result,
            "timestamp": self.timestamp,
        }

    def line(self) -> str:
        status = "OK " if self.ok else "ERR"
        return f"{self.timestamp} [{status}] {self.action} | {self.args_summary} -> {self.result}"


def make_entry(
    action: str, args_summary: str, result: str, ok: bool, *, clock: Clock | None = None,
) -> AuditEntry:
    """Build an audit entry (no IO) — so a caller can hold the entry even if the write fails."""
    now = (clock or _utc_now)()
    return AuditEntry(
        timestamp=now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        action=action,
        args_summary=args_summary,
        result=result,
        ok=ok,
    )


def write_entry(audit_path: Path, entry: AuditEntry) -> None:
    """Append one ASCII JSON line (creating parents). May raise ``OSError`` — callers guard if they
    must not raise (see ``ops.actions._finish``, which keeps the action fail-closed)."""
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    with audit_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry.to_dict(), ensure_ascii=True, sort_keys=True) + "\n")


def append_audit(
    audit_path: Path,
    action: str,
    args_summary: str,
    result: str,
    ok: bool,
    *,
    clock: Clock | None = None,
) -> AuditEntry:
    """Build + append one audit entry. Returns the entry written."""
    entry = make_entry(action, args_summary, result, ok, clock=clock)
    write_entry(audit_path, entry)
    return entry


def read_audit(audit_path: Path, limit: int = 20) -> tuple[AuditEntry, ...]:
    """Tail the last ``limit`` audit entries (pure read). Missing/malformed lines are skipped, never raised."""
    if not audit_path.exists():
        return ()
    try:
        raw_lines = audit_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return ()
    out: list[AuditEntry] = []
    for raw in raw_lines[-limit:]:
        text = raw.strip()
        if not text:
            continue
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            continue
        if not isinstance(data, dict):
            continue
        out.append(AuditEntry(
            timestamp=str(data.get("timestamp", "")),
            action=str(data.get("action", "")),
            args_summary=str(data.get("args_summary", "")),
            result=str(data.get("result", "")),
            ok=bool(data.get("ok", False)),
        ))
    return tuple(out)
