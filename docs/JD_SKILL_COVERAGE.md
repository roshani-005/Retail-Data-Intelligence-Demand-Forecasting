# Project Overview

## Purpose

This repository demonstrates an end-to-end retail analytics workflow using a public Superstore transaction dataset. The emphasis is on reproducible data preparation, relational modeling, SQL analytics, time-series forecasting, and lightweight query safety.

## Skills and implementation

- **Python ETL:** schema validation, column normalization, date parsing, duplicate handling, conservative row validation, and a data-quality report.
- **PostgreSQL:** fact/dimension star schema, loading workflow, indexes, constraints, reusable views, and audit triggers.
- **SQL analytics:** joins, CTEs, aggregations, `LAG()`, `RANK()`, running totals, and sales contribution analysis.
- **Forecasting:** lag/rolling features, chronological holdout, XGBoost, and comparison against a same-weekday-last-week baseline.
- **Text-to-SQL safety demo:** template-based query examples with read-only SQL validation; this is not a live LLM integration.
- **Power BI preparation:** dashboard specification and DAX measures are provided; a completed interactive dashboard is not included.

## Data assumptions

The source dataset includes sales value but does not provide trustworthy profit, inventory, unit quantity, cost, or store fields for this project. The model therefore forecasts daily sales value and does not infer missing business measures.

## Generated artifacts

After running the pipeline, the `data/processed/` directory contains curated dimension/fact tables, a data-quality report, analytics extracts, forecast predictions, and model-vs-baseline metrics. Model performance claims should be taken from those generated artifacts rather than estimated in advance.
