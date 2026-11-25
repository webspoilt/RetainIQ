"""Centralized configuration for RetainIQ."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXPORTS_DATA_DIR = DATA_DIR / "exports"
CONFIG_DIR = BASE_DIR / "config"

RAW_CSV_PATH = RAW_DATA_DIR / "Telco-Customer-Churn.csv"
DATASET_URL = "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv"
RISK_RULES_PATH = CONFIG_DIR / "risk_rules.yaml"

# Database configuration
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB", "retention_analytics")
POSTGRES_USER = os.getenv("POSTGRES_USER", "retainiq")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "retainiq_local_dev")

DATABASE_URL = (
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

# LLM configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "")


def ensure_directories() -> None:
    """Ensure required data directories exist."""
    for directory in (RAW_DATA_DIR, PROCESSED_DATA_DIR, EXPORTS_DATA_DIR):
        directory.mkdir(parents=True, exist_ok=True)
