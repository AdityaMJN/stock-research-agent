import pandas as pd

from database.connection import engine

from screeners.momentum_scanner import run as run_momentum
from screeners.strong_uptrend import run as run_strong_uptrend
from screeners.fifty_two_week_high import run as run_52_week_high
from screeners.combined_ranking import run as run_combined_ranking


START_DATE = "2021-06-01"


def get_month_end_dates():

    query = """
    SELECT DISTINCT trade_date
    FROM daily_prices
    WHERE trade_date >= %(start_date)s
    ORDER BY trade_date
    """

    df = pd.read_sql(
        query,
        engine,
        params={
            "start_date": START_DATE
        },
        parse_dates=["trade_date"]
    )

    df["year_month"] = (
        df["trade_date"]
        .dt
        .to_period("M")
    )

    month_end_dates = (
        df.groupby("year_month")
        ["trade_date"]
        .max()
        .tolist()
    )

    return month_end_dates


def run_for_date(trade_date):

    trade_date = (
        pd.Timestamp(trade_date)
        .date()
    )

    print()
    print("=" * 100)
    print(
        f"PROCESSING {trade_date}"
    )
    print("=" * 100)

    run_momentum(trade_date)

    run_strong_uptrend(
        trade_date
    )

    run_52_week_high(
        trade_date
    )

    run_combined_ranking(
        trade_date
    )


def run():

    dates = get_month_end_dates()

    print()
    print(
        f"Found {len(dates)} "
        f"month-end dates"
    )

    for i, trade_date in enumerate(
        dates,
        start=1
    ):

        print()
        print(
            f"[{i}/{len(dates)}]"
        )

        try:

            run_for_date(
                trade_date
            )

        except Exception as ex:

            print()
            print(
                f"FAILED: "
                f"{trade_date}"
            )

            print(ex)

    print()
    print("=" * 100)
    print(
        "HISTORICAL RANKING "
        "GENERATION COMPLETE"
    )
    print("=" * 100)


def main():
    run()


if __name__ == "__main__":
    main()