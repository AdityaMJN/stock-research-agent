import pandas as pd

from sqlalchemy import text

from database.connection import engine

from portfolio.order_generator import (
    generate_orders
)

from portfolio.rebalance_guard import (
    can_execute,
    mark_rebalanced,
    get_latest_portfolio_date
)


orders = generate_orders()

PORTFOLIO_NAME = "TOP20"


def get_latest_price(symbol):

    query = """
    SELECT
        dp.close_price

    FROM daily_prices dp

    JOIN listings l
      ON l.id = dp.listing_id

    WHERE l.symbol = %(symbol)s

    ORDER BY dp.trade_date DESC

    LIMIT 1
    """

    df = pd.read_sql(
        query,
        engine,
        params={
            "symbol": symbol
        }
    )

    if df.empty:
        return None

    return float(
        df.iloc[0]["close_price"]
    )


def get_listing_id(symbol):

    query = """
    SELECT id
    FROM listings
    WHERE symbol = %(symbol)s
    """

    df = pd.read_sql(
        query,
        engine,
        params={
            "symbol": symbol
        }
    )

    if df.empty:
        return None

    return int(
        df.iloc[0]["id"]
    )


def get_position(listing_id):

    query = """
    SELECT
        quantity,
        average_cost
    FROM portfolio_positions
    WHERE portfolio_name =
        %(portfolio_name)s
    AND listing_id =
        %(listing_id)s
    """

    df = pd.read_sql(
        query,
        engine,
        params={
            "portfolio_name":
                PORTFOLIO_NAME,
            "listing_id":
                listing_id
        }
    )

    if df.empty:
        return None

    return df.iloc[0]


def record_transaction(
    listing_id,
    action,
    quantity,
    price
):

    with engine.begin() as conn:

        conn.execute(
            text("""
            INSERT INTO
            portfolio_transactions
            (
                trade_date,
                portfolio_name,
                listing_id,
                action,
                quantity,
                price,
                amount
            )
            VALUES
            (
                CURRENT_DATE,
                :portfolio_name,
                :listing_id,
                :action,
                :quantity,
                :price,
                :amount
            )
            """),
            {
                "portfolio_name":
                    PORTFOLIO_NAME,
                "listing_id":
                    listing_id,
                "action":
                    action,
                "quantity":
                    quantity,
                "price":
                    price,
                "amount":
                    quantity * price
            }
        )


def execute_buy(
    listing_id,
    quantity,
    price
):

    existing = get_position(
        listing_id
    )

    with engine.begin() as conn:

        if existing is None:

            conn.execute(
                text("""
                INSERT INTO
                portfolio_positions
                (
                    portfolio_name,
                    listing_id,
                    quantity,
                    average_cost,
                    current_price,
                    market_value
                )
                VALUES
                (
                    :portfolio_name,
                    :listing_id,
                    :quantity,
                    :average_cost,
                    :current_price,
                    :market_value
                )
                """),
                {
                    "portfolio_name":
                        PORTFOLIO_NAME,
                    "listing_id":
                        listing_id,
                    "quantity":
                        quantity,
                    "average_cost":
                        price,
                    "current_price":
                        price,
                    "market_value":
                        quantity * price
                }
            )

        else:

            old_qty = float(
                existing["quantity"]
            )

            old_cost = float(
                existing["average_cost"]
            )

            new_qty = (
                old_qty
                + quantity
            )

            avg_cost = (
                (
                    old_qty * old_cost
                )
                +
                (
                    quantity * price
                )
            ) / new_qty

            conn.execute(
                text("""
                UPDATE portfolio_positions
                SET
                    quantity =
                        :quantity,

                    average_cost =
                        :average_cost

                WHERE portfolio_name =
                    :portfolio_name

                AND listing_id =
                    :listing_id
                """),
                {
                    "quantity":
                        new_qty,
                    "average_cost":
                        avg_cost,
                    "portfolio_name":
                        PORTFOLIO_NAME,
                    "listing_id":
                        listing_id
                }
            )


def execute_sell(
    listing_id,
    quantity
):

    existing = get_position(
        listing_id
    )

    if existing is None:
        return

    current_qty = float(
        existing["quantity"]
    )

    remaining = (
        current_qty
        - quantity
    )

    with engine.begin() as conn:

        if remaining <= 0:

            conn.execute(
                text("""
                DELETE
                FROM portfolio_positions
                WHERE portfolio_name =
                    :portfolio_name
                AND listing_id =
                    :listing_id
                """),
                {
                    "portfolio_name":
                        PORTFOLIO_NAME,
                    "listing_id":
                        listing_id
                }
            )

        else:

            conn.execute(
                text("""
                UPDATE portfolio_positions
                SET quantity =
                    :quantity
                WHERE portfolio_name =
                    :portfolio_name
                AND listing_id =
                    :listing_id
                """),
                {
                    "quantity":
                        remaining,
                    "portfolio_name":
                        PORTFOLIO_NAME,
                    "listing_id":
                        listing_id
                }
            )


def run():
    print("DEBUG RUN VERSION 2")
    print()
    print("=" * 80)
    print("PAPER EXECUTION")
    print("=" * 80)

    latest_trade_date = (
        get_latest_portfolio_date(
            PORTFOLIO_NAME
        )
    )

    print(
        f"Latest Portfolio Date: "
        f"{latest_trade_date}"
    )

    if latest_trade_date is None:

        print(
            "No portfolio date found."
        )

        return

    print(
        f"Already Rebalanced: "
        f"{not can_execute(PORTFOLIO_NAME)}"
    )

    orders = generate_orders()

    print()
    print(
        f"Generated "
        f"{len(orders)} orders"
    )

    for order in orders:

        symbol = order["symbol"]

        quantity = int(
            order["quantity"]
        )

        action = order["action"]

        listing_id = (
            get_listing_id(
                symbol
            )
        )

        price = (
            get_latest_price(
                symbol
            )
        )

        if (
            listing_id is None
            or
            price is None
        ):
            continue

        record_transaction(
            listing_id,
            action,
            quantity,
            price
        )

        if action == "BUY":

            execute_buy(
                listing_id,
                quantity,
                price
            )

        elif action == "SELL":

            execute_sell(
                listing_id,
                quantity
            )

        print(
            f"{action} "
            f"{quantity} "
            f"{symbol} "
            f" @ {price:.2f}"
        )

    print()
    print(
        f"Saving rebalance "
        f"record for "
        f"{latest_trade_date}"
    )

    mark_rebalanced(
        PORTFOLIO_NAME,
        latest_trade_date
    )

    print(
        "Rebalance saved."
    )

    print()
    print(
        "Paper execution complete."
    )

if __name__ == "__main__":
    run()