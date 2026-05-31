import pandas as pd

from sqlalchemy import text
from tqdm import tqdm

from database.connection import engine


def calculate_return(current_price, old_price):

    if old_price is None:
        return None

    if old_price <= 0:
        return None

    return ((current_price - old_price) / old_price) * 100


def main():

    listings = pd.read_sql(
        """
        SELECT DISTINCT listing_id
        FROM daily_prices
        ORDER BY listing_id
        """,
        engine
    )

    results = []

    for _, listing_row in tqdm(
        listings.iterrows(),
        total=len(listings)
    ):

        listing_id = int(
            listing_row["listing_id"]
        )

        df = pd.read_sql(
            """
            SELECT
                trade_date,
                close_price
            FROM daily_prices
            WHERE listing_id = %(listing_id)s
            ORDER BY trade_date
            """,
            engine,
            params={
                "listing_id": listing_id
            }
        )

        if len(df) < 126:
            continue

        current_price = float(
            df.iloc[-1]["close_price"]
        )

        if current_price < 20:
            continue

        price_3m = float(
            df.iloc[-63]["close_price"]
        )

        price_6m = float(
            df.iloc[-126]["close_price"]
        )

        if price_6m < 20:
            continue

        return_3m = calculate_return(
            current_price,
            price_3m
        )

        return_6m = calculate_return(
            current_price,
            price_6m
        )

        momentum_score = (
            (return_3m * 0.4)
            +
            (return_6m * 0.6)
        )

        results.append(
            {
                "listing_id": listing_id,
                "return_3m": round(
                    return_3m,
                    2
                ),
                "return_6m": round(
                    return_6m,
                    2
                ),
                "momentum_score": round(
                    momentum_score,
                    2
                )
            }
        )

    results_df = pd.DataFrame(results)

    symbols_df = pd.read_sql(
        """
        SELECT

            l.id AS listing_id,
            l.symbol,
            c.company_name

        FROM listings l

        JOIN companies c
            ON c.id = l.company_id
        """,
        engine
    )

    results_df = results_df.merge(
        symbols_df,
        on="listing_id",
        how="left"
    )

    results_df = results_df[
        [
            "listing_id",
            "symbol",
            "company_name",
            "return_3m",
            "return_6m",
            "momentum_score"
        ]
    ]

    results_df = results_df.sort_values(
        "momentum_score",
        ascending=False
    )

    print()
    print(results_df.head(50))

    print()
    print(
        f"Stocks Found: "
        f"{len(results_df)}"
    )

    top_stocks = results_df.head(100)

    latest_trade_date = pd.read_sql(
        """
        SELECT MAX(trade_date) AS trade_date
        FROM daily_prices
        """,
        engine
    ).iloc[0]["trade_date"]

    with engine.begin() as conn:

        conn.execute(
            text("""
                DELETE FROM screener_results
                WHERE screener_name = 'Momentum'
            """)
        )

    records = []

    for _, row in top_stocks.iterrows():

        records.append(
            {
                "screener_name": "Momentum",
                "listing_id": int(
                    row["listing_id"]
                ),
                "trade_date": latest_trade_date,
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

    print()
    print(
        f"Saved {len(records)} "
        f"Momentum results"
    )


if __name__ == "__main__":
    main()