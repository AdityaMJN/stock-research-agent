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

THRESHOLD = 0.97
HOLD_DAYS = 180
PORTFOLIO_SIZE = 10


RANKING_METHODS = {
    "52WH_DISTANCE": "score DESC",
    "RETURN_6M": "ti.return_6m DESC",
    "MOMENTUM_SCORE": "ti.momentum_score DESC",
    "RANDOM": "RANDOM()"
}


def get_candidates(
    trade_date,
    ranking_order
):

    query = f"""
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
        ) * 100 AS score,

        ti.return_3m,
        ti.return_6m,
        ti.momentum_score

    FROM daily_prices dp

    JOIN highs h
      ON h.listing_id = dp.listing_id

    LEFT JOIN technical_indicators ti
      ON ti.listing_id = dp.listing_id
     AND ti.trade_date = dp.trade_date

    WHERE dp.trade_date =
          %(trade_date)s

      AND dp.close_price >=
          h.high_52w *
          %(threshold)s

    ORDER BY {ranking_order}
    """

    return pd.read_sql(
        query,
        engine,
        params={
            "trade_date": trade_date,
            "threshold": THRESHOLD
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


def run_single_backtest(
    ranking_name,
    ranking_order
):

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
            entry_date,
            ranking_order
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
        "Ranking":
            ranking_name,

        "Periods":
            len(results),

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
    print("52WH (97%) RANKING METHOD COMPARISON")
    print("=" * 120)

    results = []

    for (
        ranking_name,
        ranking_order
    ) in RANKING_METHODS.items():

        print()
        print(
            f"Running "
            f"{ranking_name}"
        )

        result = run_single_backtest(
            ranking_name,
            ranking_order
        )

        if result:
            results.append(
                result
            )

    results_df = pd.DataFrame(
        results
    )

    results_df = results_df.sort_values(
        by="Average Return",
        ascending=False
    )

    print()
    print("=" * 120)
    print("FINAL RESULTS")
    print("=" * 120)

    print(
        results_df.to_string(
            index=False
        )
    )


def main():
    run()


if __name__ == "__main__":
    main()