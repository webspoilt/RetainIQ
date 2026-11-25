-- RetainIQ PostgreSQL Schema Definition
-- Database: retention_analytics

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS audit;

-- Raw customer snapshot table (preserves original source values)
CREATE TABLE IF NOT EXISTS raw.telco_customers (
    customer_id VARCHAR(32) PRIMARY KEY,
    gender VARCHAR(16),
    senior_citizen INTEGER,
    partner VARCHAR(16),
    dependents VARCHAR(16),
    tenure INTEGER,
    phone_service VARCHAR(16),
    multiple_lines VARCHAR(32),
    internet_service VARCHAR(32),
    online_security VARCHAR(32),
    online_backup VARCHAR(32),
    device_protection VARCHAR(32),
    tech_support VARCHAR(32),
    streaming_tv VARCHAR(32),
    streaming_movies VARCHAR(32),
    contract VARCHAR(32),
    paperless_billing VARCHAR(16),
    payment_method VARCHAR(64),
    monthly_charges NUMERIC(10, 2),
    total_charges VARCHAR(32),
    churn VARCHAR(16),
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Audit table for idempotent ingestion tracking
CREATE TABLE IF NOT EXISTS audit.ingestion_log (
    ingestion_id SERIAL PRIMARY KEY,
    source_name VARCHAR(255) NOT NULL,
    file_checksum VARCHAR(64) NOT NULL,
    row_count INTEGER NOT NULL,
    status VARCHAR(32) NOT NULL,
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table for AI-generated retention briefs
CREATE TABLE IF NOT EXISTS analytics.ai_retention_briefs (
    brief_id SERIAL PRIMARY KEY,
    segment_id VARCHAR(128) NOT NULL,
    input_metrics JSONB NOT NULL,
    generated_brief TEXT NOT NULL,
    provider VARCHAR(64) NOT NULL,
    model VARCHAR(128) NOT NULL,
    prompt_version VARCHAR(32) NOT NULL,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for common analytical filters
CREATE INDEX IF NOT EXISTS idx_raw_customers_churn ON raw.telco_customers (churn);
CREATE INDEX IF NOT EXISTS idx_raw_customers_contract ON raw.telco_customers (contract);
CREATE INDEX IF NOT EXISTS idx_raw_customers_payment ON raw.telco_customers (payment_method);
CREATE INDEX IF NOT EXISTS idx_raw_customers_tenure ON raw.telco_customers (tenure);
CREATE INDEX IF NOT EXISTS idx_ingestion_checksum ON audit.ingestion_log (file_checksum);
