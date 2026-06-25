"""Execution price-reference seam (SCHEMA-014 / ADR-014 bucket i) — source-pluggable GLD share price.

The execution layer marks and slips against a **GLD share price** (``exec_ref_gld_price``), not gold
spot ($/oz). This module is the single seam with two implementations:

* **Simulator / replay path** — a *versioned deterministic derived proxy*:
  ``exec_ref_gld_price = gold_price_proxy * OZ_PER_SHARE``, where ``gold_price_proxy`` is the real
  XAUUSD spot ($/oz) already carried as the ``gold_price`` feature, and ``OZ_PER_SHARE`` is a
  versioned constant (GLD's approximate gold content per share). Derived from the snapshot per the
  replay discipline — **never a live read** (ADR-011 D1 / ADR-014).
* **Live Alpaca path** — the real live GLD mark, read non-replayably by the Alpaca plug (ADR-014
  bucket ii). It plugs into this same :class:`ExecPriceRef` shape with a pinned, labelled timestamp.

``gold_price`` (spot, $/oz) is thereby **severed from execution** and stays a pure decision-context
feature; after this seam ``slippage_bps`` is GLD-vs-GLD and ``avg_cost`` / ``unrealized_pnl`` are
marked in $/share. The :data:`EXEC_PRICE_SOURCE_VERSION` axis folds into the replay key so a change
to the price source is a documented, versioned re-pin — old goldens stay byte-reproducible under the
prior version. Per ADR-003: stdlib frozen dataclass, zero runtime dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass

# Versioned price-source axis — distinct from execution_policy_version and fill_model_version. Bump
# this (and re-pin the execution + chain benchmarks) whenever the derived-proxy formula or
# OZ_PER_SHARE changes; old goldens stay byte-reproducible under the prior version.
EXEC_PRICE_SOURCE_VERSION = "1.0.0"

# GLD's approximate gold content per share (troy oz). A *versioned approximation* used ONLY by the
# deterministic sim/replay proxy — the live path uses the real broker mark, never this constant. GLD
# launched near 1/10 oz/share and declines slowly with the expense ratio; this is intentionally a
# documented constant (not a live read) so replay stays deterministic. Update only via a version bump.
OZ_PER_SHARE = 0.0933

# exec_ref_gld_price_basis labels — which mark the reference price represents (provenance). The live
# basis labels are consumed by the Alpaca plug (ADR-014 bucket ii) to tell overnight-gap slippage
# from pure execution slippage.
BASIS_DERIVED_PROXY = "sim_derived_proxy"   # sim/replay: gold_price_proxy * OZ_PER_SHARE
BASIS_LIVE_SUBMIT = "live_submit_mark"      # live: GLD mark at order submit (intraday / EOD)
BASIS_LIVE_OPEN = "live_open_mark"          # live: GLD mark at next-open routing


@dataclass(frozen=True)
class ExecPriceRef:
    """The resolved GLD-share execution price + its provenance (the ``exec_ref_gld_price`` triple).

    ``price`` flows into the record's ``instrument_price`` (marking + slippage become GLD-vs-GLD);
    ``ts`` + ``basis`` are recorded additively so overnight-gap slippage can be told from pure
    execution slippage on the live path. On the sim path ``ts`` is the snapshot clock and ``basis``
    is :data:`BASIS_DERIVED_PROXY`.
    """

    price: float
    ts: str | None
    basis: str


def resolve_sim_exec_ref(gold_price_proxy: float, as_of: str | None) -> ExecPriceRef:
    """The deterministic derived-proxy GLD share price for the simulator / replay path.

    ``exec_ref_gld_price = gold_price_proxy * OZ_PER_SHARE`` (the versioned proxy). No live read and
    no clock — a pure function of the snapshot-derived spot + the versioned constant, so replay stays
    byte-reproducible. ``as_of`` is the snapshot clock, recorded as the reference timestamp.
    """
    return ExecPriceRef(
        price=gold_price_proxy * OZ_PER_SHARE,
        ts=as_of,
        basis=BASIS_DERIVED_PROXY,
    )
