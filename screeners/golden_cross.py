import pandas as pd

from sqlalchemy import text

from database.connection import engine


SCREENER_NAME = "GOLDEN_CROSS"


def load_candidates():

    query = """
    SELECT
        listing_id,
        trade_date,

        100 -
        LEAST(
            (
                CURRENT_DATE
                - trade_date
            ),
            30
        ) AS score

    FROM golden_cross_candidates

    WHERE trade_date >=
        CURRENT_DATE - INTERVAL '30 days'
    """

    return pd.read_sql(
        query,
        engine
    )


def save_results(df):

    if df.empty:
        return

    with engine.begin() as conn:

        conn.execute(
            text("""
            DELETE FROM screener_results
            WHERE screener_name =
                :screener_name
            """),
            {
                "screener_name":
                    SCREENER_NAME
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
                    row["trade_date"],

                "score":
                    float(
                        row["score"]
                    )
            }
            for _, row
            in df.iterrows()
        ]

        conn.execute(
            text("""
            INSERT INTO
            screener_results
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


def run():

    df = load_candidates()

    if df.empty:

        print(
            "No Golden Cross "
            "candidates found."
        )
        return

    save_results(df)

    print(
        f"Golden Cross "
        f"Stocks: {len(df)}"
    )


def main():
    run()


if __name__ == "__main__":
    main()