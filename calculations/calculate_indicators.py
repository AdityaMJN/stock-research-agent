import pandas as pd

from sqlalchemy import text
from ta.trend import SMAIndicator
from ta.momentum import RSIIndicator

from database.connection import engine


LISTING_ID = 1


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
    params={"listing_id": LISTING_ID}
)

print(f"Loaded {len(df)} rows")

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

print(df.tail())

with engine.begin() as conn:

    for _, row in df.iterrows():

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
            {
                "listing_id": LISTING_ID,
                "trade_date": row["trade_date"],
                "sma20": None if pd.isna(row["sma20"]) else float(row["sma20"]),
                "sma50": None if pd.isna(row["sma50"]) else float(row["sma50"]),
                "sma200": None if pd.isna(row["sma200"]) else float(row["sma200"]),
                "rsi14": None if pd.isna(row["rsi14"]) else float(row["rsi14"])
            }
        )

print("Indicators inserted successfully")