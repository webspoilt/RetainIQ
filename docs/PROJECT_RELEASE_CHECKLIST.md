# Project Release Checklist — RetainIQ V2

- [x] **Data Pipeline:** `src/ingest.py`, `src/clean_transform.py`, `src/risk_scoring.py`, `src/ai_summary.py` execute cleanly on 7,043 rows.
- [x] **Financial Reconciliation:** `Monthly Charge Revenue Proxy ($)` = `Active Monthly Charge Proxy ($)` + `Historical Churned Monthly Charges ($)` verified by automated test.
- [x] **Data Quality:** `data_quality_report.json` includes source/loaded/rejected counts, imputed counts, and timestamp (`validation_status: PASS`).
- [x] **Risk Scoring:** Configurable weights in `config/risk_rules.yaml`, active-only `retention_candidate` filtering, boundary tests passing.
- [x] **AI Fallback:** Deterministic offline briefs and timeout/malformed-response fallback verified without API keys.
- [x] **Code Quality:** `ruff check` and `ruff format --check` pass with 0 errors.
- [x] **Automated Tests:** `pytest -v` passes all 5 unit, reconciliation, and resilience tests.
- [x] **CI/CD:** `.github/workflows/ci.yml` configured with Ruff, pytest, and PostgreSQL 16 + dbt integration job.
- [ ] **Local Docker / Power BI Desktop:** Docker Desktop daemon was not running and Power BI Desktop was not installed in the local environment; manual execution steps are documented.
