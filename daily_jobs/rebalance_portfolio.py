from portfolio.recommendation_engine import (
    generate_orders
)

from execution.paper_executor import (
    PaperExecutor
)


def run():

    executor = (
        PaperExecutor()
    )

    orders = (
        generate_orders()
    )

    for order in orders:

        if (
            order["action"]
            == "BUY"
        ):

            executor.buy(
                order["symbol"],
                1
            )

        elif (
            order["action"]
            == "SELL"
        ):

            executor.sell(
                order["symbol"],
                1
            )


if __name__ == "__main__":
    run()