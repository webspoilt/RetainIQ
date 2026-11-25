# Business Requirements Document (BRD) — RetainIQ

## 1. Business Problem
A subscription-based telecommunications business is experiencing a **26.54% historical churn rate** (1,869 churned customers out of 7,043 total customers), representing **$139,130.85** in historical churned monthly charges. Leadership lacks a unified, explainable system to quantify active revenue exposure and prioritize account-management outreach.

## 2. Business Objectives
1. Quantify historical churn rate, churned monthly charges, and active monthly revenue exposure.
2. Identify high-risk active customer segments using transparent, configurable business rules.
3. Deliver executive reporting (Power BI semantic model + Streamlit demo) and grounded AI retention briefs.

## 3. Stakeholders
- **Chief Operating Officer (COO):** Overall retention performance and financial exposure.
- **Head of Customer Success / Retention Manager:** Prioritized active customer outreach lists.
- **Account Managers:** Customer-level risk factors and recommended actions.
- **Finance Managers:** Monthly revenue proxy exposed to high-risk active segments.
- **Business Analysts:** Reproducible SQL/dbt definitions and data quality assurance.

## 4. Scope & Out-of-Scope
- **In Scope:** Snapshot ingestion, data quality validation, tenure-based cohorts (`0-2 months`, `3-11 months`, `12+ months`), rule-based risk scoring, AI retention briefs with offline fallback, Power BI assets, Streamlit app, Docker & CI.
- **Out of Scope:** Genuine acquisition-date cohort curves, support-ticket volume analysis, causal inference, or production CRM write-back.
