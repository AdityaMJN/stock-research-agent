import pandas as pd

from database.connection import engine


PORTFOLIO_NAME = "TOP20"


def load_dates():

    query = """
    SELECT DISTINCT trade_date
    FROM portfolios
    WHERE portfolio_name =
        %(portfolio_name)s
    ORDER BY trade_date
    """

    return pd.read_sql(
        query,
        engine,
        params={
            "portfolio_name":
                PORTFOLIO_NAME
        }
    )["trade_date"].tolist()


def load_portfolio(
    portfolio_name,
    trade_date
):

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
        %(trade_date)s
    """

    return pd.read_sql(
        query,
        engine,
        params={
            "portfolio_name":
                portfolio_name,

            "trade_date":
                trade_date
        }
    )


def generate_orders():

    dates = load_dates()

    if len(dates) < 2:

        print(
            "Need at least 2 portfolio "
            "snapshots to generate "
            "rebalance orders."
        )

        return []

    current_date = dates[-1]
    previous_date = dates[-2]

    current = load_portfolio(
        PORTFOLIO_NAME,
        current_date
    )

    previous = load_portfolio(
        PORTFOLIO_NAME,
        previous_date
    )

    current_symbols = set(
        current["symbol"]
    )

    previous_symbols = set(
        previous["symbol"]
    )

    buys = (
        current_symbols
        - previous_symbols
    )

    sells = (
        previous_symbols
        - current_symbols
    )

    holds = (
        current_symbols
        &
        previous_symbols
    )

    orders = []

    print()
    print(
        f"Portfolio: "
        f"{PORTFOLIO_NAME}"
    )

    print(
        f"Rebalance Date: "
        f"{current_date}"
    )

    print()
    print("BUY")

    for symbol in sorted(buys):

        print(
            f"  {symbol}"
        )

        orders.append(
            {
                "action": "BUY",
                "symbol": symbol
            }
        )

    print()
    print("SELL")

    for symbol in sorted(sells):

        print(
            f"  {symbol}"
        )

        orders.append(
            {
                "action": "SELL",
                "symbol": symbol
            }
        )

    print()
    print("HOLD")

    for symbol in sorted(holds):

        print(
            f"  {symbol}"
        )

    return orders


def run():

    orders = generate_orders()

    print()
    print(
        f"Generated "
        f"{len(orders)} orders"
    )

    return orders


def main():
    run()


if __name__ == "__main__":
    main()