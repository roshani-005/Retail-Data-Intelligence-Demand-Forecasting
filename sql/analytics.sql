-- 1. Multi-table JOIN: sales by category and region.
SELECT p.category, l.region, SUM(f.sales) AS total_sales,
       COUNT(DISTINCT f.order_id) AS orders
FROM retail.fact_sales f
JOIN retail.dim_product p ON p.product_key = f.product_key
JOIN retail.dim_location l ON l.location_key = f.location_key
GROUP BY p.category, l.region
ORDER BY total_sales DESC;

-- 2. CTE + LAG(): monthly sales and month-over-month growth.
WITH monthly AS (
    SELECT d.year, d.month, SUM(f.sales) AS sales
    FROM retail.fact_sales f
    JOIN retail.dim_date d ON d.date_key = f.order_date_key
    GROUP BY d.year, d.month
), growth AS (
    SELECT *, LAG(sales) OVER (ORDER BY year, month) AS previous_month_sales
    FROM monthly
)
SELECT year, month, sales, previous_month_sales,
       ROUND(100.0 * (sales - previous_month_sales) / NULLIF(previous_month_sales, 0), 2) AS mom_growth_pct
FROM growth
ORDER BY year, month;

-- 3. RANK(): top products inside each category.
WITH product_sales AS (
    SELECT p.category, p.product_id, p.product_name, SUM(f.sales) AS total_sales
    FROM retail.fact_sales f
    JOIN retail.dim_product p ON p.product_key = f.product_key
    GROUP BY p.category, p.product_id, p.product_name
)
SELECT *
FROM (
    SELECT *, RANK() OVER (PARTITION BY category ORDER BY total_sales DESC) AS category_rank
    FROM product_sales
) ranked
WHERE category_rank <= 5
ORDER BY category, category_rank;

-- 4. Running total using a window function.
SELECT d.year, d.month, SUM(f.sales) AS monthly_sales,
       SUM(SUM(f.sales)) OVER (ORDER BY d.year, d.month) AS running_sales
FROM retail.fact_sales f
JOIN retail.dim_date d ON d.date_key = f.order_date_key
GROUP BY d.year, d.month
ORDER BY d.year, d.month;

-- 5. Customer contribution using a CTE.
WITH customer_sales AS (
    SELECT c.customer_id, c.customer_name, SUM(f.sales) AS total_sales
    FROM retail.fact_sales f
    JOIN retail.dim_customer c ON c.customer_key = f.customer_key
    GROUP BY c.customer_id, c.customer_name
), totals AS (
    SELECT SUM(total_sales) AS grand_total FROM customer_sales
)
SELECT cs.customer_id, cs.customer_name, cs.total_sales,
       ROUND(100.0 * cs.total_sales / NULLIF(t.grand_total, 0), 2) AS sales_contribution_pct
FROM customer_sales cs CROSS JOIN totals t
ORDER BY cs.total_sales DESC;

-- 6. Shipping-mode analysis.
SELECT ship_mode, COUNT(DISTINCT order_id) AS orders,
       SUM(sales) AS total_sales, AVG(sales) AS average_line_sales
FROM retail.fact_sales
GROUP BY ship_mode
ORDER BY total_sales DESC;
