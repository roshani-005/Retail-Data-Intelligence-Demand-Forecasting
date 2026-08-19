from pathlib import Path
import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

products = pd.DataFrame([
    (101, "Laptop", "Electronics", 65000, 52000),
    (102, "Wireless Headphones", "Electronics", 3500, 2100),
    (103, "Smartphone", "Electronics", 28000, 22000),
    (104, "Office Chair", "Furniture", 8500, 5600),
    (105, "Desk Lamp", "Furniture", 1800, 1000),
    (106, "Backpack", "Accessories", 2200, 1200),
    (107, "Running Shoes", "Sports", 4200, 2600),
    (108, "Water Bottle", "Sports", 900, 450),
    (109, "Coffee Maker", "Home", 6200, 3900),
    (110, "Air Fryer", "Home", 7800, 5100),
], columns=["product_id", "product_name", "category", "unit_price", "unit_cost"])

stores = pd.DataFrame([
    (1, "Delhi Central", "North", "Delhi"),
    (2, "Mumbai West", "West", "Mumbai"),
    (3, "Bengaluru Tech Park", "South", "Bengaluru"),
    (4, "Kolkata Market", "East", "Kolkata"),
    (5, "Pune Plaza", "West", "Pune"),
], columns=["store_id", "store_name", "region", "city"])

start = pd.Timestamp("2025-01-01")
end = pd.Timestamp("2025-06-30")
dates = pd.date_range(start, end, freq="D")
rows = []
tid = 1
for date in dates:
    season = 1 + 0.12 * np.sin(2 * np.pi * date.dayofyear / 365)
    weekend = 1.15 if date.dayofweek >= 5 else 1.0
    for store in stores.itertuples(index=False):
        for product in products.itertuples(index=False):
            if RNG.random() > 0.55:
                continue
            base = {101: 3, 102: 8, 103: 7, 104: 4, 105: 9, 106: 10, 107: 7, 108: 14, 109: 5, 110: 4}[product.product_id]
            trend = 1 + 0.0015 * (date - start).days
            units = max(1, int(round(base * season * weekend * trend * RNG.lognormal(0, 0.22))))
            if RNG.random() < 0.025:
                units = np.nan
            rows.append((tid, date, store.store_id, product.product_id, units, product.unit_price, product.unit_cost))
            tid += 1

sales = pd.DataFrame(rows, columns=["transaction_id", "order_date", "store_id", "product_id", "quantity", "unit_price", "unit_cost"])
# Deliberately inject a few messy records so the ETL has something realistic to clean.
sales = pd.concat([sales, sales.sample(25, random_state=42)], ignore_index=True)
sales.loc[sales.index[-25:], "transaction_id"] = sales.loc[sales.index[-25:], "transaction_id"].values
sales.loc[sales.sample(12, random_state=7).index, "unit_price"] *= 1.0
sales.to_csv(RAW / "sales_raw.csv", index=False)
products.to_csv(RAW / "products_raw.csv", index=False)
stores.to_csv(RAW / "stores_raw.csv", index=False)
print(f"Generated {len(sales):,} raw sales rows in {RAW}")
