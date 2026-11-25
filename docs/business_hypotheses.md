# Business Hypotheses & Validation

1. **H1 — Month-to-month contracts have higher historical churn than long-term contracts.**
   - *Evidence:* `sql/02_kpi_queries.sql` / `segment_metrics.csv`.
   - *Limitation:* Cross-sectional correlation; does not prove contract type alone causes churn.
2. **H2 — Short-tenure customers (0–2 months) exhibit concentrated early attrition.**
   - *Evidence:* Tenure-bucket aggregation (`0-2 months`, `3-11 months`, `12+ months`).
   - *Limitation:* No acquisition dates; tenure is measured at snapshot time.
3. **H3 — Electronic check users show elevated churn compared to automatic payment methods.**
   - *Evidence:* Payment-method segmentation.
   - *Limitation:* Correlation may reflect customer demographics or contract preferences.
4. **H4 — Customers without `TechSupport` or `OnlineSecurity` churn at higher rates.**
   - *Evidence:* Service adoption segmentation.
   - *Limitation:* `TechSupport` is a subscription attribute, not support-ticket volume.
