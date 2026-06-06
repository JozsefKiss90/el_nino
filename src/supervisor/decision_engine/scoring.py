"""Deterministic weakness scoring for the Decision Engine (MOD-002).

Pure functions: score an upgrade option by how severely the office is weak in the
dimension the option targets, weighted by expected improvement and cost efficiency.
Realizes the scoring logic of the Supervisor Pattern (PAT-001).
"""
from __future__ import annotations

from collections.abc import Callable

from supervisor.decision_engine.models import EvaluationScorecard, UpgradeOption


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def _calibration_weakness(s: EvaluationScorecard) -> float:
    return _clamp(1.0 - s.calibration)


def _pnl_weakness(s: EvaluationScorecard) -> float:
    return 1.0 if s.realized_pnl <= 0 else 0.0


def _drawdown_weakness(s: EvaluationScorecard) -> float:
    return _clamp(s.drawdown)


def _disagreement_weakness(s: EvaluationScorecard) -> float:
    return _clamp(s.disagreement)


WEAKNESS_DIMENSIONS: dict[str, Callable[[EvaluationScorecard], float]] = {
    "calibration": _calibration_weakness,
    "pnl": _pnl_weakness,
    "drawdown": _drawdown_weakness,
    "disagreement": _disagreement_weakness,
}


def weakness_severity(dimension: str, scorecard: EvaluationScorecard) -> float:
    """Severity in [0, 1] of the office's weakness in ``dimension`` (0 if unknown)."""
    fn = WEAKNESS_DIMENSIONS.get(dimension)
    return fn(scorecard) if fn is not None else 0.0


def score_option(option: UpgradeOption, scorecard: EvaluationScorecard) -> float:
    """Cost-efficiency-weighted score: ``severity * expected_improvement / cost``."""
    if option.cost <= 0:
        raise ValueError("upgrade option cost must be > 0")
    severity = weakness_severity(option.target_dimension, scorecard)
    return severity * option.expected_improvement / option.cost
