-- Executive KPI
SELECT
    SUM(revenue) AS total_revenue,
    SUM(profit) AS total_profit,
    SUM(quantity) AS units_sold,
    COUNT(DISTINCT transaction_id) AS orders,
    ROUND(SUM(revenue) / NULLIF(COUNT(DISTINCT transaction_id), 0), 2) AS avg_order_value
FROM retail.fact_sales;

-- Revenue/profit by category
SELECT p.category, SUM(f.revenue) AS revenue, SUM(f.profit) AS profit
FROM retail.fact_sales f
JOIN retail.dim_product p ON p.product_id = f.product_id
GROUP BY p.category
ORDER BY revenue DESC;

-- Monthly growth using a CTE + window function
WITH monthly AS (
    SELECT d.year, d.month, SUM(f.revenue) AS revenue
    FROM retail.fact_sales f
    JOIN retail.dim_date d ON d.date_key = f.date_key
    GROUP BY d.year, d.month
), growth AS (
    SELECT *, LAG(revenue) OVER (ORDER BY year, month) AS previous_month_revenue
    FROM monthly
)
SELECT year, month, revenue, previous_month_revenue,
       ROUND(100.0 * (revenue - previous_month_revenue) / NULLIF(previous_month_revenue, 0), 2) AS mom_growth_pct
FROM growth
ORDER BY year, month;

-- Top products by revenue
SELECT p.product_name, p.category, SUM(f.revenue) AS revenue,
       SUM(f.profit) AS profit,
       RANK() OVER (ORDER BY SUM(f.revenue) DESC) AS revenue_rank
FROM retail.fact_sales f
JOIN retail.dim_product p ON p.product_id = f.product_id
GROUP BY p.product_name, p.category
ORDER BY revenue_rank;

-- Store performance
SELECT s.store_name, s.region, SUM(f.revenue) AS revenue,
       SUM(f.profit) AS profit, SUM(f.quantity) AS units
FROM retail.fact_sales f
JOIN retail.dim_store s ON s.store_id = f.store_id
GROUP BY s.store_name, s.region
ORDER BY revenue DESC;

-- Inventory coverage proxy: trailing 7-day units versus available stock.
-- Replace stock_on_hand with the operational inventory table when available.
WITH daily AS (
    SELECT product_id, order_date, SUM(quantity) AS units
    FROM retail.fact_sales
    GROUP BY product_id, order_date
)
SELECT product_id, order_date,
       AVG(units) OVER (
           PARTITION BY product_id ORDER BY order_date
           ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
       ) AS avg_7d_daily_demand
FROM daily;
