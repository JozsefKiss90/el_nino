"""Execution adapters behind the INT-011 port (the hexagonal split, ADR-011 §2).

``ExecutionPort`` is the broker boundary: the one method (``fill``) that differs between a
deterministic simulator and a live broker. ``SimulatedBrokerAdapter`` is the **canonical,
replay-safe core path** (``replayable = True``); the ``AlpacaPaperAdapter`` (gate f / STEP 5) is the
optional, **non-replayable** live virtual-money plug — quarantined off the replay/benchmark path and
**not built here**. The pure ``execute()`` core depends only on this abstraction.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from gold.decision_builder.models import Direction

from .config import FillModelConfig
from .models import ExecutionMode, Fill

_BPS_DENOMINATOR = 10_000.0


class ExecutionPort(Protocol):
    """The broker boundary both adapters implement (ADR-011 §2)."""

    @property
    def mode(self) -> ExecutionMode:
        """Which adapter this is (stamped onto the execution record)."""
        ...

    @property
    def replayable(self) -> bool:
        """Whether this adapter's fills are deterministic / on the replay path (ADR-011 §2)."""
        ...

    def fill(
        self,
        instrument: str,
        direction: Direction,
        size: float,
        instrument_price: float,
        fill_model: FillModelConfig,
    ) -> Fill:
        """Produce a (paper) fill for an approved LONG of ``size`` at ``instrument_price``."""
        ...


@dataclass(frozen=True)
class SimulatedBrokerAdapter:
    """Deterministic, replay-safe fill simulator — the canonical core path (ADR-011 §2).

    v0 fill model: a fixed adverse slippage. A LONG buy fills at
    ``instrument_price * (1 + slippage_bps / 1e4)``. No clock, network, or randomness — the same
    inputs always yield the same fill (the determinism the replay key rests on).
    """

    mode: ExecutionMode = ExecutionMode.SIMULATED
    replayable: bool = True

    def fill(
        self,
        instrument: str,
        direction: Direction,
        size: float,
        instrument_price: float,
        fill_model: FillModelConfig,
    ) -> Fill:
        # Only an approved LONG reaches here (the engine gates non-LONG / blocked / duplicate).
        # Slippage is adverse to the buyer: the paper fill is worse than the mark.
        fill_price = instrument_price * (1.0 + fill_model.slippage_bps / _BPS_DENOMINATOR)
        return Fill(fill_price=fill_price, quantity=size, slippage_bps=fill_model.slippage_bps)
