from sqlalchemy import text

from database.connection import engine


def get_cash_balance(
    portfolio_name
):

    with engine.begin() as conn:

        result = conn.execute(
            text("""
            SELECT
                cash_balance
            FROM portfolio_accounts
            WHERE portfolio_name =
                :portfolio_name
            """),
            {
                "portfolio_name":
                    portfolio_name
            }
        ).scalar()

    if result is None:

        raise Exception(
            f"Portfolio account "
            f"not found: "
            f"{portfolio_name}"
        )

    return float(result)


def add_cash(
    portfolio_name,
    amount
):

    with engine.begin() as conn:

        conn.execute(
            text("""
            UPDATE portfolio_accounts
            SET
                cash_balance =
                    cash_balance
                    + :amount,

                updated_at =
                    NOW()

            WHERE portfolio_name =
                :portfolio_name
            """),
            {
                "portfolio_name":
                    portfolio_name,

                "amount":
                    amount
            }
        )


def deduct_cash(
    portfolio_name,
    amount
):

    current_cash = (
        get_cash_balance(
            portfolio_name
        )
    )

    if current_cash < amount:

        raise Exception(
            f"Insufficient cash. "
            f"Need ₹{amount:,.2f}, "
            f"have ₹{current_cash:,.2f}"
        )

    with engine.begin() as conn:

        conn.execute(
            text("""
            UPDATE portfolio_accounts
            SET
                cash_balance =
                    cash_balance
                    - :amount,

                updated_at =
                    NOW()

            WHERE portfolio_name =
                :portfolio_name
            """),
            {
                "portfolio_name":
                    portfolio_name,

                "amount":
                    amount
            }
        )


def can_afford(
    portfolio_name,
    amount
):

    return (
        get_cash_balance(
            portfolio_name
        )
        >= amount
    )


def print_balance(
    portfolio_name
):

    cash = (
        get_cash_balance(
            portfolio_name
        )
    )

    print()
    print("=" * 60)
    print("CASH BALANCE")
    print("=" * 60)

    print(
        f"Portfolio : "
        f"{portfolio_name}"
    )

    print(
        f"Cash      : "
        f"₹{cash:,.2f}"
    )


def run():

    print_balance(
        "TOP20"
    )


if __name__ == "__main__":
    run()