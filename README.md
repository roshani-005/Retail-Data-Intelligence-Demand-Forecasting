# Retail Data Intelligence & Demand Forecasting

An end-to-end **Retail Data Intelligence** project built specifically around the **TresVista Analyst – Data Intelligence Group** prerequisites. It demonstrates Python data gathering/cleansing, ETL, relational DBMS design, SQL analytics, Power BI, data engineering, sales forecasting, basic Generative AI concepts, analytics, and database optimization.

## Business Objective
Turn raw retail transaction data into a reliable analytical system that answers how sales change over time, which products/customers/regions drive sales, which segments need attention, and what the near-term sales trend looks like.

## Architecture

```text
Real Superstore CSV
        ↓
Python Data Gathering
        ↓
Cleansing + Normalization + Validation
        ↓
ETL Pipeline
        ↓
PostgreSQL Relational Model
        ↓
SQL Analytics ───────────→ Curated BI Outputs
        ↓                         ↓
Power BI Dashboard         XGBoost Sales Forecast
        ↓                         ↓
Business Recommendations ←───────┘
        ↓
Basic GenAI / Text-to-SQL
```

## TresVista Prerequisite Coverage

| JD prerequisite | Project implementation |
|---|---|
| Python data gathering, cleansing & normalization | `src/etl.py` |
| Hands-on ETL | Extract → Transform → Validate → Load |
| Power BI / visualization | `powerbi/` model, dashboard plan and DAX |
| DBMS fundamentals | PK/FK constraints, normalization, integrity and transactions |
| SQL | Joins, Views, Triggers, Window Functions and CTEs |
| Analytical/problem-solving/communication | KPI definitions, business questions and recommendations |
| Data Engineering | Modular Python pipeline + PostgreSQL loading |
| Basic Generative AI | Natural-language-to-SQL concept + SQL safety validation |
| Analytics domain | Retail customer/product/region/time analytics |
| Relational design & optimization | Star schema, indexes and reusable views |

## Dataset

Place the supplied Superstore transaction CSV at:

```text
data/raw/superstore.csv
```

The pipeline is schema-aware and **does not invent unsupported fields** such as profit, quantity, inventory, cost or store IDs. Because the supplied data provides `Sales`, the forecasting target is **daily sales value** rather than fabricated unit demand.

Expected source fields include:

```text
Row ID, Order ID, Order Date, Ship Date, Ship Mode,
Customer ID, Customer Name, Segment, Country, City, State,
Postal Code, Region, Product ID, Category, Sub-Category,
Product Name, Sales
```

## Project Structure

```text
data/raw/superstore.csv

data/processed/

src/
  etl.py             # extraction, cleansing, normalization, validation
  load_sql.py        # PostgreSQL loader
  analytics.py       # analytical outputs
  forecast.py        # XGBoost sales forecasting

sql/
  schema.sql         # relational/star schema
  indexes.sql        # optimization indexes
  triggers.sql       # audit trigger
  views.sql          # reusable reporting views
  analytics.sql      # joins, CTEs and window functions

powerbi/
  dashboard.md       # dashboard design and data model
  measures.dax       # KPI measures

genai/
  text_to_sql.py     # basic NL-to-SQL concept + safety validation
  README.md

docs/
  JD_SKILL_COVERAGE.md
```

## Run

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python src/etl.py
python src/forecast.py
```

For PostgreSQL:

```text
DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@HOST:5432/retail_intelligence
```

```bash
python src/load_sql.py
```

Run SQL in this order:

```text
sql/schema.sql
sql/indexes.sql
sql/triggers.sql
sql/views.sql
sql/analytics.sql
```

## ETL Responsibilities

1. Read the raw CSV.
2. Normalize column names.
3. Parse dates safely.
4. Standardize categorical text.
5. Remove duplicate source rows.
6. Handle missing values without inventing business facts.
7. Validate IDs, dates and sales.
8. Build date, customer, product, location and sales tables.
9. Write a data-quality report.

## SQL

The SQL layer intentionally covers the exact SQL concepts named in the JD: joins, CTEs, views, triggers and window functions such as `LAG()` and `RANK()`. It also includes indexes for common joins and filters.

## Power BI

Four pages are planned:

1. **Executive Overview** — Total Sales, Orders, Customers, AOV, monthly and regional trends.
2. **Product & Category** — category/sub-category sales and top products.
3. **Customer & Region** — segment, customer and geographic performance.
4. **Forecast** — actual vs predicted sales and forecast error metrics.

## Forecasting

Features include day-of-week, month, quarter, trend, lag-1, lag-7, lag-14, 7-day rolling mean and 28-day rolling mean. The final period is held out chronologically to avoid time leakage. Evaluation uses MAE and RMSE.

## Basic Generative AI

The GenAI component demonstrates:

```text
Business Question → Natural Language → SQL → Safety Check → Database → Answer
```

It is intentionally basic because the core project focus is data engineering, SQL, BI and analytics.

## Resume Version

**Retail Data Intelligence & Demand Forecasting | Python, SQL, PostgreSQL, Power BI, XGBoost**  
Built an end-to-end retail data pipeline using Python to gather, cleanse, normalize and validate transaction data; designed a relational warehouse in PostgreSQL; developed SQL analytics using joins, CTEs, views and window functions; created Power BI KPI dashboards; and forecasted daily sales with XGBoost using lag and rolling time-series features with chronological validation.
