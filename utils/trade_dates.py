import pandas as pd

from database.connection import engine


def get_latest_complete_trade_date(
    completeness_ratio=0.95
):

    listings = pd.read_sql(
        """
        SELECT
            COUNT(*) AS total
        FROM listings
        WHERE yahoo_symbol
            IS NOT NULL
        """,
        engine
    )

    total_listings = int(
        listings.iloc[0]["total"]
    )

    minimum_rows = int(
        total_listings
        * completeness_ratio
    )

    query = """
    SELECT
        trade_date,
        COUNT(*) AS stocks
    FROM daily_prices
    GROUP BY trade_date
    HAVING COUNT(*) >= %(minimum_rows)s
    ORDER BY trade_date DESC
    LIMIT 1
    """

    df = pd.read_sql(
        query,
        engine,
        params={
            "minimum_rows":
                minimum_rows
        }
    )

    if df.empty:

        return None

    return df.iloc[0]["trade_date"]