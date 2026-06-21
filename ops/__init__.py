"""Operations Control Plane (ADR-013) — local terminal operator console for the El Niño runtime.

A sibling of the JARVIS graph console (ADR-010), and deliberately **not** coupled to it. The console
lives entirely in this top-level ``ops/`` package and is **never imported by** ``src/`` — so the trading
engine keeps ``dependencies = []`` (ADR-003 zero-runtime-deps). Textual / Rich are an optional
dependency group (``pip install -e ".[ops]"``).

- ``ops.core`` — the headless governed read-model. No Textual import; pure reads that reuse the
  ``src/`` governed functions (``load_ledger`` / ``load_portfolio`` / ``run_sequence`` / the live-plug
  ``*_from_env`` factories) and never reimplement safety, paper-only, or gate logic (ADR-013 §4).
- ``ops.app`` — the Textual TUI over ``ops.core`` (Step 1: read-only).
"""

from __future__ import annotations

__all__ = ["__version__"]
__version__ = "0.1.0"
