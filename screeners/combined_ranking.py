import pandas as pd

from sqlalchemy import text

from database.connection import engine


SCREENER_NAME = "COMBINED_RANKING"

MOMENTUM_WEIGHT = 35
STRONG_UPTREND_WEIGHT = 30
FIFTY_TWO_WEEK_HIGH_WEIGHT = 20
GOLDEN_CROSS_WEIGHT = 15


def load_screeners():

    query = """
    SELECT
        screener_name,
        listing_id,
        trade_date
    FROM screener_results
    WHERE screener_name IN
    (
        'MOMENTUM',
        'STRONG_UPTREND',
        'FIFTY_TWO_WEEK_HIGH',
        'GOLDEN_CROSS'
    )
    """

    return pd.read_sql(query, engine)


def calculate_scores(df):

    scores = {}

    for _, row in df.iterrows():

        listing_id = int(row["listing_id"])

        if listing_id not in scores:
            scores[listing_id] = 0

        if row["screener_name"] == "MOMENTUM":

            scores[listing_id] += MOMENTUM_WEIGHT

        elif row["screener_name"] == "STRONG_UPTREND":

            scores[listing_id] += STRONG_UPTREND_WEIGHT

        elif row["screener_name"] == "FIFTY_TWO_WEEK_HIGH":

            scores[listing_id] += FIFTY_TWO_WEEK_HIGH_WEIGHT

        elif row["screener_name"] == "GOLDEN_CROSS":

            scores[listing_id] += GOLDEN_CROSS_WEIGHT

    return scores


def save_results(scores, trade_date):

    with engine.begin() as conn:

        conn.execute(
            text("""
            DELETE FROM screener_results
            WHERE screener_name = :screener_name
            """),
            {
                "screener_name": SCREENER_NAME
            }
        )

        records = []

        for listing_id, score in scores.items():

            records.append(
                {
                    "screener_name": SCREENER_NAME,
                    "listing_id": listing_id,
                    "trade_date": trade_date,
                    "score": score,
                }
            )

        conn.execute(
            text("""
            INSERT INTO screener_results
            (
                screener_name,
                listing_id,
                trade_date,
                score,
                created_at
            )
            VALUES
            (
                :screener_name,
                :listing_id,
                :trade_date,
                :score,
                NOW()
            )
            """),
            records
        )


def print_top_20(scores):

    df = pd.DataFrame(
        [
            {
                "listing_id": k,
                "score": v
            }
            for k, v in scores.items()
        ]
    )

    listings = pd.read_sql(
        """
        SELECT
            id,
            symbol
        FROM listings
        """,
        engine
    )

    df = df.merge(
        listings,
        left_on="listing_id",
        right_on="id",
        how="left"
    )

    df = df.sort_values(
        by="score",
        ascending=False
    )

    print()
    print("Top Combined Ranking Stocks")
    print("=" * 80)

    print(
        df[
            [
                "symbol",
                "score"
            ]
        ]
        .head(20)
        .to_string(index=False)
    )

    return df


def run():

    df = load_screeners()

    if df.empty:

        print("No screener results found.")
        return

    trade_date = df["trade_date"].max()

    scores = calculate_scores(df)

    ranked_df = print_top_20(scores)

    save_results(
        scores,
        trade_date
    )

    print()
    print(
        f"Total ranked stocks: {len(ranked_df)}"
    )


def main():
    run()


if __name__ == "__main__":
    main()