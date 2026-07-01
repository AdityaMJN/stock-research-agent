import sys
import time

from utils.trade_dates import (
    get_latest_complete_trade_date
)

from calculations.update_indicators import (
    run as update_indicators,
)

from screeners.run_all_screeners import (
    run as run_screeners,
)

from portfolio.portfolio_builder import (
    run as build_portfolios,
)

from portfolio.order_generator import (
    run as generate_orders,
)

from execution.paper_executor import (
    run as execute_orders,
)

from portfolio.pricing_engine import (
    run as pricing_engine,
)

from portfolio.accounting_engine import (
    run as accounting_engine,
)

from portfolio.performance_report import (
    run as performance_report,
)

from ingestion.daily_price_update import (
    run as update_prices
)

from calculations.update_momentum_indicators import (
    run as update_momentum_indicators,
)


def run_step(
    name,
    func,
    *args
):

    print()
    print("=" * 80)
    print(name)
    print("=" * 80)

    start = time.time()

    func(*args)

    elapsed = (
        time.time()
        - start
    )

    print()
    print(
        f"{name} completed in "
        f"{elapsed:.2f}s"
    )


def run(
    start_step=1
):

    total_start = time.time()

    #
    # STEP 1
    #
    if start_step <= 1:

        run_step(
            "STEP 1 - PRICE UPDATE",
            update_prices
        )

    #
    # Latest trade date
    #
    trade_date = (
        get_latest_complete_trade_date()
    )

    print()
    print(
        f"Trade Date : "
        f"{trade_date}"
    )

    #
    # STEP 2
    #
    if start_step <= 2:

        run_step(
            "STEP 2 - INDICATORS",
            update_indicators
        )
    #
    # STEP 3
    #
    if start_step <= 3:

        run_step(
            "STEP 3 - MOMENTUM INDICATORS",
            update_momentum_indicators
        )
    #
    # STEP 4
    #
    if start_step <= 4:

        run_step(
            "STEP 4 - SCREENERS",
            lambda: run_screeners(trade_date)
        )

    #
    # STEP 5
    #
    if start_step <= 5:

        run_step(
            "STEP 5 - PORTFOLIO BUILD",
            lambda: build_portfolios(trade_date)
        )

    #
    # STEP 6
    #
    if start_step <= 6:

        run_step(
            "STEP 6 - ORDER GENERATION",
            generate_orders
        )

    #
    # STEP 7
    #
    if start_step <= 7:

        run_step(
            "STEP 7 - PAPER EXECUTION",
            execute_orders
        )

    #
    # STEP 8
    #
    if start_step <= 8:

        run_step(
            "STEP 8 - PRICING",
            pricing_engine
        )

    #
    # STEP 9
    #
    if start_step <= 9:

        run_step(
            "STEP 9 - ACCOUNTING",
            accounting_engine
        )

    #
    # STEP 10
    #
    if start_step <= 10:

        run_step(
            "STEP 10 - PERFORMANCE REPORT",
            performance_report
        )

    total_elapsed = (
        time.time()
        - total_start
    )

    print()
    print("=" * 100)
    print(
        f"FULL PORTFOLIO RUN COMPLETE "
        f"({total_elapsed:.2f}s)"
    )
    print("=" * 100)


def main():

    start_step = 1

    if len(sys.argv) > 1:

        try:

            start_step = int(
                sys.argv[1]
            )

        except ValueError:

            print(
                "Usage:"
            )

            print(
                "python -m "
                "daily_jobs.full_portfolio_run"
            )

            print(
                "python -m "
                "daily_jobs.full_portfolio_run 3"
            )

            return

    run(start_step)


if __name__ == "__main__":
    main()