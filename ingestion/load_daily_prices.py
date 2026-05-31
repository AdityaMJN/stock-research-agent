import yfinance as yf
import pandas as pd

from sqlalchemy import text

from database.connection import engine

TEST_SYMBOL = "TCS.NS"

# Download data
ticker = yf.Ticker(TEST_SYMBOL)
df = ticker.history(period="1y")

# Find listing_id from DB
listing = pd.read_sql(
    """
    SELECT id
    FROM listings
    WHERE yahoo_symbol = 'TCS.NS'
    """,
    engine
)

listing_id = int(listing.iloc[0]["id"])

print("Listing ID:", listing_id)

# Store into database
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
               "volume": int(row["Volume"]) if pd.notna(row["Volume"]) else 0
            }
        )

print("Import completed")