"""ETL pipeline for the supplied Superstore transaction dataset.

Scope: gathering, cleansing, normalization, validation and dimensional
transformation. The pipeline never invents fields that are absent from the
source data.
"""
from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "superstore.csv"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

EXPECTED = {
    "row_id", "order_id", "order_date", "ship_date", "ship_mode",
    "customer_id", "customer_name", "segment", "country", "city",
    "state", "postal_code", "region", "product_id", "category",
    "sub_category", "product_name", "sales"
}


def normalize_column(name: str) -> str:
    name = re.sub(r"[^a-zA-Z0-9]+", "_", str(name).strip().lower()).strip("_")
    aliases = {
        "rowid": "row_id", "orderid": "order_id", "orderdate": "order_date",
        "shipdate": "ship_date", "shipmode": "ship_mode", "customerid": "customer_id",
        "customername": "customer_name", "postalcode": "postal_code",
        "productid": "product_id", "productname": "product_name",
        "subcategory": "sub_category"
    }
    return aliases.get(name, name)


def clean_text(series: pd.Series) -> pd.Series:
    return series.astype("string").str.strip().replace({"": pd.NA, "nan": pd.NA})


def load_raw() -> pd.DataFrame:
    if not RAW.exists():
        raise FileNotFoundError(
            f"Raw dataset not found: {RAW}. Put the supplied Superstore CSV there."
        )
    df = pd.read_csv(RAW, encoding_errors="ignore")
    df.columns = [normalize_column(c) for c in df.columns]
    missing = EXPECTED - set(df.columns)
    if missing:
        raise ValueError(f"Missing required source columns: {sorted(missing)}")
    return df


def transform(df: pd.DataFrame):
    original_rows = len(df)

    for col in [
        "order_id", "ship_mode", "customer_id", "customer_name", "segment",
        "country", "city", "state", "postal_code", "region", "product_id",
        "category", "sub_category", "product_name"
    ]:
        df[col] = clean_text(df[col])

    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["ship_date"] = pd.to_datetime(df["ship_date"], errors="coerce")
    df["sales"] = pd.to_numeric(df["sales"], errors="coerce")
    df["row_id"] = pd.to_numeric(df["row_id"], errors="coerce")

    duplicate_rows = int(df.duplicated(subset=["row_id"]).sum())
    df = df.drop_duplicates(subset=["row_id"], keep="first").copy()

    required = [
        "row_id", "order_id", "order_date", "ship_mode", "customer_id",
        "product_id", "category", "sub_category", "product_name", "region", "sales"
    ]
    missing_required = int(df[required].isna().any(axis=1).sum())
    invalid_sales = int((df["sales"] < 0).fillna(False).sum())
    invalid_dates = int(df["order_date"].isna().sum())

    # Conservative handling: rows that cannot participate in a sales fact are removed.
    df = df.dropna(subset=required).copy()
    df = df[df["sales"] >= 0].copy()

    # Normalize categorical spelling/case without changing business meaning.
    for col in ["ship_mode", "segment", "region", "category", "sub_category", "country", "state"]:
        df[col] = df[col].astype("string").str.strip()

    df["order_date"] = df["order_date"].dt.normalize()
    df["ship_date"] = df["ship_date"].dt.normalize()

    # Dimension tables.
    dates = pd.concat([df[["order_date"]].rename(columns={"order_date": "full_date"}),
                      df[["ship_date"]].rename(columns={"ship_date": "full_date"})]).dropna().drop_duplicates()
    dates["full_date"] = pd.to_datetime(dates["full_date"])
    dates["date_key"] = dates["full_date"].dt.strftime("%Y%m%d").astype(int)
    dates["year"] = dates["full_date"].dt.year
    dates["quarter"] = dates["full_date"].dt.quarter
    dates["month"] = dates["full_date"].dt.month
    dates["month_name"] = dates["full_date"].dt.month_name()
    dates["week_of_year"] = dates["full_date"].dt.isocalendar().week.astype(int)
    dates["day_of_week"] = dates["full_date"].dt.dayofweek + 1
    dates["day_name"] = dates["full_date"].dt.day_name()
    dates = dates.sort_values("full_date")

    customers = df[["customer_id", "customer_name", "segment"]].drop_duplicates("customer_id")
    products = df[["product_id", "product_name", "category", "sub_category"]].drop_duplicates("product_id")
    locations = df[["country", "city", "state", "postal_code", "region"]].drop_duplicates()
    locations["postal_code"] = locations["postal_code"].astype("string")
    locations["location_key"] = range(1, len(locations) + 1)

    customer_map = customers.assign(customer_key=range(1, len(customers) + 1))
    product_map = products.assign(product_key=range(1, len(products) + 1))

    df = df.merge(customer_map[["customer_id", "customer_key"]], on="customer_id", how="left")
    df = df.merge(product_map[["product_id", "product_key"]], on="product_id", how="left")
    df = df.merge(locations[["country", "city", "state", "postal_code", "region", "location_key"]],
                  on=["country", "city", "state", "postal_code", "region"], how="left")

    date_key_map = dates[["full_date", "date_key"]]
    df = df.merge(date_key_map.rename(columns={"full_date": "order_date", "date_key": "order_date_key"}),
                  on="order_date", how="left")
    df = df.merge(date_key_map.rename(columns={"full_date": "ship_date", "date_key": "ship_date_key"}),
                  on="ship_date", how="left")

    fact = df[["row_id", "order_id", "order_date_key", "ship_date_key", "customer_key",
               "product_key", "location_key", "ship_mode", "sales"]].copy()

    report = pd.DataFrame([{
        "source_rows": original_rows,
        "duplicate_rows_removed": duplicate_rows,
        "rows_with_required_fields_missing": missing_required,
        "invalid_sales_rows": invalid_sales,
        "invalid_order_dates": invalid_dates,
        "final_fact_rows": len(fact),
        "unique_customers": len(customer_map),
        "unique_products": len(product_map),
        "unique_locations": len(locations),
        "date_dimension_rows": len(dates)
    }])

    return dates, customer_map[["customer_key", "customer_id", "customer_name", "segment"]], \
        product_map[["product_key", "product_id", "product_name", "category", "sub_category"]], \
        locations[["location_key", "country", "city", "state", "postal_code", "region"]], fact, report


def main():
    dates, customers, products, locations, fact, report = transform(load_raw())
    dates.to_csv(OUT / "dim_date.csv", index=False)
    customers.to_csv(OUT / "dim_customer.csv", index=False)
    products.to_csv(OUT / "dim_product.csv", index=False)
    locations.to_csv(OUT / "dim_location.csv", index=False)
    fact.to_csv(OUT / "fact_sales.csv", index=False)
    report.to_csv(OUT / "data_quality_report.csv", index=False)
    print(f"ETL complete. Curated rows: {len(fact)}")


if __name__ == "__main__":
    main()
