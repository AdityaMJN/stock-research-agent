import pandas as pd

from database.connection import engine


PORTFOLIO_NAME = "TOP20"


def load_account():

    return pd.read_sql(
        """
        SELECT *
        FROM portfolio_accounts
        WHERE portfolio_name =
            %(portfolio_name)s
        """,
        engine,
        params={
            "portfolio_name":
                PORTFOLIO_NAME
        }
    )


def load_positions():

    return pd.read_sql(
        """
        SELECT
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
        """,
        engine,
        params={
            "portfolio_name":
                PORTFOLIO_NAME
        }
    )


def run():

    account = (
        load_account()
    )

    positions = (
        load_positions()
    )

    if account.empty:

        print(
            "Portfolio account not found."
        )

        return

    cash = float(
        account.iloc[0][
            "cash_balance"
        ]
    )

    equity = float(
        account.iloc[0][
            "total_equity"
        ]
    )

    total_value = float(
        account.iloc[0][
            "total_value"
        ]
    )

    total_pnl = (
        positions[
            "unrealized_pnl"
        ]
        .fillna(0)
        .sum()
    )

    print()
    print("=" * 100)
    print("PORTFOLIO PERFORMANCE REPORT")
    print("=" * 100)

    print(
        f"Portfolio   : "
        f"{PORTFOLIO_NAME}"
    )

    print(
        f"Cash        : "
        f"₹{cash:,.2f}"
    )

    print(
        f"Equity      : "
        f"₹{equity:,.2f}"
    )

    print(
        f"Total Value : "
        f"₹{total_value:,.2f}"
    )

    print(
        f"PnL         : "
        f"₹{total_pnl:,.2f}"
    )

    print(
        f"Positions   : "
        f"{len(positions)}"
    )

    print()

    print("=" * 100)
    print("TOP HOLDINGS")
    print("=" * 100)

    print(
        positions[
            [
                "symbol",
                "market_value",
                "unrealized_pnl",
                "unrealized_pnl_pct"
            ]
        ]
        .head(10)
        .to_string(index=False)
    )

    print()

    print("=" * 100)
    print("FULL PORTFOLIO")
    print("=" * 100)

    print(
        positions[
            [
                "symbol",
                "quantity",
                "average_cost",
                "current_price",
                "market_value",
                "unrealized_pnl_pct"
            ]
        ]
        .to_string(index=False)
    )


if __name__ == "__main__":
    run()