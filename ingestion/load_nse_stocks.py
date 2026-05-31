import pandas as pd
from sqlalchemy import text

from database.connection import engine

CSV_FILE = "Data/nse_equity_list.csv"

df = pd.read_csv(CSV_FILE)
df.columns = df.columns.str.strip()
inserted_companies = 0
inserted_listings = 0

with engine.begin() as conn:

    for _, row in df.iterrows():

        symbol = str(row["SYMBOL"]).strip()
        company_name = str(row["NAME OF COMPANY"]).strip()
        isin = str(row["ISIN NUMBER"]).strip()

        if not isin:
            continue

        company_result = conn.execute(
            text("""
                INSERT INTO companies
                (
                    isin,
                    company_name
                )
                VALUES
                (
                    :isin,
                    :company_name
                )
                ON CONFLICT (isin)
                DO NOTHING
                RETURNING id
            """),
            {
                "isin": isin,
                "company_name": company_name
            }
        )

        company_id = company_result.scalar()

        if company_id is None:

            company_id = conn.execute(
                text("""
                    SELECT id
                    FROM companies
                    WHERE isin = :isin
                """),
                {"isin": isin}
            ).scalar()

        else:
            inserted_companies += 1

        listing_result = conn.execute(
            text("""
                INSERT INTO listings
                (
                    company_id,
                    exchange,
                    symbol
                )
                VALUES
                (
                    :company_id,
                    'NSE',
                    :symbol
                )
                ON CONFLICT
                DO NOTHING
            """),
            {
                "company_id": company_id,
                "symbol": symbol
            }
        )

        inserted_listings += listing_result.rowcount

print(f"Companies inserted: {inserted_companies}")
print(f"NSE listings inserted: {inserted_listings}")