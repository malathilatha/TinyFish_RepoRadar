import asyncio
import aiohttp
import os
import json
import re

# TINYFISH_API_KEY = os.getenv("TINYFISH_API_KEY")
TINYFISH_API_KEY="sk-tinyfish-9Kb06VX3aLaor0bIHuLS_9r5FJINIofj"
TINYFISH_URL     = "https://agent.tinyfish.ai/v1/automation/run-sse"
HEADERS          = {"X-API-Key": TINYFISH_API_KEY, "Content-Type": "application/json"}

CACHE_FILE = "analysis_cache.json"

def load_cache():
    try:
        if os.path.exists(CACHE_FILE):
            return json.load(open(CACHE_FILE))
    except: pass
    return {}

def save_cache(cache):
    try:
        json.dump(cache, open(CACHE_FILE, "w"), indent=2)
    except: pass

DEMO_DATA = {
    "microsoft/vscode": {
        "pain_points": {
            "pain_points": [
                {"title": "Chat session titles revert", "frequency": "high", "description": "Renamed chat session titles revert to default names unexpectedly.", "opportunity": "Ensure persistent storage for chat session metadata."},
                {"title": "Intermittent request failures", "frequency": "high", "description": "Users encounter generic 'request failed' errors during chat interactions.", "opportunity": "Improve error handling and descriptive feedback for network requests."},
                {"title": "Snippet rendering bugs", "frequency": "high", "description": "Code snippets disappear in the UI due to rendering issues.", "opportunity": "Fix the rendering logic for code blocks in the chat component."},
                {"title": "Terminal focus stealing", "frequency": "medium", "description": "Terminal steals focus unexpectedly when switching between editor tabs.", "opportunity": "Implement smarter focus management that respects user context."},
                {"title": "Extension host crashes", "frequency": "medium", "description": "Extension host process crashes silently causing features to stop working.", "opportunity": "Add automatic extension host recovery and user notification."}
            ],
            "top_feature_requests": ["Better AI context management across sessions", "Multi-root workspace improvements", "Native git blame inline support"],
            "repo_health": "healthy",
            "summary": "VS Code is actively maintained with clear labeling of bugs. Primary focus is stabilizing AI/Chat features and improving developer observability."
        }
    }
}


async def run_smart_agent(session, url, goal, label):
    payload = {"url": url, "goal": goal}
    collected = {}
    try:
        async with session.post(
            TINYFISH_URL, headers=HEADERS, json=payload,
            timeout=aiohttp.ClientTimeout(total=120, connect=20)
        ) as resp:
            async for line in resp.content:
                decoded = line.decode("utf-8").strip()
                if not decoded.startswith("data: "):
                    continue
                try:
                    event = json.loads(decoded[6:])
                    etype = event.get("type", "")
                    if etype in ("STARTED", "STREAMING_URL", "PROGRESS"):
                        print(f"[Agent] {label} → {etype}")
                    if etype == "COMPLETE":
                        result = event.get("result", {})
                        if isinstance(result, dict):
                            collected = result
                        elif isinstance(result, str):
                            try:
                                collected = json.loads(result)
                            except:
                                m = re.search(r'\{[\s\S]*\}', result)
                                if m:
                                    try: collected = json.loads(m.group())
                                    except: pass
                        print(f"[Agent] {label} ✅ COMPLETE — {len(collected)} keys")
                        break
                except json.JSONDecodeError:
                    pass
    except asyncio.TimeoutError:
        print(f"[Agent] {label} ⚠️ timed out")
    except Exception as e:
        print(f"[Agent] {label} ❌ {e}")

    return {"source": label, "data": collected}


async def run_all_agents(owner, repo):
    cache_key = f"{owner}/{repo}"

    cache = load_cache()
    if cache_key in cache:
        print(f"[Cache] Returning cached result for {cache_key}")
        return cache[cache_key]

    if cache_key in DEMO_DATA:
        print(f"[Cache] Returning demo data for {cache_key}")
        return DEMO_DATA[cache_key]

    repo_name = f"{owner}/{repo}"

    # Single agent — pain points only
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=5)) as session:
        result = await run_smart_agent(
            session,
            url=f"https://github.com/{owner}/{repo}/issues?q=is%3Aissue+is%3Aopen&per_page=10",
            goal=f"""Look at the issue titles on this GitHub issues page for {repo_name}.
Return ONLY this JSON with no extra text:
{{
  "pain_points": [
    {{"title": "short title", "frequency": "high", "description": "one sentence", "opportunity": "one sentence fix"}}
  ],
  "top_feature_requests": ["req 1", "req 2", "req 3"],
  "repo_health": "healthy",
  "summary": "two sentences about main problems"
}}""",
            label="pain_points"
        )

    results = {"pain_points": result["data"]}
    cache[cache_key] = results
    save_cache(cache)
    print(f"[Cache] Saved {cache_key} to file")
    return results


def merge_results(owner, repo, results):
    pain = results.get("pain_points", {})
    return {
        "repo_name":            f"{owner}/{repo}",
        "pain_points":          pain.get("pain_points", []),
        "top_feature_requests": pain.get("top_feature_requests", []),
        "repo_health":          pain.get("repo_health", "unknown"),
        "pain_summary":         pain.get("summary", ""),
    }