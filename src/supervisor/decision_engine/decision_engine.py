"""Decision Engine (MOD-002) — deterministic upgrade selection for the Supervisor Office.

Implements the Decision API (INT-006): consumes an EvaluationScorecard (SCHEMA-005) plus the
upgrade catalog, treasury state, and institutional memory; produces a DecisionPacket
(SCHEMA-004). Deterministic — identical inputs yield identical packets.
"""
from __future__ import annotations

from collections.abc import Iterable, Sequence

from supervisor.decision_engine.models import (
    DecisionConfig,
    DecisionPacket,
    EvaluationScorecard,
    RankedOption,
    TreasuryState,
    UpgradeOption,
)
from supervisor.decision_engine.scoring import score_option


class DecisionEngine:
    """Score candidate upgrades under treasury constraints and emit a decision packet."""

    def __init__(self, config: DecisionConfig | None = None) -> None:
        self._config = config or DecisionConfig()

    def decide(
        self,
        scorecard: EvaluationScorecard,
        catalog: Sequence[UpgradeOption],
        treasury: TreasuryState,
        excluded_ids: Iterable[str] | None = None,
    ) -> DecisionPacket:
        excluded = frozenset(excluded_ids or ())

        # Early exit: the office is already performing well enough.
        if (
            scorecard.realized_pnl > self._config.promotable_pnl_threshold
            and scorecard.calibration >= self._config.promotable_calibration_threshold
        ):
            return DecisionPacket(
                selected_upgrade_id=None,
                ranked_options=(),
                rationale="office is promotable (pnl above threshold, calibration met) — no upgrade needed",
                treasury_state_after=treasury,
            )

        # Score every option, then apply the exclusion + budget filters.
        scored: list[RankedOption] = []
        for option in catalog:
            score = score_option(option, scorecard)
            if option.upgrade_id in excluded:
                scored.append(
                    RankedOption(option.upgrade_id, score, False, "excluded by institutional memory")
                )
            elif option.cost > treasury.available:
                scored.append(
                    RankedOption(
                        option.upgrade_id,
                        score,
                        False,
                        f"insufficient treasury (cost {option.cost} > available {treasury.available})",
                    )
                )
            else:
                scored.append(RankedOption(option.upgrade_id, score, True, None))

        # Deterministic rank: score descending, then upgrade_id ascending as tie-break.
        ranked = tuple(sorted(scored, key=lambda r: (-r.score, r.upgrade_id)))
        allowed = [r for r in ranked if r.allowed]

        if not allowed:
            return DecisionPacket(
                selected_upgrade_id=None,
                ranked_options=ranked,
                rationale="all options blocked (budget exhausted or excluded by institutional memory)",
                treasury_state_after=treasury,
            )

        best = allowed[0]
        cost = next(o.cost for o in catalog if o.upgrade_id == best.upgrade_id)
        return DecisionPacket(
            selected_upgrade_id=best.upgrade_id,
            ranked_options=ranked,
            rationale=f"selected {best.upgrade_id} (score {best.score:.6f})",
            treasury_state_after=treasury.after_spend(cost),
        )
