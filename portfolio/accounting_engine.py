import pandas as pd

from sqlalchemy import text

from database.connection import engine


PORTFOLIO_NAME = "TOP20"


def get_cash_balance():

    df = pd.read_sql(
        """
        SELECT
            cash_balance
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

    if df.empty:
        return 0.0

    return float(
        df.iloc[0]["cash_balance"]
    )


def get_equity_value():

    df = pd.read_sql(
        """
        SELECT
            COALESCE(
                SUM(market_value),
                0
            ) AS equity
        FROM portfolio_positions
        WHERE portfolio_name =
            %(portfolio_name)s
        """,
        engine,
        params={
            "portfolio_name":
                PORTFOLIO_NAME
        }
    )

    return float(
        df.iloc[0]["equity"]
    )


def update_account():

    cash_balance = (
        get_cash_balance()
    )

    total_equity = (
        get_equity_value()
    )

    total_value = (
        cash_balance
        + total_equity
    )

    with engine.begin() as conn:

        conn.execute(
            text("""
            UPDATE portfolio_accounts
            SET
                total_equity =
                    :total_equity,

                total_value =
                    :total_value,

                updated_at =
                    NOW()

            WHERE portfolio_name =
                :portfolio_name
            """),
            {
                "portfolio_name":
                    PORTFOLIO_NAME,

                "total_equity":
                    total_equity,

                "total_value":
                    total_value
            }
        )

    print()
    print("=" * 80)
    print("ACCOUNTING UPDATE")
    print("=" * 80)

    print(
        f"Cash      : "
        f"₹{cash_balance:,.2f}"
    )

    print(
        f"Equity    : "
        f"₹{total_equity:,.2f}"
    )

    print(
        f"Total     : "
        f"₹{total_value:,.2f}"
    )


def run():

    update_account()


if __name__ == "__main__":
    run()