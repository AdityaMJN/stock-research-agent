import pandas as pd

from sqlalchemy import text

from database.connection import engine

from utils.trade_dates import (
    get_latest_complete_trade_date
)


SCREENER_NAME = "COMBINED_RANKING"

MOMENTUM_WEIGHT = 35
STRONG_UPTREND_WEIGHT = 30
FIFTY_TWO_WEEK_HIGH_WEIGHT = 20
GOLDEN_CROSS_WEIGHT = 15


def load_screeners(trade_date):

    query = """
    SELECT
        sr.screener_name,
        sr.listing_id,
        sr.trade_date,
        ti.momentum_score

    FROM screener_results sr

    LEFT JOIN technical_indicators ti
      ON ti.listing_id = sr.listing_id
     AND ti.trade_date = sr.trade_date

    WHERE sr.trade_date = %(trade_date)s

      AND sr.screener_name IN
      (
          'MOMENTUM',
          'STRONG_UPTREND',
          'FIFTY_TWO_WEEK_HIGH',
          'GOLDEN_CROSS'
      )
    """

    return pd.read_sql(
        query,
        engine,
        params={
            "trade_date": trade_date
        }
    )


def calculate_scores(df):

    scores = {}

    momentum_scores = {}

    for _, row in df.iterrows():

        listing_id = int(
            row["listing_id"]
        )

        if listing_id not in scores:

            scores[listing_id] = 0

        if listing_id not in momentum_scores:

            momentum_scores[listing_id] = (
                0.0
                if pd.isna(
                    row["momentum_score"]
                )
                else float(
                    row["momentum_score"]
                )
            )

        if row["screener_name"] == "MOMENTUM":

            scores[listing_id] += MOMENTUM_WEIGHT

        elif row["screener_name"] == "STRONG_UPTREND":

            scores[listing_id] += STRONG_UPTREND_WEIGHT

        elif row["screener_name"] == "FIFTY_TWO_WEEK_HIGH":

            scores[listing_id] += (
                FIFTY_TWO_WEEK_HIGH_WEIGHT
            )

        elif row["screener_name"] == "GOLDEN_CROSS":

            scores[listing_id] += (
                GOLDEN_CROSS_WEIGHT
            )

    return (
        scores,
        momentum_scores
    )


def build_rankings(
    scores,
    momentum_scores
):

    ranked_df = pd.DataFrame(
        [
            {
                "listing_id":
                    listing_id,

                "screener_score":
                    score,

                "momentum_score":
                    momentum_scores.get(
                        listing_id,
                        0.0
                    )
            }
            for listing_id, score
            in scores.items()
        ]
    )

    ranked_df["final_score"] = (
        ranked_df["screener_score"]
        * 1000
        +
        ranked_df["momentum_score"]
    )

    ranked_df = ranked_df.sort_values(
        by="final_score",
        ascending=False
    ).reset_index(
        drop=True
    )

    ranked_df["rank_position"] = (
        ranked_df.index + 1
    )

    return ranked_df


def save_results(
    ranked_df,
    trade_date
):

    with engine.begin() as conn:

        conn.execute(
        text("""
        DELETE FROM screener_results
        WHERE screener_name = :screener_name
        AND trade_date = :trade_date
        """),
        {
            "screener_name": SCREENER_NAME,
            "trade_date": trade_date
        }
    )

        records = []

        for _, row in ranked_df.iterrows():

            records.append(
                {
                    "screener_name":
                        SCREENER_NAME,

                    "listing_id":
                        int(
                            row["listing_id"]
                        ),

                    "trade_date":
                        trade_date,

                    "score":
                        float(
                            row["final_score"]
                        ),

                    "rank_position":
                        int(
                            row["rank_position"]
                        )
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
                rank_position,
                created_at
            )
            VALUES
            (
                :screener_name,
                :listing_id,
                :trade_date,
                :score,
                :rank_position,
                NOW()
            )
            """),
            records
        )


def print_top_20(ranked_df):

    listings = pd.read_sql(
        """
        SELECT
            id,
            symbol
        FROM listings
        """,
        engine
    )

    df = ranked_df.merge(
        listings,
        left_on="listing_id",
        right_on="id",
        how="left"
    )

    print()
    print("=" * 100)
    print("TOP COMBINED RANKING")
    print("=" * 100)

    print(
        df[
            [
                "rank_position",
                "symbol",
                "screener_score",
                "momentum_score",
                "final_score"
            ]
        ]
        .head(20)
        .to_string(index=False)
    )

    return df


def run(trade_date=None):

    if trade_date is None:
        trade_date = (get_latest_complete_trade_date())

    print()
    print("=" * 100)
    print(
        f"COMBINED RANKING "
        f"({trade_date})"
    )
    print("=" * 100)

    df = load_screeners(
        trade_date
    )

    if df.empty:

        print(
            f"No screener results "
            f"found for {trade_date}"
        )

        return pd.DataFrame()

    print()
    print(
        df["screener_name"]
        .value_counts()
    )

    scores, momentum_scores = (
        calculate_scores(df)
    )

    ranked_df = build_rankings(
        scores,
        momentum_scores
    )

    print_top_20(
        ranked_df
    )

    save_results(
        ranked_df,
        trade_date
    )

    print()

    print(
        f"Total ranked stocks: "
        f"{len(ranked_df)}"
    )

    return ranked_df


def main():
    run()


if __name__ == "__main__":
    main()