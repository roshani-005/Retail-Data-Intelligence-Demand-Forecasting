import os
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"
OUTPUTS.mkdir(exist_ok=True)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise SystemExit("Set DATABASE_URL before running analytics.py")

engine = create_engine(DATABASE_URL)
queries = {
    "executive_kpis": """
        SELECT SUM(revenue) AS total_revenue,
               SUM(profit) AS total_profit,
               SUM(quantity) AS units_sold,
               COUNT(DISTINCT transaction_id) AS orders,
               ROUND(SUM(revenue) / NULLIF(COUNT(DISTINCT transaction_id), 0), 2) AS avg_order_value
        FROM retail.fact_sales;
    """,
    "category_performance": """
        SELECT p.category, SUM(f.revenue) AS revenue, SUM(f.profit) AS profit
        FROM retail.fact_sales f JOIN retail.dim_product p ON p.product_id=f.product_id
        GROUP BY p.category ORDER BY revenue DESC;
    """,
    "monthly_growth": """
        WITH monthly AS (
            SELECT d.year, d.month, SUM(f.revenue) AS revenue
            FROM retail.fact_sales f JOIN retail.dim_date d ON d.date_key=f.date_key
            GROUP BY d.year, d.month
        ), growth AS (
            SELECT *, LAG(revenue) OVER (ORDER BY year, month) AS previous_month_revenue
            FROM monthly
        )
        SELECT *, ROUND(100.0*(revenue-previous_month_revenue)/NULLIF(previous_month_revenue,0),2) AS mom_growth_pct
        FROM growth ORDER BY year, month;
    """,
    "store_performance": """
        SELECT s.store_name, s.region, SUM(f.revenue) AS revenue,
               SUM(f.profit) AS profit, SUM(f.quantity) AS units
        FROM retail.fact_sales f JOIN retail.dim_store s ON s.store_id=f.store_id
        GROUP BY s.store_name, s.region ORDER BY revenue DESC;
    """,
    "top_products": """
        SELECT p.product_name, p.category, SUM(f.revenue) AS revenue,
               SUM(f.profit) AS profit,
               RANK() OVER (ORDER BY SUM(f.revenue) DESC) AS revenue_rank
        FROM retail.fact_sales f JOIN retail.dim_product p ON p.product_id=f.product_id
        GROUP BY p.product_name, p.category ORDER BY revenue_rank;
    """,
}

for name, query in queries.items():
    df = pd.read_sql(text(query), engine)
    df.to_csv(OUTPUTS / f"{name}.csv", index=False)
    print(f"Exported {name}: {len(df):,} rows")
