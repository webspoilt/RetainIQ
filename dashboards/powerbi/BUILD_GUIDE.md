# Power BI Build Guide (RetainIQ)

> **Environment Note:** Power BI Desktop is not installed in the current build environment, so a `.pbix` binary was not generated. All required semantic model assets (Power Query M, DAX measures, theme JSON, and import-ready CSVs) are provided.

## Step-by-Step Build Instructions

1. Open **Power BI Desktop**.
2. Go to **View -> Themes -> Browse for themes** and select `dashboards/themes/retainiq_theme.json`.
3. Import `data/processed/customer_risk_scores.csv`, `data/processed/cleaned_customers.csv`, and `data/processed/ai_retention_briefs.csv` (or connect directly to PostgreSQL `analytics.*` tables).
4. Create the DAX measures defined in `dashboards/dax/measures.dax`.
5. Build the 3 report pages:
   - **Page 1: Executive Overview** — 5 KPI cards + Churn by Contract, Tenure Bucket, Payment Method, and Revenue Exposure by Risk Tier.
   - **Page 2: Customer Retention Action Center** — Interactive table of active customers (`retention_candidate = TRUE`) sorted by `risk_score` and `monthly_revenue_proxy`, paired with AI Retention Briefs.
   - **Page 3: Churn Driver & Cohort Analysis** — Tenure cohort breakdown, service adoption (`TechSupport`, `OnlineSecurity`), and revenue concentration.
