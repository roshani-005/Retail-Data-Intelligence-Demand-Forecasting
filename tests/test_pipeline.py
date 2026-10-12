import numpy as np
import pandas as pd
import pytest

from src.etl import normalize_column, transform
from src.forecast import metric_summary, pct_improvement
from genai.text_to_sql import generate_sql, validate_sql


def sample_source():
    return pd.DataFrame({
        "row_id": [1, 2, 3],
        "order_id": ["CA-1", "CA-2", "CA-3"],
        "order_date": ["2024-01-01", "2024-01-02", "2024-01-03"],
        "ship_date": ["2024-01-03", "2024-01-04", "2024-01-05"],
        "ship_mode": ["Second Class", "Standard Class", "First Class"],
        "customer_id": ["C1", "C2", "C1"],
        "customer_name": ["Customer 1", "Customer 2", "Customer 1"],
        "segment": ["Consumer", "Corporate", "Consumer"],
        "country": ["United States"] * 3,
        "city": ["Seattle", "Portland", "Seattle"],
        "state": ["Washington", "Oregon", "Washington"],
        "postal_code": ["98101", "97201", "98101"],
        "region": ["West"] * 3,
        "product_id": ["P1", "P2", "P1"],
        "category": ["Office Supplies", "Technology", "Office Supplies"],
        "sub_category": ["Paper", "Accessories", "Paper"],
        "product_name": ["Paper", "Accessory", "Paper"],
        "sales": [10.0, 20.0, 15.0],
    })


def test_normalize_column_names():
    assert normalize_column("Order Date") == "order_date"
    assert normalize_column("Sub-Category") == "sub_category"
    assert normalize_column("Row ID") == "row_id"


def test_etl_transform_outputs_valid_fact_and_report():
    dates, customers, products, locations, fact, report = transform(sample_source())
    assert len(fact) == 3
    assert fact["sales"].sum() == pytest.approx(45.0)
    assert fact["customer_key"].notna().all()
    assert fact["product_key"].notna().all()
    assert report.loc[0, "final_fact_rows"] == 3
    assert len(dates) >= 3
    assert len(customers) == 2
    assert len(products) == 2
    assert len(locations) == 2


def test_etl_drops_duplicate_row_ids_and_reports_it():
    source = pd.concat([sample_source(), sample_source().iloc[[0]]], ignore_index=True)
    _, _, _, _, fact, report = transform(source)
    assert len(fact) == 3
    assert report.loc[0, "duplicate_rows_removed"] == 1


def test_forecast_metrics_handle_zero_actuals():
    metrics = metric_summary([0, 100, 200], [10, 90, 220])
    assert metrics["mae"] == pytest.approx(13.333333, rel=1e-5)
    assert metrics["rmse"] == pytest.approx(np.sqrt(200), rel=1e-5)
    assert metrics["mape_pct"] == pytest.approx(10.0)
    assert metrics["mape_rows"] == 2


def test_percentage_improvement_is_positive_when_error_falls():
    assert pct_improvement(20, 15) == pytest.approx(25.0)
    assert np.isnan(pct_improvement(0, 0))


def test_text_to_sql_demo_returns_read_only_query():
    sql = generate_sql("show total sales by region")
    assert sql.lstrip().upper().startswith("SELECT")
    assert validate_sql(sql) == sql


@pytest.mark.parametrize("sql", [
    "DROP TABLE retail.fact_sales",
    "SELECT 1; DELETE FROM retail.fact_sales",
    "UPDATE retail.fact_sales SET sales = 0",
])
def test_text_to_sql_rejects_mutating_or_multiple_statements(sql):
    with pytest.raises(ValueError):
        validate_sql(sql)
