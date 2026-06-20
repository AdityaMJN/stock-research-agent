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

THRESHOLDS = [
    0.95,
    0.97,
    0.98,
    0.99
]


def get_candidates(
    trade_date,
    threshold
):

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
            NULLIF(
                h.high_52w,
                0
            )
        ) * 100 AS score

    FROM daily_prices dp

    JOIN highs h
      ON h.listing_id = dp.listing_id

    WHERE dp.trade_date =
          %(trade_date)s

      AND dp.close_price >=
          h.high_52w *
          %(threshold)s

    ORDER BY score DESC
    """

    return pd.read_sql(
        query,
        engine,
        params={
            "trade_date": trade_date,
            "threshold": threshold
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


def run_single_threshold(
    threshold
):

    dates = get_rebalance_dates(
        START_DATE,
        END_DATE
    )

    results = []

    total_candidates = []

    for _, row in dates.iterrows():

        entry_date = row["trade_date"]

        exit_date = get_exit_date(
            entry_date,
            HOLD_DAYS
        )

        if exit_date is None:
            continue

        candidates = get_candidates(
            entry_date,
            threshold
        )

        total_candidates.append(
            len(candidates)
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

        return None

    results_series = pd.Series(
        results
    )

    return {
        "Threshold":
            f"{int(threshold*100)}%",

        "Periods":
            len(results),

        "Avg Candidates":
            round(
                sum(total_candidates)
                /
                len(total_candidates),
                1
            ),

        "Average Return":
            round(
                results_series.mean(),
                2
            ),

        "Median Return":
            round(
                results_series.median(),
                2
            ),

        "Best Return":
            round(
                results_series.max(),
                2
            ),

        "Worst Return":
            round(
                results_series.min(),
                2
            ),

        "Win Rate":
            round(
                (results_series > 0)
                .mean() * 100,
                2
            )
    }


def run():

    print()
    print("=" * 120)
    print("52 WEEK HIGH THRESHOLD COMPARISON")
    print("=" * 120)

    all_results = []

    for threshold in THRESHOLDS:

        print()
        print(
            f"Running "
            f"{int(threshold*100)}%"
        )

        result = run_single_threshold(
            threshold
        )

        if result:
            all_results.append(
                result
            )

    comparison_df = pd.DataFrame(
        all_results
    )

    comparison_df = (
        comparison_df
        .sort_values(
            by="Average Return",
            ascending=False
        )
    )

    print()
    print("=" * 120)
    print("FINAL RESULTS")
    print("=" * 120)

    print(
        comparison_df.to_string(
            index=False
        )
    )


def main():
    run()


if __name__ == "__main__":
    main()