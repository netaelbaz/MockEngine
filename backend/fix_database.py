#!/usr/bin/env python3
"""Fix database schema to make mode column nullable."""

import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'mockengine.db')

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

print(f"Fixing database at {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if mode column exists and is NOT NULL
    cursor.execute("PRAGMA table_info(rules)")
    columns = cursor.fetchall()

    mode_column = None
    for col in columns:
        if col[1] == 'mode':
            mode_column = col
            break

    if mode_column is None:
        print("Mode column doesn't exist - nothing to fix")
    elif mode_column[3] == 1:  # 1 means NOT NULL
        print("Mode column is NOT NULL - making it nullable...")

        # SQLite doesn't support ALTER COLUMN directly, need to recreate table
        cursor.execute("""
            CREATE TABLE rules_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR NOT NULL,
                url_pattern VARCHAR NOT NULL,
                status_code INTEGER NOT NULL,
                delay_ms INTEGER NOT NULL DEFAULT 0,
                mode VARCHAR,
                mock_data TEXT NOT NULL,
                is_enabled BOOLEAN NOT NULL DEFAULT 1,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                created_by_key_id INTEGER,
                FOREIGN KEY(created_by_key_id) REFERENCES api_keys (id)
            )
        """)

        # Copy data
        cursor.execute("""
            INSERT INTO rules_new (id, name, url_pattern, status_code, delay_ms, mode, mock_data, is_enabled, created_at, updated_at, created_by_key_id)
            SELECT id, name, url_pattern, status_code, delay_ms, mode, mock_data, is_enabled, created_at, updated_at, created_by_key_id
            FROM rules
        """)

        # Drop old table and rename new one
        cursor.execute("DROP TABLE rules")
        cursor.execute("ALTER TABLE rules_new RENAME TO rules")

        # Recreate indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_rules_id ON rules (id)")

        conn.commit()
        print("SUCCESS: Database schema updated successfully!")
    else:
        print("Mode column is already nullable - nothing to do")

except Exception as e:
    print(f"ERROR: {e}")
    conn.rollback()
finally:
    conn.close()
