import pandas as pd

from database.connection import engine

from backtesting.utils import (
    get_rebalance_dates,
    get_exit_date,
    get_price,
    calculate_return
)


START_DATE = "2022-01-01"
END_DATE = "2025-01-01"

PORTFOLIO_SIZE = 20
HOLD_DAYS = 90


def get_candidates(trade_date):

    query = """
    WITH ordered_data AS
    (
        SELECT
            listing_id,
            trade_date,
            sma50,
            sma200,

            LAG(sma50)
            OVER
            (
                PARTITION BY listing_id
                ORDER BY trade_date
            ) AS prev_sma50,

            LAG(sma200)
            OVER
            (
                PARTITION BY listing_id
                ORDER BY trade_date
            ) AS prev_sma200

        FROM technical_indicators
    )

    SELECT
        listing_id,
        trade_date

    FROM ordered_data

    WHERE trade_date = %(trade_date)s

      AND prev_sma50 <= prev_sma200

      AND sma50 > sma200
    """

    return pd.read_sql(
        query,
        engine,
        params={
            "trade_date": trade_date
        }
    )


def evaluate_portfolio(
    entry_date,
    exit_date,
    portfolio
):

    returns = []

    for _, row in portfolio.iterrows():

        listing_id = int(
            row["listing_id"]
        )

        entry_price = get_price(
            listing_id,
            entry_date
        )

        exit_price = get_price(
            listing_id,
            exit_date
        )

        r = calculate_return(
            entry_price,
            exit_price
        )

        if r is not None:
            returns.append(r)

    if not returns:
        return None

    return sum(returns) / len(returns)


def run():

    dates = get_rebalance_dates(
        START_DATE,
        END_DATE
    )

    results = []

    for _, row in dates.iterrows():

        entry_date = row["trade_date"]

        exit_date = get_exit_date(
            entry_date,
            HOLD_DAYS
        )

        if exit_date is None:
            continue

        candidates = get_candidates(
            entry_date
        )

        if candidates.empty:
            continue

        portfolio = candidates.head(
            PORTFOLIO_SIZE
        )

        portfolio_return = (
            evaluate_portfolio(
                entry_date,
                exit_date,
                portfolio
            )
        )

        if portfolio_return is None:
            continue

        results.append(
            portfolio_return
        )

    if not results:

        print(
            "No results generated."
        )
        return

    results_series = pd.Series(
        results
    )

    print()
    print("=" * 60)
    print("GOLDEN CROSS BACKTEST")
    print("=" * 60)

    print(
        f"Periods Tested : "
        f"{len(results)}"
    )

    print(
        f"Average Return : "
        f"{results_series.mean():.2f}%"
    )

    print(
        f"Median Return  : "
        f"{results_series.median():.2f}%"
    )

    print(
        f"Best Return    : "
        f"{results_series.max():.2f}%"
    )

    print(
        f"Worst Return   : "
        f"{results_series.min():.2f}%"
    )

    print(
        f"Win Rate       : "
        f"{(results_series > 0).mean() * 100:.2f}%"
    )


def main():
    run()


if __name__ == "__main__":
    main()