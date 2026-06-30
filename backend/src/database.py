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
        rule_col_rows = list(result)
        rule_columns = [row[1] for row in rule_col_rows]
        if "delay_ms" in rule_columns and "delay_s" not in rule_columns:
            conn.execute(text("ALTER TABLE rules RENAME COLUMN delay_ms TO delay_s"))
            conn.commit()

        result = conn.execute(text("PRAGMA table_info(interception_logs)"))
        il_columns = [row[1] for row in result]
        if "method" not in il_columns:
            conn.execute(text("ALTER TABLE interception_logs ADD COLUMN method VARCHAR"))
            conn.commit()

        # Normalize mixed timestamp formats (T-separator vs space) to space format
        # so SQLite string comparisons work correctly across all records.
        for table, col in [("call_logs", "timestamp"), ("interception_logs", "timestamp"),
                           ("devices", "first_seen"), ("devices", "last_seen")]:
            conn.execute(text(f"""
                UPDATE {table}
                SET {col} = datetime({col})
                WHERE {col} LIKE '%T%'
            """))
        conn.commit()

        # Make rules.status_code nullable (SQLite requires full table recreation)
        result = conn.execute(text("PRAGMA table_info(rules)"))
        rules_notnull = {row[1]: row[3] for row in result}  # col_name -> notnull flag
        if rules_notnull.get("status_code", 0) == 1:
            existing_cols = list(rules_notnull.keys())
            cols_csv = ", ".join(existing_cols)
            conn.execute(text("ALTER TABLE rules RENAME TO rules_old"))
            conn.execute(text("""
                CREATE TABLE rules (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR NOT NULL,
                    url_pattern VARCHAR NOT NULL,
                    method VARCHAR,
                    status_code INTEGER,
                    delay_s INTEGER NOT NULL DEFAULT 0,
                    mode VARCHAR,
                    mock_data TEXT NOT NULL,
                    use_mock_backend BOOLEAN NOT NULL DEFAULT 1,
                    ai_prompt TEXT,
                    is_enabled BOOLEAN NOT NULL,
                    created_at DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP),
                    updated_at DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP),
                    created_by_key_id INTEGER REFERENCES api_keys(id)
                )
            """))
            conn.execute(text(f"INSERT INTO rules ({cols_csv}) SELECT {cols_csv} FROM rules_old"))
            conn.execute(text("DROP TABLE rules_old"))
            conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS uq_rules_name ON rules (name)"))
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
