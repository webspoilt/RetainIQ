# RetainIQ — AI-Assisted Customer Retention & Churn Cohort Analytics Platform

[![RetainIQ CI](https://github.com/YOUR_USERNAME/retainiq/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/retainiq/actions/workflows/ci.yml)

RetainIQ is an end-to-end Business Intelligence, Customer Analytics, and AI-Assisted Decision Support platform built on the IBM Telco Customer Churn dataset (7,043 customer records).

## Architecture

`Raw CSV -> Python Ingestion (src/ingest.py) -> PostgreSQL (raw) -> Cleaning & Feature Engineering (src/clean_transform.py) -> dbt Star Schema (dbt/) -> Risk Scoring (src/risk_scoring.py) -> Power BI Assets & Streamlit App (src/app.py) + Grounded AI Briefs (src/ai_summary.py)`

## Verified Key Results

- **Total Customers:** 7,043 (5,174 Active | 1,869 Historical Churned)
- **Historical Churn Rate:** 26.54%
- **Monthly Charge Revenue Proxy:** $456,116.60
- **Historical Churned Monthly Charges:** $139,130.85
- **Estimated Monthly Charges Exposed (High/Critical Active):** $76,131.85 across 1,148 customers
- **Average Revenue Per Active User (ARPAU):** $61.27

## Quick Start (Local)

```bash
pip install -r requirements.txt
python -m src.ingest
python -m src.clean_transform
python -m src.risk_scoring
python -m src.ai_summary
streamlit run src/app.py
```

## Docker Deployment

```bash
docker compose build
docker compose up -d
docker compose ps
docker compose logs -f
docker compose down
```

## Testing & Code Quality

```bash
ruff check src tests
pytest -v
```
