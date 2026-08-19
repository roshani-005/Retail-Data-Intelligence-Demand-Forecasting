"""Load curated ETL outputs into PostgreSQL."""
from pathlib import Path
import os
import pandas as pd
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
SCHEMA = ROOT / "sql" / "schema.sql"


def main():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("Set DATABASE_URL before loading PostgreSQL.")

    engine = create_engine(url)
    with engine.begin() as conn:
        conn.execute(text(SCHEMA.read_text(encoding="utf-8")))

        tables = [
            ("dim_date", "dim_date.csv"),
            ("dim_customer", "dim_customer.csv"),
            ("dim_product", "dim_product.csv"),
            ("dim_location", "dim_location.csv"),
            ("fact_sales", "fact_sales.csv"),
        ]
        for table, filename in tables:
            path = DATA / filename
            if not path.exists():
                raise FileNotFoundError(f"Run src/etl.py first; missing {path}")
            df = pd.read_csv(path)
            df.to_sql(table, conn, schema="retail", if_exists="append", index=False, method="multi")

    print("PostgreSQL load completed.")


if __name__ == "__main__":
    main()
