"""TEST-013 — paper-runtime guard predicates (PRED-006/007 + snapshot echoes), in isolation.

Each guard is a pure function of explicit inputs (packet / ledger / operational input). Covers the
once-ever dedup semantics (prior ADMIT only), the operational preconditions, the snapshot echoes,
and default-closed behavior when provenance / operational state is absent.
"""

from __future__ import annotations

from gold.decision_builder.models import (
    ConfidenceInputs,
    DecisionMode,
    Direction,
    GoldDecisionPacket,
    GuardRefs,
    SnapshotGuards,
)
from gold.paper_runtime import (
    LedgerEntry,
    OperationalInput,
    RuntimeLedger,
    RuntimePolicyConfig,
    Verdict,
    cooldown_ok,
    data_ok,
    duplicate_ok,
    freshness_ok,
    operational_ok,
)

_SG_TRUE = SnapshotGuards(data_ok=True, freshness_ok=True, cooldown_ok=True)
_OP_OPEN = OperationalInput("GLD", tradeable=True, venue_open=True, halt=False, degraded=False)
# Computed-cooldown (PRED-008) configs: default 20h window, plus a wide 48h window for the unit tests.
_CFG = RuntimePolicyConfig()
_CFG48 = RuntimePolicyConfig(cooldown_window_hours=48.0)


def _packet(
    snapshot_id: str = "S1",
    direction: Direction = Direction.LONG,
    sg: SnapshotGuards | None = _SG_TRUE,
    regime: str = "RESTRICTIVE_RATES",
    instrument: str = "GLD",
    as_of: str | None = "2026-05-01T00:00:00+00:00",
) -> GoldDecisionPacket:
    return GoldDecisionPacket(
        packet_id=f"gold-v0:{snapshot_id}",
        packet_schema_version="0.2.0",
        instrument=instrument,
        decision_mode=DecisionMode.PAPER_ONLY,
        regime=regime,
        direction=direction,
        confidence=0.5,
        uncertainty=0.5,
        rationale="r",
        source_snapshot_id=snapshot_id,
        source_feature_schema_version="0.1.0",
        regime_taxonomy_version="1.0.0",
        regime_classifier_version="0.1.0",
        regime_classification_trace_version="0.1.0",
        matched_rule_id="rule",
        cited_features=(),
        decision_policy_version="0.1.0",
        confidence_inputs=ConfidenceInputs(0.5, 0, 0, 0, False, 0),
        guard_refs=GuardRefs(),
        non_execution_notice="n",
        constraints=(),
        as_of=as_of,
        snapshot_guards=sg,
    )


def _entry(snapshot_id: str, verdict: str, triggered: str | None, seq: int = 0) -> LedgerEntry:
    return LedgerEntry(snapshot_id, f"gold-v0:{snapshot_id}", "t", verdict, triggered, "d", "f", seq)


def _admit_entry(snapshot_id: str, as_of: str, seq: int = 0) -> LedgerEntry:
    """An ADMIT ledger entry with a real ``as_of`` — the time source for the cooldown guard."""
    return LedgerEntry(snapshot_id, f"gold-v0:{snapshot_id}", as_of, Verdict.ADMIT.value, None, "d", "f", seq)


def _ledger(*entries: LedgerEntry) -> RuntimeLedger:
    return RuntimeLedger("0.1.0", tuple(entries))


# --- duplicate_ok (PRED-006): once-ever, keyed on a prior ADMIT --------------------------------

def test_duplicate_ok_pass_on_unseen() -> None:
    assert duplicate_ok(_packet("S1"), RuntimeLedger.empty())[0] is True


def test_duplicate_ok_fail_after_prior_admit() -> None:
    led = _ledger(_entry("S1", Verdict.ADMIT.value, None))
    passed, reason = duplicate_ok(_packet("S1"), led)
    assert passed is False
    assert "already admitted" in reason


def test_duplicate_ok_pass_if_prior_was_not_admit() -> None:
    # a prior HOLD/REJECT of the same snapshot did NOT produce a packet — does not block a later admit
    led = _ledger(_entry("S1", Verdict.REJECT.value, "operational_ok"))
    assert duplicate_ok(_packet("S1"), led)[0] is True


def test_duplicate_ok_pass_for_a_different_snapshot() -> None:
    led = _ledger(_entry("S1", Verdict.ADMIT.value, None))
    assert duplicate_ok(_packet("S2"), led)[0] is True


# --- operational_ok (PRED-007) ----------------------------------------------------------------

def test_operational_ok_pass_when_open() -> None:
    assert operational_ok(_packet(), _OP_OPEN)[0] is True


def test_operational_ok_fail_on_halt() -> None:
    op = OperationalInput("GLD", tradeable=True, venue_open=True, halt=True, degraded=False)
    assert operational_ok(_packet(), op)[0] is False


def test_operational_ok_fail_on_degraded() -> None:
    op = OperationalInput("GLD", tradeable=True, venue_open=True, halt=False, degraded=True)
    assert operational_ok(_packet(), op)[0] is False


def test_operational_ok_fail_on_not_tradeable() -> None:
    op = OperationalInput("GLD", tradeable=False, venue_open=True, halt=False, degraded=False)
    assert operational_ok(_packet(), op)[0] is False


def test_operational_ok_fail_on_venue_closed() -> None:
    op = OperationalInput("GLD", tradeable=True, venue_open=False, halt=False, degraded=False)
    assert operational_ok(_packet(), op)[0] is False


def test_operational_ok_fail_on_wrong_instrument() -> None:
    op = OperationalInput("SLV", tradeable=True, venue_open=True, halt=False, degraded=False)
    passed, reason = operational_ok(_packet(instrument="GLD"), op)
    assert passed is False
    assert "instrument" in reason


def test_operational_ok_default_closed_state_fails() -> None:
    assert operational_ok(_packet(), OperationalInput.closed())[0] is False


# --- snapshot echoes (data / freshness) -------------------------------------------------------

def test_echoes_true_from_snapshot_provenance() -> None:
    pkt = _packet(sg=SnapshotGuards(data_ok=True, freshness_ok=True, cooldown_ok=True))
    assert data_ok(pkt)[0] is True
    assert freshness_ok(pkt)[0] is True


def test_echoes_false_from_snapshot_provenance() -> None:
    pkt = _packet(sg=SnapshotGuards(data_ok=False, freshness_ok=False, cooldown_ok=False))
    assert data_ok(pkt)[0] is False
    assert freshness_ok(pkt)[0] is False


def test_echoes_default_closed_when_provenance_absent() -> None:
    pkt = _packet(sg=None)
    for guard in (data_ok, freshness_ok):
        passed, reason = guard(pkt)
        assert passed is False
        assert "absent" in reason


# --- cooldown_ok (PRED-008): COMPUTED L3 cooldown (v0.2.0, no longer an echo) ------------------

def test_cooldown_ok_pass_when_no_prior_admit() -> None:
    # nothing to pace against ⇒ pass (the L2 snapshot cooldown flag is no longer echoed here)
    assert cooldown_ok(_packet("S1"), RuntimeLedger.empty(), _CFG)[0] is True


def test_cooldown_ok_fail_within_window() -> None:
    # a prior ADMIT of a DIFFERENT snapshot 24h ago; 48h window ⇒ still cooling down
    led = _ledger(_admit_entry("S0", "2026-05-01T00:00:00+00:00"))
    passed, reason = cooldown_ok(_packet("S1", as_of="2026-05-02T00:00:00+00:00"), led, _CFG48)
    assert passed is False
    assert "cooldown active" in reason


def test_cooldown_ok_pass_when_window_elapsed() -> None:
    led = _ledger(_admit_entry("S0", "2026-05-01T00:00:00+00:00"))  # 72h gap > 48h window
    passed, reason = cooldown_ok(_packet("S1", as_of="2026-05-04T00:00:00+00:00"), led, _CFG48)
    assert passed is True
    assert "cooldown elapsed" in reason


def test_cooldown_ok_excludes_self_re_presentation() -> None:
    # an exact re-presentation does NOT cool down against its own prior ADMIT (that is duplicate_ok's job)
    led = _ledger(_admit_entry("S1", "2026-05-01T00:00:00+00:00"))
    assert cooldown_ok(_packet("S1", as_of="2026-05-01T00:00:00+00:00"), led, _CFG48)[0] is True


def test_cooldown_ok_only_counts_admits() -> None:
    # a prior REJECT (not ADMIT) of another snapshot does not start a cooldown
    led = _ledger(_entry("S0", Verdict.REJECT.value, "operational_ok"))
    assert cooldown_ok(_packet("S1"), led, _CFG48)[0] is True


def test_cooldown_ok_fail_closed_on_missing_as_of() -> None:
    led = _ledger(_admit_entry("S0", "2026-05-01T00:00:00+00:00"))
    passed, reason = cooldown_ok(_packet("S1", as_of=None), led, _CFG48)
    assert passed is False
    assert "timing unavailable" in reason


def test_cooldown_ok_fail_closed_on_out_of_order() -> None:
    # presenting an OLDER snapshot after a newer ADMIT ⇒ negative gap ⇒ fail-closed (block)
    led = _ledger(_admit_entry("S0", "2026-05-05T00:00:00+00:00"))
    assert cooldown_ok(_packet("S1", as_of="2026-05-01T00:00:00+00:00"), led, _CFG48)[0] is False
