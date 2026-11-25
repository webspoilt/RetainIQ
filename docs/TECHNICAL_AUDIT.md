# Technical Audit — RetainIQ V2

## 1. Component Status Classification

| Component | Status | Notes |
|---|---|---|
| `src/ingest.py` | Implemented & Verified (CSV) / Unverified (Live PG) | Downloads 7,043 rows, computes SHA-256; live PG load skipped when daemon offline. |
| `src/clean_transform.py` | Implemented & Verified | Cleans 7,043 rows, imputes 11 blank `TotalCharges` for `tenure = 0`, exports CSV/JSON. |
| `src/risk_scoring.py` | Implemented & Verified | Scores 7,043 customers; separates active candidates from historical churned. |
| `src/ai_summary.py` | Implemented & Verified (Mock) | Deterministic offline fallback verified; live LLM provider unverified without API key. |
| `src/app.py` | Implemented but Unverified (UI) | Syntax/imports clean; interactive UI not yet launched in browser. |
| `sql/*.sql` & `dbt/` | Implemented but Unverified (Live PG) | Valid PostgreSQL SQL & dbt models; requires running PostgreSQL instance. |
| `docker-compose.yml` & `Dockerfile` | Implemented but Unverified | Docker Desktop daemon not running in current environment. |
| `.github/workflows/ci.yml` | Implemented & Verified (Local) | Ruff + pytest verified locally; adding PostgreSQL service container for dbt CI. |

## 2. Identified Issues & Severity

- **P1 — Financial Reconciliation Completeness:** `retention_summary.csv` did not explicitly output `Active Monthly Charge Proxy ($)` alongside `Historical Churned Monthly Charges ($)` to make `Total = Active + Churned` self-evident. **Fixed in Phase 2.**
- **P1 — Data Quality Report Completeness:** `data_quality_report.json` lacked `source_checksum`, `transformation_timestamp`, `rejected_record_count`, and `validation_errors` list. **Fixed in Phase 3.**
- **P1 — Test Coverage Depth:** Only 4 unit tests existed; missing financial reconciliation, boundary tests for every risk rule/tier, AI malformed-response/timeout fallback, and duplicate-ingestion idempotency tests. **Fixed in Phase 9.**
- **P2 — CI PostgreSQL/dbt Integration:** CI workflow only ran Ruff and pytest; adding a PostgreSQL service container in GitHub Actions enables automated SQL/dbt validation. **Fixed in Phase 10.**
- **P2 — Streamlit Empty-Data Guard:** `src/app.py` should gracefully handle empty filter selections without raising division-by-zero or empty-chart errors. **Fixed in Phase 7.**
