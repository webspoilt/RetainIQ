SELECT DISTINCT
    MD5(payment_method) AS payment_method_key,
    payment_method,
    payment_category
FROM {{ ref('int_customer_features') }}
