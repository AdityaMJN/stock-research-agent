import pandas as pd
import yfinance as yf
from tqdm import tqdm
from sqlalchemy import text

from database.connection import engine
import time

start_time = time.time()

stocks = pd.read_sql("""
SELECT id, yahoo_symbol
FROM listings
WHERE yahoo_symbol IS NOT NULL
""", engine)

print(f"Found {len(stocks)} stocks")

for _, stock in tqdm(stocks.iterrows(), total=len(stocks)):

    listing_id = int(stock["id"])
    yahoo_symbol = stock["yahoo_symbol"]

    try:

        df = yf.download(
            yahoo_symbol,
            period="5y",
            progress=False,
            auto_adjust=False
        )
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        if df.empty:
            continue

        with engine.begin() as conn:

            for trade_date, row in df.iterrows():

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
                    ON CONFLICT
                    (
                        listing_id,
                        trade_date
                    )
                    DO NOTHING
                    """),
                    {
                        "listing_id": int(listing_id),
                        "trade_date": trade_date.date(),
                        "open_price": float(row["Open"]),
                        "high_price": float(row["High"]),
                        "low_price": float(row["Low"]),
                        "close_price": float(row["Close"]),
                        "adjusted_close": float(row["Adj Close"]),
                        "volume": int(row["Volume"])
            }
                )

    except Exception as ex:

        with engine.begin() as conn:

            conn.execute(
                text("""
                INSERT INTO download_failures
                (
                    listing_id,
                    yahoo_symbol,
                    error_message
                )
                VALUES
                (
                    :listing_id,
                    :yahoo_symbol,
                    :error_message
                )
                """),
                {
                    "listing_id": listing_id,
                    "yahoo_symbol": yahoo_symbol,
                    "error_message": str(ex)
                }
            )

print("Finished")
end_time = time.time()
print(f"Total time taken: {end_time - start_time} seconds")