"""Shared analytical functions reading from validated processed outputs."""

from pathlib import Path

import pandas as pd

from src.config import PROCESSED_DATA_DIR


def load_processed_data(
    processed_dir: Path = PROCESSED_DATA_DIR,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load cleaned customers, risk scores, segment metrics, and retention summary."""
    cleaned = pd.read_csv(processed_dir / "cleaned_customers.csv")
    risk_scores = pd.read_csv(processed_dir / "customer_risk_scores.csv")
    segments = pd.read_csv(processed_dir / "segment_metrics.csv")
    summary = pd.read_csv(processed_dir / "retention_summary.csv")
    return cleaned, risk_scores, segments, summary


def compute_top_priority_segments(risk_scores: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """Rank active customer segments by monthly revenue exposure and high-risk volume."""
    active = risk_scores[risk_scores["is_active"]].copy()
    grouped = (
        active.groupby(["contract", "tenure_bucket", "payment_method"], dropna=False)
        .agg(
            active_customers=("customer_id", "count"),
            high_critical_customers=("risk_tier", lambda s: s.isin(["Critical", "High"]).sum()),
            total_monthly_charges=("monthly_revenue_proxy", "sum"),
            exposed_monthly_charges=(
                "monthly_revenue_proxy",
                lambda s: s[active.loc[s.index, "risk_tier"].isin(["Critical", "High"])].sum(),
            ),
            avg_risk_score=("risk_score", "mean"),
        )
        .reset_index()
    )
    grouped["segment_id"] = (
        grouped["contract"] + " | " + grouped["tenure_bucket"] + " | " + grouped["payment_method"]
    )
    grouped = grouped.sort_values(
        ["exposed_monthly_charges", "high_critical_customers"], ascending=[False, False]
    ).head(top_n)
    return grouped.round(2)


def compute_risk_validation(risk_scores: pd.DataFrame) -> pd.DataFrame:
    """Evaluate historical churn concentration across risk tiers (same-snapshot)."""
    grouped = (
        risk_scores.groupby("risk_tier", dropna=False)
        .agg(
            total_customers=("customer_id", "count"),
            churned_customers=("churn", lambda s: (s == "Yes").sum()),
            active_customers=("is_active", "sum"),
            monthly_charges_total=("monthly_revenue_proxy", "sum"),
        )
        .reset_index()
    )
    grouped["historical_churn_rate_pct"] = (
        (grouped["churned_customers"] / grouped["total_customers"]) * 100
    ).round(2)
    return grouped.sort_values("historical_churn_rate_pct", ascending=False)
