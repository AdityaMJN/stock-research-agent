import pandas as pd

from sqlalchemy import text

from database.connection import engine


def load_prices():

    query = """
    SELECT
        listing_id,
        trade_date,
        adjusted_close
    FROM daily_prices
    ORDER BY
        listing_id,
        trade_date
    """

    return pd.read_sql(
        query,
        engine,
        parse_dates=["trade_date"]
    )


def calculate_momentum(df):

    result_frames = []

    for listing_id, stock_df in df.groupby("listing_id"):

        stock_df = stock_df.copy()

        stock_df = stock_df.sort_values(
            "trade_date"
        )

        stock_df["return_3m"] = (
            (
                stock_df["adjusted_close"]
                /
                stock_df["adjusted_close"].shift(63)
            )
            - 1
        ) * 100

        stock_df["return_6m"] = (
            (
                stock_df["adjusted_close"]
                /
                stock_df["adjusted_close"].shift(126)
            )
            - 1
        ) * 100

        stock_df["momentum_score"] = (
            stock_df["return_3m"] * 0.4
            +
            stock_df["return_6m"] * 0.6
        )

        result_frames.append(
            stock_df[
                [
                    "listing_id",
                    "trade_date",
                    "return_3m",
                    "return_6m",
                    "momentum_score"
                ]
            ]
        )

    return pd.concat(
        result_frames,
        ignore_index=True
    )


def update_indicators(momentum_df):

    total = len(momentum_df)

    processed = 0

    with engine.begin() as conn:

        for _, row in momentum_df.iterrows():

            conn.execute(
                text("""
                UPDATE technical_indicators
                SET
                    return_3m = :return_3m,
                    return_6m = :return_6m,
                    momentum_score = :momentum_score
                WHERE
                    listing_id = :listing_id
                AND
                    trade_date = :trade_date
                """),
                {
                    "listing_id": int(
                        row["listing_id"]
                    ),
                    "trade_date": row[
                        "trade_date"
                    ].date(),
                    "return_3m":
                        None
                        if pd.isna(
                            row["return_3m"]
                        )
                        else float(
                            row["return_3m"]
                        ),
                    "return_6m":
                        None
                        if pd.isna(
                            row["return_6m"]
                        )
                        else float(
                            row["return_6m"]
                        ),
                    "momentum_score":
                        None
                        if pd.isna(
                            row["momentum_score"]
                        )
                        else float(
                            row["momentum_score"]
                        )
                }
            )

            processed += 1

            if processed % 10000 == 0:

                print(
                    f"Updated "
                    f"{processed:,} / "
                    f"{total:,}"
                )

    print()
    print(
        f"Completed "
        f"{processed:,} rows"
    )


def run():

    print(
        "Loading price history..."
    )

    prices = load_prices()

    print(
        f"Loaded "
        f"{len(prices):,} rows"
    )

    print(
        "Calculating momentum..."
    )

    momentum_df = calculate_momentum(
        prices
    )

    print(
        "Updating technical indicators..."
    )

    update_indicators(
        momentum_df
    )

    print(
        "Momentum backfill complete."
    )


def main():
    run()


if __name__ == "__main__":
    main()