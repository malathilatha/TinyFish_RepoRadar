import asyncio
import aiohttp
import os
import json
import re
import smtplib
import sqlite3
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

TINYFISH_API_KEY = os.getenv("TINYFISH_API_KEY")
TINYFISH_URL = "https://agent.tinyfish.ai/v1/automation/run-sse"
HEADERS = {"X-API-Key": TINYFISH_API_KEY, "Content-Type": "application/json"}

# Email config (user provides via .env)
SMTP_HOST     = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT     = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER     = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

DB_PATH = "reporadar_monitor.db"


# ── Database ──────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS monitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner TEXT, repo TEXT, email TEXT,
            created_at TEXT, last_checked TEXT,
            last_snapshot TEXT
        )
    """)
    conn.commit()
    conn.close()


def add_monitor(owner, repo, email):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO monitors (owner, repo, email, created_at, last_checked, last_snapshot) VALUES (?,?,?,?,?,?)",
        (owner, repo, email, datetime.now().isoformat(), None, None)
    )
    conn.commit()
    conn.close()


def get_all_monitors():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT id, owner, repo, email, last_snapshot FROM monitors").fetchall()
    conn.close()
    return [{"id": r[0], "owner": r[1], "repo": r[2], "email": r[3], "last_snapshot": r[4]} for r in rows]


def update_snapshot(monitor_id, snapshot_json):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "UPDATE monitors SET last_checked=?, last_snapshot=? WHERE id=?",
        (datetime.now().isoformat(), snapshot_json, monitor_id)
    )
    conn.commit()
    conn.close()


# ── TinyFish Snapshot Agent ───────────────────────────────────
async def take_snapshot(owner, repo):
    """
    TinyFish browses the repo and captures a point-in-time snapshot.
    This is what gets compared week-over-week.
    """
    payload = {
        "url": f"https://github.com/{owner}/{repo}",
        "goal": f"""
Visit GitHub repo {owner}/{repo}.
Capture a complete snapshot of its current state.
Return ONLY valid JSON:
{{
  "stars": <number>,
  "forks": <number>,
  "open_issues": <number>,
  "last_commit": "date or description",
  "top_issues": ["issue title 1", "issue title 2", "issue title 3"],
  "recent_activity": "description of recent commits or releases",
  "readme_summary": "2 sentence summary of what repo does",
  "captured_at": "{datetime.now().strftime('%Y-%m-%d')}"
}}
"""
    }

    collected = ""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                TINYFISH_URL, headers=HEADERS, json=payload,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as resp:
                async for line in resp.content:
                    decoded = line.decode("utf-8").strip()
                    if decoded.startswith("data: "):
                        try:
                            event = json.loads(decoded[6:])
                            if event.get("result"):    collected = event["result"]
                            elif event.get("data"):    collected = event["data"]
                            elif event.get("content"): collected += event["content"]
                        except json.JSONDecodeError:
                            collected += decoded[6:]
    except Exception as e:
        return {"error": str(e)}

    try:
        return json.loads(collected)
    except Exception:
        m = re.search(r'\{[\s\S]*\}', collected)
        if m:
            try: return json.loads(m.group())
            except: pass
    return {}


# ── Diff Engine (Pure Python) ─────────────────────────────────
def compute_diff(old_snapshot, new_snapshot):
    """
    Pure Python diff — no LLM needed.
    Compares two snapshots and returns human-readable changes.
    """
    if not old_snapshot:
        return {"is_first_run": True, "changes": []}

    changes = []

    # Stars diff
    old_stars = old_snapshot.get("stars", 0) or 0
    new_stars  = new_snapshot.get("stars", 0) or 0
    star_diff  = new_stars - old_stars
    if star_diff != 0:
        direction = "gained" if star_diff > 0 else "lost"
        changes.append({
            "type":  "stars",
            "emoji": "⭐" if star_diff > 0 else "📉",
            "message": f"{direction} {abs(star_diff)} stars ({old_stars} → {new_stars})"
        })

    # Issues diff
    old_issues = old_snapshot.get("open_issues", 0) or 0
    new_issues  = new_snapshot.get("open_issues", 0) or 0
    issue_diff  = new_issues - old_issues
    if issue_diff != 0:
        direction = "opened" if issue_diff > 0 else "closed"
        changes.append({
            "type":  "issues",
            "emoji": "🐛" if issue_diff > 0 else "✅",
            "message": f"{abs(issue_diff)} issues {direction} ({old_issues} → {new_issues})"
        })

    # Forks diff
    old_forks = old_snapshot.get("forks", 0) or 0
    new_forks  = new_snapshot.get("forks", 0) or 0
    fork_diff  = new_forks - old_forks
    if fork_diff > 0:
        changes.append({
            "type":  "forks",
            "emoji": "🍴",
            "message": f"gained {fork_diff} new forks ({old_forks} → {new_forks})"
        })

    # Activity diff
    if new_snapshot.get("recent_activity") != old_snapshot.get("recent_activity"):
        changes.append({
            "type":  "activity",
            "emoji": "🔨",
            "message": f"New activity: {new_snapshot.get('recent_activity', 'unknown')}"
        })

    return {"is_first_run": False, "changes": changes}


# ── Email Report ──────────────────────────────────────────────
def send_email_report(email, owner, repo, diff, new_snapshot):
    """Send weekly diff report via email."""
    if not SMTP_USER or not SMTP_PASSWORD:
        print(f"[Monitor] Email not configured — skipping send for {owner}/{repo}")
        return False

    repo_name = f"{owner}/{repo}"
    subject   = f"📡 RepoRadar Weekly: {repo_name}"

    changes_html = ""
    if diff.get("is_first_run"):
        changes_html = "<p>✅ Monitoring started! You'll receive weekly diffs from now on.</p>"
    elif not diff.get("changes"):
        changes_html = "<p>😴 No significant changes this week.</p>"
    else:
        for c in diff["changes"]:
            changes_html += f"<p>{c['emoji']} {c['message']}</p>"

    html = f"""
<html><body style="font-family:monospace;background:#0a0a0a;color:#eee;padding:24px;">
  <h2 style="color:#00ff88;">📡 RepoRadar Weekly Report</h2>
  <h3 style="color:#aaa;">{repo_name}</h3>
  <hr style="border-color:#222;">
  <h4 style="color:#00ff88;">This Week's Changes</h4>
  {changes_html}
  <hr style="border-color:#222;">
  <h4 style="color:#00ff88;">Current Snapshot</h4>
  <p>⭐ Stars: <b>{new_snapshot.get('stars', '—')}</b></p>
  <p>🍴 Forks: <b>{new_snapshot.get('forks', '—')}</b></p>
  <p>🐛 Open Issues: <b>{new_snapshot.get('open_issues', '—')}</b></p>
  <p>🔨 Recent Activity: {new_snapshot.get('recent_activity', '—')}</p>
  <hr style="border-color:#222;">
  <p style="color:#555;font-size:12px;">Powered by RepoRadar + TinyFish Web Agent API</p>
</body></html>
"""

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = SMTP_USER
        msg["To"]      = email
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, email, msg.as_string())
        return True
    except Exception as e:
        print(f"[Monitor] Email error: {e}")
        return False


# ── Main Monitor Loop ─────────────────────────────────────────
async def run_monitor_cycle():
    """
    Run one monitoring cycle for all registered repos.
    Call this via cron or APScheduler every 7 days.
    """
    monitors = get_all_monitors()
    print(f"[Monitor] Running cycle for {len(monitors)} repos...")

    for m in monitors:
        owner, repo = m["owner"], m["repo"]
        print(f"[Monitor] Checking {owner}/{repo}...")

        new_snapshot = await take_snapshot(owner, repo)
        if not new_snapshot or "error" in new_snapshot:
            print(f"[Monitor] Snapshot failed for {owner}/{repo}")
            continue

        old_snapshot = json.loads(m["last_snapshot"]) if m["last_snapshot"] else None
        diff         = compute_diff(old_snapshot, new_snapshot)

        update_snapshot(m["id"], json.dumps(new_snapshot))
        sent = send_email_report(m["email"], owner, repo, diff, new_snapshot)

        print(f"[Monitor] {owner}/{repo} — {len(diff.get('changes', []))} changes, email={'sent' if sent else 'skipped'}")
