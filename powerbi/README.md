# Power BI Dashboard Specification

The project intentionally keeps Power BI as the presentation layer rather than committing a binary `.pbix` file to GitHub. Import the generated CSVs from `outputs/` or connect Power BI directly to PostgreSQL.

## Recommended data model

Use `fact_sales` as the central fact table.

```text
             dim_date
                 |
dim_product -- fact_sales -- dim_store
```

Relationships:
- dim_date[date_key] 1 -> * fact_sales[date_key]
- dim_product[product_id] 1 -> * fact_sales[product_id]
- dim_store[store_id] 1 -> * fact_sales[store_id]

## Page 1: Executive Overview
Cards:
- Total Revenue
- Total Profit
- Units Sold
- Orders
- Average Order Value

Visuals:
- Monthly Revenue and Profit trend
- Revenue by Category
- Revenue by Region
- Top 10 Products

## Page 2: Product Performance
- Product revenue/profit table
- Category contribution
- Units sold by product
- Product revenue ranking
- Monthly product trend

## Page 3: Store Performance
- Revenue and profit by store
- Regional comparison
- Units sold by store
- Store ranking

## Page 4: Demand Forecast
Use `outputs/demand_forecast.csv`.
- Actual vs predicted demand line chart
- Forecast gap by product
- Forecast MAE and RMSE cards
- Recommendation table from `business_recommendations.csv`

## Core DAX measures

```DAX
Total Revenue = SUM(fact_sales[revenue])
Total Profit = SUM(fact_sales[profit])
Units Sold = SUM(fact_sales[quantity])
Orders = DISTINCTCOUNT(fact_sales[transaction_id])
Average Order Value = DIVIDE([Total Revenue], [Orders])
Profit Margin = DIVIDE([Total Profit], [Total Revenue])
```

For interview discussion, explain that Power BI is the stakeholder-facing layer while Python/SQL remain responsible for data preparation, business logic, quality and forecasting.
