import pandas as pd

from sqlalchemy import text

from database.connection import engine


SCREENER_NAME = "STRONG_UPTREND"


def get_latest_trade_date():

    query = """
    SELECT MAX(trade_date) AS trade_date
    FROM technical_indicators
    """

    return pd.read_sql(
        query,
        engine
    ).iloc[0]["trade_date"]


def calculate_trend_score(row):

    return (
        row["rsi14"] * 0.4
        + row["pct_above_sma20"] * 0.3
        + row["pct_above_sma50"] * 0.2
        + row["pct_above_sma200"] * 0.1
    )


def load_candidates(trade_date):

    query = """
    SELECT
        ti.listing_id,
        ti.trade_date,
        l.symbol,

        dp.close_price,

        ti.sma20,
        ti.sma50,
        ti.sma200,
        ti.rsi14,

        ROUND(
            (
                (dp.close_price - ti.sma20)
                / NULLIF(ti.sma20, 0)
            ) * 100,
            2
        ) AS pct_above_sma20,

        ROUND(
            (
                (dp.close_price - ti.sma50)
                / NULLIF(ti.sma50, 0)
            ) * 100,
            2
        ) AS pct_above_sma50,

        ROUND(
            (
                (dp.close_price - ti.sma200)
                / NULLIF(ti.sma200, 0)
            ) * 100,
            2
        ) AS pct_above_sma200

    FROM technical_indicators ti

    JOIN daily_prices dp
      ON dp.listing_id = ti.listing_id
     AND dp.trade_date = ti.trade_date

    JOIN listings l
      ON l.id = ti.listing_id

    WHERE ti.trade_date = %(trade_date)s

      AND dp.close_price > ti.sma20
      AND ti.sma20 > ti.sma50
      AND ti.sma50 > ti.sma200
      AND ti.rsi14 > 60
    """

    return pd.read_sql(
        query,
        engine,
        params={
            "trade_date": trade_date
        }
    )


def save_results(
    df,
    trade_date
):

    if df.empty:

        print(
            "No Strong Uptrend stocks found."
        )
        return

    with engine.begin() as conn:

        conn.execute(
        text("""
        DELETE FROM screener_results
        WHERE screener_name = :screener_name
        AND trade_date = :trade_date
        """),
        {
            "screener_name": SCREENER_NAME,
            "trade_date": trade_date
        }
    )
        records = [
            {
                "screener_name":
                    SCREENER_NAME,

                "listing_id":
                    int(
                        row["listing_id"]
                    ),

                "trade_date":
                    trade_date,

                "score":
                    float(
                        row["score"]
                    ),
            }
            for _, row in df.iterrows()
        ]

        conn.execute(
            text("""
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
            """),
            records
        )

    print(
        f"Saved {len(df)} "
        f"Strong Uptrend stocks."
    )


def run(trade_date=None):

    if trade_date is None:

        trade_date = (
            get_latest_trade_date()
        )

    print()
    print("=" * 80)
    print(
        f"STRONG UPTREND "
        f"({trade_date})"
    )
    print("=" * 80)

    df = load_candidates(
        trade_date
    )

    if df.empty:

        print(
            f"No candidates found "
            f"for {trade_date}"
        )
        return pd.DataFrame()

    df["score"] = df.apply(
        calculate_trend_score,
        axis=1
    )

    df = df.sort_values(
        by="score",
        ascending=False
    )

    print()

    print(
        df[
            [
                "symbol",
                "score",
                "rsi14",
                "pct_above_sma20",
                "pct_above_sma50",
                "pct_above_sma200"
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
        f"Total qualifying stocks: "
        f"{len(df)}"
    )

    return df


def main():
    run()


if __name__ == "__main__":
    main()