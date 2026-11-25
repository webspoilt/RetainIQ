SELECT DISTINCT
    MD5(contract) AS contract_key,
    contract AS contract_type,
    contract_category,
    is_month_to_month
FROM {{ ref('int_customer_features') }}
