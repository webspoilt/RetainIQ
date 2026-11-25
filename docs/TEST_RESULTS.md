# Test Results — RetainIQ V2

- **Ruff Lint & Format:** `ruff check src tests` — **0 errors**.
- **Pytest Suite (`tests/test_pipeline.py`):** **5/5 passed**:
  - `test_tenure_buckets` — PASSED
  - `test_clean_and_transform_idempotent` — PASSED
  - `test_financial_reconciliation_and_risk_tiers` — PASSED
  - `test_full_dataset_reconciliation_if_present` — PASSED (7,043 rows reconciled)
  - `test_offline_ai_brief_and_timeout_fallback` — PASSED
