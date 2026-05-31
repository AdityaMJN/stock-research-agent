import pandas as pd
import yfinance as yf

from datetime import timedelta

from sqlalchemy import text

from database.connection import engine


def get_all_listings():

    query = """
    SELECT
        id,
        yahoo_symbol
    FROM listings
    WHERE yahoo_symbol IS NOT NULL
    """

    return pd.read_sql(query, engine)


def get_latest_date(listing_id):

    query = text("""
        SELECT MAX(trade_date)
        FROM daily_prices
        WHERE listing_id = :listing_id
    """)

    with engine.begin() as conn:

        result = conn.execute(
            query,
            {"listing_id": listing_id}
        ).scalar()

    return result


def download_missing_data(symbol, start_date):

    ticker = yf.Ticker(symbol)

    df = ticker.history(
        start=start_date
    )

    return df


def save_prices(df, listing_id):

    inserted = 0

    with engine.begin() as conn:

        for index, row in df.iterrows():

            conn.execute(
                text("""
                    INSERT INTO daily_prices
                    (
                        listing_id,
                        trade_date,
                        open_price,
                        high_price,
                        low_price,
                        close_price,
                        adjusted_close,
                        volume
                    )
                    VALUES
                    (
                        :listing_id,
                        :trade_date,
                        :open_price,
                        :high_price,
                        :low_price,
                        :close_price,
                        :adjusted_close,
                        :volume
                    )
                    ON CONFLICT (listing_id, trade_date)
                    DO NOTHING
                """),
                {
                    "listing_id": listing_id,
                    "trade_date": index.date(),
                    "open_price": float(row["Open"]),
                    "high_price": float(row["High"]),
                    "low_price": float(row["Low"]),
                    "close_price": float(row["Close"]),
                    "adjusted_close": float(row["Close"]),
                    "volume": int(row["Volume"])
                    if pd.notna(row["Volume"])
                    else 0,
                }
            )

            inserted += 1

    return inserted


def run():

    listings = get_all_listings()
    listings = listings.head(50)

    print(f"Found {len(listings)} listings")

    total_rows = 0

    for _, listing in listings.iterrows():

        listing_id = int(listing["id"])
        symbol = listing["yahoo_symbol"]

        latest_date = get_latest_date(listing_id)

        if latest_date is None:

            print(
                f"{symbol}: no history found, skipping"
            )

            continue

        start_date = latest_date + timedelta(days=1)

        print(
            f"{symbol}: updating from {start_date}"
        )

        try:

            df = download_missing_data(
                symbol,
                start_date
            )

            if df.empty:

                continue

            inserted = save_prices(
                df,
                listing_id
            )

            total_rows += inserted

        except Exception as ex:

            print(
                f"Failed {symbol}: {ex}"
            )

    print()
    print(
        f"Update complete. Inserted approximately {total_rows} rows."
    )


if __name__ == "__main__":
    run()