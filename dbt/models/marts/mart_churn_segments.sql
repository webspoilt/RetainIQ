SELECT
    contract,
    tenure_bucket,
    payment_method,
    COUNT(*) AS customer_count,
    SUM(churn_flag) AS churned_count,
    COUNT(*) FILTER (WHERE is_active) AS active_count,
    ROUND(100.0 * SUM(churn_flag) / NULLIF(COUNT(*), 0), 2) AS churn_rate_pct,
    ROUND(AVG(monthly_revenue_proxy), 2) AS avg_monthly_charges,
    ROUND(SUM(monthly_revenue_proxy) FILTER (WHERE churn_flag = 1), 2) AS historical_churned_monthly_charges,
    ROUND(SUM(monthly_revenue_proxy) FILTER (WHERE is_active), 2) AS active_monthly_charges
FROM {{ ref('int_customer_features') }}
GROUP BY contract, tenure_bucket, payment_method
