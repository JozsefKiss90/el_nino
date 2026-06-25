"""TEST — exec_ref_gld_price seam (SCHEMA-014 / ADR-014 bucket i).

The sim/replay resolver returns the versioned derived proxy (``gold_price_proxy * OZ_PER_SHARE``),
labels it, and is a pure deterministic function (no live read / no clock). ``gold_price`` ($/oz) is
severed from execution: the GLD share reference is a different, smaller number.
"""

from __future__ import annotations

from execution import (
    BASIS_DERIVED_PROXY,
    EXEC_PRICE_SOURCE_VERSION,
    OZ_PER_SHARE,
    ExecPriceRef,
    resolve_sim_exec_ref,
)


def test_sim_resolver_is_derived_proxy() -> None:
    ref = resolve_sim_exec_ref(4624.5, "2026-05-01T00:00:00+00:00")
    assert isinstance(ref, ExecPriceRef)
    assert ref.price == 4624.5 * OZ_PER_SHARE
    assert ref.basis == BASIS_DERIVED_PROXY
    assert ref.ts == "2026-05-01T00:00:00+00:00"


def test_sim_resolver_severs_gold_spot() -> None:
    # The GLD share reference is materially different from (and smaller than) gold spot ($/oz):
    # execution is no longer marked or slipped in $/oz.
    spot = 4624.5
    ref = resolve_sim_exec_ref(spot, None)
    assert ref.price != spot
    assert ref.price < spot  # OZ_PER_SHARE < 1


def test_sim_resolver_is_deterministic() -> None:
    assert resolve_sim_exec_ref(1234.5, "t") == resolve_sim_exec_ref(1234.5, "t")


def test_price_source_version_is_pinned() -> None:
    # A dedicated, non-empty version axis distinct from execution_policy_version / fill_model_version.
    assert isinstance(EXEC_PRICE_SOURCE_VERSION, str) and EXEC_PRICE_SOURCE_VERSION
