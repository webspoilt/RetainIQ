WITH base AS (
    SELECT * FROM {{ ref('stg_customers') }}
),

active_pct AS (
    SELECT
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY monthly_charges) AS active_75th_monthly
    FROM base
    WHERE churn = 'No'
)

SELECT
    b.*,
    CASE
        WHEN b.tenure <= 2 THEN '0-2 months'
        WHEN b.tenure <= 11 THEN '3-11 months'
        ELSE '12+ months'
    END AS tenure_bucket,
    b.monthly_charges AS monthly_revenue_proxy,
    b.total_charges AS total_revenue,
    CASE WHEN b.churn = 'Yes' THEN 1 ELSE 0 END AS churn_flag,
    (b.churn = 'No') AS is_active,
    CASE WHEN b.contract = 'Month-to-month' THEN 'Short-term' ELSE 'Long-term' END AS contract_category,
    CASE WHEN b.payment_method ILIKE '%automatic%' THEN 'Automatic' ELSE 'Manual' END AS payment_category,
    (b.contract = 'Month-to-month') AS is_month_to_month,
    (b.tech_support = 'Yes') AS has_tech_support,
    (b.online_security = 'Yes') AS has_online_security,
    (b.monthly_charges > a.active_75th_monthly) AS high_monthly_charge_flag
FROM base b
CROSS JOIN active_pct a
