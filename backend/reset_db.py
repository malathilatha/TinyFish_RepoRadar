"""
Resets the database completely - clears all watchlist and signals.
Run: python reset_db.py
"""
import sqlite3
import os

DB_PATH = "reporadar_watchlist.db"

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print("✅ Database deleted")

# Recreate fresh
conn = sqlite3.connect(DB_PATH)
conn.execute("""
    CREATE TABLE watchlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner TEXT, repo TEXT, email TEXT,
        auto_tweet INTEGER DEFAULT 0,
        created_at TEXT, last_checked TEXT,
        last_snapshot TEXT, signals_fired TEXT
    )
""")
conn.execute("""
    CREATE TABLE signal_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner TEXT, repo TEXT,
        signal_key TEXT, severity TEXT,
        title TEXT, detail TEXT, metric TEXT,
        action TEXT, post_draft TEXT,
        emoji TEXT, auto_posted INTEGER DEFAULT 0,
        detected_at TEXT
    )
""")
conn.commit()
conn.close()
print("✅ Fresh database created")
print("→ Restart uvicorn now")