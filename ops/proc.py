"""Shared subprocess + output-sanitization helpers for the ops action tiers (ADR-013).

Used by both the safe (``ops.actions``) and gated-live (``ops.gated``) tiers so the subprocess invocation
and the secret-redaction pass have ONE governed implementation. Stdlib-only; no Textual.
"""

from __future__ import annotations

import os
import subprocess
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ops.core import OpsPaths

# Env vars whose VALUES must never surface in the Log pane — scrubbed from any subprocess output tail
# before it is shown (defense in depth; the governed scripts do not echo these — ADR-013 sec.6).
_SECRET_ENV_VARS = ("ALPACA_API_SECRET_KEY", "ALPACA_API_KEY_ID", "NEO4J_PASSWORD")


@dataclass(frozen=True)
class ProcResult:
    returncode: int
    stdout: str
    stderr: str


Runner = Callable[[Sequence[str], "OpsPaths"], ProcResult]


def default_runner(cmd: Sequence[str], paths: OpsPaths) -> ProcResult:
    """Run a subprocess from the repo root, capturing output. Never raises (errors -> returncode -1)."""
    try:
        out = subprocess.run(
            list(cmd), cwd=str(paths.repo_root), capture_output=True, text=True, timeout=600,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return ProcResult(returncode=-1, stdout="", stderr=str(exc))
    return ProcResult(returncode=out.returncode, stdout=out.stdout or "", stderr=out.stderr or "")


def tail(text: str, limit: int = 12) -> tuple[str, ...]:
    return tuple(ln.rstrip() for ln in text.splitlines() if ln.strip())[-limit:]


def redact(lines: tuple[str, ...]) -> tuple[str, ...]:
    """Replace any known-secret env-var VALUE with '***' in surfaced lines (defense in depth)."""
    secrets: list[str] = []
    for var in _SECRET_ENV_VARS:
        val = os.environ.get(var)
        if val:
            secrets.append(val)
    if not secrets:
        return lines
    out: list[str] = []
    for line in lines:
        scrubbed = line
        for secret in secrets:
            scrubbed = scrubbed.replace(secret, "***")
        out.append(scrubbed)
    return tuple(out)
