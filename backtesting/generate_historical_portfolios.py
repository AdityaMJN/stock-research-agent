import pandas as pd

from database.connection import engine
from portfolio.portfolio_builder import (
    save_portfolio
)


PORTFOLIOS = [
    ("TOP10", 10),
    ("TOP20", 20),
    ("TOP50", 50)
]


def load_ranking_dates():

    query = """
    SELECT DISTINCT trade_date
    FROM screener_results
    WHERE screener_name = 'COMBINED_RANKING'
    ORDER BY trade_date
    """

    return pd.read_sql(
        query,
        engine,
        parse_dates=["trade_date"]
    )["trade_date"].tolist()


def load_rankings(trade_date):

    query = """
    SELECT
        listing_id,
        rank_position,
        score,
        trade_date
    FROM screener_results
    WHERE screener_name =
        'COMBINED_RANKING'
    AND trade_date =
        %(trade_date)s
    ORDER BY rank_position
    """

    return pd.read_sql(
        query,
        engine,
        params={
            "trade_date": trade_date
        }
    )


def run():

    dates = load_ranking_dates()

    print()
    print(
        f"Found {len(dates)} ranking dates"
    )

    total_portfolios = 0

    for trade_date in dates:

        print()
        print(
            f"Processing {trade_date.date()}"
        )

        rankings = load_rankings(
            trade_date
        )

        if rankings.empty:

            continue

        for portfolio_name, size in PORTFOLIOS:

            portfolio_df = (
                rankings
                .head(size)
                .copy()
            )

            save_portfolio(
                portfolio_name,
                portfolio_df,
                trade_date.date()
            )

            total_portfolios += 1

    print()
    print("=" * 80)
    print(
        f"Generated {total_portfolios} "
        f"portfolio snapshots"
    )
    print("=" * 80)


def main():
    run()


if __name__ == "__main__":
    main()