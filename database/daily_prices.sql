CREATE TABLE daily_prices (
    id BIGSERIAL PRIMARY KEY,
    listing_id INTEGER NOT NULL REFERENCES listings (id),
    trade_date DATE NOT NULL,
    open_price NUMERIC(15, 4),
    high_price NUMERIC(15, 4),
    low_price NUMERIC(15, 4),
    close_price NUMERIC(15, 4),
    adjusted_close NUMERIC(15, 4),
    volume BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (listing_id, trade_date)
);