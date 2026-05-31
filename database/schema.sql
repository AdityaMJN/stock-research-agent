CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    isin VARCHAR(20) UNIQUE NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    industry VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE listings (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies (id),
    exchange VARCHAR(10) NOT NULL,
    symbol VARCHAR(50) NOT NULL,
    exchange_code VARCHAR(50),
    UNIQUE (exchange, symbol)
);