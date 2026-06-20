import pandas as pd

from sqlalchemy import text

from database.connection import engine


PORTFOLIO_NAME = "TOP20"


def load_positions():

    query = """
    SELECT
       pp.listing_id,
        l.symbol,
        pp.quantity,
        pp.average_cost,
        pp.current_price,
        pp.market_value,
        pp.unrealized_pnl,
        pp.unrealized_pnl_pct
    FROM portfolio_positions pp

    JOIN listings l
      ON l.id = pp.listing_id

    WHERE pp.portfolio_name =
        %(portfolio_name)s

    ORDER BY
        pp.market_value DESC
    """

    return pd.read_sql(
        query,
        engine,
        params={
            "portfolio_name":
                PORTFOLIO_NAME
        }
    )


def portfolio_summary(df):

    total_value = (
        df["market_value"]
        .fillna(0)
        .sum()
    )

    print()
    print("=" * 80)
    print("PORTFOLIO SUMMARY")
    print("=" * 80)

    print(
        f"Portfolio : "
        f"{PORTFOLIO_NAME}"
    )

    print(
        f"Positions : "
        f"{len(df)}"
    )

    print(
        f"Value     : "
        f"₹{total_value:,.2f}"
    )


def print_positions(df):

    print()
    print("=" * 80)
    print("CURRENT POSITIONS")
    print("=" * 80)

    if df.empty:

        print(
            "No positions found."
        )

        return

    print(
        df[
            [
                "symbol",
                "quantity",
                "average_cost",
                "current_price",
                "market_value"
            ]
        ]
        .to_string(
            index=False
        )
    )


def run():

    positions = (
        load_positions()
    )

    portfolio_summary(
        positions
    )

    print_positions(
        positions
    )

    return positions


def main():
    run()


if __name__ == "__main__":
    main()