SELECT DISTINCT
    MD5(tenure_bucket) AS tenure_bucket_key,
    tenure_bucket,
    CASE
        WHEN tenure_bucket = '0-2 months' THEN 1
        WHEN tenure_bucket = '3-11 months' THEN 2
        ELSE 3
    END AS sort_order
FROM {{ ref('int_customer_features') }}
