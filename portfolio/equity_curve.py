import pandas as pd

from sqlalchemy import text

from database.connection import engine


PORTFOLIOS = [
    "TOP10",
    "TOP20",
    "TOP50"
]

STARTING_CAPITAL = 1_000_000


def load_returns(portfolio_name):

    query = """
    SELECT
        trade_date,
        return_pct
    FROM portfolio_backtest_results
    WHERE portfolio_name = %(portfolio_name)s
    ORDER BY trade_date
    """

    return pd.read_sql(
        query,
        engine,
        params={"portfolio_name":portfolio_name},
        parse_dates=[
            "trade_date"
        ]
    )


def build_equity_curve(portfolio_name,df):

    portfolio_value = STARTING_CAPITAL

    peak_value = STARTING_CAPITAL

    records = []

    for _, row in df.iterrows():

        monthly_return = float(
            row["return_pct"]
        )

        portfolio_value *= (
            1
            +
            monthly_return / 100
        )

        if portfolio_value > peak_value:

            peak_value = portfolio_value

        drawdown = (
            (
                portfolio_value
                -
                peak_value
            )
            /
            peak_value
        ) * 100

        cumulative_return = (
            (
                portfolio_value
                /
                STARTING_CAPITAL
            )
            - 1
        ) * 100

        records.append(
            {
                "portfolio_name":portfolio_name,
                "trade_date":
                    row["trade_date"],

                "monthly_return_pct":
                    monthly_return,

                "portfolio_value":
                    portfolio_value,

                "cumulative_return":
                    cumulative_return,

                "peak_value":
                    peak_value,

                "drawdown_pct":
                    drawdown
            }
        )

    return pd.DataFrame(
        records
    )


def save_results(portfolio_name,df):

    if df.empty:

        return

    with engine.begin() as conn:

        conn.execute(
            text("""
            DELETE FROM
            portfolio_equity_curve
            WHERE portfolio_name =
                :portfolio_name
            """),
            {
                "portfolio_name":portfolio_name
            }
        )

        conn.execute(
            text("""
            INSERT INTO
            portfolio_equity_curve
            (
                portfolio_name,
                trade_date,
                monthly_return_pct,
                portfolio_value,
                cumulative_return,
                peak_value,
                drawdown_pct
            )
            VALUES
            (
                :portfolio_name,
                :trade_date,
                :monthly_return_pct,
                :portfolio_value,
                :cumulative_return,
                :peak_value,
                :drawdown_pct
            )
            """),
            df.to_dict(
                orient="records"
            )
        )


def print_summary(portfolio_name,df):

    print()

    print("=" * 80)

    print("EQUITY CURVE")

    print("=" * 80)

    print(
        f"Portfolio : {portfolio_name}"
    )

    print(
        f"Periods   : {len(df)}"
    )

    print(
        f"Start     : ₹{STARTING_CAPITAL:,.2f}"
    )

    print(
        f"End       : ₹{df.iloc[-1]['portfolio_value']:,.2f}"
    )

    print(
        f"Cumulative: "
        f"{df.iloc[-1]['cumulative_return']:.2f}%"
    )

    print(
        f"Max Peak  : "
        f"₹{df['peak_value'].max():,.2f}"
    )

    print(
        f"Max DD    : "
        f"{df['drawdown_pct'].min():.2f}%"
    )

    print()

    print(
        df.tail(20)
    )


def run():

    for portfolio_name in PORTFOLIOS:

        returns = load_returns(
            portfolio_name
        )

        if returns.empty:

            print(
                f"No backtest data for "
                f"{portfolio_name}"
            )

            continue

        curve = build_equity_curve(
            portfolio_name,
            returns
        )

        save_results(
            portfolio_name,
            curve
        )

        print_summary(
            portfolio_name,
            curve
        )


def main():

    run()


if __name__ == "__main__":

    main()