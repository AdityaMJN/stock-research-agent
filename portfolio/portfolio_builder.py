import pandas as pd

from sqlalchemy import text

from database.connection import engine

from utils.trade_dates import (
    get_latest_complete_trade_date
)


PORTFOLIOS = [
    ("TOP10", 10),
    ("TOP20", 20),
    ("TOP50", 50)
]


def load_rankings():

    query = """
    SELECT
        listing_id,
        rank_position,
        score,
        trade_date
    FROM screener_results
    WHERE screener_name = 'COMBINED_RANKING'
    ORDER BY rank_position
    """

    return pd.read_sql(
        query,
        engine
    )


def save_portfolio(
    portfolio_name,
    portfolio_df,
    trade_date
):

    weight = round(
        1.0 / len(portfolio_df),
        4
    )

    records = []

    for _, row in portfolio_df.iterrows():

        records.append(
            {
                "portfolio_name":
                    portfolio_name,

                "trade_date":
                    trade_date,

                "listing_id":
                    int(
                        row["listing_id"]
                    ),

                "rank_position":
                    int(
                        row["rank_position"]
                    ),

                "weight":
                    weight,

                "score":
                    float(
                        row["score"]
                    )
            }
        )

    with engine.begin() as conn:

        conn.execute(
            text("""
            DELETE FROM portfolios
            WHERE portfolio_name =
                :portfolio_name
            AND trade_date =
                :trade_date
            """),
            {
                "portfolio_name":
                    portfolio_name,
                "trade_date":
                    trade_date
            }
        )

        conn.execute(
            text("""
            INSERT INTO portfolios
            (
                portfolio_name,
                trade_date,
                listing_id,
                rank_position,
                weight,
                score,
                created_at
            )
            VALUES
            (
                :portfolio_name,
                :trade_date,
                :listing_id,
                :rank_position,
                :weight,
                :score,
                NOW()
            )
            """),
            records
        )


def print_portfolio(
    portfolio_name,
    portfolio_df
):

    listings = pd.read_sql(
        """
        SELECT
            id,
            symbol
        FROM listings
        """,
        engine
    )

    result = portfolio_df.merge(
        listings,
        left_on="listing_id",
        right_on="id",
        how="left"
    )

    print()
    print("=" * 80)
    print(portfolio_name)
    print("=" * 80)

    print(
        result[
            [
                "rank_position",
                "symbol",
                "score"
            ]
        ]
        .to_string(index=False)
    )


def run(trade_date=None):

    rankings = load_rankings()

    if rankings.empty:

        print(
            "No combined ranking data found."
        )
        return

    if trade_date is None:
        trade_date = get_latest_complete_trade_date()
    
    rankings = rankings[rankings["trade_date"]== trade_date].copy()

    print()
    print(
        f"Building portfolios "
        f"for {trade_date}"
    )

    for portfolio_name, size in PORTFOLIOS:

        portfolio_df = (
            rankings
            .head(size)
            .copy()
        )

        save_portfolio(
            portfolio_name,
            portfolio_df,
            trade_date
        )

        print_portfolio(
            portfolio_name,
            portfolio_df.head(10)
        )

        print()
        print(
            f"{portfolio_name}: "
            f"{len(portfolio_df)} stocks"
        )

    print()
    print("=" * 80)
    print(
        "PORTFOLIO BUILD COMPLETE"
    )
    print("=" * 80)


def main():
    run()


if __name__ == "__main__":
    main()