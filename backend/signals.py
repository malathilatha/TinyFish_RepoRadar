"""
Signal Detection Engine — inspired by PHAROS
Detects repo danger signals BEFORE they become disasters.
100x faster than manual review. No external LLM needed.
"""

from datetime import datetime


# ── Signal Thresholds ─────────────────────────────────────────
THRESHOLDS = {
    "bug_wave":          {"issues_spike_pct": 200,  "window_hours": 48},
    "abandonment_risk":  {"days_silent": 30},
    "bad_release":       {"star_drop_pct": 5,       "window_hours": 24},
    "market_threat":     {"competitor_star_gain":   500},
    "viral_moment":      {"star_gain_pct": 20,      "window_hours": 24},
    "community_revolt":  {"negative_issues_pct": 60},
}

# ── Signal Definitions ────────────────────────────────────────
SIGNALS = {
    "bug_wave": {
        "emoji":    "🚨",
        "severity": "critical",
        "title":    "Bug Wave Detected",
        "action":   "Acknowledge publicly within 2 hours to prevent community backlash.",
        "post_template": "We're aware of the recent issues reported in {repo}. Our team is actively investigating. Updates to follow. #opensource #bugfix"
    },
    "abandonment_risk": {
        "emoji":    "⚠️",
        "severity": "high",
        "title":    "Abandonment Risk Signal",
        "action":   "Post a project status update to reassure the community.",
        "post_template": "Quick update on {repo}: we're still active! Here's what's been happening behind the scenes... #opensource"
    },
    "bad_release": {
        "emoji":    "📉",
        "severity": "high",
        "title":    "Bad Release Signal",
        "action":   "Consider a hotfix release or public post-mortem.",
        "post_template": "We hear you — the latest {repo} release had issues. Here's our fix plan and timeline. #transparency"
    },
    "market_threat": {
        "emoji":    "⚔️",
        "severity": "medium",
        "title":    "Competitor Gaining Fast",
        "action":   "Publish a comparison post highlighting your advantages.",
        "post_template": "What makes {repo} different? Here's our honest comparison with alternatives. #devtools"
    },
    "viral_moment": {
        "emoji":    "🚀",
        "severity": "opportunity",
        "title":    "Viral Moment Detected",
        "action":   "Post NOW while momentum is high. Strike while hot.",
        "post_template": "{repo} is trending! Here's why developers are talking about us today. #opensource #trending"
    },
    "community_revolt": {
        "emoji":    "🔥",
        "severity": "critical",
        "title":    "Community Revolt Signal",
        "action":   "Immediate public response required. Engage with top complaints directly.",
        "post_template": "We've read every issue and comment. Here's our honest response to the community feedback on {repo}. #transparency"
    },
}


def detect_signals(old_snapshot: dict, new_snapshot: dict, repo_name: str) -> list:
    """
    Pure Python signal detection — no LLM needed.
    Compares two snapshots and fires signals when thresholds are crossed.
    Inspired by PHAROS pharmacovigilance pattern detection.
    """
    if not old_snapshot:
        return []

    signals_fired = []
    now = datetime.now().isoformat()

    old_issues = old_snapshot.get("open_issues", 0) or 0
    new_issues  = new_snapshot.get("open_issues", 0) or 0
    old_stars   = old_snapshot.get("stars", 0) or 0
    new_stars   = new_snapshot.get("stars", 0) or 0

    # ── Signal 1: Bug Wave ────────────────────────────────────
    if old_issues > 0:
        issue_spike_pct = ((new_issues - old_issues) / old_issues) * 100
        if issue_spike_pct >= THRESHOLDS["bug_wave"]["issues_spike_pct"]:
            sig = _build_signal("bug_wave", repo_name, {
                "detail": f"Issues jumped {issue_spike_pct:.0f}% ({old_issues} → {new_issues})",
                "metric": f"+{new_issues - old_issues} new issues"
            }, now)
            signals_fired.append(sig)

    # ── Signal 2: Abandonment Risk ────────────────────────────
    last_activity = new_snapshot.get("recent_activity", "") or ""
    if "month" in last_activity.lower() or "weeks ago" in last_activity.lower():
        sig = _build_signal("abandonment_risk", repo_name, {
            "detail": f"Last activity: {last_activity}",
            "metric": "No recent commits detected"
        }, now)
        signals_fired.append(sig)

    # ── Signal 3: Bad Release ─────────────────────────────────
    if old_stars > 0:
        star_change_pct = ((new_stars - old_stars) / old_stars) * 100
        if star_change_pct <= -THRESHOLDS["bad_release"]["star_drop_pct"]:
            sig = _build_signal("bad_release", repo_name, {
                "detail": f"Stars dropped {abs(star_change_pct):.1f}% ({old_stars} → {new_stars})",
                "metric": f"{new_stars - old_stars} stars lost"
            }, now)
            signals_fired.append(sig)

        # ── Signal 5: Viral Moment ────────────────────────────
        if star_change_pct >= THRESHOLDS["viral_moment"]["star_gain_pct"]:
            sig = _build_signal("viral_moment", repo_name, {
                "detail": f"Stars up {star_change_pct:.1f}% ({old_stars} → {new_stars})",
                "metric": f"+{new_stars - old_stars} stars gained"
            }, now)
            signals_fired.append(sig)

    # ── Signal 6: Community Revolt ────────────────────────────
    top_issues = new_snapshot.get("top_issues", []) or []
    negative_keywords = ["broken", "bug", "crash", "terrible", "unusable", "regression", "failed", "error", "wrong"]
    if top_issues:
        negative_count = sum(
            1 for issue in top_issues
            if any(kw in issue.lower() for kw in negative_keywords)
        )
        negative_pct = (negative_count / len(top_issues)) * 100
        if negative_pct >= THRESHOLDS["community_revolt"]["negative_issues_pct"]:
            sig = _build_signal("community_revolt", repo_name, {
                "detail": f"{negative_pct:.0f}% of top issues are negative sentiment",
                "metric": f"{negative_count}/{len(top_issues)} issues flagged"
            }, now)
            signals_fired.append(sig)

    return signals_fired


def _build_signal(signal_key: str, repo_name: str, context: dict, timestamp: str) -> dict:
    """Build a complete signal object with action and ready-to-post draft."""
    definition = SIGNALS[signal_key]
    post_draft  = definition["post_template"].format(repo=repo_name.split("/")[-1])

    return {
        "signal_key":  signal_key,
        "emoji":       definition["emoji"],
        "severity":    definition["severity"],
        "title":       definition["title"],
        "detail":      context.get("detail", ""),
        "metric":      context.get("metric", ""),
        "action":      definition["action"],
        "post_draft":  post_draft,
        "repo_name":   repo_name,
        "detected_at": timestamp,
    }


def prioritize_signals(signals: list) -> list:
    """Sort signals by severity — critical first."""
    order = {"critical": 0, "high": 1, "opportunity": 2, "medium": 3}
    return sorted(signals, key=lambda s: order.get(s["severity"], 99))