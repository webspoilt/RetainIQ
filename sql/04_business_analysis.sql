-- RetainIQ Advanced Business Analysis Queries

-- 1. Churn Contribution & Revenue Exposure by Contract + Tenure Bucket
WITH enriched AS (
    SELECT
        customer_id,
        contract,
        CASE
            WHEN tenure <= 2 THEN '0-2 months'
            WHEN tenure <= 11 THEN '3-11 months'
            ELSE '12+ months'
        END AS tenure_bucket,
        payment_method,
        tech_support,
        online_security,
        monthly_charges,
        churn
    FROM raw.telco_customers
)
SELECT
    contract,
    tenure_bucket,
    COUNT(*) AS total_customers,
    COUNT(*) FILTER (WHERE churn = 'Yes') AS churned_customers,
    ROUND(100.0 * COUNT(*) FILTER (WHERE churn = 'Yes') / NULLIF(COUNT(*), 0), 2) AS churn_rate_pct,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE churn = 'Yes')
        / NULLIF(SUM(COUNT(*) FILTER (WHERE churn = 'Yes')) OVER (), 0),
        2
    ) AS share_of_total_churn_pct,
    ROUND(SUM(monthly_charges) FILTER (WHERE churn = 'Yes'), 2) AS historical_churned_monthly_charges,
    ROUND(SUM(monthly_charges) FILTER (WHERE churn = 'No'), 2) AS active_monthly_charges
FROM enriched
GROUP BY contract, tenure_bucket
ORDER BY historical_churned_monthly_charges DESC;

-- 2. Service Adoption Analysis (TechSupport & OnlineSecurity)
SELECT
    tech_support,
    online_security,
    COUNT(*) AS customer_count,
    COUNT(*) FILTER (WHERE churn = 'Yes') AS churned_count,
    ROUND(100.0 * COUNT(*) FILTER (WHERE churn = 'Yes') / NULLIF(COUNT(*), 0), 2) AS churn_rate_pct,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charges
FROM raw.telco_customers
GROUP BY tech_support, online_security
ORDER BY churn_rate_pct DESC;
