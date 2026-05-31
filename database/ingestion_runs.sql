CREATE TABLE ingestion_runs (
    id BIGSERIAL PRIMARY KEY,
    source_name VARCHAR(50),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    status VARCHAR(20),
    total_records INTEGER,
    success_records INTEGER,
    failed_records INTEGER,
    notes TEXT
);