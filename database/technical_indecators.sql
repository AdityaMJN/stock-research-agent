CREATE TABLE technical_indicators (
    listing_id INTEGER NOT NULL,
    trade_date DATE NOT NULL,
    sma20 NUMERIC(15, 4),
    sma50 NUMERIC(15, 4),
    sma200 NUMERIC(15, 4),
    rsi14 NUMERIC(10, 4),
    PRIMARY KEY (listing_id, trade_date)
);