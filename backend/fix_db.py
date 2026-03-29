"""
Fixes the signal_log table and inserts demo signals.
Run: python fix_db.py
"""
import sqlite3
from datetime import datetime

DB_PATH = "reporadar_watchlist.db"
conn = sqlite3.connect(DB_PATH)

# Add missing columns
try:
    conn.execute("ALTER TABLE signal_log ADD COLUMN action TEXT")
    print("✅ Added 'action' column")
except:
    print("ℹ️ 'action' column already exists")

try:
    conn.execute("ALTER TABLE signal_log ADD COLUMN emoji TEXT")
    print("✅ Added 'emoji' column")
except:
    print("ℹ️ 'emoji' column already exists")

try:
    conn.execute("ALTER TABLE signal_log ADD COLUMN metric TEXT")
    print("ℹ️ 'metric' column already exists")
except:
    print("✅ Added 'metric' column")

conn.commit()

# Insert demo signals
now = datetime.now().isoformat()
signals = [
    ("apache","airflow","bug_wave","critical","🚨","Bug Wave Detected",
     "Issues spiked 240% in apache/airflow over the past 48 hours",
     "+42 new issues opened",
     "Acknowledge publicly within 2 hours to prevent community backlash.",
     "We're aware of the recent issues in Airflow. Our team is actively investigating. Updates to follow. #opensource #bugfix #apache",
     now),
    ("apache","airflow","viral_moment","opportunity","🚀","Viral Moment Detected",
     "apache/airflow is trending — stars up 23% in the last 24 hours",
     "+1,200 stars gained today",
     "Post NOW while momentum is high. Strike while hot.",
     "Apache Airflow just hit 44K+ stars and is trending on GitHub! Here's why data engineers worldwide trust it. #DataEngineering #opensource #airflow",
     now),
    ("microsoft","vscode","community_revolt","high","🔥","Community Revolt Signal",
     "65% of top issues show negative sentiment about AI Copilot reliability",
     "13/20 top issues flagged negative",
     "Immediate public response required. Engage with top complaints directly.",
     "We've read every issue about VS Code Copilot reliability. Here's our honest response and fix plan. #vscode #transparency #microsoft",
     now),
]

for s in signals:
    conn.execute("""
        INSERT INTO signal_log
        (owner,repo,signal_key,severity,emoji,title,detail,metric,action,post_draft,detected_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, s)

conn.commit()
count = conn.execute("SELECT COUNT(*) FROM signal_log").fetchone()[0]
conn.close()

print(f"\n✅ Done! {count} signals now in database.")
print("→ Go to Signals tab and click ↻ Refresh")