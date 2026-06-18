"""Pure full-chain core (MOD-010) — ``run_chain`` over a loaded snapshot + prior runtime state.

``run_chain(snapshot, prior_ledger, prior_portfolio, …) -> ChainResult``. Pure: no IO, clock,
randomness, or hidden state. It threads the already-governed per-layer pure cores
(``build_features → classify → build_decision → evaluate → execute``) and runs the GATE-001 guard
**here in the orchestrator** before ``execute`` (ADR-009 §3 / ADR-011 gate c) — the orchestrator is the
only cross-context importer (incl. ``src/risk`` via ``run_guard``); the per-layer cores stay clean.

Forwarded provenance (the orchestrator holds the snapshot + FeatureVector, so it forwards rather than
re-derives): ``SnapshotGuards`` + ``as_of`` ← the snapshot (ADR-009 §3); ``direction`` ←
``packet.direction`` and ``instrument_price`` ← ``fv.value("gold_price")`` — the **in-hand** values
handed to ``execute`` (ADR-011 D1; the ADMIT record carries neither). ``guards=None`` into
``build_decision`` (wrap-not-enrich; the packet stays pure, ADR-009 §2).

Execution is gated on ADMIT (``execute`` requires an ADMIT record): on HOLD/REJECT there is no
``ExecutionRecord`` and the portfolio is returned unchanged. The ledger always advances by one entry.
"""

from __future__ import annotations

from execution import execute, run_guard
from execution.adapters import ExecutionPort, SimulatedBrokerAdapter
from execution.config import (
    DEFAULT_EXECUTION_POLICY_CONFIG,
    DEFAULT_FILL_MODEL,
    ExecutionPolicyConfig,
    FillModelConfig,
)
from execution.models import ExecutionRecord, PortfolioState
from features.feature_builder import build_features
from gold.decision_builder import SnapshotGuards, build_decision
from gold.decision_builder.config import DecisionPolicyConfig
from gold.paper_runtime import evaluate
from gold.paper_runtime.config import DEFAULT_RUNTIME_POLICY_CONFIG, RuntimePolicyConfig
from gold.paper_runtime.models import OperationalInput, RuntimeLedger, Verdict
from regime.regime_classifier import classify
from regime.regime_classifier.config import RegimeConfig
from risk.guardrail_engine.models import GuardrailConfig
from snapshot.snapshot_consumer.models import Snapshot

from .config import DEFAULT_GUARD_CONFIG, DEFAULT_OPERATIONAL_INPUT
from .models import ChainContractError, ChainResult

_DEFAULT_PORT: ExecutionPort = SimulatedBrokerAdapter()
_PRICE_FEATURE = "gold_price"


def run_chain(
    snapshot: Snapshot,
    prior_ledger: RuntimeLedger,
    prior_portfolio: PortfolioState,
    *,
    operational_input: OperationalInput = DEFAULT_OPERATIONAL_INPUT,
    guard_config: GuardrailConfig = DEFAULT_GUARD_CONFIG,
    runtime_config: RuntimePolicyConfig = DEFAULT_RUNTIME_POLICY_CONFIG,
    regime_config: RegimeConfig | None = None,
    decision_config: DecisionPolicyConfig | None = None,
    exec_config: ExecutionPolicyConfig = DEFAULT_EXECUTION_POLICY_CONFIG,
    fill_model: FillModelConfig = DEFAULT_FILL_MODEL,
    port: ExecutionPort = _DEFAULT_PORT,
) -> ChainResult:
    """Thread one loaded, consumable snapshot through the whole Layer-3 chain. Pure; no IO."""
    # 1. Analysis (pure): features → regime → gold decision. as_of into classify is left at the chain
    #    idiom default (None); the packet's as_of is the snapshot clock (forwarded below).
    fv = build_features(snapshot)
    rc = classify(fv, regime_config)
    snapshot_guards = SnapshotGuards(
        data_ok=snapshot.guards.data_ok,
        freshness_ok=snapshot.guards.freshness_ok,
        cooldown_ok=snapshot.guards.cooldown_ok,
    )
    # guards=None: wrap-not-enrich — the pure packet never carries runtime state (ADR-009 §2).
    packet = build_decision(
        fv,
        rc,
        guards=None,
        snapshot_guards=snapshot_guards,
        config=decision_config,
        as_of=snapshot.clock_ts,
    )

    # 2. Stateful admission (pure): wrap the packet against the prior ledger + captured operational input.
    runtime_record, new_ledger = evaluate(packet, prior_ledger, operational_input, runtime_config)

    # 3. Execution — only on ADMIT (execute() requires an ADMIT record). Forward the in-hand direction
    #    + gold_price (ADR-011 D1); run the GATE-001 guard here before execute (ADR-011 gate c).
    execution_record: ExecutionRecord | None
    new_portfolio: PortfolioState
    if runtime_record.verdict is Verdict.ADMIT:
        if _PRICE_FEATURE not in fv.features:
            raise ChainContractError(
                f"ADMIT packet has no in-hand {_PRICE_FEATURE} to forward (ADR-011 D1): "
                f"snapshot {snapshot.snapshot_id} lacks the {_PRICE_FEATURE} feature"
            )
        instrument_price = fv.value(_PRICE_FEATURE)
        guard_result = run_guard(packet.direction, prior_portfolio, guard_config, exec_config)
        execution_record, new_portfolio = execute(
            runtime_record,
            packet.direction,
            instrument_price,
            prior_portfolio,
            guard_result,
            port,
            fill_model,
            exec_config,
        )
    else:
        execution_record, new_portfolio = None, prior_portfolio

    return ChainResult(
        feature_vector=fv,
        regime=rc,
        packet=packet,
        runtime_record=runtime_record,
        execution_record=execution_record,
        ledger=new_ledger,
        portfolio=new_portfolio,
    )
