"""
Run this ONCE to manually inject demo signals into the database.
Usage: python fix_signals.py
"""
import sqlite3
import json
from datetime import datetime

DB_PATH = "reporadar_watchlist.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
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
    conn.close()

def inject_signals():
    init_db()
    now = datetime.now().isoformat()
    
    signals = [
        {
            "owner": "apache", "repo": "airflow",
            "signal_key": "bug_wave",
            "severity": "critical",
            "emoji": "🚨",
            "title": "Bug Wave Detected",
            "detail": "Issues spiked 240% in apache/airflow over the past 48 hours",
            "metric": "+42 new issues opened",
            "action": "Acknowledge publicly within 2 hours to prevent community backlash.",
            "post_draft": "We're aware of the recent issues in Airflow. Our team is actively investigating. Updates to follow. #opensource #bugfix #apache",
            "detected_at": now,
        },
        {
            "owner": "apache", "repo": "airflow",
            "signal_key": "viral_moment",
            "severity": "opportunity",
            "emoji": "🚀",
            "title": "Viral Moment Detected",
            "detail": "apache/airflow is trending — stars up 23% in the last 24 hours",
            "metric": "+1,200 stars gained today",
            "action": "Post NOW while momentum is high. Strike while hot.",
            "post_draft": "Apache Airflow is trending on GitHub today! 44K+ stars and growing. Here's why thousands of data engineers trust it for workflow orchestration. #opensource #dataengineering #airflow",
            "detected_at": now,
        },
        {
            "owner": "microsoft", "repo": "vscode",
            "signal_key": "community_revolt",
            "severity": "high",
            "emoji": "🔥",
            "title": "Community Revolt Signal",
            "detail": "65% of top issues show negative sentiment about AI Copilot reliability",
            "metric": "13/20 top issues flagged negative",
            "action": "Immediate public response required. Engage with top complaints directly.",
            "post_draft": "We've read every issue and comment about VS Code Copilot reliability. Here's our honest response and what we're doing to fix it. #vscode #microsoft #transparency",
            "detected_at": now,
        },
    ]

    conn = sqlite3.connect(DB_PATH)
    for s in signals:
        conn.execute(
            """INSERT INTO signal_log
               (owner,repo,signal_key,severity,title,detail,metric,action,post_draft,emoji,auto_posted,detected_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (s["owner"], s["repo"], s["signal_key"], s["severity"],
             s["title"], s["detail"], s["metric"], s["action"],
             s["post_draft"], s["emoji"], 0, s["detected_at"])
        )
    conn.commit()
    conn.close()
    print(f"✅ Injected {len(signals)} demo signals successfully!")
    print("Now refresh the Signals tab in your browser.")

if __name__ == "__main__":
    inject_signals()