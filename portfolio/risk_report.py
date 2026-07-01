import pandas as pd
import numpy as np

from database.connection import engine

PORTFOLIO_NAME = "TOP10"
RISK_FREE_RATE = 0.06

def load_returns():
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


def calculate_drawdown(returns):
    equity = (1 + returns).cumprod()
    peak = equity.cummax()
    drawdown = equity / peak - 1
    return drawdown.min() * 100


def run():
    df = load_returns()

    if df.empty:
        print("No returns found.")
        return

    monthly = df["return_pct"] / 100
    annual_return = ((1 + monthly).prod()) ** (12 / len(monthly)) - 1
    annual_vol = monthly.std() * np.sqrt(12)
    sharpe = (annual_return - RISK_FREE_RATE) / annual_vol

    downside = monthly[monthly < 0]
    sortino = (annual_return - RISK_FREE_RATE) / (downside.std() * np.sqrt(12))

    max_dd = calculate_drawdown(monthly)
    calmar = annual_return / abs(max_dd / 100)

    print()
    print("=" * 80)
    print("RISK REPORT")
    print("=" * 80)
    print(f"Annual Return % : {annual_return * 100:.2f}")
    print(f"Volatility %    : {annual_vol * 100:.2f}")
    print(f"Sharpe Ratio    : {sharpe:.2f}")
    print(f"Sortino Ratio   : {sortino:.2f}")
    print(f"Max Drawdown %  : {max_dd:.2f}")
    print(f"Calmar Ratio    : {calmar:.2f}")


if __name__ == "__main__":
    run()
