CREATE TABLE screener_results (
    screener_name VARCHAR(100),
    listing_id INTEGER,
    trade_date DATE,
    score NUMERIC(10, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);