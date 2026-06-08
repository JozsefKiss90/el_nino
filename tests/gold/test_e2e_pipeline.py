"""Full-chain E2E determinism (TEST-012): the complete Layer-3 analysis pipeline.

snapshot -> MOD-003.consume -> MOD-004.build_features -> MOD-005.classify -> MOD-006.build_decision.

Closes the Regime Taxonomy audit's Warning 4 (no snapshot→…→Gold end-to-end test) now that all
five modules exist. Asserts the final GoldDecisionPacket is byte-identical across two independent
runs, that the snapshot_id flows unchanged through every stage (the replay anchor), and pins the
golden packet for the real snapshot.
"""

from __future__ import annotations

import json
from pathlib import Path

from features.feature_builder import build_features
from gold.decision_builder import GoldDecisionPacket, build_decision
from regime.regime_classifier import classify
from snapshot.snapshot_consumer import consume

_REPO_ROOT = Path(__file__).resolve().parents[2]
_REAL_PASS = _REPO_ROOT / "tests" / "snapshot" / "fixtures" / "latest_snapshot_pass.json"
_REAL_SNAPSHOT_ID = "952cc83a8f930e27a7c3636cb03cf1c5d9b93a5363fa8d9b1a4891f6af7afaef"


def _run_pipeline(path: Path) -> GoldDecisionPacket:
    snap = consume(path)
    assert snap is not None
    fv = build_features(snap)
    rc = classify(fv)
    return build_decision(fv, rc)


def test_full_chain_byte_identical_replay() -> None:
    first = _run_pipeline(_REAL_PASS)
    second = _run_pipeline(_REAL_PASS)
    assert json.dumps(first.to_dict(), sort_keys=True) == json.dumps(second.to_dict(), sort_keys=True)


def test_full_chain_golden_packet() -> None:
    pkt = _run_pipeline(_REAL_PASS)
    assert pkt.source_snapshot_id == _REAL_SNAPSHOT_ID
    assert pkt.regime == "RESTRICTIVE_RATES"
    assert pkt.direction.value == "AVOID"
    assert round(pkt.confidence, 6) == 0.39744
    assert pkt.decision_mode.value == "paper_only"
    assert pkt.packet_id == "gold-v0:5653d07a0b3949d5"


def test_full_chain_snapshot_id_flows_unchanged() -> None:
    snap = consume(_REAL_PASS)
    assert snap is not None
    fv = build_features(snap)
    rc = classify(fv)
    pkt = build_decision(fv, rc)
    # one replay anchor threads every stage
    assert snap.snapshot_id == fv.snapshot_id == rc.snapshot_id == pkt.source_snapshot_id
    # and the consumed snapshot's recomputed id matches the published id (no tampering)
    assert snap.id_matches
