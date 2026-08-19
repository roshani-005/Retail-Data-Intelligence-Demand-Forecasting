import os
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise SystemExit("Set DATABASE_URL, e.g. postgresql+psycopg2://postgres:password@localhost:5432/retail_intelligence")

engine = create_engine(DATABASE_URL)
schema = (ROOT / "sql" / "schema.sql").read_text(encoding="utf-8")
with engine.begin() as conn:
    for statement in schema.split(";"):
        if statement.strip():
            conn.execute(text(statement))

for table, file in [
    ("dim_date", "dim_date.csv"),
    ("dim_product", "dim_product.csv"),
    ("dim_store", "dim_store.csv"),
    ("fact_sales", "fact_sales.csv"),
]:
    df = pd.read_csv(PROCESSED / file)
    if table == "dim_date":
        df["date"] = pd.to_datetime(df["date"]).dt.date
    if table == "fact_sales":
        df["order_date"] = pd.to_datetime(df["order_date"]).dt.date
    df.to_sql(table, engine, schema="retail", if_exists="append", index=False, method="multi")
    print(f"Loaded {len(df):,} rows into retail.{table}")
