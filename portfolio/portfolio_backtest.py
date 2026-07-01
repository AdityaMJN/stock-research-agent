import pandas as pd
import numpy as np

from database.connection import engine
from sqlalchemy import text
from execution.cost_models import (
    calculate_transaction_cost
)

PORTFOLIOS = [
    ("TOP10", 10),
    ("TOP20", 20),
    ("TOP50", 50)
]
TRADE_SIZE = 100000


def load_rankings():

    query = """
    SELECT
        trade_date,
        listing_id,
        rank_position
    FROM screener_results
    WHERE screener_name = 'COMBINED_RANKING'
    """

    return pd.read_sql(
        query,
        engine,
        parse_dates=["trade_date"]
    )


def load_prices():

    query = """
    SELECT
        listing_id,
        trade_date,
        adjusted_close
    FROM daily_prices
    """

    return pd.read_sql(
        query,
        engine,
        parse_dates=["trade_date"]
    )


def calculate_portfolio_returns(portfolio_name,portfolio_size):

    rankings = load_rankings()

    prices = load_prices()

    rebalance_dates = (
        rankings["trade_date"]
        .drop_duplicates()
        .sort_values()
        .tolist()
    )

    results = []

    for rebalance_date in rebalance_dates:

        portfolio = rankings[
            (rankings["trade_date"] == rebalance_date)
            &
            (rankings["rank_position"] <= portfolio_size)
        ]

        if len(portfolio) < portfolio_size:

            continue

        portfolio_return = []

        for _, stock in portfolio.iterrows():

            listing_id = stock["listing_id"]

            stock_prices = prices[
                prices["listing_id"]
                == listing_id
            ]

            entry = stock_prices[
                stock_prices["trade_date"]
                >= rebalance_date
            ].head(1)

            exit_date = (
                rebalance_date
                + pd.DateOffset(months=1)
            )

            exit_row = stock_prices[
                stock_prices["trade_date"]
                >= exit_date
            ].head(1)

            if (
                entry.empty
                or
                exit_row.empty
            ):
                continue

            entry_price = float(
                entry.iloc[0][
                    "adjusted_close"
                ]
            )

            exit_price = float(
                exit_row.iloc[0][
                    "adjusted_close"
                ]
            )

            #
            # Simulate investing a fixed amount
            #
            shares = (
                TRADE_SIZE
                / entry_price
            )

            buy_value = TRADE_SIZE

            sell_value = (
                shares
                * exit_price
            )

            cost = calculate_transaction_cost(
                buy_value=buy_value,
                sell_value=sell_value
            )
            stock_return = (cost.net_pnl / buy_value) * 100
            portfolio_return.append(stock_return)

        if not portfolio_return:

            continue

        results.append(
            {
                "rebalance_date": rebalance_date,
                "portfolio_return": np.mean(portfolio_return),
            }
        )

    return pd.DataFrame(
        results
    )


def print_summary(portfolio_name,portfolio_size,results):

    if results.empty:

        print(
            "No backtest results."
        )
        return

    avg_return = (
        results[
            "portfolio_return"
        ].mean()
    )

    median_return = (
        results[
            "portfolio_return"
        ].median()
    )

    best_return = (
        results[
            "portfolio_return"
        ].max()
    )

    worst_return = (
        results[
            "portfolio_return"
        ].min()
    )

    win_rate = (
        (
            results[
                "portfolio_return"
            ] > 0
        )
        .mean()
    ) * 100

    cumulative = (
        (
            1
            +
            results[
                "portfolio_return"
            ] / 100
        )
        .prod()
        - 1
    ) * 100

    print()
    print("=" * 80)
    print(
    f"{portfolio_name} BACKTEST"
)
    print("=" * 80)

    print(
        f"Periods       : {len(results)}"
    )
    print(
        f"Average Return: {avg_return:.2f}%"
    )
    print(
        f"Median Return : {median_return:.2f}%"
    )
    print(
        f"Best Return   : {best_return:.2f}%"
    )
    print(
        f"Worst Return  : {worst_return:.2f}%"
    )
    print(
        f"Win Rate      : {win_rate:.2f}%"
    )
    print(
        f"Cumulative    : {cumulative:.2f}%"
    )

def save_results(portfolio_name,portfolio_size,results):

    if results.empty:
        return

    records = []

    for _, row in results.iterrows():

        records.append(
            {
                "portfolio_name": portfolio_name,
                "trade_date":
                    row["rebalance_date"],

                "return_pct":
                    float(
                        row[
                            "portfolio_return"
                        ]
                    )
            }
        )

    with engine.begin() as conn:

        conn.execute(
            text("""
            DELETE FROM
            portfolio_backtest_results
            WHERE portfolio_name =
                :portfolio_name
            """),
            {
                "portfolio_name": portfolio_name
            }
        )

        conn.execute(
            text("""
            INSERT INTO
            portfolio_backtest_results
            (
                portfolio_name,
                trade_date,
                return_pct
            )
            VALUES
            (
                :portfolio_name,
                :trade_date,
                :return_pct
            )
            """),
            records
        )

    print()
    print(
        f"Saved {len(records)} "
        f"backtest periods"
    )


def run():

    for portfolio_name, portfolio_size in PORTFOLIOS:

        results = calculate_portfolio_returns(
            portfolio_name,
            portfolio_size
        )

        save_results(
            portfolio_name,
            portfolio_size,
            results
        )

        print_summary(
            portfolio_name,
            portfolio_size,
            results
        )

        print()

        print(
            results.tail(20)
        )

def main():
    run()


if __name__ == "__main__":
    main()