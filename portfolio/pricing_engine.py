import pandas as pd

from sqlalchemy import text

from database.connection import engine


def load_positions():

    query = """
    SELECT
        portfolio_name,
        listing_id,
        quantity,
        average_cost
    FROM portfolio_positions
    """

    return pd.read_sql(
        query,
        engine
    )


def load_latest_prices():

    query = """
    SELECT
        dp.listing_id,
        dp.close_price
    FROM daily_prices dp

    JOIN
    (
        SELECT
            listing_id,
            MAX(trade_date)
                AS trade_date
        FROM daily_prices
        GROUP BY listing_id
    ) latest

      ON latest.listing_id =
            dp.listing_id

     AND latest.trade_date =
            dp.trade_date
    """

    return pd.read_sql(
        query,
        engine
    )


def update_prices(df):

    with engine.begin() as conn:

        for _, row in df.iterrows():

            current_price = float(
                row["close_price"]
            )

            market_value = (
                float(
                    row["quantity"]
                )
                *
                current_price
            )

            pnl = (
                current_price
                -
                float(
                    row["average_cost"]
                )
            ) * float(
                row["quantity"]
            )

            pnl_pct = (
                (
                    current_price
                    /
                    float(
                        row[
                            "average_cost"
                        ]
                    )
                )
                - 1
            ) * 100

            conn.execute(
                text("""
                UPDATE portfolio_positions
                SET
                    current_price =
                        :current_price,

                    market_value =
                        :market_value,

                    unrealized_pnl =
                        :pnl,

                    unrealized_pnl_pct =
                        :pnl_pct

                WHERE portfolio_name =
                    :portfolio_name

                AND listing_id =
                    :listing_id
                """),
                {
                    "portfolio_name":
                        row[
                            "portfolio_name"
                        ],

                    "listing_id":
                        int(
                            row[
                                "listing_id"
                            ]
                        ),

                    "current_price":
                        current_price,

                    "market_value":
                        market_value,

                    "pnl":
                        pnl,

                    "pnl_pct":
                        pnl_pct
                }
            )


def run():

    positions = (
        load_positions()
    )

    prices = (
        load_latest_prices()
    )

    df = positions.merge(
        prices,
        on="listing_id",
        how="left"
    )

    update_prices(df)

    print(
        f"Updated "
        f"{len(df)} positions"
    )


if __name__ == "__main__":
    run()