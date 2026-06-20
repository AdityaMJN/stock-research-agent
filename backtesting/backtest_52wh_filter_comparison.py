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

PORTFOLIO_SIZE = 10
HOLD_DAYS = 180

THRESHOLD = 0.97

MIN_PRICE = 50
MIN_TURNOVER = 50000000


FILTERS = {

    "ORIGINAL": {
        "price_filter": False,
        "turnover_filter": False
    },

    "PRICE_ONLY": {
        "price_filter": True,
        "turnover_filter": False
    },

    "TURNOVER_ONLY": {
        "price_filter": False,
        "turnover_filter": True
    },

    "PRICE_AND_TURNOVER": {
        "price_filter": True,
        "turnover_filter": True
    }
}


def get_candidates(
    trade_date,
    price_filter,
    turnover_filter
):

    conditions = [
        """
        dp.close_price >=
        h.high_52w * %(threshold)s
        """
    ]

    if price_filter:

        conditions.append(
            """
            dp.close_price >=
            %(min_price)s
            """
        )

    if turnover_filter:

        conditions.append(
            """
            (
                dp.close_price
                *
                dp.volume
            ) >= %(min_turnover)s
            """
        )

    where_clause = "\nAND\n".join(
        conditions
    )

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

        dp.volume,

        (
            dp.close_price
            *
            dp.volume
        ) AS turnover,

        h.high_52w,

        (
            dp.close_price
            /
            NULLIF(h.high_52w, 0)
        ) * 100 AS score

    FROM daily_prices dp

    JOIN highs h
      ON h.listing_id = dp.listing_id

    WHERE dp.trade_date =
          %(trade_date)s

      AND {where_clause}

    ORDER BY score DESC
    """

    return pd.read_sql(
        query,
        engine,
        params={
            "trade_date": trade_date,
            "threshold": THRESHOLD,
            "min_price": MIN_PRICE,
            "min_turnover": MIN_TURNOVER
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
    filter_name,
    config
):

    dates = get_rebalance_dates(
        START_DATE,
        END_DATE
    )

    results = []
    candidate_counts = []

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
            config["price_filter"],
            config["turnover_filter"]
        )

        candidate_counts.append(
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
        "Filter":
            filter_name,

        "Periods":
            len(results),

        "Avg Candidates":
            round(
                sum(candidate_counts)
                /
                len(candidate_counts),
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
    print("52WH FILTER COMPARISON")
    print("=" * 120)

    results = []

    for (
        filter_name,
        config
    ) in FILTERS.items():

        print()
        print(
            f"Running {filter_name}"
        )

        result = run_single_backtest(
            filter_name,
            config
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