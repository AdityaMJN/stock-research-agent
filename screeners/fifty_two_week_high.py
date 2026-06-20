import pandas as pd

from sqlalchemy import text

from database.connection import engine


SCREENER_NAME = "FIFTY_TWO_WEEK_HIGH"


def get_latest_trade_date():

    query = """
    SELECT MAX(trade_date) AS trade_date
    FROM daily_prices
    """

    return pd.read_sql(
        query,
        engine
    ).iloc[0]["trade_date"]


def load_candidates(trade_date):

    query = """
    WITH highs AS
    (
        SELECT
            dp1.listing_id,

            MAX(dp2.close_price)
                AS high_52w

        FROM daily_prices dp1

        JOIN daily_prices dp2
          ON dp2.listing_id =
             dp1.listing_id

         AND dp2.trade_date
             BETWEEN
             dp1.trade_date
             - INTERVAL '365 days'
             AND
             dp1.trade_date

        WHERE dp1.trade_date =
              %(trade_date)s

        GROUP BY
            dp1.listing_id
    )

    SELECT
        dp.listing_id,
        dp.trade_date,
        l.symbol,

        dp.close_price,

        h.high_52w,

        ROUND(
            (
                dp.close_price
                /
                NULLIF(
                    h.high_52w,
                    0
                )
            ) * 100,
            2
        ) AS score

    FROM daily_prices dp

    JOIN highs h
      ON h.listing_id =
         dp.listing_id

    JOIN listings l
      ON l.id =
         dp.listing_id

    WHERE dp.trade_date =
          %(trade_date)s

      AND dp.close_price >=
          h.high_52w * 0.95
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


def run(trade_date=None):

    if trade_date is None:

        trade_date = (
            get_latest_trade_date()
        )

    print()
    print("=" * 80)
    print(
        f"52 WEEK HIGH "
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

    df = df.sort_values(
        by="score",
        ascending=False
    )

    print()

    print(
        df[
            [
                "symbol",
                "close_price",
                "high_52w",
                "score"
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