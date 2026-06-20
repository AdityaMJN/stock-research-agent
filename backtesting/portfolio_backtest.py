import pandas as pd
import numpy as np

from database.connection import engine


TOP_N = 20


def load_rebalance_dates():

    query = """
    SELECT DISTINCT trade_date
    FROM screener_results
    WHERE screener_name = 'COMBINED_RANKING'
    ORDER BY trade_date
    """

    return pd.read_sql(
        query,
        engine,
        parse_dates=["trade_date"]
    )["trade_date"].tolist()


def load_top_stocks(
    trade_date,
    top_n
):

    query = """
    SELECT
        listing_id,
        rank_position
    FROM screener_results
    WHERE screener_name =
        'COMBINED_RANKING'
    AND trade_date =
        %(trade_date)s
    ORDER BY rank_position
    LIMIT %(top_n)s
    """

    return pd.read_sql(
        query,
        engine,
        params={
            "trade_date": trade_date,
            "top_n": top_n
        }
    )


def load_prices(
    listing_ids,
    trade_date
):

    query = """
    SELECT
        listing_id,
        close_price
    FROM daily_prices
    WHERE trade_date =
        %(trade_date)s
    AND listing_id = ANY(%(ids)s)
    """

    return pd.read_sql(
        query,
        engine,
        params={
            "trade_date": trade_date,
            "ids": list(listing_ids)
        }
    )


def calculate_period_return(
    current_date,
    next_date,
    top_n
):

    portfolio = load_top_stocks(
        current_date,
        top_n
    )


    if portfolio.empty:

        return None

    buy_prices = load_prices(
        portfolio["listing_id"],
        current_date
    )

    sell_prices = load_prices(
        portfolio["listing_id"],
        next_date
    )

    df = portfolio.merge(
        buy_prices,
        on="listing_id",
        how="inner"
    )

    df = df.rename(
        columns={
            "close_price":
                "buy_price"
        }
    )

    df = df.merge(
        sell_prices,
        on="listing_id",
        how="inner"
    )

    df = df.rename(
        columns={
            "close_price":
                "sell_price"
        }
    )

    if len(df) == 0:

        return None

    df["return_pct"] = (
        (
            df["sell_price"]
            -
            df["buy_price"]
        )
        /
        df["buy_price"]
    ) * 100

    portfolio_return = (
        df["return_pct"]
        .mean()
    )

    print(
    current_date,
    len(portfolio),
    len(df)
)

    return {
        "trade_date":
            current_date.date(),

        "next_date":
            next_date.date(),

        "stocks":
            len(df),

        "return_pct":
            portfolio_return
    }


def calculate_statistics(
    results_df
):

    monthly_returns = (
        results_df["return_pct"]
        / 100
    )

    equity_curve = (
        1 + monthly_returns
    ).cumprod()

    total_return = (
        equity_curve.iloc[-1]
        - 1
    ) * 100

    years = (
        len(results_df)
        / 12
    )

    cagr = (
        (
            equity_curve.iloc[-1]
        )
        ** (1 / years)
        - 1
    ) * 100

    rolling_max = (
        equity_curve.cummax()
    )

    drawdown = (
        equity_curve
        /
        rolling_max
        - 1
    )

    max_drawdown = (
        drawdown.min()
        * 100
    )

    return {
        "Total Return %":
            round(total_return, 2),

        "CAGR %":
            round(cagr, 2),

        "Win Rate %":
            round(
                (
                    results_df[
                        "return_pct"
                    ] > 0
                ).mean() * 100,
                2
            ),

        "Average Month %":
            round(
                results_df[
                    "return_pct"
                ].mean(),
                2
            ),

        "Best Month %":
            round(
                results_df[
                    "return_pct"
                ].max(),
                2
            ),

        "Worst Month %":
            round(
                results_df[
                    "return_pct"
                ].min(),
                2
            ),

        "Max Drawdown %":
            round(
                max_drawdown,
                2
            )
    }


def run():

    dates = (
        load_rebalance_dates()
    )

    results = []

    for i in range(
        len(dates) - 1
    ):

        current_date = dates[i]

        next_date = (
            dates[i + 1]
        )

        result = (
            calculate_period_return(
                current_date,
                next_date,
                TOP_N
            )
        )

        if result:

            results.append(
                result
            )

    results_df = (
        pd.DataFrame(results)
    )

    print()
    print("=" * 80)
    print("MONTHLY RESULTS")
    print("=" * 80)

    print(
        results_df
        .head(20)
        .to_string(index=False)
    )

    stats = (
        calculate_statistics(
            results_df
        )
    )

    print()
    print("=" * 80)
    print("BACKTEST SUMMARY")
    print("=" * 80)

    for key, value in stats.items():

        print(
            f"{key:<20}"
            f"{value}"
        )

    return (
        results_df,
        stats
    )


def main():
    run()


if __name__ == "__main__":
    main()