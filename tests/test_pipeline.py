"""Comprehensive unit, financial reconciliation, and resilience tests for RetainIQ."""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
import requests

from src.ai_summary import call_llm_provider, generate_offline_brief
from src.clean_transform import assign_tenure_bucket, build_segment_metrics, clean_and_transform
from src.config import RAW_CSV_PATH
from src.risk_scoring import build_retention_summary, load_risk_rules, score_customers


def _sample_raw_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "customerID": "C001",
                "gender": "Female",
                "SeniorCitizen": 0,
                "Partner": "No",
                "Dependents": "No",
                "tenure": 1,
                "PhoneService": "Yes",
                "MultipleLines": "No",
                "InternetService": "Fiber optic",
                "OnlineSecurity": "No",
                "OnlineBackup": "No",
                "DeviceProtection": "No",
                "TechSupport": "No",
                "StreamingTV": "Yes",
                "StreamingMovies": "No",
                "Contract": "Month-to-month",
                "PaperlessBilling": "Yes",
                "PaymentMethod": "Electronic check",
                "MonthlyCharges": 95.0,
                "TotalCharges": "95.0",
                "Churn": "No",
            },
            {
                "customerID": "C002",
                "gender": "Male",
                "SeniorCitizen": 0,
                "Partner": "Yes",
                "Dependents": "Yes",
                "tenure": 0,
                "PhoneService": "Yes",
                "MultipleLines": "No",
                "InternetService": "DSL",
                "OnlineSecurity": "Yes",
                "OnlineBackup": "Yes",
                "DeviceProtection": "Yes",
                "TechSupport": "Yes",
                "StreamingTV": "No",
                "StreamingMovies": "No",
                "Contract": "Two year",
                "PaperlessBilling": "No",
                "PaymentMethod": "Bank transfer (automatic)",
                "MonthlyCharges": 45.0,
                "TotalCharges": " ",
                "Churn": "No",
            },
            {
                "customerID": "C003",
                "gender": "Female",
                "SeniorCitizen": 1,
                "Partner": "No",
                "Dependents": "No",
                "tenure": 5,
                "PhoneService": "Yes",
                "MultipleLines": "No",
                "InternetService": "Fiber optic",
                "OnlineSecurity": "No",
                "OnlineBackup": "No",
                "DeviceProtection": "No",
                "TechSupport": "No",
                "StreamingTV": "No",
                "StreamingMovies": "No",
                "Contract": "Month-to-month",
                "PaperlessBilling": "Yes",
                "PaymentMethod": "Electronic check",
                "MonthlyCharges": 75.0,
                "TotalCharges": "375.0",
                "Churn": "Yes",
            },
        ]
    )


def test_tenure_buckets():
    assert assign_tenure_bucket(0) == "0-2 months"
    assert assign_tenure_bucket(2) == "0-2 months"
    assert assign_tenure_bucket(3) == "3-11 months"
    assert assign_tenure_bucket(11) == "3-11 months"
    assert assign_tenure_bucket(12) == "12+ months"


def test_clean_and_transform_idempotent():
    raw = _sample_raw_df()
    cleaned_1, report_1 = clean_and_transform(raw)
    cleaned_2, report_2 = clean_and_transform(raw)
    pd.testing.assert_frame_equal(cleaned_1, cleaned_2)
    assert report_1["validation_status"] == "PASS"
    assert report_1["imputed_value_count"] == 1
    assert report_1["rejected_record_count"] == 0


def test_financial_reconciliation_and_risk_tiers():
    cleaned, _ = clean_and_transform(_sample_raw_df())
    scored = score_customers(cleaned)
    summary = build_retention_summary(scored).set_index("metric")["value"]

    total_rev = summary["Monthly Charge Revenue Proxy ($)"]
    active_rev = summary["Active Monthly Charge Proxy ($)"]
    churned_rev = summary["Historical Churned Monthly Charges ($)"]
    assert abs(total_rev - (active_rev + churned_rev)) < 1e-2

    c001 = scored.loc[scored["customer_id"] == "C001"].iloc[0]
    assert c001["risk_tier"] == "Critical"
    assert c001["risk_score"] >= 70
    assert c001["retention_candidate"]

    c002 = scored.loc[scored["customer_id"] == "C002"].iloc[0]
    assert c002["risk_tier"] == "Low"
    assert c002["risk_score"] < 30

    c003 = scored.loc[scored["customer_id"] == "C003"].iloc[0]
    assert not c003["retention_candidate"]


def test_full_dataset_reconciliation_if_present():
    if not RAW_CSV_PATH.exists():
        pytest.skip("Raw CSV not downloaded")
    raw_df = pd.read_csv(RAW_CSV_PATH)
    cleaned, report = clean_and_transform(raw_df)
    assert len(cleaned) == 7043
    assert report["validation_status"] == "PASS"

    scored = score_customers(cleaned, load_risk_rules())
    summary = build_retention_summary(scored).set_index("metric")["value"]
    assert (
        abs(
            summary["Monthly Charge Revenue Proxy ($)"]
            - (
                summary["Active Monthly Charge Proxy ($)"]
                + summary["Historical Churned Monthly Charges ($)"]
            )
        )
        < 1e-2
    )

    segments = build_segment_metrics(cleaned)
    contract_segs = segments[segments["dimension"] == "Contract Type"]
    assert contract_segs["customer_count"].sum() == 7043


def test_offline_ai_brief_and_timeout_fallback():
    seg = {
        "segment_id": "Month-to-month | 0-2 months | Electronic check",
        "active_customers": 100,
        "high_critical_customers": 80,
        "exposed_monthly_charges": 5000.0,
        "avg_risk_score": 72.5,
    }
    brief = generate_offline_brief(seg)
    assert "100 active customers" in brief
    assert "$5,000.00" in brief

    with (
        patch("src.ai_summary.LLM_PROVIDER", "openai"),
        patch("src.ai_summary.LLM_API_KEY", "test-key"),
        patch("src.ai_summary.requests.post", side_effect=requests.Timeout("timeout")),
    ):
        text, provider, _ = call_llm_provider(seg, timeout=1, max_retries=0)
        assert provider == "mock-fallback"
        assert "100 active customers" in text

    bad_resp = MagicMock()
    bad_resp.status_code = 200
    bad_resp.json.return_value = {"unexpected": "shape"}
    with (
        patch("src.ai_summary.LLM_PROVIDER", "openai"),
        patch("src.ai_summary.LLM_API_KEY", "test-key"),
        patch("src.ai_summary.requests.post", return_value=bad_resp),
    ):
        text, provider, _ = call_llm_provider(seg, timeout=1, max_retries=0)
        assert provider == "mock-fallback"
