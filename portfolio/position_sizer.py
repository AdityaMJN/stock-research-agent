import pandas as pd

from database.connection import engine


PORTFOLIO_NAME = "TOP20"

PORTFOLIO_VALUE = 1000000


def load_target_portfolio():

    query = """
    SELECT
        p.listing_id,
        l.symbol,
        p.rank_position,
        p.weight
    FROM portfolios p

    JOIN listings l
      ON l.id = p.listing_id

    WHERE p.portfolio_name =
        %(portfolio_name)s

    AND p.trade_date =
    (
        SELECT MAX(trade_date)
        FROM portfolios
        WHERE portfolio_name =
            %(portfolio_name)s
    )

    ORDER BY rank_position
    """

    return pd.read_sql(
        query,
        engine,
        params={
            "portfolio_name":
                PORTFOLIO_NAME
        }
    )


def load_latest_prices():

    query = """
    SELECT
        l.symbol,
        dp.close_price
    FROM daily_prices dp

    JOIN listings l
      ON l.id = dp.listing_id

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


def build_position_sizes():

    portfolio = (
        load_target_portfolio()
    )

    prices = (
        load_latest_prices()
    )

    df = portfolio.merge(
        prices,
        on="symbol",
        how="left"
    )

    target_value = (
        PORTFOLIO_VALUE
        /
        len(df)
    )

    df["target_value"] = (
        target_value
    )

    df["target_quantity"] = (
        df["target_value"]
        /
        df["close_price"]
    ).astype(int)

    df["actual_value"] = (
        df["target_quantity"]
        *
        df["close_price"]
    )

    return df


def print_positions(df):

    print()
    print("=" * 120)
    print("POSITION SIZING")
    print("=" * 120)

    print(
        df[
            [
                "rank_position",
                "symbol",
                "close_price",
                "target_quantity",
                "actual_value"
            ]
        ]
        .to_string(
            index=False
        )
    )

    print()
    print("=" * 120)

    print(
        f"Portfolio Value : "
        f"₹{PORTFOLIO_VALUE:,.0f}"
    )

    print(
        f"Stocks          : "
        f"{len(df)}"
    )

    print(
        f"Target/Stock    : "
        f"₹{PORTFOLIO_VALUE / len(df):,.0f}"
    )

    print(
        f"Allocated       : "
        f"₹{df['actual_value'].sum():,.0f}"
    )

    print(
        f"Cash Left       : "
        f"₹{PORTFOLIO_VALUE - df['actual_value'].sum():,.0f}"
    )


def run():

    df = (
        build_position_sizes()
    )

    print_positions(
        df
    )

    return df


def main():
    run()


if __name__ == "__main__":
    main()