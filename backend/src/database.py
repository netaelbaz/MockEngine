"""Database connection and session management for MockEngine."""

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./mockengine.db"

# Create engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite
)

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def run_migrations(engine):
    """Run lightweight column-level migrations for SQLite."""
    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA table_info(call_logs)"))
        columns = [row[1] for row in result]
        if "status_code" not in columns:
            conn.execute(text("ALTER TABLE call_logs ADD COLUMN status_code INTEGER"))
            conn.commit()

        result = conn.execute(text("PRAGMA table_info(rules)"))
        rule_columns = [row[1] for row in result]
        if "delay_ms" in rule_columns and "delay_s" not in rule_columns:
            conn.execute(text("ALTER TABLE rules RENAME COLUMN delay_ms TO delay_s"))
            conn.commit()


def get_db():
    """
    Dependency function to get database session.

    Yields database session and ensures it's closed after use.
    Used in FastAPI endpoints with Depends(get_db).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
