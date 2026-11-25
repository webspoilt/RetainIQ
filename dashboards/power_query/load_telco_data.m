// Power Query M Script: Load Processed RetainIQ Tables from PostgreSQL or CSV
let
    Source = Csv.Document(
        File.Contents("E:\PROJECTS\Data analytics\AI-Assisted Customer Retention & Churn Cohort Analytics Platform\data\processed\customer_risk_scores.csv"),
        [Delimiter=",", Columns=15, Encoding=65001, QuoteStyle=QuoteStyle.None]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangedTypes = Table.TransformColumnTypes(PromotedHeaders, {
        {"customer_id", type text},
        {"churn", type text},
        {"is_active", type logical},
        {"contract", type text},
        {"tenure", Int64.Type},
        {"tenure_bucket", type text},
        {"payment_method", type text},
        {"internet_service", type text},
        {"monthly_revenue_proxy", type number},
        {"risk_score", Int64.Type},
        {"risk_tier", type text},
        {"contributing_risk_factors", type text},
        {"retention_candidate", type logical},
        {"retention_priority", type text},
        {"recommended_action", type text}
    })
in
    ChangedTypes
