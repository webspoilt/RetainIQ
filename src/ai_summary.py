"""Grounded AI retention brief generator with provider abstraction and offline fallback."""

import json
import logging
import time
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
import requests

from src.analytics import compute_top_priority_segments
from src.config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, LLM_PROVIDER, PROCESSED_DATA_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

PROMPT_VERSION = "v1.0"


def generate_offline_brief(segment: dict) -> str:
    """Generate a deterministic, grounded 2-sentence retention brief without an LLM API key."""
    seg_id = segment["segment_id"]
    active_cnt = int(segment["active_customers"])
    high_cnt = int(segment["high_critical_customers"])
    exposed = float(segment["exposed_monthly_charges"])
    avg_score = float(segment["avg_risk_score"])

    return (
        f"Segment '{seg_id}' has {active_cnt} active customers, of whom {high_cnt} are classified "
        f"as High/Critical risk (avg score {avg_score:.1f}) representing ${exposed:,.2f} in exposed monthly charges. "
        f"Prioritize proactive outreach, evaluate contract-upgrade incentives, and review payment or support-bundle adoption."
    )


def call_llm_provider(
    segment: dict, timeout: int = 15, max_retries: int = 2
) -> tuple[str, str, str]:
    """Call configured LLM provider with retry/timeout, falling back to offline mode on failure."""
    if LLM_PROVIDER == "mock" or not LLM_API_KEY:
        return generate_offline_brief(segment), "mock", "deterministic-template-v1"

    base_url = LLM_BASE_URL.rstrip("/") if LLM_BASE_URL else "https://api.openai.com/v1"
    url = f"{base_url}/chat/completions"
    headers = {"Authorization": f"Bearer {LLM_API_KEY}", "Content-Type": "application/json"}
    prompt = (
        "You are a senior retention analyst. Write exactly 2 concise sentences summarizing this "
        "customer segment using ONLY the provided verified metrics. Do not invent numbers or claim causality.\n"
        f"Metrics: {json.dumps(segment)}"
    )
    payload = {
        "model": LLM_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 180,
        "temperature": 0.2,
    }

    for attempt in range(max_retries + 1):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
            if resp.status_code == 429 and attempt < max_retries:
                time.sleep(2**attempt)
                continue
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"].strip()
            if content:
                return content, LLM_PROVIDER, LLM_MODEL
        except Exception as exc:
            logger.warning("LLM call failed (attempt %d): %s", attempt + 1, exc)
            if attempt < max_retries:
                time.sleep(1)

    logger.info("Falling back to offline deterministic brief for %s", segment["segment_id"])
    return generate_offline_brief(segment), "mock-fallback", "deterministic-template-v1"


def generate_and_save_briefs(
    processed_dir: Path = PROCESSED_DATA_DIR, top_n: int = 5
) -> pd.DataFrame:
    """Generate retention briefs for top priority segments and save to processed artifacts."""
    risk_scores = pd.read_csv(processed_dir / "customer_risk_scores.csv")
    top_segments = compute_top_priority_segments(risk_scores, top_n=top_n)

    briefs = []
    for _, row in top_segments.iterrows():
        seg_dict = row.to_dict()
        text, provider, model = call_llm_provider(seg_dict)
        briefs.append(
            {
                "segment_id": seg_dict["segment_id"],
                "active_customers": int(seg_dict["active_customers"]),
                "high_critical_customers": int(seg_dict["high_critical_customers"]),
                "exposed_monthly_charges": float(seg_dict["exposed_monthly_charges"]),
                "generated_brief": text,
                "provider": provider,
                "model": model,
                "prompt_version": PROMPT_VERSION,
                "generated_at": datetime.now(UTC).isoformat(),
            }
        )

    briefs_df = pd.DataFrame(briefs)
    briefs_df.to_csv(processed_dir / "ai_retention_briefs.csv", index=False)
    logger.info("Generated %d retention briefs.", len(briefs_df))
    return briefs_df


if __name__ == "__main__":
    generate_and_save_briefs()
