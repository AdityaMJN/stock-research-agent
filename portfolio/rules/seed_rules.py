from decimal import Decimal

from database.models import PortfolioRule
from database.session import get_session


INITIAL_RULES = (
    ("Momentum", "Scores positive 3- and 6-month price momentum.", "momentum", "0.25"),
    ("Strong Uptrend", "Checks price, moving-average, and RSI trend alignment.", "strong_uptrend", "0.20"),
    ("Golden Cross", "Detects an SMA50 crossover above SMA200.", "golden_cross", "0.10"),
    ("52 Week High", "Rewards prices trading close to their 52-week high.", "fifty_two_week_high", "0.15"),
    ("RSI", "Rewards relative strength index readings of 60 or higher.", "rsi", "0.15"),
    ("SMA200", "Rewards prices trading above their 200-day moving average.", "sma200", "0.15"),
)


def run() -> None:
    """Create missing default rules without overwriting user-managed settings."""
    session = get_session()
    try:
        existing_names = {name for (name,) in session.query(PortfolioRule.rule_name)}
        for name, description, rule_type, weight in INITIAL_RULES:
            if name not in existing_names:
                session.add(PortfolioRule(
                    rule_name=name,
                    description=description,
                    rule_type=rule_type,
                    weight=Decimal(weight),
                    enabled=True,
                ))
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    run()
