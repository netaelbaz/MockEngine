#!/usr/bin/env python3
"""Check detailed database schema."""

import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'mockengine.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Detailed schema for 'rules' table:")
cursor.execute("PRAGMA table_info(rules)")
columns = cursor.fetchall()

print("Column Name          | Type           | NotNull | PrimaryKey")
print("-" * 65)

for col in columns:
    col_id, name, type_name, notnull, default_val, is_pk = col
    print(f"{name:20} | {type_name:14} | {str(notnull):8} | {str(is_pk):10}")

print("\nNotNull meaning: 1 = has NOT NULL constraint, 0 = nullable")

# Also check the actual CREATE statement
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='rules'")
create_sql = cursor.fetchone()
if create_sql:
    print("\nActual CREATE TABLE statement:")
    print(create_sql[0])

conn.close()
