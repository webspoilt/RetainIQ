# KPI Dictionary — RetainIQ

| Metric | Definition | Formula | Calculated Value | Limitations |
|---|---|---|---|---|
| **Total Customers** | Total customer records in snapshot | `COUNT(customer_id)` | **7,043** | Static point-in-time snapshot |
| **Active Customers** | Customers with `Churn = No` | `COUNT(*) WHERE churn = 'No'` | **5,174** | Snapshot status only |
| **Historical Churned Customers** | Customers with `Churn = Yes` | `COUNT(*) WHERE churn = 'Yes'` | **1,869** | No churn timestamp |
| **Historical Churn Rate** | Share of snapshot customers who churned | `Churned / Total` | **26.54%** | Not a time-windowed rate |
| **Monthly Charge Revenue Proxy** | Sum of `MonthlyCharges` across all customers | `SUM(monthly_charges)` | **$456,116.60** | Proxy, not GAAP MRR |
| **Historical Churned Monthly Charges** | Sum of `MonthlyCharges` for churned customers | `SUM(monthly_charges) WHERE churn = 'Yes'` | **$139,130.85** | Retrospective |
| **Estimated Monthly Charges Exposed** | Sum of `MonthlyCharges` for High/Critical active customers | `SUM(monthly_charges) WHERE is_active AND risk_tier IN ('Critical','High')` | **$76,131.85** | Heuristic exposure proxy, not a forecast |
| **Average Revenue Per Active User** | Mean `MonthlyCharges` among active customers | `AVG(monthly_charges) WHERE is_active` | **$61.27** | Excludes one-time fees |
| **Average Customer Tenure** | Mean tenure in months | `AVG(tenure)` | **32.37 months** | Cross-sectional snapshot |
| **High-Risk Active Customers** | Active customers scored >= 50 (High or Critical) | `COUNT(*) WHERE is_active AND risk_score >= 50` | **1,148** | Rule-based heuristic |
