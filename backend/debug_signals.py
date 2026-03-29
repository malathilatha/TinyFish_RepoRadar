"""
Run this to debug signal issues completely.
Usage: python debug_signals.py
"""
import sqlite3
import json
import os
from datetime import datetime

DB_PATH = "reporadar_watchlist.db"

print("=" * 60)
print("REPORADAR SIGNAL DEBUG TOOL")
print("=" * 60)

# Check 1: Database exists
if not os.path.exists(DB_PATH):
    print(f"❌ DATABASE NOT FOUND: {DB_PATH}")
    print("Creating it now...")
else:
    print(f"✅ Database found: {DB_PATH}")

# Check 2: Connect and inspect tables
try:
    conn = sqlite3.connect(DB_PATH)
    
    # List all tables
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    print(f"\n📋 Tables found: {[t[0] for t in tables]}")
    
    # Check watchlist table
    if ('watchlist',) in tables:
        rows = conn.execute("SELECT * FROM watchlist").fetchall()
        print(f"\n👁 Watchlist entries: {len(rows)}")
        for r in rows:
            print(f"  ID:{r[0]} | {r[1]}/{r[2]} | email:{r[3]} | last_checked:{r[5]}")
    else:
        print("❌ watchlist table missing!")
        print("Creating watchlist table...")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner TEXT, repo TEXT, email TEXT,
                auto_tweet INTEGER DEFAULT 0,
                created_at TEXT, last_checked TEXT,
                last_snapshot TEXT, signals_fired TEXT
            )
        """)
        conn.commit()
        print("✅ watchlist table created")

    # Check signal_log table
    if ('signal_log',) in tables:
        cols = [c[1] for c in conn.execute("PRAGMA table_info(signal_log)").fetchall()]
        print(f"\n🚨 signal_log columns: {cols}")
        
        count = conn.execute("SELECT COUNT(*) FROM signal_log").fetchone()[0]
        print(f"🚨 Total signals in DB: {count}")
        
        if count > 0:
            rows = conn.execute("SELECT * FROM signal_log ORDER BY detected_at DESC LIMIT 5").fetchall()
            print("\nLatest signals:")
            for r in rows:
                print(f"  {r}")
        else:
            print("❌ No signals in database!")
            print("\nInserting demo signals now...")
            
            now = datetime.now().isoformat()
            conn.execute("""
                INSERT INTO signal_log 
                (owner,repo,signal_key,severity,title,detail,metric,action,post_draft,emoji,auto_posted,detected_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """, ("apache","airflow","bug_wave","critical",
                  "Bug Wave Detected",
                  "Issues spiked 240% in apache/airflow over 48 hours",
                  "+42 new issues opened",
                  "Acknowledge publicly within 2 hours.",
                  "We're aware of recent Airflow issues. Team is investigating. #opensource #bugfix",
                  "🚨", 0, now))
            
            conn.execute("""
                INSERT INTO signal_log 
                (owner,repo,signal_key,severity,title,detail,metric,action,post_draft,emoji,auto_posted,detected_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """, ("apache","airflow","viral_moment","opportunity",
                  "Viral Moment Detected",
                  "apache/airflow trending — stars up 23% in 24 hours",
                  "+1,200 stars gained today",
                  "Post NOW while momentum is high.",
                  "Apache Airflow is trending! 44K+ stars. Here's why data engineers love it. #DataEngineering #opensource",
                  "🚀", 0, now))
            
            conn.commit()
            print("✅ Demo signals inserted!")
    else:
        print("❌ signal_log table missing!")
        print("Creating signal_log table...")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS signal_log (
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
        
        now = datetime.now().isoformat()
        conn.execute("""
            INSERT INTO signal_log 
            (owner,repo,signal_key,severity,title,detail,metric,action,post_draft,emoji,auto_posted,detected_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, ("apache","airflow","bug_wave","critical",
              "Bug Wave Detected",
              "Issues spiked 240% in apache/airflow over 48 hours",
              "+42 new issues opened",
              "Acknowledge publicly within 2 hours.",
              "We're aware of recent Airflow issues. Team is investigating. #opensource #bugfix",
              "🚨", 0, now))
        
        conn.execute("""
            INSERT INTO signal_log 
            (owner,repo,signal_key,severity,title,detail,metric,action,post_draft,emoji,auto_posted,detected_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, ("apache","airflow","viral_moment","opportunity",
              "Viral Moment Detected",
              "apache/airflow trending — stars up 23% in 24 hours",
              "+1,200 stars gained today",
              "Post NOW while momentum is high.",
              "Apache Airflow is trending! 44K+ stars. Here's why data engineers love it. #DataEngineering #opensource",
              "🚀", 0, now))
        
        conn.commit()
        print("✅ signal_log table created and signals inserted!")

    conn.close()
    print("\n" + "=" * 60)
    print("✅ Debug complete! Now check /watchlist/signals API:")
    print("curl -UseBasicParsing http://localhost:8000/watchlist/signals")
    print("=" * 60)

except Exception as e:
    print(f"❌ Database error: {e}")
    import traceback
    traceback.print_exc()