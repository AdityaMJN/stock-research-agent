import pandas as pd
import numpy as np

from database.connection import engine

PORTFOLIO_NAME = "TOP10"

def load_portfolio_returns():
    return pd.read_sql(
        """
        SELECT
            trade_date,
            return_pct
        FROM portfolio_backtest_results
        WHERE portfolio_name = %(portfolio_name)s
        ORDER BY trade_date
        """,
        engine,
        params={"portfolio_name": PORTFOLIO_NAME},
    )

def calculate_stats(df):
    monthly = df["return_pct"] / 100

    cumulative = (1 + monthly).prod()

    years = len(monthly) / 12

    total_return = (cumulative - 1) * 100

    cagr = (cumulative ** (1 / years) - 1) * 100

    return {
        "months": len(df),
        "total_return": total_return,
        "cagr": cagr,
    }

def run():
    df = load_portfolio_returns()

    if df.empty:
        print("No backtest results.")
        return

    stats = calculate_stats(df)

    print()
    print("=" * 80)
    print("BENCHMARK REPORT")
    print("=" * 80)

    print(f"Portfolio : {PORTFOLIO_NAME}")
    print(f"Months     : {stats['months']}")
    print(f"Total %    : {stats['total_return']:.2f}")
    print(f"CAGR %     : {stats['cagr']:.2f}")

if __name__ == "__main__":
    run()
