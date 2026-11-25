"""Idempotent dataset ingestion for RetainIQ."""

import hashlib
import logging
from pathlib import Path

import pandas as pd
import requests
from sqlalchemy import text

from src.config import DATASET_URL, RAW_CSV_PATH, ensure_directories
from src.database import get_engine, test_connection

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def compute_sha256(file_path: Path) -> str:
    """Compute SHA-256 checksum of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def download_dataset(url: str = DATASET_URL, dest_path: Path = RAW_CSV_PATH) -> Path:
    """Download the raw dataset if not already present locally."""
    ensure_directories()
    if dest_path.exists() and dest_path.stat().st_size > 0:
        logger.info("Raw dataset already exists at %s", dest_path)
        return dest_path

    logger.info("Downloading dataset from %s", url)
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        dest_path.write_bytes(response.content)
        logger.info("Saved raw dataset (%d bytes) to %s", len(response.content), dest_path)
        return dest_path
    except requests.RequestException as exc:
        raise RuntimeError(f"Failed to download dataset from {url}: {exc}") from exc


def load_raw_to_postgres(csv_path: Path = RAW_CSV_PATH) -> dict:
    """Load raw CSV into PostgreSQL raw.telco_customers idempotently."""
    if not csv_path.exists():
        raise FileNotFoundError(f"Source file not found: {csv_path}")

    checksum = compute_sha256(csv_path)
    df = pd.read_csv(csv_path)

    if df.empty:
        raise ValueError("Source CSV is empty.")

    if not test_connection():
        logger.warning("PostgreSQL is not reachable. Skipping database load; local CSV is ready.")
        return {
            "status": "skipped_db_offline",
            "checksum": checksum,
            "row_count": len(df),
            "path": str(csv_path),
        }

    engine = get_engine()
    with engine.begin() as conn:
        existing = conn.execute(
            text(
                "SELECT ingestion_id FROM audit.ingestion_log "
                "WHERE file_checksum = :checksum AND status = 'success' LIMIT 1"
            ),
            {"checksum": checksum},
        ).fetchone()

        if existing:
            logger.info(
                "Dataset with checksum %s already ingested. Skipping duplicate load.", checksum
            )
            return {
                "status": "already_ingested",
                "checksum": checksum,
                "row_count": len(df),
            }

        db_df = df.rename(
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

        conn.execute(text("TRUNCATE TABLE raw.telco_customers"))
        db_df.to_sql("telco_customers", conn, schema="raw", if_exists="append", index=False)

        conn.execute(
            text(
                "INSERT INTO audit.ingestion_log (source_name, file_checksum, row_count, status) "
                "VALUES (:source_name, :checksum, :row_count, 'success')"
            ),
            {"source_name": csv_path.name, "checksum": checksum, "row_count": len(db_df)},
        )

    logger.info("Successfully ingested %d rows into raw.telco_customers.", len(df))
    return {"status": "success", "checksum": checksum, "row_count": len(df)}


def run_ingestion() -> dict:
    """Execute full ingestion step."""
    csv_path = download_dataset()
    return load_raw_to_postgres(csv_path)


if __name__ == "__main__":
    result = run_ingestion()
    logger.info("Ingestion result: %s", result)
