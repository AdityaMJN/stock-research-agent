from decimal import Decimal
import unittest

from portfolio.position_sizing import (
    PositionSizingConfig,
    PositionSizingEngine,
    SizingStrategy,
)
from portfolio.rules.scoring_engine import ScoredStock


class PositionSizingEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.stocks = [
            ScoredStock(stock_id=1, symbol="ALPHA", score=60, rank=1),
            ScoredStock(stock_id=2, symbol="BETA", score=30, rank=2),
            ScoredStock(stock_id=3, symbol="GAMMA", score=10, rank=3),
        ]
        self.prices = {1: Decimal("100"), 2: Decimal("100"), 3: Decimal("100")}

    def test_equal_weight_allocates_whole_shares_and_returns_cash(self) -> None:
        engine = PositionSizingEngine(PositionSizingConfig(
            strategy=SizingStrategy.EQUAL_WEIGHT,
            max_number_of_positions=3,
        ))

        result = engine.size(self.stocks, Decimal("1000"), self.prices)

        self.assertEqual([item.quantity for item in result.allocations], [4, 3, 3])
        self.assertEqual(result.total_allocated, Decimal("1000"))
        self.assertEqual(result.remaining_cash, Decimal("0"))
        self.assertTrue(all(item.remaining_cash == Decimal("0") for item in result.allocations))

    def test_score_weighted_normalizes_scores_and_allocates_proportionally(self) -> None:
        engine = PositionSizingEngine(PositionSizingConfig(
            strategy=SizingStrategy.SCORE_WEIGHTED,
            max_number_of_positions=3,
        ))

        result = engine.size(self.stocks, Decimal("1000"), self.prices)

        self.assertEqual([item.quantity for item in result.allocations], [6, 3, 1])
        self.assertEqual(result.total_allocated, Decimal("1000"))
        self.assertEqual(sum(item.weight_percent for item in result.allocations), Decimal("100"))

    def test_max_position_percent_caps_score_weighted_allocation(self) -> None:
        stocks = [
            ScoredStock(stock_id=1, symbol="ALPHA", score=90, rank=1),
            ScoredStock(stock_id=2, symbol="BETA", score=5, rank=2),
            ScoredStock(stock_id=3, symbol="GAMMA", score=5, rank=3),
        ]
        engine = PositionSizingEngine(PositionSizingConfig(
            strategy=SizingStrategy.SCORE_WEIGHTED,
            max_position_percent=Decimal("0.50"),
            max_number_of_positions=3,
        ))

        result = engine.size(stocks, Decimal("1000"), self.prices)

        self.assertEqual(result.allocations[0].allocated_amount, Decimal("500"))
        self.assertTrue(all(item.allocated_amount <= Decimal("500") for item in result.allocations))

    def test_maximum_number_of_positions_limits_ranked_universe(self) -> None:
        engine = PositionSizingEngine(PositionSizingConfig(max_number_of_positions=2))

        result = engine.size(self.stocks, Decimal("1000"), self.prices)

        self.assertEqual([item.stock_id for item in result.allocations], [1, 2])

    def test_minimum_position_percent_removes_undersized_positions(self) -> None:
        engine = PositionSizingEngine(PositionSizingConfig(
            strategy=SizingStrategy.SCORE_WEIGHTED,
            min_position_percent=Decimal("0.20"),
            max_position_percent=Decimal("0.80"),
            max_number_of_positions=3,
        ))

        result = engine.size(self.stocks, Decimal("1000"), self.prices)

        self.assertEqual([item.stock_id for item in result.allocations], [1, 2])
        self.assertTrue(all(item.weight_percent >= Decimal("20") for item in result.allocations))

    def test_remaining_cash_is_reported_when_no_whole_share_is_affordable(self) -> None:
        engine = PositionSizingEngine(PositionSizingConfig(max_number_of_positions=1))

        result = engine.size(self.stocks[:1], Decimal("250"), {1: Decimal("300")})

        self.assertEqual(result.total_allocated, Decimal("0"))
        self.assertEqual(result.remaining_cash, Decimal("250"))
        self.assertEqual(result.allocations[0].quantity, 0)

    def test_score_weighted_rejects_all_non_positive_scores(self) -> None:
        stocks = [ScoredStock(stock_id=1, symbol="ALPHA", score=0, rank=1)]
        engine = PositionSizingEngine(PositionSizingConfig(strategy=SizingStrategy.SCORE_WEIGHTED))

        with self.assertRaisesRegex(ValueError, "positive portfolio score"):
            engine.size(stocks, Decimal("1000"), {1: Decimal("100")})

    def test_future_strategies_have_explicit_placeholders(self) -> None:
        cases = (
            (SizingStrategy.MARKET_CAP_WEIGHTED, "market-cap data"),
            (SizingStrategy.VOLATILITY_ADJUSTED, "volatility data"),
        )

        for strategy, message in cases:
            with self.subTest(strategy=strategy):
                engine = PositionSizingEngine(PositionSizingConfig(strategy=strategy))
                with self.assertRaisesRegex(NotImplementedError, message):
                    engine.size(self.stocks, Decimal("1000"), self.prices)

    def test_invalid_maximum_position_constraint_is_rejected(self) -> None:
        engine = PositionSizingEngine(PositionSizingConfig(
            max_position_percent=Decimal("0.30"),
            max_number_of_positions=3,
        ))

        with self.assertRaisesRegex(ValueError, "too low"):
            engine.size(self.stocks, Decimal("1000"), self.prices)


if __name__ == "__main__":
    unittest.main()
