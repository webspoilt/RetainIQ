SELECT customer_id
FROM {{ ref('fact_customer_snapshot') }}
WHERE monthly_revenue_proxy < 0 OR total_revenue < 0
