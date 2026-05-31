import time

from ingestion.daily_price_update import run as update_prices

from calculations.update_indicators import run as update_indicators

from screeners.momentum_scanner import run as run_momentum

from screeners.strong_uptrend import run as run_strong_uptrend

from screeners.fifty_two_week_high import run as run_52_week_high

from screeners.combined_ranking import run as run_combined_ranking


def run_step(name, func):

    print()
    print("=" * 60)
    print(name)
    print("=" * 60)

    start = time.time()

    func()

    elapsed = (
        time.time()
        - start
    )

    print()
    print(
        f"{name} completed "
        f"in {elapsed:.2f}s"
    )


def run():

    total_start = time.time()

    run_step(
        "STEP 1 - UPDATE PRICES",
        update_prices
    )

    run_step(
        "STEP 2 - UPDATE INDICATORS",
        update_indicators
    )

    run_step(
        "STEP 3 - MOMENTUM",
        run_momentum
    )

    run_step(
        "STEP 4 - STRONG UPTREND",
        run_strong_uptrend
    )

    run_step(
        "STEP 5 - 52 WEEK HIGH",
        run_52_week_high
    )

    run_step(
        "STEP 6 - COMBINED RANKING",
        run_combined_ranking
    )

    total_elapsed = (
        time.time()
        - total_start
    )

    print()
    print("=" * 80)
    print(
        f"DAILY UPDATE COMPLETE "
        f"({total_elapsed:.2f}s)"
    )
    print("=" * 80)


def main():
    run()


if __name__ == "__main__":
    main()