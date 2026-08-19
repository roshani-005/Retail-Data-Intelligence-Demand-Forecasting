CREATE SCHEMA IF NOT EXISTS retail;

CREATE TABLE IF NOT EXISTS retail.dim_date (
    date_key INTEGER PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    quarter VARCHAR(2) NOT NULL,
    day_of_week VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS retail.dim_product (
    product_id INTEGER PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL,
    category VARCHAR(80) NOT NULL,
    list_price NUMERIC(12,2) NOT NULL,
    unit_cost NUMERIC(12,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS retail.dim_store (
    store_id INTEGER PRIMARY KEY,
    store_name VARCHAR(150) NOT NULL,
    region VARCHAR(80) NOT NULL,
    city VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS retail.fact_sales (
    transaction_id BIGINT PRIMARY KEY,
    date_key INTEGER NOT NULL REFERENCES retail.dim_date(date_key),
    order_date DATE NOT NULL,
    product_id INTEGER NOT NULL REFERENCES retail.dim_product(product_id),
    store_id INTEGER NOT NULL REFERENCES retail.dim_store(store_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(12,2) NOT NULL CHECK (unit_price >= 0),
    unit_cost NUMERIC(12,2) NOT NULL CHECK (unit_cost >= 0),
    revenue NUMERIC(14,2) NOT NULL,
    cost NUMERIC(14,2) NOT NULL,
    profit NUMERIC(14,2) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_fact_sales_date ON retail.fact_sales(date_key);
CREATE INDEX IF NOT EXISTS idx_fact_sales_product ON retail.fact_sales(product_id);
CREATE INDEX IF NOT EXISTS idx_fact_sales_store ON retail.fact_sales(store_id);
