"""
Watchlist — Simplified and fixed version
"""
import asyncio
import aiohttp
import os
import json
import re
import sqlite3
from datetime import datetime
# from dotenv import load_dotenv
# load_dotenv()

# TINYFISH_API_KEY = os.getenv("TINYFISH_API_KEY")
TINYFISH_API_KEY="sk-tinyfish-9Kb06VX3aLaor0bIHuLS_9r5FJINIofj"
TINYFISH_URL     = "https://agent.tinyfish.ai/v1/automation/run-sse"
HEADERS          = {"X-API-Key": TINYFISH_API_KEY, "Content-Type": "application/json"}
DB_PATH          = "reporadar_watchlist.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS watchlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner TEXT, repo TEXT, email TEXT,
            auto_tweet INTEGER DEFAULT 0,
            created_at TEXT, last_checked TEXT,
            last_snapshot TEXT, signals_fired TEXT
        )
    """)
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


def add_to_watchlist(owner, repo, email, auto_tweet=False):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    existing = conn.execute(
        "SELECT id FROM watchlist WHERE owner=? AND repo=? AND email=?",
        (owner, repo, email)
    ).fetchone()
    if not existing:
        conn.execute(
            "INSERT INTO watchlist (owner,repo,email,auto_tweet,created_at,signals_fired) VALUES (?,?,?,?,?,?)",
            (owner, repo, email, 1 if auto_tweet else 0, datetime.now().isoformat(), "[]")
        )
        conn.commit()
    conn.close()


def get_watchlist():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id,owner,repo,email,auto_tweet,last_snapshot,signals_fired FROM watchlist"
    ).fetchall()
    conn.close()
    return [
        {
            "id": r[0], "owner": r[1], "repo": r[2],
            "email": r[3], "auto_tweet": bool(r[4]),
            "last_snapshot": r[5],
            "signals_fired": json.loads(r[6] or "[]")
        }
        for r in rows
    ]


def get_signal_log(owner=None, repo=None, limit=50):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    try:
        if owner and repo:
            rows = conn.execute(
                "SELECT id,owner,repo,signal_key,severity,title,detail,metric,action,post_draft,emoji,auto_posted,detected_at FROM signal_log WHERE owner=? AND repo=? ORDER BY detected_at DESC LIMIT ?",
                (owner, repo, limit)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id,owner,repo,signal_key,severity,title,detail,metric,action,post_draft,emoji,auto_posted,detected_at FROM signal_log ORDER BY detected_at DESC LIMIT ?",
                (limit,)
            ).fetchall()
    except Exception as e:
        print(f"[DB] signal_log query error: {e}")
        rows = []
    conn.close()
    return [
        {
            "id": r[0], "owner": r[1], "repo": r[2],
            "signal_key": r[3], "severity": r[4],
            "title": r[5], "detail": r[6],
            "metric": r[7], "action": r[8],
            "post_draft": r[9], "emoji": r[10],
            "auto_posted": bool(r[11]),
            "detected_at": r[12]
        }
        for r in rows
    ]


def inject_demo_signals(owner, repo):
    """Inject demo signals for first-time watchlist entry."""
    init_db()
    now = datetime.now().isoformat()
    signals = [
        {
            "owner": owner, "repo": repo,
            "signal_key": "bug_wave", "severity": "critical",
            "emoji": "🚨", "title": "Bug Wave Detected",
            "detail": f"Issues spiked 240% in {owner}/{repo} over 48 hours",
            "metric": "+42 new issues opened",
            "action": "Acknowledge publicly within 2 hours to prevent backlash.",
            "post_draft": f"We're aware of the recent issues in {repo}. Our team is actively investigating. Updates to follow. #opensource #bugfix",
            "detected_at": now,
        },
        {
            "owner": owner, "repo": repo,
            "signal_key": "viral_moment", "severity": "opportunity",
            "emoji": "🚀", "title": "Viral Moment Detected",
            "detail": f"{owner}/{repo} is trending — stars up 23% in 24 hours",
            "metric": "+1,200 stars gained today",
            "action": "Post NOW while momentum is high.",
            "post_draft": f"{repo} is trending on GitHub! Here's why thousands of developers are talking about it today. #opensource #trending",
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
    return signals


async def run_watchlist_cycle():
    """Run signal check cycle."""
    entries = get_watchlist()
    if not entries:
        return []

    all_alerts = []
    for entry in entries:
        owner, repo = entry["owner"], entry["repo"]
        # Inject demo signals on first run
        if not entry["last_snapshot"]:
            signals = inject_demo_signals(owner, repo)
            # Mark as checked
            conn = sqlite3.connect(DB_PATH)
            conn.execute(
                "UPDATE watchlist SET last_checked=?, last_snapshot=? WHERE id=?",
                (datetime.now().isoformat(), '{"checked": true}', entry["id"])
            )
            conn.commit()
            conn.close()
            all_alerts.append({"repo": f"{owner}/{repo}", "signals_count": len(signals)})
            print(f"[Watchlist] Injected {len(signals)} signals for {owner}/{repo}")

    return all_alerts