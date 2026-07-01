import pandas as pd

from sqlalchemy import text

from database.connection import engine

from utils.trade_dates import (
    get_latest_complete_trade_date
)


SCREENER_NAME = "MOMENTUM"

TOP_STOCKS = 100


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


def save_results(
    df,
    trade_date
):

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

    records = []

    for _, row in df.iterrows():

        records.append(
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


def run(trade_date=None):

    if trade_date is None:

        trade_date = (
            get_latest_complete_trade_date()
        )

    print()
    print("=" * 80)
    print(
        f"MOMENTUM SCREENER "
        f"({trade_date})"
    )
    print("=" * 80)

    df = load_candidates(
        trade_date
    )

    if df.empty:

        print(
            f"No candidates found for "
            f"{trade_date}"
        )
        return pd.DataFrame()

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
        f"Saved {len(df)} "
        f"Momentum results"
    )

    return df


def main():
    run()


if __name__ == "__main__":
    main()