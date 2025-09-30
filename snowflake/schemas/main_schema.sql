-- Create database and schema
CREATE DATABASE IF NOT EXISTS MCP_PLATFORM;
CREATE SCHEMA IF NOT EXISTS MCP_PLATFORM.PUBLIC;

-- Create tables for different sectors
CREATE OR REPLACE TABLE energy_data (
    timestamp TIMESTAMP_NTZ,
    energy_type VARCHAR(50),
    price DECIMAL(10,4),
    region VARCHAR(50),
    unit VARCHAR(20)
);

CREATE OR REPLACE TABLE transport_data (
    timestamp TIMESTAMP_NTZ,
    line_name VARCHAR(100),
    status VARCHAR(50),
    delay_minutes INTEGER,
    passengers_count INTEGER
);

CREATE OR REPLACE TABLE financial_data (
    timestamp TIMESTAMP_NTZ,
    symbol VARCHAR(20),
    price DECIMAL(10,2),
    volume INTEGER,
    change DECIMAL(5,2)
);

-- Create streams for real-time data
CREATE OR REPLACE STREAM energy_stream ON TABLE energy_data;
CREATE OR REPLACE STREAM transport_stream ON TABLE transport_data;

-- Create views for analytics
CREATE OR REPLACE VIEW energy_analytics AS
SELECT 
    DATE_TRUNC('hour', timestamp) as hour,
    energy_type,
    AVG(price) as avg_price,
    COUNT(*) as records_count
FROM energy_data
GROUP BY 1, 2;