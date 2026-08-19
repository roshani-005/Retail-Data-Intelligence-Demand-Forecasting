-- Relational database optimization: indexes for common joins and filters.
CREATE INDEX IF NOT EXISTS idx_fact_sales_order_date ON retail.fact_sales(order_date_key);
CREATE INDEX IF NOT EXISTS idx_fact_sales_customer ON retail.fact_sales(customer_key);
CREATE INDEX IF NOT EXISTS idx_fact_sales_product ON retail.fact_sales(product_key);
CREATE INDEX IF NOT EXISTS idx_fact_sales_location ON retail.fact_sales(location_key);
CREATE INDEX IF NOT EXISTS idx_fact_sales_order_id ON retail.fact_sales(order_id);
CREATE INDEX IF NOT EXISTS idx_product_category ON retail.dim_product(category, sub_category);
CREATE INDEX IF NOT EXISTS idx_location_region_state ON retail.dim_location(region, state);
CREATE INDEX IF NOT EXISTS idx_customer_segment ON retail.dim_customer(segment);
