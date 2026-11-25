-- RetainIQ Data Quality Validation Queries
-- Returns failing row counts for each check (0 = PASS)

SELECT 'duplicate_customer_id' AS check_name, COUNT(*) - COUNT(DISTINCT customer_id) AS failing_rows
FROM raw.telco_customers
UNION ALL
SELECT 'null_customer_id', COUNT(*)
FROM raw.telco_customers
WHERE customer_id IS NULL OR TRIM(customer_id) = ''
UNION ALL
SELECT 'invalid_tenure', COUNT(*)
FROM raw.telco_customers
WHERE tenure IS NULL OR tenure < 0
UNION ALL
SELECT 'invalid_churn', COUNT(*)
FROM raw.telco_customers
WHERE churn NOT IN ('Yes', 'No') OR churn IS NULL
UNION ALL
SELECT 'invalid_contract', COUNT(*)
FROM raw.telco_customers
WHERE contract NOT IN ('Month-to-month', 'One year', 'Two year') OR contract IS NULL
UNION ALL
SELECT 'invalid_payment_method', COUNT(*)
FROM raw.telco_customers
WHERE payment_method NOT IN (
    'Electronic check',
    'Mailed check',
    'Bank transfer (automatic)',
    'Credit card (automatic)'
) OR payment_method IS NULL
UNION ALL
SELECT 'negative_monthly_charges', COUNT(*)
FROM raw.telco_customers
WHERE monthly_charges IS NULL OR monthly_charges < 0
UNION ALL
SELECT 'non_numeric_total_charges', COUNT(*)
FROM raw.telco_customers
WHERE TRIM(total_charges) <> '' AND total_charges !~ '^[0-9]+(\.[0-9]+)?$';
