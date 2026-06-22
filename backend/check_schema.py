#!/usr/bin/env python3
"""Check database schema."""

import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'mockengine.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Current database schema for 'rules' table:")
cursor.execute("PRAGMA table_info(rules)")
columns = cursor.fetchall()

for col in columns:
    print(f"  {col[1]:20} {col[2]:15} NOT NULL: {col[3] == 0}")

conn.close()
