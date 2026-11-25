# Dataset Source & Limitations

## Primary Dataset

- **Name:** IBM Telco Customer Churn Dataset
- **Official Repository:** https://github.com/IBM/telco-customer-churn-on-icp4d
- **Direct CSV URL:** https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv
- **Attribution:** IBM Sample Data Sets (Telco Customer Churn)
- **License:** Publicly available IBM sample dataset for educational and analytical demonstration purposes.
- **Grain:** One row per customer (`customerID`) in a static point-in-time snapshot (~7,043 records).

## Field Descriptions

| Column | Type | Description |
|---|---|---|
| `customerID` | String | Unique customer identifier |
| `gender` | Categorical | Customer gender (`Male`, `Female`) |
| `SeniorCitizen` | Integer (0/1) | Whether the customer is a senior citizen |
| `Partner` | Categorical | Whether the customer has a partner (`Yes`, `No`) |
| `Dependents` | Categorical | Whether the customer has dependents (`Yes`, `No`) |
| `tenure` | Integer | Number of months the customer has stayed with the company |
| `PhoneService` | Categorical | Whether the customer has phone service (`Yes`, `No`) |
| `MultipleLines` | Categorical | Whether the customer has multiple lines (`Yes`, `No`, `No phone service`) |
| `InternetService` | Categorical | Internet service provider (`DSL`, `Fiber optic`, `No`) |
| `OnlineSecurity` | Categorical | Online security add-on (`Yes`, `No`, `No internet service`) |
| `OnlineBackup` | Categorical | Online backup add-on (`Yes`, `No`, `No internet service`) |
| `DeviceProtection` | Categorical | Device protection add-on (`Yes`, `No`, `No internet service`) |
| `TechSupport` | Categorical | Technical support add-on (`Yes`, `No`, `No internet service`) |
| `StreamingTV` | Categorical | Streaming TV add-on (`Yes`, `No`, `No internet service`) |
| `StreamingMovies` | Categorical | Streaming movies add-on (`Yes`, `No`, `No internet service`) |
| `Contract` | Categorical | Contract term (`Month-to-month`, `One year`, `Two year`) |
| `PaperlessBilling` | Categorical | Whether the customer uses paperless billing (`Yes`, `No`) |
| `PaymentMethod` | Categorical | Payment method (`Electronic check`, `Mailed check`, `Bank transfer (automatic)`, `Credit card (automatic)`) |
| `MonthlyCharges` | Numeric | Current monthly amount charged to the customer |
| `TotalCharges` | Numeric (raw string) | Total amount charged to the customer (contains blank strings for 0-tenure customers) |
| `Churn` | Categorical | Whether the customer churned (`Yes`, `No`) |

## Known Analytical Limitations

1. **No acquisition timestamps:** Genuine monthly acquisition cohort retention curves cannot be computed; tenure-based cohorts (`0-2 months`, `3-11 months`, `12+ months`) are used instead.
2. **No support-ticket counts or CSAT:** `TechSupport` is a service subscription attribute, not a support-ticket volume metric.
3. **No accounting MRR:** `MonthlyCharges` is used as a monthly revenue proxy, not verified SaaS accounting MRR.
4. **Static snapshot:** There are no multiple monthly observation periods, actual contract renewal events, or future churn observation windows.
5. **Historical vs. prospective:** Historical churn analysis describes past/current snapshot labels; active customer risk scoring (`Churn = No`) is a transparent rule-based prioritization heuristic, not a time-validated ML prediction.
