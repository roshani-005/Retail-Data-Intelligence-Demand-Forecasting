from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
OUTPUTS = ROOT / "outputs"
PROCESSED.mkdir(parents=True, exist_ok=True)
OUTPUTS.mkdir(parents=True, exist_ok=True)

required = ["transaction_id", "order_date", "store_id", "product_id", "quantity", "unit_price", "unit_cost"]
sales = pd.read_csv(RAW / "sales_raw.csv")
products = pd.read_csv(RAW / "products_raw.csv")
stores = pd.read_csv(RAW / "stores_raw.csv")

report = []
def check(name, value):
    report.append((name, int(value)))

check("raw_rows", len(sales))
check("duplicate_transaction_ids", sales.duplicated("transaction_id").sum())
check("missing_required_cells", sales[required].isna().sum().sum())

sales = sales.drop_duplicates("transaction_id", keep="first").copy()
sales["order_date"] = pd.to_datetime(sales["order_date"], errors="coerce")
sales = sales.dropna(subset=["order_date", "store_id", "product_id", "quantity", "unit_price", "unit_cost"])
sales = sales[(sales["quantity"] > 0) & (sales["unit_price"] >= 0) & (sales["unit_cost"] >= 0)]
sales["store_id"] = sales["store_id"].astype(int)
sales["product_id"] = sales["product_id"].astype(int)
sales["quantity"] = sales["quantity"].astype(int)

products["product_name"] = products["product_name"].str.strip()
products["category"] = products["category"].str.strip().str.title()
stores["store_name"] = stores["store_name"].str.strip()
stores["region"] = stores["region"].str.strip().str.title()
stores["city"] = stores["city"].str.strip().str.title()

valid_products = set(products.product_id)
valid_stores = set(stores.store_id)
invalid_product_refs = ~sales.product_id.isin(valid_products)
invalid_store_refs = ~sales.store_id.isin(valid_stores)
check("invalid_product_references", invalid_product_refs.sum())
check("invalid_store_references", invalid_store_refs.sum())
sales = sales[~invalid_product_refs & ~invalid_store_refs].copy()

sales["revenue"] = sales["quantity"] * sales["unit_price"]
sales["cost"] = sales["quantity"] * sales["unit_cost"]
sales["profit"] = sales["revenue"] - sales["cost"]

# Dimension tables
dim_date = pd.DataFrame({"date": pd.date_range(sales.order_date.min(), sales.order_date.max(), freq="D")})
dim_date["date_key"] = dim_date["date"].dt.strftime("%Y%m%d").astype(int)
dim_date["year"] = dim_date["date"].dt.year
dim_date["month"] = dim_date["date"].dt.month
dim_date["month_name"] = dim_date["date"].dt.month_name()
dim_date["quarter"] = "Q" + dim_date["date"].dt.quarter.astype(str)
dim_date["day_of_week"] = dim_date["date"].dt.day_name()

dim_product = products.rename(columns={"unit_price": "list_price"}).copy()
dim_store = stores.copy()
fact_sales = sales.copy()
fact_sales["date_key"] = fact_sales["order_date"].dt.strftime("%Y%m%d").astype(int)
fact_sales = fact_sales[["transaction_id", "date_key", "order_date", "product_id", "store_id", "quantity", "unit_price", "unit_cost", "revenue", "cost", "profit"]]

for name, frame in [("dim_date", dim_date), ("dim_product", dim_product), ("dim_store", dim_store), ("fact_sales", fact_sales)]:
    frame.to_csv(PROCESSED / f"{name}.csv", index=False)

report.extend([
    ("clean_rows", len(fact_sales)),
    ("revenue_total", round(fact_sales.revenue.sum(), 2)),
    ("profit_total", round(fact_sales.profit.sum(), 2)),
])
pd.DataFrame(report, columns=["metric", "value"]).to_csv(OUTPUTS / "data_quality_report.csv", index=False)
print(f"ETL complete: {len(fact_sales):,} clean fact rows")
