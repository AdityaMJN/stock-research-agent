import pandas as pd

from sqlalchemy import text

from database.connection import engine


SCREENER_NAME = "STRONG_UPTREND"


def calculate_trend_score(row):
    return (
        row["rsi14"] * 0.4
        + row["pct_above_sma20"] * 0.3
        + row["pct_above_sma50"] * 0.2
        + row["pct_above_sma200"] * 0.1
    )


def load_candidates():

    query = """
    SELECT
        listing_id,
        trade_date,
        symbol,
        close_price,
        sma20,
        sma50,
        sma200,
        rsi14,

        ROUND(
            ((close_price - sma20) / NULLIF(sma20, 0)) * 100,
            2
        ) AS pct_above_sma20,

        ROUND(
            ((close_price - sma50) / NULLIF(sma50, 0)) * 100,
            2
        ) AS pct_above_sma50,

        ROUND(
            ((close_price - sma200) / NULLIF(sma200, 0)) * 100,
            2
        ) AS pct_above_sma200

    FROM latest_stock_snapshot

    WHERE close_price > sma20
      AND sma20 > sma50
      AND sma50 > sma200
      AND rsi14 > 60
    """

    return pd.read_sql(query, engine)


def save_results(df):

    if df.empty:
        print("No Strong Uptrend stocks found.")
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

    print(f"Saved {len(df)} Strong Uptrend stocks.")


def run():

    print("Loading Strong Uptrend candidates...")

    df = load_candidates()

    if df.empty:
        print("No candidates found.")
        return

    df["score"] = df.apply(
        calculate_trend_score,
        axis=1,
    )

    df = df.sort_values(
        by="score",
        ascending=False,
    )

    print()
    print("Top 20 Strong Uptrend Stocks")
    print("=" * 80)

    print(
        df[
            [
                "symbol",
                "score",
                "rsi14",
                "pct_above_sma20",
                "pct_above_sma50",
                "pct_above_sma200",
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