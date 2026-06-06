"""Unit tests for the Decision Engine scoring functions (covers scoring.py)."""
from __future__ import annotations

from typing import Any

import pytest

from supervisor.decision_engine.models import EvaluationScorecard, UpgradeOption
from supervisor.decision_engine.scoring import score_option, weakness_severity


def card(**overrides: Any) -> EvaluationScorecard:
    base: dict[str, Any] = dict(realized_pnl=-10.0, calibration=0.5, drawdown=0.2, disagreement=0.3)
    base.update(overrides)
    return EvaluationScorecard(**base)


def test_calibration_weakness() -> None:
    assert weakness_severity("calibration", card(calibration=0.5)) == 0.5


def test_pnl_weakness_is_binary() -> None:
    assert weakness_severity("pnl", card(realized_pnl=-1.0)) == 1.0
    assert weakness_severity("pnl", card(realized_pnl=5.0)) == 0.0


def test_unknown_dimension_is_zero() -> None:
    assert weakness_severity("nonsense", card()) == 0.0


def test_score_option_is_cost_efficiency_weighted() -> None:
    opt = UpgradeOption("a", cost=100.0, target_dimension="calibration", expected_improvement=0.8)
    # 0.5 * 0.8 / 100 = 0.004
    assert score_option(opt, card(calibration=0.5)) == pytest.approx(0.004)


def test_score_option_rejects_nonpositive_cost() -> None:
    with pytest.raises(ValueError):
        score_option(UpgradeOption("a", 0.0, "pnl", 0.5), card())
