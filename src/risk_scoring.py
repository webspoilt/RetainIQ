"""Transparent, rule-based customer risk scoring engine."""

import logging
from pathlib import Path

import pandas as pd
import yaml

from src.config import PROCESSED_DATA_DIR, RISK_RULES_PATH

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def load_risk_rules(rules_path: Path = RISK_RULES_PATH) -> dict:
    """Load configurable risk scoring weights and tier thresholds."""
    with open(rules_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def score_customers(df: pd.DataFrame, rules: dict | None = None) -> pd.DataFrame:
    """Score customers using transparent business rules."""
    if rules is None:
        rules = load_risk_rules()

    weights = rules["weights"]
    thresholds = rules["thresholds"]
    tiers = rules["risk_tiers"]

    active_75th = float(
        df.loc[df["is_active"], "monthly_charges"].quantile(
            thresholds["high_monthly_charge_percentile"] / 100.0
        )
    )

    records = []
    for _, row in df.iterrows():
        score = 0
        factors = []

        if row["contract"] == "Month-to-month":
            score += weights["month_to_month_contract"]
            factors.append("Month-to-month contract")
        if row["tenure"] < thresholds["tenure_short_months"]:
            score += weights["tenure_below_3_months"]
            factors.append("Tenure < 3 months")
        if row["payment_method"] == "Electronic check":
            score += weights["electronic_check_payment"]
            factors.append("Electronic check")
        if not bool(row["has_tech_support"]):
            score += weights["no_tech_support"]
            factors.append("No TechSupport")
        if not bool(row["has_online_security"]):
            score += weights["no_online_security"]
            factors.append("No OnlineSecurity")
        if float(row["monthly_charges"]) > active_75th:
            score += weights["high_monthly_charges"]
            factors.append("High MonthlyCharges (>75th pct)")

        if score >= tiers["critical"]["min_score"]:
            tier = "Critical"
            priority = tiers["critical"]["priority"]
            action = tiers["critical"]["action"]
        elif score >= tiers["high"]["min_score"]:
            tier = "High"
            priority = tiers["high"]["priority"]
            action = tiers["high"]["action"]
        elif score >= tiers["medium"]["min_score"]:
            tier = "Medium"
            priority = tiers["medium"]["priority"]
            action = tiers["medium"]["action"]
        else:
            tier = "Low"
            priority = tiers["low"]["priority"]
            action = tiers["low"]["action"]

        is_active = bool(row["is_active"])
        records.append(
            {
                "customer_id": row["customer_id"],
                "churn": row["churn"],
                "is_active": is_active,
                "contract": row["contract"],
                "tenure": int(row["tenure"]),
                "tenure_bucket": row["tenure_bucket"],
                "payment_method": row["payment_method"],
                "internet_service": row["internet_service"],
                "monthly_revenue_proxy": round(float(row["monthly_revenue_proxy"]), 2),
                "risk_score": int(score),
                "risk_tier": tier,
                "contributing_risk_factors": "; ".join(factors) if factors else "None",
                "retention_candidate": is_active,
                "retention_priority": priority if is_active else "Historical Churned",
                "recommended_action": action if is_active else "Retrospective analysis only",
            }
        )

    return pd.DataFrame(records)


def build_retention_summary(scored_df: pd.DataFrame) -> pd.DataFrame:
    """Summarize executive KPIs and active vs historical populations."""
    total_customers = len(scored_df)
    active_df = scored_df[scored_df["is_active"]]
    churned_df = scored_df[~scored_df["is_active"]]
    high_risk_active = active_df[active_df["risk_tier"].isin(["Critical", "High"])]

    summary = [
        {"metric": "Total Customers", "value": total_customers},
        {"metric": "Active Customers", "value": len(active_df)},
        {"metric": "Historical Churned Customers", "value": len(churned_df)},
        {
            "metric": "Historical Churn Rate (%)",
            "value": round((len(churned_df) / total_customers) * 100, 2)
            if total_customers
            else 0.0,
        },
        {
            "metric": "Monthly Charge Revenue Proxy ($)",
            "value": round(float(scored_df["monthly_revenue_proxy"].sum()), 2),
        },
        {
            "metric": "Active Monthly Charge Proxy ($)",
            "value": round(float(active_df["monthly_revenue_proxy"].sum()), 2),
        },
        {
            "metric": "Historical Churned Monthly Charges ($)",
            "value": round(float(churned_df["monthly_revenue_proxy"].sum()), 2),
        },
        {
            "metric": "Estimated Monthly Charges Exposed ($)",
            "value": round(float(high_risk_active["monthly_revenue_proxy"].sum()), 2),
        },
        {
            "metric": "Average Revenue Per Active User ($)",
            "value": round(float(active_df["monthly_revenue_proxy"].mean()), 2)
            if len(active_df)
            else 0.0,
        },
        {
            "metric": "Average Customer Tenure (Months)",
            "value": round(float(scored_df["tenure"].mean()), 2) if total_customers else 0.0,
        },
        {"metric": "High-Risk Active Customers", "value": len(high_risk_active)},
    ]
    return pd.DataFrame(summary)


def run_risk_scoring(
    cleaned_path: Path = PROCESSED_DATA_DIR / "cleaned_customers.csv",
    output_dir: Path = PROCESSED_DATA_DIR,
) -> pd.DataFrame:
    """Run risk scoring and export customer_risk_scores.csv and retention_summary.csv."""
    df = pd.read_csv(cleaned_path)
    scored_df = score_customers(df)
    summary_df = build_retention_summary(scored_df)

    scored_df.to_csv(output_dir / "customer_risk_scores.csv", index=False)
    summary_df.to_csv(output_dir / "retention_summary.csv", index=False)
    logger.info("Risk scoring complete: %d customers scored.", len(scored_df))
    return scored_df


if __name__ == "__main__":
    run_risk_scoring()
