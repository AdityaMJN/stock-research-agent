import pandas as pd

from sqlalchemy import text

from database.connection import engine


SCREENER_NAME = "FIFTY_TWO_WEEK_HIGH"


def load_candidates():

    query = """
    SELECT
        s.listing_id,
        s.trade_date,
        s.symbol,
        s.close_price,
        h.high_52w,

        ROUND(
            (s.close_price / NULLIF(h.high_52w,0)) * 100,
            2
        ) AS score

    FROM latest_stock_snapshot s

    JOIN stock_52w_stats h
        ON h.listing_id = s.listing_id

    WHERE s.close_price >= h.high_52w * 0.95
    """

    return pd.read_sql(query, engine)


def save_results(df):

    if df.empty:
        return

    latest_trade_date = df["trade_date"].max()

    with engine.begin() as conn:

        conn.execute(
            text(
                """
                DELETE FROM screener_results
                WHERE screener_name = :screener_name
                  AND trade_date = :trade_date
                """
            ),
            {
                "screener_name": SCREENER_NAME,
                "trade_date": latest_trade_date,
            },
        )

        records = [
            {
                "screener_name": SCREENER_NAME,
                "listing_id": int(row["listing_id"]),
                "trade_date": row["trade_date"],
                "score": float(row["score"]),
            }
            for _, row in df.iterrows()
        ]

        conn.execute(
            text(
                """
                INSERT INTO screener_results
                (
                    screener_name,
                    listing_id,
                    trade_date,
                    score,
                    created_at
                )
                VALUES
                (
                    :screener_name,
                    :listing_id,
                    :trade_date,
                    :score,
                    NOW()
                )
                """
            ),
            records,
        )


def run():

    df = load_candidates()

    if df.empty:
        print("No candidates found.")
        return

    df = df.sort_values(
        by="score",
        ascending=False,
    )

    print()
    print("Top 20 Near 52 Week High Stocks")
    print("=" * 80)

    print(
        df[
            [
                "symbol",
                "close_price",
                "high_52w",
                "score",
            ]
        ]
        .head(20)
        .to_string(index=False)
    )

    save_results(df)

    print()
    print(f"Total qualifying stocks: {len(df)}")


if __name__ == "__main__":
    run()