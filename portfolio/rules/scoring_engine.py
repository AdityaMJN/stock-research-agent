from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from database.models import PortfolioRule, RuleResult
from database.session import get_session
from portfolio.rules.evaluators import EVALUATOR_REGISTRY


@dataclass(frozen=True)
class ScoredStock:
    stock_id: int
    symbol: str
    score: float
    rank: int


class PortfolioScoringEngine:
    """Evaluate enabled rules, persist their results, and rank the stock universe."""

    def __init__(self, session: Session | None = None) -> None:
        self._session = session

    def rank(self, trade_date: date) -> list[ScoredStock]:
        """Score every stock with data on ``trade_date`` and return descending ranks."""
        owns_session = self._session is None
        session = self._session or get_session()

        try:
            rules = self._load_enabled_rules(session)
            snapshots = self._load_stock_snapshots(session, trade_date)
            rankings, results = self._evaluate(rules, snapshots, trade_date)
            session.add_all(results)
            if owns_session:
                session.commit()
            return rankings
        except Exception:
            if owns_session:
                session.rollback()
            raise
        finally:
            if owns_session:
                session.close()

    @staticmethod
    def _load_enabled_rules(session: Session) -> list[PortfolioRule]:
        rules = list(
            session.query(PortfolioRule)
            .filter(PortfolioRule.enabled.is_(True))
            .order_by(PortfolioRule.id)
        )
        if not rules:
            raise ValueError("No enabled portfolio rules are configured.")
        unknown_types = sorted({rule.rule_type for rule in rules} - EVALUATOR_REGISTRY.keys())
        if unknown_types:
            raise ValueError(f"No evaluator is registered for rule types: {', '.join(unknown_types)}")
        if sum(Decimal(rule.weight) for rule in rules) <= 0:
            raise ValueError("Enabled portfolio rules must have a total weight greater than zero.")
        return rules

    @staticmethod
    def _load_stock_snapshots(session: Session, trade_date: date) -> list[dict[str, Any]]:
        query = text("""
            WITH indicator_history AS (
                SELECT
                    ti.listing_id,
                    ti.trade_date,
                    ti.sma20,
                    ti.sma50,
                    ti.sma200,
                    ti.rsi14,
                    ti.momentum_score,
                    LAG(ti.sma50) OVER (
                        PARTITION BY ti.listing_id ORDER BY ti.trade_date
                    ) AS previous_sma50,
                    LAG(ti.sma200) OVER (
                        PARTITION BY ti.listing_id ORDER BY ti.trade_date
                    ) AS previous_sma200
                FROM technical_indicators ti
            )
            SELECT
                l.id AS stock_id,
                l.symbol,
                dp.close_price,
                ih.sma20,
                ih.sma50,
                ih.sma200,
                ih.rsi14,
                ih.momentum_score,
                ih.previous_sma50,
                ih.previous_sma200,
                highs.high_52w
            FROM daily_prices dp
            JOIN listings l ON l.id = dp.listing_id
            LEFT JOIN indicator_history ih
              ON ih.listing_id = dp.listing_id
             AND ih.trade_date = dp.trade_date
            LEFT JOIN LATERAL (
                SELECT MAX(history.close_price) AS high_52w
                FROM daily_prices history
                WHERE history.listing_id = dp.listing_id
                  AND history.trade_date BETWEEN :trade_date - INTERVAL '365 days'
                                             AND :trade_date
            ) highs ON TRUE
            WHERE dp.trade_date = :trade_date
            ORDER BY l.id
        """)
        return [dict(row) for row in session.execute(query, {"trade_date": trade_date}).mappings()]

    @staticmethod
    def _evaluate(
        rules: list[PortfolioRule], snapshots: list[dict[str, Any]], trade_date: date
    ) -> tuple[list[ScoredStock], list[RuleResult]]:
        evaluators = {rule.id: EVALUATOR_REGISTRY[rule.rule_type]() for rule in rules}
        total_weight = sum(Decimal(rule.weight) for rule in rules)
        scored: list[tuple[int, str, Decimal]] = []
        persisted_results: list[RuleResult] = []

        for stock in snapshots:
            weighted_total = Decimal("0")
            for rule in rules:
                evaluation = evaluators[rule.id].evaluate(stock)
                score = Decimal(str(evaluation.score))
                weighted_total += score * Decimal(rule.weight)
                persisted_results.append(
                    RuleResult(
                        stock_id=int(stock["stock_id"]),
                        rule_name=rule.rule_name,
                        score=score,
                        passed=evaluation.passed,
                        details={**evaluation.details, "evaluation_date": trade_date.isoformat()},
                    )
                )
            scored.append((int(stock["stock_id"]), str(stock["symbol"]), weighted_total / total_weight))

        scored.sort(key=lambda item: (-item[2], item[1]))
        rankings = [
            ScoredStock(stock_id=stock_id, symbol=symbol, score=float(score), rank=index)
            for index, (stock_id, symbol, score) in enumerate(scored, start=1)
        ]
        return rankings, persisted_results
