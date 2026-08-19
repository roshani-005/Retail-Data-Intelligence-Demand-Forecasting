CREATE SCHEMA IF NOT EXISTS retail;

CREATE TABLE IF NOT EXISTS retail.dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    week_of_year INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS retail.dim_customer (
    customer_key BIGSERIAL PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL UNIQUE,
    customer_name VARCHAR(150) NOT NULL,
    segment VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS retail.dim_product (
    product_key BIGSERIAL PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL UNIQUE,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    sub_category VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS retail.dim_location (
    location_key BIGSERIAL PRIMARY KEY,
    country VARCHAR(100),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    postal_code VARCHAR(30),
    region VARCHAR(50) NOT NULL,
    UNIQUE(country, city, state, postal_code, region)
);

CREATE TABLE IF NOT EXISTS retail.fact_sales (
    sales_key BIGSERIAL PRIMARY KEY,
    row_id BIGINT NOT NULL UNIQUE,
    order_id VARCHAR(50) NOT NULL,
    order_date_key INTEGER NOT NULL REFERENCES retail.dim_date(date_key),
    ship_date_key INTEGER REFERENCES retail.dim_date(date_key),
    customer_key BIGINT NOT NULL REFERENCES retail.dim_customer(customer_key),
    product_key BIGINT NOT NULL REFERENCES retail.dim_product(product_key),
    location_key BIGINT NOT NULL REFERENCES retail.dim_location(location_key),
    ship_mode VARCHAR(80) NOT NULL,
    sales NUMERIC(14,2) NOT NULL CHECK (sales >= 0)
);

CREATE TABLE IF NOT EXISTS retail.etl_audit (
    audit_id BIGSERIAL PRIMARY KEY,
    row_id BIGINT,
    event_type VARCHAR(40) NOT NULL,
    event_time TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    details TEXT
);
