import time

import pandas as pd

from tqdm import tqdm

from sqlalchemy import text

from ta.trend import SMAIndicator
from ta.momentum import RSIIndicator

from database.connection import engine


def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:

    df["sma20"] = SMAIndicator(
        close=df["close_price"],
        window=20
    ).sma_indicator()

    df["sma50"] = SMAIndicator(
        close=df["close_price"],
        window=50
    ).sma_indicator()

    df["sma200"] = SMAIndicator(
        close=df["close_price"],
        window=200
    ).sma_indicator()

    df["rsi14"] = RSIIndicator(
        close=df["close_price"],
        window=14
    ).rsi()

    return df


def insert_indicators(listing_id: int, df: pd.DataFrame):

    records = []

    for _, row in df.iterrows():

        records.append(
            {
                "listing_id": listing_id,
                "trade_date": row["trade_date"],

                "sma20": None if pd.isna(row["sma20"])
                else float(row["sma20"]),

                "sma50": None if pd.isna(row["sma50"])
                else float(row["sma50"]),

                "sma200": None if pd.isna(row["sma200"])
                else float(row["sma200"]),

                "rsi14": None if pd.isna(row["rsi14"])
                else float(row["rsi14"])
            }
        )

    if not records:
        return

    with engine.begin() as conn:

        conn.execute(
            text("""
                INSERT INTO technical_indicators
                (
                    listing_id,
                    trade_date,
                    sma20,
                    sma50,
                    sma200,
                    rsi14
                )
                VALUES
                (
                    :listing_id,
                    :trade_date,
                    :sma20,
                    :sma50,
                    :sma200,
                    :rsi14
                )
                ON CONFLICT
                (
                    listing_id,
                    trade_date
                )
                DO UPDATE SET

                    sma20 = EXCLUDED.sma20,
                    sma50 = EXCLUDED.sma50,
                    sma200 = EXCLUDED.sma200,
                    rsi14 = EXCLUDED.rsi14
            """),
            records
        )


def run():

    start_time = time.time()

    listings = pd.read_sql(
        """
        SELECT DISTINCT listing_id
        FROM daily_prices
        ORDER BY listing_id
        """,
        engine
    )

    total_listings = len(listings)

    print(f"Found {total_listings} listings")

    processed = 0
    skipped = 0

    for _, listing_row in tqdm(
        listings.iterrows(),
        total=total_listings
    ):

        listing_id = int(listing_row["listing_id"])

        try:

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

            if len(df) < 20:

                skipped += 1
                continue

            df = calculate_indicators(df)

            insert_indicators(
                listing_id,
                df
            )

            processed += 1

        except Exception as ex:

            print(
                f"Error processing "
                f"listing_id={listing_id}: "
                f"{str(ex)}"
            )

    elapsed = time.time() - start_time

    print()
    print("====================================")
    print(f"Processed Listings : {processed}")
    print(f"Skipped Listings   : {skipped}")
    print(f"Total Listings     : {total_listings}")
    print(f"Time Taken         : {elapsed:.2f} seconds")
    print("====================================")


def main():
    run()


if __name__ == "__main__":
    main()