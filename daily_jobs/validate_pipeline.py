import pandas as pd

from database.connection import engine
from utils.trade_dates import (
    get_latest_complete_trade_date
)


PASS = 0
FAIL = 0


def print_header(title):

    print()
    print("=" * 80)
    print(title)
    print("=" * 80)


def print_pass(message):

    global PASS

    PASS += 1

    print(f"✓ {message}")


def print_fail(message):

    global FAIL

    FAIL += 1

    print(f"✗ {message}")


def check_database():

    try:

        pd.read_sql(
            "SELECT 1",
            engine
        )

        print_pass(
            "Database Connection"
        )

        return True

    except Exception as ex:

        print_fail(
            f"Database Connection ({ex})"
        )

        return False


def check_daily_prices():

    trade_date = (
        get_latest_complete_trade_date()
    )

    df = pd.read_sql(
        """
        SELECT
            COUNT(*) AS stocks
        FROM daily_prices
        WHERE trade_date = %(trade_date)s
        """,
        engine,
        params={
            "trade_date": trade_date
        }
    )

    stocks = int(
        df.iloc[0]["stocks"]
    )

    if stocks > 0:

        print_pass(
            "Daily Prices"
        )

        print(
            f"    Trade Date : {trade_date}"
        )

        print(
            f"    Stocks     : {stocks}"
        )

    else:

        print_fail(
            "Daily Prices"
        )


def check_indicators():

    trade_date = (
        get_latest_complete_trade_date()
    )

    df = pd.read_sql(
        """
        SELECT
            COUNT(*) AS rows,
            COUNT(sma20) AS sma20,
            COUNT(sma50) AS sma50,
            COUNT(sma200) AS sma200,
            COUNT(rsi14) AS rsi14,
            COUNT(return_3m) AS return_3m,
            COUNT(return_6m) AS return_6m,
            COUNT(momentum_score) AS momentum_score
        FROM technical_indicators
        WHERE trade_date = %(trade_date)s
        """,
        engine,
        params={
            "trade_date": trade_date
        }
    )

    row = df.iloc[0]

    if int(row["rows"]) == 0:

        print_fail(
            "Technical Indicators"
        )

        return

    print_pass(
        "Technical Indicators"
    )

    print(
        f"    Rows            : {int(row['rows'])}"
    )

    print(
        f"    SMA20           : {int(row['sma20'])}"
    )

    print(
        f"    SMA50           : {int(row['sma50'])}"
    )

    print(
        f"    SMA200          : {int(row['sma200'])}"
    )

    print(
        f"    RSI14           : {int(row['rsi14'])}"
    )

    print(
        f"    Return 3M       : {int(row['return_3m'])}"
    )

    print(
        f"    Return 6M       : {int(row['return_6m'])}"
    )

    print(
        f"    Momentum Score  : {int(row['momentum_score'])}"
    )


def check_screeners():

    trade_date = (
        get_latest_complete_trade_date()
    )

    screeners = [

        "MOMENTUM",

        "STRONG_UPTREND",

        "FIFTY_TWO_WEEK_HIGH",

        "COMBINED_RANKING"

    ]

    for screener in screeners:

        df = pd.read_sql(
            """
            SELECT
                COUNT(*) AS stocks
            FROM screener_results
            WHERE screener_name = %(name)s
            AND trade_date = %(trade_date)s
            """,
            engine,
            params={
                "name": screener,
                "trade_date": trade_date
            }
        )

        stocks = int(
            df.iloc[0]["stocks"]
        )

        if stocks > 0:

            print_pass(
                screener
            )

            print(
                f"    Stocks : {stocks}"
            )

        else:

            print_fail(
                screener
            )


def check_portfolios():

    trade_date = (
        get_latest_complete_trade_date()
    )

    portfolios = [

        ("TOP10", 10),

        ("TOP20", 20),

        ("TOP50", 50)

    ]

    for name, expected in portfolios:

        df = pd.read_sql(
            """
            SELECT
                COUNT(*) AS stocks
            FROM portfolios
            WHERE portfolio_name = %(name)s
            AND trade_date = %(trade_date)s
            """,
            engine,
            params={
                "name": name,
                "trade_date": trade_date
            }
        )

        stocks = int(
            df.iloc[0]["stocks"]
        )

        if stocks == expected:

            print_pass(
                name
            )

            print(
                f"    Stocks : {stocks}"
            )

        else:

            print_fail(
                f"{name} ({stocks}/{expected})"
            )


def check_positions():

    df = pd.read_sql(
        """
        SELECT
            COUNT(*) AS positions
        FROM portfolio_positions
        """,
        engine
    )

    positions = int(
        df.iloc[0]["positions"]
    )

    if positions >= 0:

        print_pass(
            "Portfolio Positions"
        )

        print(
            f"    Positions : {positions}"
        )

    else:

        print_fail(
            "Portfolio Positions"
        )


def check_accounts():

    df = pd.read_sql(
        """
        SELECT
            portfolio_name,
            cash_balance,
            total_value
        FROM portfolio_accounts
        """,
        engine
    )

    if df.empty:

        print_fail(
            "Portfolio Accounts"
        )

        return

    print_pass(
        "Portfolio Accounts"
    )

    for _, row in df.iterrows():

        print(
            f"    {row['portfolio_name']}"
            f" | Cash ₹{row['cash_balance']:,.2f}"
            f" | Total ₹{row['total_value']:,.2f}"
        )


def check_backtest():

    df = pd.read_sql(
        """
        SELECT
            portfolio_name,
            COUNT(*) AS months
        FROM portfolio_backtest_results
        GROUP BY portfolio_name
        ORDER BY portfolio_name
        """,
        engine
    )

    if df.empty:

        print_fail(
            "Backtest Results"
        )

        return

    print_pass(
        "Backtest Results"
    )

    for _, row in df.iterrows():

        print(
            f"    {row['portfolio_name']}"
            f" : {int(row['months'])} months"
        )


def run():

    print_header(
        "SYSTEM HEALTH CHECK"
    )

    if not check_database():

        return

    print()

    check_daily_prices()

    print()

    check_indicators()

    print()

    check_screeners()

    print()

    check_portfolios()

    print()

    check_positions()

    print()

    check_accounts()

    print()

    check_backtest()

    print()

    print("=" * 80)

    print(
        f"PASS : {PASS}"
    )

    print(
        f"FAIL : {FAIL}"
    )

    if FAIL == 0:

        print(
            "STATUS : HEALTHY"
        )

    else:

        print(
            "STATUS : ATTENTION REQUIRED"
        )

    print("=" * 80)


def main():

    run()


if __name__ == "__main__":

    main()