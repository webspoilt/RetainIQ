"""Data cleaning, validation, feature engineering, and deterministic exports."""

import json
import logging
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd

from src.config import PROCESSED_DATA_DIR, RAW_CSV_PATH, ensure_directories

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

VALID_CHURN = {"Yes", "No"}
VALID_CONTRACTS = {"Month-to-month", "One year", "Two year"}
VALID_PAYMENTS = {
    "Electronic check",
    "Mailed check",
    "Bank transfer (automatic)",
    "Credit card (automatic)",
}


def assign_tenure_bucket(tenure: int) -> str:
    """Assign mutually exclusive tenure cohorts: 0-2 months, 3-11 months, 12+ months."""
    if tenure <= 2:
        return "0-2 months"
    if tenure <= 11:
        return "3-11 months"
    return "12+ months"


def clean_and_transform(raw_df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Clean raw Telco data, engineer features, and return (cleaned_df, quality_report)."""
    original_row_count = len(raw_df)
    df = raw_df.copy()

    # Standardize column naming to snake_case
    df = df.rename(
        columns={
            "customerID": "customer_id",
            "SeniorCitizen": "senior_citizen",
            "Partner": "partner",
            "Dependents": "dependents",
            "PhoneService": "phone_service",
            "MultipleLines": "multiple_lines",
            "InternetService": "internet_service",
            "OnlineSecurity": "online_security",
            "OnlineBackup": "online_backup",
            "DeviceProtection": "device_protection",
            "TechSupport": "tech_support",
            "StreamingTV": "streaming_tv",
            "StreamingMovies": "streaming_movies",
            "Contract": "contract",
            "PaperlessBilling": "paperless_billing",
            "PaymentMethod": "payment_method",
            "MonthlyCharges": "monthly_charges",
            "TotalCharges": "total_charges",
            "Churn": "churn",
        }
    )

    # Strip whitespace from string columns
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str).str.strip()

    # Detect duplicates
    duplicate_count = int(df.duplicated(subset=["customer_id"]).sum())
    if duplicate_count > 0:
        df = df.drop_duplicates(subset=["customer_id"], keep="first")

    # Convert TotalCharges to numeric; blank strings become NaN
    df["total_charges_raw"] = df["total_charges"]
    df["total_charges"] = pd.to_numeric(df["total_charges"], errors="coerce")
    blank_total_charges = int(df["total_charges"].isna().sum())

    # Business rule: for tenure == 0 with blank TotalCharges, impute 0.0; otherwise monthly_charges * tenure
    zero_tenure_mask = df["total_charges"].isna() & (df["tenure"] == 0)
    df.loc[zero_tenure_mask, "total_charges"] = 0.0
    remaining_na_mask = df["total_charges"].isna()
    df.loc[remaining_na_mask, "total_charges"] = (
        df.loc[remaining_na_mask, "monthly_charges"] * df.loc[remaining_na_mask, "tenure"]
    )

    # Validate ranges and categories
    invalid_tenure = int((df["tenure"] < 0).sum())
    invalid_monthly = int((df["monthly_charges"] < 0).sum())
    invalid_total = int((df["total_charges"] < 0).sum())
    invalid_churn = int((~df["churn"].isin(VALID_CHURN)).sum())
    invalid_contract = int((~df["contract"].isin(VALID_CONTRACTS)).sum())
    invalid_payment = int((~df["payment_method"].isin(VALID_PAYMENTS)).sum())

    invalid_value_count = (
        invalid_tenure
        + invalid_monthly
        + invalid_total
        + invalid_churn
        + invalid_contract
        + invalid_payment
    )

    # Feature engineering
    df["tenure_bucket"] = df["tenure"].apply(assign_tenure_bucket)
    df["monthly_revenue_proxy"] = df["monthly_charges"].astype(float)
    df["total_revenue"] = df["total_charges"].astype(float)
    df["churn_flag"] = (df["churn"] == "Yes").astype(int)
    df["is_active"] = (df["churn"] == "No").astype(bool)
    df["contract_category"] = np.where(
        df["contract"] == "Month-to-month", "Short-term", "Long-term"
    )
    df["payment_category"] = np.where(
        df["payment_method"].str.contains("automatic", case=False, na=False),
        "Automatic",
        "Manual",
    )
    df["is_month_to_month"] = (df["contract"] == "Month-to-month").astype(bool)
    df["has_tech_support"] = (df["tech_support"] == "Yes").astype(bool)
    df["has_online_security"] = (df["online_security"] == "Yes").astype(bool)

    active_75th = float(df.loc[df["is_active"], "monthly_charges"].quantile(0.75))
    df["high_monthly_charge_flag"] = (df["monthly_charges"] > active_75th).astype(bool)

    # Deterministic ordering
    df = df.sort_values("customer_id").reset_index(drop=True)

    quality_report = {
        "source_record_count": original_row_count,
        "loaded_record_count": len(df),
        "rejected_record_count": 0,
        "original_row_count": original_row_count,
        "final_row_count": len(df),
        "duplicate_count": duplicate_count,
        "missing_value_count": blank_total_charges,
        "imputed_value_count": int(zero_tenure_mask.sum() + remaining_na_mask.sum()),
        "invalid_value_count": invalid_value_count,
        "validation_errors": [],
        "transformation_timestamp": datetime.now(UTC).isoformat(),
        "active_75th_percentile_monthly_charges": round(active_75th, 2),
        "transformation_summary": {
            "total_charges_blank_imputed_zero_tenure": int(zero_tenure_mask.sum()),
            "total_charges_blank_imputed_other": int(remaining_na_mask.sum()),
            "tenure_buckets": ["0-2 months", "3-11 months", "12+ months"],
        },
        "validation_status": "PASS"
        if invalid_value_count == 0 and duplicate_count == 0
        else "WARN",
    }

    return df, quality_report


def build_segment_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Compute weighted segment metrics across key business dimensions."""
    dimensions = [
        ("contract", "Contract Type"),
        ("tenure_bucket", "Tenure Bucket"),
        ("payment_method", "Payment Method"),
        ("internet_service", "Internet Service"),
        ("tech_support", "Tech Support"),
        ("online_security", "Online Security"),
    ]
    rows = []
    for col, dim_label in dimensions:
        grouped = (
            df.groupby(col, dropna=False)
            .agg(
                customer_count=("customer_id", "count"),
                churned_count=("churn_flag", "sum"),
                active_count=("is_active", "sum"),
                avg_monthly_charges=("monthly_revenue_proxy", "mean"),
                avg_tenure=("tenure", "mean"),
                total_monthly_charges=("monthly_revenue_proxy", "sum"),
                historical_churned_monthly_charges=(
                    "monthly_revenue_proxy",
                    lambda s: s[df.loc[s.index, "churn_flag"] == 1].sum(),
                ),
            )
            .reset_index()
        )
        for _, r in grouped.iterrows():
            cust_cnt = int(r["customer_count"])
            churn_cnt = int(r["churned_count"])
            rows.append(
                {
                    "dimension": dim_label,
                    "segment": str(r[col]),
                    "customer_count": cust_cnt,
                    "active_count": int(r["active_count"]),
                    "churned_count": churn_cnt,
                    "churn_rate_pct": round((churn_cnt / cust_cnt) * 100, 2) if cust_cnt else 0.0,
                    "avg_monthly_charges": round(float(r["avg_monthly_charges"]), 2),
                    "avg_tenure_months": round(float(r["avg_tenure"]), 2),
                    "total_monthly_charges": round(float(r["total_monthly_charges"]), 2),
                    "historical_churned_monthly_charges": round(
                        float(r["historical_churned_monthly_charges"]), 2
                    ),
                }
            )
    return pd.DataFrame(rows)


def run_cleaning_pipeline(
    raw_path: Path = RAW_CSV_PATH, output_dir: Path = PROCESSED_DATA_DIR
) -> tuple[pd.DataFrame, dict]:
    """Run cleaning, feature engineering, and export processed artifacts."""
    ensure_directories()
    raw_df = pd.read_csv(raw_path)
    cleaned_df, quality_report = clean_and_transform(raw_df)
    segment_df = build_segment_metrics(cleaned_df)

    cleaned_df.to_csv(output_dir / "cleaned_customers.csv", index=False)
    segment_df.to_csv(output_dir / "segment_metrics.csv", index=False)
    (output_dir / "data_quality_report.json").write_text(json.dumps(quality_report, indent=2))

    logger.info(
        "Cleaning complete: %d rows, status=%s",
        len(cleaned_df),
        quality_report["validation_status"],
    )
    return cleaned_df, quality_report


if __name__ == "__main__":
    run_cleaning_pipeline()
