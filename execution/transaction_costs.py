BROKERAGE = 0.0003
STT = 0.001
GST = 0.18


def calculate_cost(
    turnover
):

    brokerage = (
        turnover
        * BROKERAGE
    )

    stt = (
        turnover
        * STT
    )

    gst = (
        brokerage
        * GST
    )

    return (
        brokerage
        + stt
        + gst
    )