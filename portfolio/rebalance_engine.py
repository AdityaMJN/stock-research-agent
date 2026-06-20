import pandas as pd

from database.connection import engine


PORTFOLIO_NAME = "TOP20"


def load_current_positions():

    query = """
    SELECT
        pp.listing_id,
        l.symbol,
        pp.quantity,
        pp.average_cost,
        pp.current_price,
        pp.market_value
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


def load_target_portfolio():

    query = """
    SELECT
        p.listing_id,
        l.symbol,
        p.rank_position,
        p.weight,
        p.score
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


def generate_rebalance_actions():

    current_df = (
        load_current_positions()
    )

    target_df = (
        load_target_portfolio()
    )

    current_symbols = set(
        current_df["symbol"]
    )

    target_symbols = set(
        target_df["symbol"]
    )

    buys = (
        target_symbols
        - current_symbols
    )

    sells = (
        current_symbols
        - target_symbols
    )

    holds = (
        current_symbols
        & target_symbols
    )

    actions = []

    for symbol in sorted(buys):

        actions.append(
            {
                "action": "BUY",
                "symbol": symbol
            }
        )

    for symbol in sorted(sells):

        actions.append(
            {
                "action": "SELL",
                "symbol": symbol
            }
        )

    for symbol in sorted(holds):

        actions.append(
            {
                "action": "HOLD",
                "symbol": symbol
            }
        )

    return actions


def print_rebalance(actions):

    print()
    print("=" * 80)
    print("REBALANCE ACTIONS")
    print("=" * 80)

    buy_count = 0
    sell_count = 0
    hold_count = 0

    print()
    print("BUY")

    for action in actions:

        if action["action"] == "BUY":

            print(
                f"  {action['symbol']}"
            )

            buy_count += 1

    print()
    print("SELL")

    for action in actions:

        if action["action"] == "SELL":

            print(
                f"  {action['symbol']}"
            )

            sell_count += 1

    print()
    print("HOLD")

    for action in actions:

        if action["action"] == "HOLD":

            print(
                f"  {action['symbol']}"
            )

            hold_count += 1

    print()
    print("=" * 80)
    print(
        f"BUY  : {buy_count}"
    )
    print(
        f"SELL : {sell_count}"
    )
    print(
        f"HOLD : {hold_count}"
    )
    print("=" * 80)


def run():

    actions = (
        generate_rebalance_actions()
    )

    print_rebalance(
        actions
    )

    return actions


def main():
    run()


if __name__ == "__main__":
    main()