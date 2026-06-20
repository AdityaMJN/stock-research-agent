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
    WITH highs AS
    (
        SELECT
            dp.listing_id,
            MAX(dp.high_price) AS high_52w

        FROM daily_prices dp

        WHERE dp.trade_date
              BETWEEN
                  %(trade_date)s::date - INTERVAL '365 days'
              AND
                  %(trade_date)s

        GROUP BY dp.listing_id
    )

    SELECT
        dp.listing_id,
        dp.close_price,
        h.high_52w,

        (
            dp.close_price
            /
            NULLIF(h.high_52w, 0)
        ) * 100 AS score

    FROM daily_prices dp

    JOIN highs h
      ON h.listing_id = dp.listing_id

    WHERE dp.trade_date = %(trade_date)s

      AND dp.close_price >= h.high_52w * 0.95

    ORDER BY score DESC
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
    print("52 WEEK HIGH BACKTEST")
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