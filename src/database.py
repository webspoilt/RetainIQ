"""Database connection and helper utilities."""

import logging
from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from src.config import DATABASE_URL

logger = logging.getLogger(__name__)


def get_engine(database_url: str = DATABASE_URL) -> Engine:
    """Create a SQLAlchemy engine."""
    return create_engine(database_url, pool_pre_ping=True)


@contextmanager
def get_connection(database_url: str = DATABASE_URL) -> Iterator:
    """Context manager for database connections."""
    engine = get_engine(database_url)
    with engine.connect() as conn:
        yield conn


def test_connection(database_url: str = DATABASE_URL) -> bool:
    """Verify database connectivity."""
    try:
        with get_connection(database_url) as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.warning("Database connection unavailable: %s", exc)
        return False
