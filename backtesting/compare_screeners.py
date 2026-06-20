import pandas as pd


def run():

    results = [
        {
            "Screener": "52 Week High",
            "Average Return": 49.64,
            "Median Return": 36.67,
            "Win Rate": 88.00,
            "Best Return": 216.41,
            "Worst Return": -14.11,
        },
        {
            "Screener": "Strong Uptrend",
            "Average Return": 28.04,
            "Median Return": 26.78,
            "Win Rate": 91.30,
            "Best Return": 113.52,
            "Worst Return": -28.83,
        },
        {
            "Screener": "Momentum",
            "Average Return": 10.72,
            "Median Return": 13.27,
            "Win Rate": 80.00,
            "Best Return": 45.66,
            "Worst Return": -25.75,
        },
        {
            "Screener": "Golden Cross",
            "Average Return": 5.67,
            "Median Return": 11.72,
            "Win Rate": 59.09,
            "Best Return": 50.89,
            "Worst Return": -39.65,
        },
    ]

    df = pd.DataFrame(results)

    df = df.sort_values(
        by="Average Return",
        ascending=False
    )

    print()
    print("=" * 110)
    print("SCREENER PERFORMANCE COMPARISON")
    print("=" * 110)

    print(
        df.to_string(
            index=False,
            formatters={
                "Average Return": "{:.2f}%".format,
                "Median Return": "{:.2f}%".format,
                "Win Rate": "{:.2f}%".format,
                "Best Return": "{:.2f}%".format,
                "Worst Return": "{:.2f}%".format,
            }
        )
    )

    print()
    print("Ranking by Average Return")
    print("=" * 40)

    for rank, (_, row) in enumerate(
        df.iterrows(),
        start=1
    ):
        print(
            f"{rank}. "
            f"{row['Screener']} "
            f"({row['Average Return']:.2f}%)"
        )


def main():
    run()


if __name__ == "__main__":
    main()