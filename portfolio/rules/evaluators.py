from __future__ import annotations

from typing import Any, Mapping

from portfolio.rules.base import EvaluationResult, RuleEvaluator


def _number(stock: Mapping[str, Any], field: str) -> float | None:
    value = stock.get(field)
    return None if value is None else float(value)


class MomentumRuleEvaluator(RuleEvaluator):
    rule_type = "momentum"

    def evaluate(self, stock: Mapping[str, Any]) -> EvaluationResult:
        momentum = _number(stock, "momentum_score")
        if momentum is None:
            return EvaluationResult(0, False, {"reason": "Momentum is unavailable."})
        score = max(0.0, min(momentum, 100.0))
        return EvaluationResult(score, momentum > 0, {"momentum_score": momentum})


class StrongUptrendRuleEvaluator(RuleEvaluator):
    rule_type = "strong_uptrend"

    def evaluate(self, stock: Mapping[str, Any]) -> EvaluationResult:
        close = _number(stock, "close_price")
        sma20 = _number(stock, "sma20")
        sma50 = _number(stock, "sma50")
        sma200 = _number(stock, "sma200")
        rsi = _number(stock, "rsi14")
        if any(value is None for value in (close, sma20, sma50, sma200, rsi)):
            return EvaluationResult(0, False, {"reason": "Required indicators are unavailable."})
        checks = {
            "price_above_sma20": close > sma20,
            "sma20_above_sma50": sma20 > sma50,
            "sma50_above_sma200": sma50 > sma200,
            "rsi_above_60": rsi > 60,
        }
        passed_checks = sum(checks.values())
        return EvaluationResult(passed_checks * 25.0, passed_checks == len(checks), checks)


class GoldenCrossRuleEvaluator(RuleEvaluator):
    rule_type = "golden_cross"

    def evaluate(self, stock: Mapping[str, Any]) -> EvaluationResult:
        sma50 = _number(stock, "sma50")
        sma200 = _number(stock, "sma200")
        previous_sma50 = _number(stock, "previous_sma50")
        previous_sma200 = _number(stock, "previous_sma200")
        if any(value is None for value in (sma50, sma200, previous_sma50, previous_sma200)):
            return EvaluationResult(0, False, {"reason": "Current or previous SMA values are unavailable."})
        passed = previous_sma50 <= previous_sma200 and sma50 > sma200
        return EvaluationResult(100.0 if passed else 0.0, passed, {
            "previous_sma50": previous_sma50, "previous_sma200": previous_sma200,
            "sma50": sma50, "sma200": sma200,
        })


class FiftyTwoWeekHighRuleEvaluator(RuleEvaluator):
    rule_type = "fifty_two_week_high"

    def evaluate(self, stock: Mapping[str, Any]) -> EvaluationResult:
        close = _number(stock, "close_price")
        high = _number(stock, "high_52w")
        if close is None or high is None or high <= 0:
            return EvaluationResult(0, False, {"reason": "52-week high is unavailable."})
        score = max(0.0, min((close / high) * 100, 100.0))
        return EvaluationResult(score, score >= 95.0, {"close_price": close, "high_52w": high})


class RsiRuleEvaluator(RuleEvaluator):
    rule_type = "rsi"

    def evaluate(self, stock: Mapping[str, Any]) -> EvaluationResult:
        rsi = _number(stock, "rsi14")
        if rsi is None:
            return EvaluationResult(0, False, {"reason": "RSI is unavailable."})
        score = max(0.0, min(rsi, 100.0))
        return EvaluationResult(score, rsi >= 60.0, {"rsi14": rsi})


class Sma200RuleEvaluator(RuleEvaluator):
    rule_type = "sma200"

    def evaluate(self, stock: Mapping[str, Any]) -> EvaluationResult:
        close = _number(stock, "close_price")
        sma200 = _number(stock, "sma200")
        if close is None or sma200 is None or sma200 <= 0:
            return EvaluationResult(0, False, {"reason": "SMA200 is unavailable."})
        distance_pct = ((close - sma200) / sma200) * 100
        score = max(0.0, min(50.0 + distance_pct * 2, 100.0))
        return EvaluationResult(score, close > sma200, {
            "close_price": close, "sma200": sma200, "distance_pct": distance_pct,
        })


EVALUATOR_REGISTRY: dict[str, type[RuleEvaluator]] = {
    evaluator.rule_type: evaluator
    for evaluator in (
        MomentumRuleEvaluator,
        StrongUptrendRuleEvaluator,
        GoldenCrossRuleEvaluator,
        FiftyTwoWeekHighRuleEvaluator,
        RsiRuleEvaluator,
        Sma200RuleEvaluator,
    )
}
