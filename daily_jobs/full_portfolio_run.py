import time

from ingestion.daily_price_update import run as update_prices

from calculations.update_indicators import run as update_indicators

from screeners.run_all_screeners import run as run_screeners

from portfolio.portfolio_builder import run as build_portfolios

from portfolio.order_generator import run as generate_orders

from execution.paper_executor import run as execute_orders

from portfolio.pricing_engine import run as pricing_engine

from portfolio.accounting_engine import run as accounting_engine

from portfolio.performance_report import run as performance_report


def run_step(name, func):

    print()
    print("=" * 80)
    print(name)
    print("=" * 80)

    start = time.time()

    func()

    elapsed = (
        time.time()
        - start
    )

    print()
    print(
        f"{name} completed in "
        f"{elapsed:.2f}s"
    )


def run():

    total_start = time.time()

    run_step(
        "STEP 1 - PRICE UPDATE",
        update_prices
    )

    run_step(
        "STEP 2 - INDICATORS",
        update_indicators
    )

    run_step(
        "STEP 3 - SCREENERS",
        run_screeners
    )

    run_step(
        "STEP 4 - PORTFOLIO BUILD",
        build_portfolios
    )

    run_step(
        "STEP 5 - ORDER GENERATION",
        generate_orders
    )

    run_step(
        "STEP 6 - PAPER EXECUTION",
        execute_orders
    )

    run_step(
        "STEP 7 - PRICING",
        pricing_engine
    )

    run_step(
        "STEP 8 - ACCOUNTING",
        accounting_engine
    )

    run_step(
        "STEP 9 - PERFORMANCE REPORT",
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


if __name__ == "__main__":
    run()