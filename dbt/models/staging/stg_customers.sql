WITH source AS (
    SELECT * FROM raw.telco_customers
)

SELECT
    TRIM(customer_id) AS customer_id,
    TRIM(gender) AS gender,
    senior_citizen,
    TRIM(partner) AS partner,
    TRIM(dependents) AS dependents,
    tenure,
    TRIM(phone_service) AS phone_service,
    TRIM(multiple_lines) AS multiple_lines,
    TRIM(internet_service) AS internet_service,
    TRIM(online_security) AS online_security,
    TRIM(online_backup) AS online_backup,
    TRIM(device_protection) AS device_protection,
    TRIM(tech_support) AS tech_support,
    TRIM(streaming_tv) AS streaming_tv,
    TRIM(streaming_movies) AS streaming_movies,
    TRIM(contract) AS contract,
    TRIM(paperless_billing) AS paperless_billing,
    TRIM(payment_method) AS payment_method,
    CAST(monthly_charges AS NUMERIC(10, 2)) AS monthly_charges,
    CASE
        WHEN TRIM(total_charges) = '' OR total_charges IS NULL THEN
            CASE WHEN tenure = 0 THEN 0.00 ELSE CAST(monthly_charges * tenure AS NUMERIC(12, 2)) END
        ELSE CAST(TRIM(total_charges) AS NUMERIC(12, 2))
    END AS total_charges,
    TRIM(churn) AS churn,
    ingested_at
FROM source
