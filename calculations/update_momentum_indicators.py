import pandas as pd

from sqlalchemy import text
from tqdm import tqdm

from database.connection import engine


CHUNK_SIZE = 5000


def load_prices():

    query = """
    SELECT
        listing_id,
        trade_date,
        close_price
    FROM daily_prices
    ORDER BY
        listing_id,
        trade_date
    """

    return pd.read_sql(
        query,
        engine
    )


def calculate_momentum(df):

    print()
    print("Calculating momentum indicators...")

    df["price_3m"] = (
        df.groupby("listing_id")["close_price"]
        .shift(63)
    )

    df["price_6m"] = (
        df.groupby("listing_id")["close_price"]
        .shift(126)
    )

    df["return_3m"] = (
        (
            df["close_price"]
            - df["price_3m"]
        )
        / df["price_3m"]
    ) * 100

    df["return_6m"] = (
        (
            df["close_price"]
            - df["price_6m"]
        )
        / df["price_6m"]
    ) * 100

    df["momentum_score"] = (
        (df["return_3m"] * 0.4)
        +
        (df["return_6m"] * 0.6)
    )

    df = df[
        [
            "listing_id",
            "trade_date",
            "return_3m",
            "return_6m",
            "momentum_score"
        ]
    ]

    df = df.dropna(
        subset=[
            "momentum_score"
        ]
    )

    return df


def update_indicators(df):

    records = df.to_dict(
        orient="records"
    )

    update_sql = """
    UPDATE technical_indicators
    SET
        return_3m = :return_3m,
        return_6m = :return_6m,
        momentum_score = :momentum_score
    WHERE
        listing_id = :listing_id
    AND
        trade_date = :trade_date
    """

    print()
    print(
        f"Updating {len(records):,} rows..."
    )

    for i in tqdm(
        range(
            0,
            len(records),
            CHUNK_SIZE
        )
    ):

        chunk = records[
            i:i + CHUNK_SIZE
        ]

        with engine.begin() as conn:

            conn.execute(
                text(update_sql),
                chunk
            )

    print()
    print(
        "Momentum indicators updated."
    )


def run():

    print()
    print("=" * 60)
    print("MOMENTUM INDICATOR UPDATE")
    print("=" * 60)

    prices_df = load_prices()

    print()
    print(
        f"Loaded {len(prices_df):,} price rows"
    )

    momentum_df = calculate_momentum(
        prices_df
    )

    print()
    print(
        f"Calculated {len(momentum_df):,} momentum rows"
    )

    update_indicators(
        momentum_df
    )

    print()
    print("Completed successfully.")


def main():
    run()


if __name__ == "__main__":
    main()