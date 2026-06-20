import pandas as pd

from sqlalchemy import text

from database.connection import engine


SCREENER_NAME = "MOMENTUM"

TOP_STOCKS = 100


def get_latest_trade_date():

    query = """
    SELECT MAX(trade_date) AS trade_date
    FROM technical_indicators
    WHERE momentum_score IS NOT NULL
    """

    return pd.read_sql(
        query,
        engine
    ).iloc[0]["trade_date"]


def load_candidates(trade_date):

    query = """
    SELECT
        ti.listing_id,
        ti.return_3m,
        ti.return_6m,
        ti.momentum_score,
        dp.close_price

    FROM technical_indicators ti

    JOIN daily_prices dp
      ON dp.listing_id = ti.listing_id
     AND dp.trade_date = ti.trade_date

    WHERE ti.trade_date = %(trade_date)s

      AND ti.momentum_score IS NOT NULL

      AND dp.close_price >= 20

    ORDER BY
        ti.momentum_score DESC
    """

    return pd.read_sql(
        query,
        engine,
        params={
            "trade_date": trade_date
        }
    )


def save_results(df, trade_date):

    with engine.begin() as conn:

        conn.execute(
            text("""
            DELETE FROM screener_results
            WHERE screener_name = :screener_name
            """),
            {
                "screener_name": SCREENER_NAME
            }
        )

    records = []

    for _, row in df.iterrows():

        records.append(
            {
                "screener_name": SCREENER_NAME,
                "listing_id": int(
                    row["listing_id"]
                ),
                "trade_date": trade_date,
                "score": float(
                    row["momentum_score"]
                )
            }
        )

    with engine.begin() as conn:

        conn.execute(
            text("""
            INSERT INTO screener_results
            (
                screener_name,
                listing_id,
                trade_date,
                score
            )
            VALUES
            (
                :screener_name,
                :listing_id,
                :trade_date,
                :score
            )
            """),
            records
        )


def run():

    trade_date = get_latest_trade_date()

    df = load_candidates(
        trade_date
    )

    if df.empty:

        print(
            "No candidates found."
        )
        return

    df = df.head(
        TOP_STOCKS
    )

    symbols = pd.read_sql(
        """
        SELECT
            id,
            symbol
        FROM listings
        """,
        engine
    )

    df = df.merge(
        symbols,
        left_on="listing_id",
        right_on="id",
        how="left"
    )

    print()
    print("=" * 80)
    print("TOP MOMENTUM STOCKS")
    print("=" * 80)

    print(
        df[
            [
                "symbol",
                "return_3m",
                "return_6m",
                "momentum_score"
            ]
        ]
        .head(20)
        .to_string(index=False)
    )

    save_results(
        df,
        trade_date
    )

    print()
    print(
        f"Saved {len(df)} Momentum results"
    )


def main():
    run()


if __name__ == "__main__":
    main()