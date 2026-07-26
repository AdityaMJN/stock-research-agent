"""Portfolio position sizing for ranked stock selections.

This module deliberately has no database dependency. Callers provide rankings and
prices, which makes sizing deterministic, straightforward to test, and usable by
both backtests and live portfolio workflows.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN
from enum import Enum
from typing import Mapping, Sequence

from portfolio.rules.scoring_engine import ScoredStock


class SizingStrategy(str, Enum):
    EQUAL_WEIGHT = "equal_weight"
    SCORE_WEIGHTED = "score_weighted"
    MARKET_CAP_WEIGHTED = "market_cap_weighted"
    VOLATILITY_ADJUSTED = "volatility_adjusted"


@dataclass(frozen=True)
class PositionSizingConfig:
    """Limits and strategy used to turn rankings into investable positions.

    Percentages are fractions: ``Decimal('0.10')`` represents 10%.
    """

    strategy: SizingStrategy = SizingStrategy.EQUAL_WEIGHT
    max_position_percent: Decimal = Decimal("1.00")
    min_position_percent: Decimal = Decimal("0.00")
    max_number_of_positions: int = 20

    def __post_init__(self) -> None:
        if not 0 < self.max_position_percent <= 1:
            raise ValueError("max_position_percent must be greater than 0 and at most 1.")
        if not 0 <= self.min_position_percent <= self.max_position_percent:
            raise ValueError("min_position_percent must be between 0 and max_position_percent.")
        if self.max_number_of_positions < 1:
            raise ValueError("max_number_of_positions must be at least 1.")


@dataclass(frozen=True)
class PortfolioAllocation:
    stock_id: int
    symbol: str
    portfolio_score: Decimal
    weight_percent: Decimal
    allocated_amount: Decimal
    share_price: Decimal
    quantity: int
    remaining_cash: Decimal


@dataclass(frozen=True)
class PortfolioSizingResult:
    allocations: tuple[PortfolioAllocation, ...]
    total_investment: Decimal
    total_allocated: Decimal
    remaining_cash: Decimal


class PositionSizingEngine:
    """Convert ranked stocks and current prices into whole-share allocations."""

    def __init__(self, configuration: PositionSizingConfig) -> None:
        self.configuration = configuration

    def size(
        self,
        ranked_stocks: Sequence[ScoredStock],
        total_investment: Decimal | int | float,
        prices_by_stock_id: Mapping[int, Decimal | int | float],
    ) -> PortfolioSizingResult:
        """Size positions and return allocations plus uninvested cash.

        The result always satisfies ``total_allocated + remaining_cash ==
        total_investment``. Prices and allocations use ``Decimal`` so financial
        calculations do not inherit binary floating-point rounding errors.
        """
        investment = self._money(total_investment)
        if investment <= 0:
            raise ValueError("total_investment must be greater than zero.")

        candidates = self._select_candidates(ranked_stocks, prices_by_stock_id)
        if not candidates:
            return PortfolioSizingResult((), investment, Decimal("0"), investment)

        weights = self._constrained_weights(candidates)
        candidates = [
            candidate
            for candidate in candidates
            if candidate[0].stock_id in weights
        ]
        quantities, allocated = self._round_to_whole_shares(candidates, weights, investment)
        remaining_cash = investment - sum(allocated.values(), Decimal("0"))

        allocations = tuple(
            PortfolioAllocation(
                stock_id=stock.stock_id,
                symbol=stock.symbol,
                portfolio_score=Decimal(str(stock.score)),
                weight_percent=(allocated[stock.stock_id] / investment) * Decimal("100"),
                allocated_amount=allocated[stock.stock_id],
                share_price=price_values[stock.stock_id],
                quantity=quantities[stock.stock_id],
                remaining_cash=remaining_cash,
            )
            for stock, price_values in candidates
        )
        return PortfolioSizingResult(
            allocations=allocations,
            total_investment=investment,
            total_allocated=investment - remaining_cash,
            remaining_cash=remaining_cash,
        )

    def _select_candidates(
        self,
        ranked_stocks: Sequence[ScoredStock],
        prices_by_stock_id: Mapping[int, Decimal | int | float],
    ) -> list[tuple[ScoredStock, dict[int, Decimal]]]:
        selected: list[tuple[ScoredStock, dict[int, Decimal]]] = []
        seen_ids: set[int] = set()
        for stock in ranked_stocks:
            if len(selected) == self.configuration.max_number_of_positions:
                break
            if stock.stock_id in seen_ids:
                raise ValueError(f"Duplicate stock_id in rankings: {stock.stock_id}")
            seen_ids.add(stock.stock_id)
            if stock.stock_id not in prices_by_stock_id:
                raise ValueError(f"No price supplied for stock_id {stock.stock_id}.")
            price = self._money(prices_by_stock_id[stock.stock_id])
            if price <= 0:
                raise ValueError(f"Price for stock_id {stock.stock_id} must be greater than zero.")
            selected.append((stock, {stock.stock_id: price}))
        return selected

    def _constrained_weights(
        self, candidates: list[tuple[ScoredStock, dict[int, Decimal]]]
    ) -> dict[int, Decimal]:
        if self.configuration.max_position_percent * len(candidates) < 1:
            raise ValueError("max_position_percent is too low for the selected number of positions.")

        raw_weights = self._initial_weights(candidates)
        active_ids = set(raw_weights)
        while True:
            weights = self._apply_maximum(raw_weights, active_ids)
            below_minimum = {
                stock_id
                for stock_id, weight in weights.items()
                if weight < self.configuration.min_position_percent
            }
            if not below_minimum:
                return weights
            active_ids -= below_minimum
            if not active_ids:
                raise ValueError("Position constraints leave no investable positions.")
            if self.configuration.max_position_percent * len(active_ids) < 1:
                raise ValueError("Position constraints cannot be satisfied for the selected stocks.")

    def _initial_weights(
        self, candidates: list[tuple[ScoredStock, dict[int, Decimal]]]
    ) -> dict[int, Decimal]:
        strategy = self.configuration.strategy
        if strategy == SizingStrategy.EQUAL_WEIGHT:
            weight = Decimal("1") / len(candidates)
            return {stock.stock_id: weight for stock, _ in candidates}
        if strategy == SizingStrategy.SCORE_WEIGHTED:
            scores = {stock.stock_id: max(Decimal("0"), Decimal(str(stock.score))) for stock, _ in candidates}
            total_score = sum(scores.values(), Decimal("0"))
            if total_score == 0:
                raise ValueError("Score-weighted sizing requires at least one positive portfolio score.")
            return {stock_id: score / total_score for stock_id, score in scores.items()}
        if strategy == SizingStrategy.MARKET_CAP_WEIGHTED:
            raise NotImplementedError("Market-cap-weighted sizing requires market-cap data and is not implemented yet.")
        if strategy == SizingStrategy.VOLATILITY_ADJUSTED:
            raise NotImplementedError("Volatility-adjusted sizing requires volatility data and is not implemented yet.")
        raise ValueError(f"Unsupported sizing strategy: {strategy}")

    def _apply_maximum(
        self, raw_weights: Mapping[int, Decimal], active_ids: set[int]
    ) -> dict[int, Decimal]:
        raw_total = sum((raw_weights[stock_id] for stock_id in active_ids), Decimal("0"))
        normalized = {stock_id: raw_weights[stock_id] / raw_total for stock_id in active_ids}
        available = set(active_ids)
        capped: dict[int, Decimal] = {}
        maximum = self.configuration.max_position_percent

        while available:
            available_weight = sum((normalized[stock_id] for stock_id in available), Decimal("0"))
            remaining_weight = Decimal("1") - sum(capped.values(), Decimal("0"))
            proposed = {
                stock_id: normalized[stock_id] / available_weight * remaining_weight
                for stock_id in available
            }
            newly_capped = {stock_id for stock_id, weight in proposed.items() if weight > maximum}
            if not newly_capped:
                capped.update(proposed)
                return capped
            for stock_id in newly_capped:
                capped[stock_id] = maximum
            available -= newly_capped
        raise ValueError("Unable to apply maximum position constraints.")

    def _round_to_whole_shares(
        self,
        candidates: list[tuple[ScoredStock, dict[int, Decimal]]],
        weights: Mapping[int, Decimal],
        investment: Decimal,
    ) -> tuple[dict[int, int], dict[int, Decimal]]:
        prices = {stock.stock_id: values[stock.stock_id] for stock, values in candidates}
        target_amounts = {stock_id: investment * weight for stock_id, weight in weights.items()}
        quantities = {
            stock_id: int((target_amounts[stock_id] / price).to_integral_value(rounding=ROUND_DOWN))
            for stock_id, price in prices.items()
        }
        allocated = {stock_id: quantities[stock_id] * price for stock_id, price in prices.items()}
        remaining = investment - sum(allocated.values(), Decimal("0"))
        maximum_amount = investment * self.configuration.max_position_percent

        # Spend residual cash on the positions furthest below their target amount,
        # while preserving the configured maximum position size.
        while True:
            affordable = [
                stock_id
                for stock_id, price in prices.items()
                if price <= remaining and allocated[stock_id] + price <= maximum_amount
            ]
            if not affordable:
                break
            stock_id = max(
                affordable,
                key=lambda item: (target_amounts[item] - allocated[item], -prices[item], -item),
            )
            quantities[stock_id] += 1
            allocated[stock_id] += prices[stock_id]
            remaining -= prices[stock_id]
        return quantities, allocated

    @staticmethod
    def _money(value: Decimal | int | float) -> Decimal:
        return Decimal(str(value))
