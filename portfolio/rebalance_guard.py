import pandas as pd

from sqlalchemy import text

from database.connection import engine


def already_rebalanced(
    portfolio_name,
    trade_date
):

    print(
        f"DEBUG already_rebalanced: "
        f"{portfolio_name} "
        f"{trade_date}"
    )

    df = pd.read_sql(
        """
        SELECT 1
        FROM portfolio_rebalance_history
        WHERE portfolio_name =
            %(portfolio_name)s
        AND trade_date =
            %(trade_date)s
        """,
        engine,
        params={
            "portfolio_name":
                portfolio_name,
            "trade_date":
                trade_date
        }
    )

    print(
        f"DEBUG rows found = "
        f"{len(df)}"
    )

    return not df.empty


def mark_rebalanced(
    portfolio_name,
    trade_date
):

    print(
        f"DEBUG inserting: "
        f"{portfolio_name} "
        f"{trade_date}"
    )

    with engine.begin() as conn:

        conn.execute(
            text("""
            INSERT INTO
            portfolio_rebalance_history
            (
                portfolio_name,
                trade_date
            )
            VALUES
            (
                :portfolio_name,
                :trade_date
            )
            ON CONFLICT
            DO NOTHING
            """),
            {
                "portfolio_name":
                    portfolio_name,
                "trade_date":
                    trade_date
            }
        )

    print(
        "DEBUG insert complete"
    )


def get_latest_portfolio_date(
    portfolio_name
):

    df = pd.read_sql(
        """
        SELECT
            MAX(trade_date)
            AS trade_date
        FROM portfolios
        WHERE portfolio_name =
            %(portfolio_name)s
        """,
        engine,
        params={
            "portfolio_name":
                portfolio_name
        }
    )

    trade_date = (
        df.iloc[0]["trade_date"]
    )

    print(
        f"DEBUG latest "
        f"portfolio date = "
        f"{trade_date}"
    )

    return trade_date


def can_execute(
    portfolio_name
):

    trade_date = (
        get_latest_portfolio_date(
            portfolio_name
        )
    )

    if pd.isna(trade_date):

        print(
            "DEBUG trade_date "
            "is NULL"
        )

        return False

    return not already_rebalanced(
        portfolio_name,
        trade_date
    )


def run():

    portfolio_name = "TOP20"

    trade_date = (
        get_latest_portfolio_date(
            portfolio_name
        )
    )

    print()

    if already_rebalanced(
        portfolio_name,
        trade_date
    ):

        print(
            f"{portfolio_name} already "
            f"rebalanced on "
            f"{trade_date}"
        )

    else:

        print(
            f"{portfolio_name} ready "
            f"for rebalance on "
            f"{trade_date}"
        )


if __name__ == "__main__":
    run()