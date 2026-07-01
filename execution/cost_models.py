from dataclasses import dataclass


#
# Default assumptions
#
BROKERAGE_RATE = 0.0003          # 0.03%
BROKERAGE_CAP = 20.00            # ₹20/order

STT_RATE = 0.001                # 0.10% on sell

EXCHANGE_RATE = 0.0000325

SEBI_RATE = 0.000001

GST_RATE = 0.18

STAMP_RATE = 0.00015            # Buy side only

DEFAULT_SLIPPAGE = 0.0005


@dataclass
class TransactionCost:

    buy_value: float

    sell_value: float

    brokerage: float

    stt: float

    exchange_charge: float

    sebi_charge: float

    gst: float

    stamp_duty: float

    slippage: float

    total_cost: float

    net_pnl: float


def calculate_transaction_cost(
    buy_value: float,
    sell_value: float,
    intraday: bool = False,
    slippage_rate=DEFAULT_SLIPPAGE
) -> TransactionCost:

    #
    # Brokerage
    #
    brokerage_buy = min(
        buy_value * BROKERAGE_RATE,
        BROKERAGE_CAP
    )

    brokerage_sell = min(
        sell_value * BROKERAGE_RATE,
        BROKERAGE_CAP
    )

    brokerage = (
        brokerage_buy
        + brokerage_sell
    )

    #
    # STT
    #
    stt = (
        sell_value
        * STT_RATE
    )

    #
    # Exchange Charges
    #
    exchange = (
        (buy_value + sell_value)
        * EXCHANGE_RATE
    )

    #
    # SEBI Charges
    #
    sebi = (
        (buy_value + sell_value)
        * SEBI_RATE
    )

    #
    # GST
    #
    gst = (
        brokerage
        + exchange
    ) * GST_RATE

    #
    # Stamp Duty
    #
    stamp = (
        buy_value
        * STAMP_RATE
    )

    #
    # Slippage
    #
    slippage = (
        buy_value
        + sell_value
    ) * slippage_rate

    total_cost = (
        brokerage
        + stt
        + exchange
        + sebi
        + gst
        + stamp
        + slippage
    )

    gross_pnl = (
        sell_value
        - buy_value
    )

    net_pnl = (
        gross_pnl
        - total_cost
    )

    return TransactionCost(
        buy_value=buy_value,
        sell_value=sell_value,
        brokerage=round(
            brokerage,
            2
        ),
        stt=round(
            stt,
            2
        ),
        exchange_charge=round(
            exchange,
            2
        ),
        sebi_charge=round(
            sebi,
            2
        ),
        gst=round(
            gst,
            2
        ),
        stamp_duty=round(
            stamp,
            2
        ),
        slippage=round(
            slippage,
            2
        ),
        total_cost=round(
            total_cost,
            2
        ),
        net_pnl=round(
            net_pnl,
            2
        )
    )


def run():

    buy = 100000

    sell = 112500

    result = calculate_transaction_cost(
        buy,
        sell
    )

    print()

    print("=" * 60)
    print("TRANSACTION COST MODEL")
    print("=" * 60)

    print(f"Buy Value         : ₹{result.buy_value:,.2f}")
    print(f"Sell Value        : ₹{result.sell_value:,.2f}")

    print()

    print(f"Brokerage         : ₹{result.brokerage:,.2f}")
    print(f"STT               : ₹{result.stt:,.2f}")
    print(f"Exchange Charges  : ₹{result.exchange_charge:,.2f}")
    print(f"SEBI Charges      : ₹{result.sebi_charge:,.2f}")
    print(f"GST               : ₹{result.gst:,.2f}")
    print(f"Stamp Duty        : ₹{result.stamp_duty:,.2f}")
    print(f"Slippage          : ₹{result.slippage:,.2f}")

    print()

    print(f"Total Cost        : ₹{result.total_cost:,.2f}")
    print(f"Net PnL           : ₹{result.net_pnl:,.2f}")

    print("=" * 60)


def main():

    run()


if __name__ == "__main__":

    main()