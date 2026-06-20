import pandas as pd

from database.connection import engine


PORTFOLIO_NAME = "TOP20"


def load_portfolio_returns():

    return pd.read_sql(
        """
        SELECT
            trade_date,
            return_pct
        FROM portfolio_backtest_results
        WHERE portfolio_name =
            %(portfolio_name)s
        ORDER BY trade_date
        """,
        engine,
        params={
            "portfolio_name":
                PORTFOLIO_NAME
        }
    )


def load_nifty_returns():

    query = """
    WITH monthly_prices AS
    (
        SELECT
            trade_date,
            adjusted_close,

            ROW_NUMBER() OVER
            (
                PARTITION BY
                    DATE_TRUNC(
                        'month',
                        trade_date
                    )
                ORDER BY
                    trade_date DESC
            ) AS rn

        FROM daily_prices dp

        JOIN listings l
          ON l.id = dp.listing_id

        WHERE l.symbol = 'NIFTYBEES'
    )

    SELECT
        trade_date,
        adjusted_close
    FROM monthly_prices
    WHERE rn = 1
    ORDER BY trade_date
    """

    prices = pd.read_sql(
        query,
        engine
    )

    prices["return_pct"] = (
        prices[
            "adjusted_close"
        ].pct_change()
        * 100
    )

    return prices.dropna()


def calculate_stats(
    returns_df
):

    monthly = (
        returns_df[
            "return_pct"
        ] / 100
    )

    cumulative = (
        monthly + 1
    ).prod()

    years = (
        len(monthly)
        / 12
    )

    cagr = (
        cumulative
        ** (1 / years)
        - 1
    ) * 100

    return {
        "total_return":
            (
                cumulative - 1
            ) * 100,
        "cagr":
            cagr,
        "months":
            len(monthly)
    }


def run():

    portfolio = (
        load_portfolio_returns()
    )

    nifty = (
        load_nifty_returns()
    )

    if portfolio.empty:

        print(
            "No portfolio "
            "returns found."
        )

        return

    portfolio_stats = (
        calculate_stats(
            portfolio
        )
    )

    nifty_stats = (
        calculate_stats(
            nifty
        )
    )

    print()
    print("=" * 80)
    print("BENCHMARK REPORT")
    print("=" * 80)

    print()

    print(
        f"{'Metric':25}"
        f"{'Portfolio':15}"
        f"{'Nifty':15}"
    )

    print("-" * 55)

    print(
        f"{'Total Return %':25}"
        f"{portfolio_stats['total_return']:15.2f}"
        f"{nifty_stats['total_return']:15.2f}"
    )

    print(
        f"{'CAGR %':25}"
        f"{portfolio_stats['cagr']:15.2f}"
        f"{nifty_stats['cagr']:15.2f}"
    )

    print(
        f"{'Months':25}"
        f"{portfolio_stats['months']:15}"
        f"{nifty_stats['months']:15}"
    )

    print()

    alpha = (
        portfolio_stats["cagr"]
        -
        nifty_stats["cagr"]
    )

    print(
        f"Alpha vs Nifty: "
        f"{alpha:.2f}%"
    )


if __name__ == "__main__":
    run()