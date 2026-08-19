-- Reusable analytical views for Power BI / ad-hoc reporting.

CREATE OR REPLACE VIEW retail.v_sales_daily AS
SELECT
    d.full_date,
    d.year,
    d.month,
    d.month_name,
    SUM(f.sales) AS total_sales,
    COUNT(DISTINCT f.order_id) AS orders,
    COUNT(DISTINCT f.customer_key) AS customers,
    SUM(f.sales) / NULLIF(COUNT(DISTINCT f.order_id), 0) AS average_order_value
FROM retail.fact_sales f
JOIN retail.dim_date d ON d.date_key = f.order_date_key
GROUP BY d.full_date, d.year, d.month, d.month_name;

CREATE OR REPLACE VIEW retail.v_product_performance AS
SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.sub_category,
    SUM(f.sales) AS total_sales,
    COUNT(DISTINCT f.order_id) AS orders
FROM retail.fact_sales f
JOIN retail.dim_product p ON p.product_key = f.product_key
GROUP BY p.product_id, p.product_name, p.category, p.sub_category;

CREATE OR REPLACE VIEW retail.v_customer_performance AS
SELECT
    c.customer_id,
    c.customer_name,
    c.segment,
    SUM(f.sales) AS total_sales,
    COUNT(DISTINCT f.order_id) AS orders,
    MAX(d.full_date) AS last_order_date
FROM retail.fact_sales f
JOIN retail.dim_customer c ON c.customer_key = f.customer_key
JOIN retail.dim_date d ON d.date_key = f.order_date_key
GROUP BY c.customer_id, c.customer_name, c.segment;

CREATE OR REPLACE VIEW retail.v_region_performance AS
SELECT
    l.region,
    l.state,
    SUM(f.sales) AS total_sales,
    COUNT(DISTINCT f.order_id) AS orders,
    COUNT(DISTINCT f.customer_key) AS customers
FROM retail.fact_sales f
JOIN retail.dim_location l ON l.location_key = f.location_key
GROUP BY l.region, l.state;
