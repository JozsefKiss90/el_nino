"""Pure runtime admission engine (MOD-007) — ``evaluate`` over a gold packet + runtime state.

``evaluate(packet, prior_ledger, operational_input, config) -> (record, new_ledger)``. No IO,
clock, randomness, or hidden state (ADR-009 §3/§4): state is an explicit argument and return value.
The six-guard block is computed in the canonical ``_GUARD_NAMES`` order (a full audit trail); the
verdict is a short-circuit conjunction over the *required* guards (first failure names the guard).
Fail-closed: a WATCH/INDETERMINATE packet HOLDs (no actionable stance); a required-but-failed guard
REJECTs; otherwise ADMIT. Every evaluation appends exactly one self-describing ledger entry.
"""

from __future__ import annotations

from gold.decision_builder.models import (
    DecisionMode,
    Direction,
    GoldDecisionPacket,
    _GUARD_NAMES,
)

from .config import DEFAULT_RUNTIME_POLICY_CONFIG, RuntimePolicyConfig
from .models import (
    RECORD_SCHEMA_VERSION,
    GuardOutcome,
    LedgerEntry,
    OperationalInput,
    RuntimeDecisionRecord,
    RuntimeLedger,
    Verdict,
    compute_record_id,
    digest_snapshot_guards,
)
from .predicates import (
    GuardResult,
    cooldown_ok,
    data_ok,
    duplicate_ok,
    freshness_ok,
    operational_ok,
)

_SUPERVISOR_STUB_REASON = "no supervisor in v0 (ADR-009 §6 stub) — not required to ADMIT"
_ACTIONABLE_GUARD = "actionable_stance"

_NON_EXECUTION_NOTICE = (
    "PAPER TRADING ADMISSION — not a live order, broker instruction, or execution command (ADR-009)."
)
_CONSTRAINTS: tuple[str, ...] = (
    "wraps the pure GoldDecisionPacket; never mutates or re-emits it",
    "stateful via an explicit append-only ledger (no hidden state, clock, or wall-clock)",
    "deterministic: same (packet, prior ledger, operational input, policy) => identical record + ledger",
    "paper_only: an admission decision, never a live order",
)


def _required_guards(config: RuntimePolicyConfig) -> tuple[str, ...]:
    """The guards that gate ADMIT, in canonical ``_GUARD_NAMES`` order (duplicate always required)."""
    required = {"duplicate_ok"}
    if config.require_operational:
        required.add("operational_ok")
    if config.require_snapshot_guards:
        required.update(("data_ok", "freshness_ok"))
    return tuple(name for name in _GUARD_NAMES if name in required)


def evaluate(
    packet: GoldDecisionPacket,
    prior_ledger: RuntimeLedger,
    operational_input: OperationalInput,
    config: RuntimePolicyConfig = DEFAULT_RUNTIME_POLICY_CONFIG,
) -> tuple[RuntimeDecisionRecord, RuntimeLedger]:
    """Admit / hold / reject a gold packet against runtime state. Pure; no IO."""
    # 1. Evaluate every guard (the full audit block), keyed by name. supervisor_ok is a None stub.
    results: dict[str, GuardResult] = {
        "duplicate_ok": duplicate_ok(packet, prior_ledger),
        "operational_ok": operational_ok(packet, operational_input),
        "data_ok": data_ok(packet),
        "freshness_ok": freshness_ok(packet),
        "cooldown_ok": cooldown_ok(packet),
        "supervisor_ok": (None, _SUPERVISOR_STUB_REASON),
    }
    guard_outcomes = tuple(
        GuardOutcome(name, results[name][0], results[name][1]) for name in _GUARD_NAMES
    )

    # 2. Verdict (fail-closed). WATCH/INDETERMINATE packet => HOLD (no actionable stance); else the
    #    first failing *required* guard (in _GUARD_NAMES order) => REJECT; else ADMIT.
    triggered: str | None
    if packet.direction is Direction.WATCH:
        verdict, triggered, reason = (
            Verdict.HOLD,
            _ACTIONABLE_GUARD,
            f"packet direction {packet.direction.value} — no actionable stance",
        )
    else:
        first_failed = next(
            (name for name in _required_guards(config) if results[name][0] is False), None
        )
        if first_failed is not None:
            verdict, triggered, reason = Verdict.REJECT, first_failed, results[first_failed][1]
        else:
            verdict, triggered, reason = Verdict.ADMIT, None, "all required guards passed"

    # 3. Append exactly one self-describing ledger entry (carrying this evaluation's inputs).
    op_fingerprint = operational_input.fingerprint()
    sg_digest = digest_snapshot_guards(packet)
    prior_state_hash = prior_ledger.state_hash()
    entry = LedgerEntry(
        source_snapshot_id=packet.source_snapshot_id,
        source_packet_id=packet.packet_id,
        as_of=packet.as_of,
        verdict=verdict.value,
        triggered_guard=triggered,
        snapshot_guards_digest=sg_digest,
        operational_fingerprint=op_fingerprint,
        seq=prior_ledger.next_seq(),
    )
    new_ledger = prior_ledger.append(entry)

    # 4. Build the record. record_id binds the prior ledger state — a per-evaluation identity,
    #    distinct from the snapshot/idempotency key (source_snapshot_id).
    record = RuntimeDecisionRecord(
        record_id=compute_record_id(
            source_packet_id=packet.packet_id,
            runtime_policy_fingerprint=config.runtime_policy_fingerprint(),
            as_of=packet.as_of,
            operational_fingerprint=op_fingerprint,
            snapshot_guards_digest=sg_digest,
            prior_ledger_state_hash=prior_state_hash,
        ),
        record_schema_version=RECORD_SCHEMA_VERSION,
        source_packet_id=packet.packet_id,
        source_snapshot_id=packet.source_snapshot_id,
        decision_mode=DecisionMode.PAPER_ONLY,
        verdict=verdict,
        triggered_guard=triggered,
        reason=reason,
        guard_outcomes=guard_outcomes,
        runtime_policy_version=config.runtime_policy_version,
        as_of=packet.as_of,
        prior_ledger_state_hash=prior_state_hash,
        new_ledger_state_hash=new_ledger.state_hash(),
        non_execution_notice=_NON_EXECUTION_NOTICE,
        constraints=_CONSTRAINTS,
    )
    return record, new_ledger
