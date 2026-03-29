from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json, re, asyncio
from tinyfish import run_all_agents, merge_results
from competitor import run_competitor_benchmark
from autopost import auto_post_tweet
from watchlist import (
    add_to_watchlist, get_watchlist,
    run_watchlist_cycle, get_signal_log
)
from signals import detect_signals, prioritize_signals

app = FastAPI(title="RepoRadar API — v4 Final")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Models ─────────────────────────────────────────────────────
class AnalyzeRequest(BaseModel):
    github_url: str

class BenchmarkRequest(BaseModel):
    github_url: str

class WatchlistRequest(BaseModel):
    github_url: str
    email: str
    auto_tweet: bool = False

class AutoPostRequest(BaseModel):
    tweet_text: str


# ── Helpers ────────────────────────────────────────────────────
def extract_owner_repo(url):
    match = re.search(r"github\.com/([^/]+)/([^/\s?#]+)", url)
    if not match:
        raise HTTPException(status_code=400, detail="Invalid GitHub URL")
    return match.group(1), match.group(2)


# ── Routes ─────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": "v4",
        "powered_by": "TinyFish only — zero external LLM",
        "features": [
            "core analysis",
            "competitor benchmark",
            "watchlist + signal detection (PHAROS-inspired)",
            "8-second alert dispatch (AfriGov-inspired)",
            "auto-tweet (TinyFish browser automation)",
            "FrankenSlide-style auto-draft posts"
        ]
    }


# CORE — Main intelligence report
@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    owner, repo = extract_owner_repo(req.github_url)

    async def event_stream():
        try:
            yield f"data: {json.dumps({'step':'start','message':'Launching 5 parallel TinyFish agents...'})}\n\n"
            yield f"data: {json.dumps({'step':'scraping','message':'Browsing GitHub Issues, HackerNews, LinkedIn, ProductHunt simultaneously...'})}\n\n"
            results = await run_all_agents(owner, repo)
            yield f"data: {json.dumps({'step':'merging','message':'Merging agent results...'})}\n\n"
            report = merge_results(owner, repo, results)
            yield f"data: {json.dumps({'step':'done','report':report})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'step':'error','message':str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# FEATURE 2 — Competitor Benchmark
@app.post("/benchmark")
async def benchmark(req: BenchmarkRequest):
    owner, repo = extract_owner_repo(req.github_url)

    async def event_stream():
        try:
            yield f"data: {json.dumps({'step':'start','message':'Finding competitors on GitHub...'})}\n\n"
            yield f"data: {json.dumps({'step':'scraping','message':'TinyFish scraping all repos in parallel...'})}\n\n"
            result = await run_competitor_benchmark(owner, repo)
            yield f"data: {json.dumps({'step':'done','benchmark':result})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'step':'error','message':str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# FEATURE 3 — Watchlist (PHAROS + AfriGov)
@app.post("/watchlist/add")
async def watchlist_add(req: WatchlistRequest):
    owner, repo = extract_owner_repo(req.github_url)
    add_to_watchlist(owner, repo, req.email, req.auto_tweet)
    return {
        "success": True,
        "message": f"👁 Now watching {owner}/{repo}",
        "auto_tweet": req.auto_tweet,
        "signals": "PHAROS-style signal detection active",
        "alert_speed": "AfriGov-style 8-second dispatch enabled"
    }


@app.get("/watchlist")
async def watchlist_list():
    entries = get_watchlist()
    return {"watching": len(entries), "repos": [
        {"repo": f"{e['owner']}/{e['repo']}", "email": e["email"],
         "auto_tweet": e["auto_tweet"], "signals_fired": len(e["signals_fired"])}
        for e in entries
    ]}


@app.post("/watchlist/check")
async def watchlist_check(background_tasks: BackgroundTasks):
    """Manually trigger a watchlist cycle."""
    background_tasks.add_task(run_watchlist_cycle)
    return {"success": True, "message": "Watchlist cycle started — signal detection running..."}


@app.get("/watchlist/signals")
async def signal_log():
    """Get all fired signals across all watched repos."""
    signals = get_signal_log(limit=100)
    return {"total": len(signals), "signals": signals}


# FEATURE 1 — Auto-post tweet
@app.post("/autopost/tweet")
async def autopost_tweet(req: AutoPostRequest):
    result = await auto_post_tweet(req.tweet_text)
    return result