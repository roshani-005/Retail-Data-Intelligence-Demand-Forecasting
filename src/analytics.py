"""Generate business analytics from curated CSVs without requiring PostgreSQL."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
OUT = ROOT / "data" / "processed"


def main():
    fact = pd.read_csv(DATA / "fact_sales.csv")
    dates = pd.read_csv(DATA / "dim_date.csv")
    products = pd.read_csv(DATA / "dim_product.csv")
    customers = pd.read_csv(DATA / "dim_customer.csv")
    locations = pd.read_csv(DATA / "dim_location.csv")

    fact["order_date"] = pd.to_datetime(fact["order_date_key"].astype(str), format="%Y%m%d")
    fact = fact.merge(products[["product_key", "product_id", "product_name", "category", "sub_category"]], on="product_key")
    fact = fact.merge(customers[["customer_key", "customer_id", "customer_name", "segment"]], on="customer_key")
    fact = fact.merge(locations[["location_key", "state", "region"]], on="location_key")

    monthly = fact.groupby(fact["order_date"].dt.to_period("M")).agg(
        total_sales=("sales", "sum"),
        orders=("order_id", "nunique"),
        customers=("customer_key", "nunique")
    ).reset_index()
    monthly["month"] = monthly["order_date"].astype(str)
    monthly["mom_growth_pct"] = monthly["total_sales"].pct_change().mul(100)
    monthly.drop(columns="order_date").to_csv(OUT / "bi_monthly_sales.csv", index=False)

    product = fact.groupby(["product_id", "product_name", "category", "sub_category"], as_index=False).agg(
        total_sales=("sales", "sum"), orders=("order_id", "nunique")
    ).sort_values("total_sales", ascending=False)
    product.to_csv(OUT / "bi_product_performance.csv", index=False)

    customer = fact.groupby(["customer_id", "customer_name", "segment"], as_index=False).agg(
        total_sales=("sales", "sum"), orders=("order_id", "nunique")
    ).sort_values("total_sales", ascending=False)
    customer.to_csv(OUT / "bi_customer_performance.csv", index=False)

    region = fact.groupby(["region", "state"], as_index=False).agg(
        total_sales=("sales", "sum"), orders=("order_id", "nunique"), customers=("customer_key", "nunique")
    ).sort_values("total_sales", ascending=False)
    region.to_csv(OUT / "bi_region_performance.csv", index=False)

    print("Analytics outputs written to data/processed/")


if __name__ == "__main__":
    main()
