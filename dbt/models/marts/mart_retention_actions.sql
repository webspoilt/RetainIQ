WITH scored AS (
    SELECT
        *,
        (CASE WHEN is_month_to_month THEN 25 ELSE 0 END)
        + (CASE WHEN tenure < 3 THEN 20 ELSE 0 END)
        + (CASE WHEN payment_method = 'Electronic check' THEN 15 ELSE 0 END)
        + (CASE WHEN NOT has_tech_support THEN 10 ELSE 0 END)
        + (CASE WHEN NOT has_online_security THEN 10 ELSE 0 END)
        + (CASE WHEN high_monthly_charge_flag THEN 10 ELSE 0 END) AS risk_score
    FROM {{ ref('int_customer_features') }}
)

SELECT
    customer_id,
    contract,
    tenure,
    tenure_bucket,
    payment_method,
    internet_service,
    monthly_revenue_proxy,
    risk_score,
    CASE
        WHEN risk_score >= 70 THEN 'Critical'
        WHEN risk_score >= 50 THEN 'High'
        WHEN risk_score >= 30 THEN 'Medium'
        ELSE 'Low'
    END AS risk_tier,
    is_active AS retention_candidate
FROM scored
WHERE is_active
ORDER BY risk_score DESC, monthly_revenue_proxy DESC
