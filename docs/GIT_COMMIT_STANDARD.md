# RetainIQ Git Commit Message Engineering Standard

## 1. Purpose

This document defines the mandatory, repository-level Git commit message and change-hygiene standard for **RetainIQ**. Every commit must be an accurate, auditable engineering record derived from the actual staged/unstaged Git diff—never from generic task descriptions.

---

## 2. Subject Line Format (Conventional Commits)

```text
<type>(<scope>): <imperative summary>
```

- **Length:** 50–72 characters maximum.
- **Mood:** Imperative, present tense (e.g., `add`, `fix`, `reconcile`, `harden`), no trailing period.
- **Prohibited generic subjects:** `"update project"`, `"fix bugs"`, `"add files"`, `"code improvements"`, `"misc changes"`.

### Allowed Commit Types

| Type | When to Use |
|---|---|
| `feat` | New user-facing capability or pipeline module |
| `fix` | Bug fix in Python, SQL, dbt, or UI |
| `refactor` | Code restructuring without behavior change |
| `perf` | Query, Pandas, or rendering performance optimization |
| `test` | Adding or updating `pytest` or `dbt` tests |
| `docs` | Documentation, KPI dictionary, audit, or README updates |
| `build` | `Dockerfile`, `docker-compose.yml`, `requirements.txt`, `pyproject.toml` |
| `ci` | `.github/workflows/` CI/CD pipeline changes |
| `data` | Ingestion, cleaning, or data-quality rule changes |
| `sql` | PostgreSQL schema (`sql/01_schema.sql`) or analytical queries |
| `analytics` | KPI definitions, cohort logic, or risk-scoring rules |
| `dashboard` | Streamlit (`src/app.py`) or Power BI (`dashboards/`) assets |
| `ai` | LLM provider abstraction, prompts, or offline fallback (`src/ai_summary.py`) |
| `security` | Secret handling, `.env.example`, non-root container hardening |
| `chore` | Maintenance, `.gitignore`, formatting |

---

## 3. Structured Commit Body

Every non-trivial commit must include a structured body with the following sections:

```text
What changed:
- Concise bullet list of the exact files and behaviors modified in the diff.

Why it changed:
- Root cause, business requirement, or audit finding addressed.

Technical & business impact:
- Effect on downstream models, KPIs, revenue exposure, or operations.

Validation performed:
- Exact commands executed (e.g., `pytest -v`, `ruff check src tests`) and observed results.
- Explicitly state if an integration (e.g., Docker, Power BI Desktop) was not run.

Breaking changes:
- None (or explicit description of schema/API/config breaking changes).
```

---

## 4. Pre-Commit Engineering Discipline

1. **Inspect before staging:** Run `git status`, `git diff`, and `git diff --staged` to verify every line being committed.
2. **Generate from the diff:** Write the commit message from the actual diff, not from memory or prompt text.
3. **Atomic commits:** Group logically related changes together; never stage unrelated files.
4. **Honest validation:** Never fabricate test results or claim PostgreSQL, dbt, Docker, or Power BI integrations were validated unless actually executed.
5. **Authorship & history:** Never invent Git authors or co-authors. Never force-push or rewrite published history without explicit authorization.
6. **Push policy:** Never push automatically unless explicitly authorized.
7. **Post-commit reporting:** Report the commit hash, complete commit message, included files, validation results, remaining unstaged/untracked changes, and push status.

---

## 5. RetainIQ-Specific Examples

### Example 1: Financial KPI Reconciliation (`analytics`)
```text
analytics(risk-scoring): add active monthly charge proxy for KPI reconciliation

What changed:
- Added `Active Monthly Charge Proxy ($)` to `build_retention_summary` in `src/risk_scoring.py`.
- Added `test_full_dataset_reconciliation_if_present` in `tests/test_pipeline.py`.

Why it changed:
- Audit finding P1: `retention_summary.csv` needed explicit active-only and churned-only
  totals to verify `Total = Active + Historical Churned`.

Technical & business impact:
- Guarantees `Monthly Charge Revenue Proxy ($)` ($456,116.60) reconciles with
  `Active Monthly Charge Proxy ($)` + `Historical Churned Monthly Charges ($)` ($139,130.85).

Validation performed:
- `pytest -v`: 5/5 passed (including 7,043-row reconciliation).
- `ruff check src tests`: 0 errors.

Breaking changes:
- None.
```

### Example 2: PostgreSQL & dbt CI Integration (`ci`)
```text
ci(github-actions): add PostgreSQL 16 service container for dbt validation

What changed:
- Added `postgres:16-alpine` service with health check to `.github/workflows/ci.yml`.
- Added steps to execute `sql/01_schema.sql`, `src.ingest`, `dbt debug`, `dbt run`, and `dbt test`.

Why it changed:
- Local environment lacked a running PostgreSQL daemon; CI now validates SQL and dbt models
  automatically on every push and pull request.

Technical & business impact:
- Prevents SQL syntax regressions and broken dbt schema tests from merging to `main`.

Validation performed:
- YAML syntax and step commands reviewed against `dbt/profiles.yml.example`.
- Live GitHub Actions execution pending push.

Breaking changes:
- None.
```
