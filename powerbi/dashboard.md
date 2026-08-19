# Power BI Dashboard

## Data Model

Use a star schema:

```text
                 dim_date
                    |
dim_customer — fact_sales — dim_product
                    |
              dim_location
```

Relationships should use the surrogate keys from the curated tables. Keep `fact_sales` on the many side and dimensions on the one side.

## Page 1 — Executive Overview

Visuals:
- KPI cards: Total Sales, Orders, Customers, Average Order Value
- Monthly sales line chart
- Sales by region
- Sales by segment
- Date slicer

## Page 2 — Product & Category

Visuals:
- Sales by category
- Sales by sub-category
- Top 10 products
- Product contribution to total sales
- Category slicer

## Page 3 — Customer & Region

Visuals:
- Top customers
- Customer segment sales
- Sales by region/state map or bar chart
- Orders by region
- Region and segment slicers

## Page 4 — Forecast

Import `sales_forecast.csv` after running `src/forecast.py`.

Visuals:
- Actual vs predicted sales
- Absolute forecast error
- MAE and RMSE cards
- Forecast period slicer

## Business Questions

The dashboard should let a stakeholder answer:

1. What is total sales and how is it trending?
2. Which category and products contribute most?
3. Which customers/segments drive sales?
4. Which regions/states perform best?
5. How does sales change over time?
6. How close is the forecast to actual sales?

Do not add profit, inventory or unit-demand visuals because those measures are not present in the supplied dataset.
