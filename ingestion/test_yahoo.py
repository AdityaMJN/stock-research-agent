import yfinance as yf

symbols = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "ANSALAPI.NS"
]

for symbol in symbols:

    print("=" * 60)
    print(symbol)

    try:

        ticker = yf.Ticker(symbol)

        df = ticker.history(
            start="2026-06-26"
        )

        print("Rows:", len(df))

        if df.empty:

            print("No data returned")

        else:

            print(df.tail())

    except Exception as e:

        print("ERROR:", e)