-- RetainIQ Executive & Segmentation KPI Queries
-- Database: retention_analytics

-- 1. Executive KPIs
SELECT
    COUNT(*) AS total_customers,
    COUNT(*) FILTER (WHERE churn = 'No') AS active_customers,
    COUNT(*) FILTER (WHERE churn = 'Yes') AS historical_churned_customers,
    ROUND(100.0 * COUNT(*) FILTER (WHERE churn = 'Yes') / NULLIF(COUNT(*), 0), 2) AS historical_churn_rate_pct,
    ROUND(SUM(monthly_charges), 2) AS monthly_charge_revenue_proxy,
    ROUND(SUM(monthly_charges) FILTER (WHERE churn = 'Yes'), 2) AS historical_churned_monthly_charges,
    ROUND(AVG(monthly_charges) FILTER (WHERE churn = 'No'), 2) AS avg_revenue_per_active_user,
    ROUND(AVG(tenure), 2) AS avg_customer_tenure_months
FROM raw.telco_customers;

-- 2. Churn Rate by Contract Type
SELECT
    contract,
    COUNT(*) AS customer_count,
    COUNT(*) FILTER (WHERE churn = 'Yes') AS churned_count,
    ROUND(100.0 * COUNT(*) FILTER (WHERE churn = 'Yes') / NULLIF(COUNT(*), 0), 2) AS churn_rate_pct,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charges,
    ROUND(SUM(monthly_charges) FILTER (WHERE churn = 'Yes'), 2) AS historical_churned_monthly_charges
FROM raw.telco_customers
GROUP BY contract
ORDER BY churn_rate_pct DESC;

-- 3. Churn Rate by Tenure Bucket
WITH bucketed AS (
    SELECT
        *,
        CASE
            WHEN tenure <= 2 THEN '0-2 months'
            WHEN tenure <= 11 THEN '3-11 months'
            ELSE '12+ months'
        END AS tenure_bucket
    FROM raw.telco_customers
)
SELECT
    tenure_bucket,
    COUNT(*) AS customer_count,
    COUNT(*) FILTER (WHERE churn = 'Yes') AS churned_count,
    ROUND(100.0 * COUNT(*) FILTER (WHERE churn = 'Yes') / NULLIF(COUNT(*), 0), 2) AS churn_rate_pct,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charges,
    ROUND(SUM(monthly_charges) FILTER (WHERE churn = 'Yes'), 2) AS historical_churned_monthly_charges
FROM bucketed
GROUP BY tenure_bucket
ORDER BY churn_rate_pct DESC;

-- 4. Churn Rate by Payment Method
SELECT
    payment_method,
    COUNT(*) AS customer_count,
    COUNT(*) FILTER (WHERE churn = 'Yes') AS churned_count,
    ROUND(100.0 * COUNT(*) FILTER (WHERE churn = 'Yes') / NULLIF(COUNT(*), 0), 2) AS churn_rate_pct,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charges
FROM raw.telco_customers
GROUP BY payment_method
ORDER BY churn_rate_pct DESC;
