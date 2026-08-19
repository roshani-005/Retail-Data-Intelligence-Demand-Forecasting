# Retail Data Intelligence & Demand Forecasting

An end-to-end retail analytics and forecasting pipeline designed around real business workflows: data ingestion, cleansing, validation, dimensional modeling, SQL analytics, Power BI-ready outputs, demand forecasting, and business recommendations.

## Architecture

```text
Raw CSV / source data
        |
        v
Python ETL (clean + validate + transform)
        |
        +--------------------+
        |                    |
        v                    v
Dimensional SQL model    Clean analytics CSV
        |                    |
        v                    v
SQL KPIs / insights     XGBoost forecasting
        |                    |
        +---------+----------+
                  v
          Business recommendations
                  |
                  v
          Power BI-ready outputs
```

## Business problem
Retail teams need reliable daily sales data to answer: What is selling? Which stores/products drive revenue? How is demand changing? What should we expect next week? This project turns messy transaction-level data into trusted analytics and forecasts.

## Tech stack
- Python: pandas, NumPy, SQLAlchemy
- SQL: PostgreSQL-compatible dimensional model, CTEs, joins, window functions, views
- ML: XGBoost regression with chronological holdout
- BI: Power BI-ready CSVs and documented KPI queries
- Engineering: modular ETL, validation, reproducible synthetic data generation

## Project structure

```text
src/
  generate_data.py       # Creates realistic raw retail transactions
  etl.py                 # Cleans, validates and creates dimensional tables
  load_sql.py            # Loads transformed tables into PostgreSQL
  analytics.py           # Runs SQL analytics and exports BI datasets
  forecast.py            # Feature engineering + XGBoost demand forecasting
sql/
  schema.sql             # Star-schema DDL
  analytics.sql          # KPI queries, CTEs and window functions
outputs/                 # Generated datasets and forecast results
powerbi/
  README.md              # Dashboard design + data model instructions
```

## Quick start

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
python src/generate_data.py
python src/etl.py
python src/forecast.py
```

The ETL and forecasting flow runs without a database. To load PostgreSQL:

```bash
set DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/retail_intelligence
python src/load_sql.py
python src/analytics.py
```

For macOS/Linux, use `export DATABASE_URL=...` instead.

## Data quality checks
The ETL layer checks for:
- duplicate transaction IDs
- missing required fields
- invalid dates and non-positive quantities
- negative prices/costs
- invalid product/store references
- category and region normalization

A validation report is written to `outputs/data_quality_report.csv`.

## Forecasting methodology
Daily product demand is aggregated and enriched with:
- day of week
- month
- trend index
- lag-1, lag-7 and lag-14 demand
- 7-day rolling mean

The final 30 days are kept as a chronological test set to avoid time leakage. Model quality is reported with MAE and RMSE. The forecast output includes actual demand, predicted demand and forecast error.

## SQL analytics
The SQL layer demonstrates production-relevant concepts requested in analytics roles:
- joins across fact and dimension tables
- CTEs
- `LAG()` and other window functions
- views
- revenue/profit aggregation
- month-over-month growth
- top product and store analysis
- inventory coverage metrics

## Power BI dashboard
The `powerbi/README.md` defines a four-page dashboard:
1. Executive Overview
2. Product Performance
3. Store Performance
4. Demand Forecast

Recommended KPIs: Revenue, Profit, Units Sold, Orders, Average Order Value, MoM Revenue Growth, Top Product, Top Store, and Forecast MAE.

## Resume-ready description
**Retail Data Intelligence & Demand Forecasting | Python, SQL, PostgreSQL, Power BI, XGBoost**
Built an end-to-end retail data pipeline that cleans and validates raw transactions, loads a dimensional warehouse, generates SQL-based business KPIs, produces Power BI-ready datasets, and forecasts daily product demand with XGBoost using lag and rolling time-series features and a chronological holdout.
