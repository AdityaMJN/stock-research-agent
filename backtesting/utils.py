import pandas as pd

from sqlalchemy import text

from database.connection import engine


def get_rebalance_dates(
    start_date,
    end_date,
    interval_days=30
):

    query = """
    SELECT DISTINCT trade_date
    FROM daily_prices
    WHERE trade_date BETWEEN %(start_date)s
                        AND %(end_date)s
    ORDER BY trade_date
    """

    dates = pd.read_sql(
        query,
        engine,
        params={
            "start_date": start_date,
            "end_date": end_date
        }
    )

    return dates.iloc[::interval_days]


def get_exit_date(
    entry_date,
    hold_days
):

    query = """
    SELECT MIN(trade_date)
    FROM daily_prices
    WHERE trade_date >= %(target_date)s
    """

    result = pd.read_sql(
        query,
        engine,
        params={
            "target_date":
                entry_date +
                pd.Timedelta(
                    days=hold_days
                )
        }
    )

    return result.iloc[0, 0]


def get_price(
    listing_id,
    trade_date
):

    query = """
    SELECT close_price
    FROM daily_prices
    WHERE listing_id = %(listing_id)s
      AND trade_date = %(trade_date)s
    """

    result = pd.read_sql(
        query,
        engine,
        params={
            "listing_id": listing_id,
            "trade_date": trade_date
        }
    )

    if result.empty:
        return None

    return float(
        result.iloc[0]["close_price"]
    )


def calculate_return(
    entry_price,
    exit_price
):

    if entry_price is None:
        return None

    if exit_price is None:
        return None

    return (
        (exit_price - entry_price)
        / entry_price
    ) * 100