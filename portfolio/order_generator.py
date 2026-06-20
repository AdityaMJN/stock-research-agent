import pandas as pd

from database.connection import engine

from portfolio.position_sizer import (
    build_position_sizes
)


PORTFOLIO_NAME = "TOP20"


def load_current_positions():

    query = """
    SELECT
        pp.listing_id,
        l.symbol,
        pp.quantity
    FROM portfolio_positions pp

    JOIN listings l
      ON l.id = pp.listing_id

    WHERE pp.portfolio_name =
        %(portfolio_name)s
    """

    return pd.read_sql(
        query,
        engine,
        params={
            "portfolio_name":
                PORTFOLIO_NAME
        }
    )


def generate_orders():

    target = (
        build_position_sizes()
    )

    current = (
        load_current_positions()
    )

    current_map = {}

    for _, row in current.iterrows():

        current_map[
            row["symbol"]
        ] = int(
            row["quantity"]
        )

    orders = []

    for _, row in target.iterrows():

        symbol = row["symbol"]

        target_qty = int(
            row["target_quantity"]
        )

        current_qty = (
            current_map.get(
                symbol,
                0
            )
        )

        difference = (
            target_qty
            - current_qty
        )

        if difference > 0:

            orders.append(
                {
                    "action": "BUY",
                    "symbol": symbol,
                    "quantity":
                        difference
                }
            )

        elif difference < 0:

            orders.append(
                {
                    "action": "SELL",
                    "symbol": symbol,
                    "quantity":
                        abs(
                            difference
                        )
                }
            )

    return orders


def run():

    orders = (
        generate_orders()
    )

    print()
    print("=" * 80)
    print("ORDERS")
    print("=" * 80)

    for order in orders:

        print(
            f"{order['action']} "
            f"{order['quantity']} "
            f"{order['symbol']}"
        )

    return orders


if __name__ == "__main__":
    run()