# Known Limitations — RetainIQ V2

1. **Static Snapshot:** No acquisition dates or longitudinal monthly observations; tenure cohorts (`0-2 months`, `3-11 months`, `12+ months`) are used instead of acquisition cohorts.
2. **Revenue Proxy:** `MonthlyCharges` is a monthly charge proxy, not verified GAAP MRR.
3. **Rule-Based Risk Score:** The 90-point heuristic in `config/risk_rules.yaml` is an explainable prioritization rule, not a time-validated ML probability.
4. **Local Environment:** Power BI Desktop is not installed (no `.pbix` binary generated; full M/DAX/theme/build guide provided), and Docker Desktop daemon was not running during this session.
