from screeners.momentum_scanner import run as run_momentum

from screeners.strong_uptrend import run as run_strong_uptrend

from screeners.fifty_two_week_high import run as run_52_week_high

from screeners.combined_ranking import run as run_combined_ranking

import sys

def run(trade_date):

    print()
    print("=" * 100)
    print(
        f"RUNNING ALL SCREENERS "
        f"FOR {trade_date}"
    )
    print("=" * 100)

    print()
    print("STEP 1 - MOMENTUM")
    run_momentum(trade_date)

    print()
    print("STEP 2 - STRONG UPTREND")
    run_strong_uptrend(trade_date)

    print()
    print("STEP 3 - 52 WEEK HIGH")
    run_52_week_high(trade_date)

    print()
    print("STEP 4 - COMBINED RANKING")
    ranked_df = run_combined_ranking(
        trade_date
    )

    print()
    print("=" * 100)
    print("ALL SCREENERS COMPLETE")
    print("=" * 100)

    return ranked_df


def main():

    if len(sys.argv) < 2:

        print(
            "Usage: python -m screeners.run_all_screeners YYYY-MM-DD"
        )
        return

    trade_date = sys.argv[1]

    run(trade_date)


if __name__ == "__main__":
    main()