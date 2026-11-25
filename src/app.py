"""RetainIQ: Interactive Customer Retention & Churn Cohort Analytics Platform."""

import json

import pandas as pd
import plotly.express as px
import streamlit as st

from src.analytics import (
    compute_risk_validation,
    compute_top_priority_segments,
    load_processed_data,
)
from src.config import PROCESSED_DATA_DIR

st.set_page_config(
    page_title="RetainIQ | Customer Retention Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def get_data():
    cleaned, risk_scores, segments, summary = load_processed_data()
    briefs_path = PROCESSED_DATA_DIR / "ai_retention_briefs.csv"
    briefs = pd.read_csv(briefs_path) if briefs_path.exists() else pd.DataFrame()
    dq_path = PROCESSED_DATA_DIR / "data_quality_report.json"
    dq = json.loads(dq_path.read_text()) if dq_path.exists() else {}
    return cleaned, risk_scores, segments, summary, briefs, dq


def main():
    cleaned, risk_scores, segments, summary, briefs, dq = get_data()

    st.sidebar.title("RetainIQ")
    st.sidebar.caption("Customer Retention & Churn Cohort Analytics")
    page = st.sidebar.radio(
        "Navigation",
        [
            "Executive Overview",
            "Retention Action Center",
            "Churn Drivers & Cohorts",
            "Data Quality",
            "Methodology & Limitations",
        ],
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("Global Filters")
    contract_filter = st.sidebar.multiselect(
        "Contract Type",
        options=sorted(risk_scores["contract"].unique()),
        default=sorted(risk_scores["contract"].unique()),
    )
    tenure_filter = st.sidebar.multiselect(
        "Tenure Bucket",
        options=["0-2 months", "3-11 months", "12+ months"],
        default=["0-2 months", "3-11 months", "12+ months"],
    )
    payment_filter = st.sidebar.multiselect(
        "Payment Method",
        options=sorted(risk_scores["payment_method"].unique()),
        default=sorted(risk_scores["payment_method"].unique()),
    )

    filtered = risk_scores[
        risk_scores["contract"].isin(contract_filter)
        & risk_scores["tenure_bucket"].isin(tenure_filter)
        & risk_scores["payment_method"].isin(payment_filter)
    ]

    if filtered.empty:
        st.warning(
            "No customer records match the selected sidebar filters. Please broaden your selection."
        )
        return

    if page == "Executive Overview":
        st.title("Executive Overview")
        st.caption(
            "Point-in-time snapshot analytics. Revenue exposure is a monthly charge proxy, not a financial forecast."
        )

        total_cust = len(filtered)
        active_df = filtered[filtered["is_active"]]
        churned_df = filtered[~filtered["is_active"]]
        high_risk_active = active_df[active_df["risk_tier"].isin(["Critical", "High"])]
        churn_rate = (len(churned_df) / total_cust * 100) if total_cust else 0.0
        exposed_rev = float(high_risk_active["monthly_revenue_proxy"].sum())

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total Customers", f"{total_cust:,}")
        c2.metric("Historical Churn Rate", f"{churn_rate:.2f}%")
        c3.metric("Active Customers", f"{len(active_df):,}")
        c4.metric("Monthly Charges Exposed", f"${exposed_rev:,.2f}")
        c5.metric("High/Critical Active", f"{len(high_risk_active):,}")

        col1, col2 = st.columns(2)
        with col1:
            contract_agg = filtered.groupby("contract", as_index=False).agg(
                customers=("customer_id", "count"),
                churned=("churn", lambda s: (s == "Yes").sum()),
            )
            contract_agg["churn_rate_pct"] = (
                contract_agg["churned"] / contract_agg["customers"] * 100
            ).round(2)
            fig = px.bar(
                contract_agg,
                x="contract",
                y="churn_rate_pct",
                title="Historical Churn Rate by Contract Type (%)",
                text="churn_rate_pct",
                color="contract",
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            tenure_agg = filtered.groupby("tenure_bucket", as_index=False).agg(
                customers=("customer_id", "count"),
                churned=("churn", lambda s: (s == "Yes").sum()),
            )
            tenure_agg["churn_rate_pct"] = (
                tenure_agg["churned"] / tenure_agg["customers"] * 100
            ).round(2)
            fig2 = px.bar(
                tenure_agg,
                x="tenure_bucket",
                y="churn_rate_pct",
                title="Historical Churn Rate by Tenure Cohort (%)",
                text="churn_rate_pct",
                category_orders={"tenure_bucket": ["0-2 months", "3-11 months", "12+ months"]},
            )
            st.plotly_chart(fig2, use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            tier_agg = (
                active_df.groupby("risk_tier", as_index=False)["monthly_revenue_proxy"]
                .sum()
                .rename(columns={"monthly_revenue_proxy": "exposed_monthly_charges"})
            )
            fig3 = px.bar(
                tier_agg,
                x="risk_tier",
                y="exposed_monthly_charges",
                title="Active Monthly Revenue Proxy by Risk Tier ($)",
                category_orders={"risk_tier": ["Critical", "High", "Medium", "Low"]},
                color="risk_tier",
            )
            st.plotly_chart(fig3, use_container_width=True)

        with col4:
            pay_agg = filtered.groupby("payment_method", as_index=False).agg(
                customers=("customer_id", "count"),
                churned=("churn", lambda s: (s == "Yes").sum()),
            )
            pay_agg["churn_rate_pct"] = (pay_agg["churned"] / pay_agg["customers"] * 100).round(2)
            fig4 = px.bar(
                pay_agg,
                x="churn_rate_pct",
                y="payment_method",
                orientation="h",
                title="Historical Churn Rate by Payment Method (%)",
                text="churn_rate_pct",
            )
            st.plotly_chart(fig4, use_container_width=True)

    elif page == "Retention Action Center":
        st.title("Customer Retention Action Center")
        active_candidates = filtered[filtered["retention_candidate"]].copy()

        tier_sel = st.multiselect(
            "Filter by Risk Tier",
            options=["Critical", "High", "Medium", "Low"],
            default=["Critical", "High"],
        )
        search_id = st.text_input("Search Customer ID")

        action_df = active_candidates[active_candidates["risk_tier"].isin(tier_sel)]
        if search_id:
            action_df = action_df[
                action_df["customer_id"].str.contains(search_id.strip(), case=False, na=False)
            ]

        action_df = action_df.sort_values(
            ["risk_score", "monthly_revenue_proxy"], ascending=[False, False]
        )

        st.subheader("Prioritized Active Customers")
        st.dataframe(
            action_df[
                [
                    "customer_id",
                    "risk_score",
                    "risk_tier",
                    "contract",
                    "tenure",
                    "payment_method",
                    "monthly_revenue_proxy",
                    "contributing_risk_factors",
                    "retention_priority",
                    "recommended_action",
                ]
            ],
            use_container_width=True,
            height=400,
        )

        st.download_button(
            "Download Action List CSV",
            data=action_df.to_csv(index=False).encode("utf-8"),
            file_name="retainiq_action_list.csv",
            mime="text/csv",
        )

        if not briefs.empty:
            st.subheader("AI-Generated Segment Retention Briefs (Decision Support)")
            st.caption(
                "Generated from verified segment metrics. Treat as decision support, not verified fact."
            )
            for _, b in briefs.iterrows():
                with st.expander(
                    f"{b['segment_id']} — ${b['exposed_monthly_charges']:,.2f} exposed ({b['high_critical_customers']} High/Critical)"
                ):
                    st.write(b["generated_brief"])
                    st.caption(
                        f"Provider: {b['provider']} | Model: {b['model']} | Prompt: {b['prompt_version']}"
                    )

    elif page == "Churn Drivers & Cohorts":
        st.title("Churn Drivers & Tenure Cohort Analysis")
        st.dataframe(segments, use_container_width=True)

        st.subheader("Top Priority Active Segments by Revenue Exposure")
        top_seg = compute_top_priority_segments(filtered, top_n=10)
        st.dataframe(top_seg, use_container_width=True)

        st.subheader("Same-Snapshot Risk Tier Validation")
        val_df = compute_risk_validation(filtered)
        st.dataframe(val_df, use_container_width=True)

    elif page == "Data Quality":
        st.title("Data Quality & Pipeline Validation")
        if dq:
            st.json(dq)
        else:
            st.info("Run `python -m src.clean_transform` to generate data_quality_report.json.")

    elif page == "Methodology & Limitations":
        st.title("Methodology & Analytical Limitations")
        st.markdown(
            """
            - **Dataset:** IBM Telco Customer Churn (7,043 customer snapshot records).
            - **Tenure Cohorts:** `0-2 months`, `3-11 months`, `12+ months` (used instead of acquisition cohorts because signup dates are unavailable).
            - **Revenue Proxy:** `MonthlyCharges` is used as a monthly revenue proxy, not verified SaaS accounting MRR.
            - **Risk Scoring:** Transparent, configurable rule-based heuristic (max 90 points) in `config/risk_rules.yaml`. Not a time-validated ML probability.
            - **AI Briefs:** Grounded strictly in aggregated segment metrics; runs in deterministic offline mode when no API key is configured.
            """
        )


if __name__ == "__main__":
    main()
