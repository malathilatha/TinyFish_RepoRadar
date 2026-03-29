import asyncio
import aiohttp
import os
import json
import re

# TINYFISH_API_KEY = os.getenv("TINYFISH_API_KEY")
TINYFISH_API_KEY="sk-tinyfish-9Kb06VX3aLaor0bIHuLS_9r5FJINIofj"
TINYFISH_URL     = "https://agent.tinyfish.ai/v1/automation/run-sse"
HEADERS          = {"X-API-Key": TINYFISH_API_KEY, "Content-Type": "application/json"}
_cache = {}

GH_HEADERS = {"Accept": "application/vnd.github.v3+json"}


async def fetch_repo_stats_from_api(session, owner, repo):
    """Fetch stars, forks, language directly from GitHub REST API — fast & reliable."""
    try:
        async with session.get(
            f"https://api.github.com/repos/{owner}/{repo}",
            headers=GH_HEADERS,
            timeout=aiohttp.ClientTimeout(total=10)
        ) as r:
            if r.status == 200:
                data = await r.json()
                return {
                    "name": f"{owner}/{repo}",
                    "description": data.get("description", ""),
                    "stars": data.get("stargazers_count", 0),
                    "forks": data.get("forks_count", 0),
                    "language": data.get("language", "—"),
                    "last_updated": data.get("pushed_at", "")[:10] if data.get("pushed_at") else "—",
                    "maturity": "mature" if data.get("stargazers_count", 0) > 10000 else "growing",
                }
    except Exception as e:
        print(f"[Benchmark] GitHub API fetch failed for {owner}/{repo}: {e}")
    return {}


async def get_top_competitor(session, owner, repo, language):
    """Find #1 starred repo in same language, skipping the main repo."""
    try:
        async with session.get(
            f"https://api.github.com/search/repositories?q=language:{language}&sort=stars&order=desc&per_page=5",
            headers=GH_HEADERS,
            timeout=aiohttp.ClientTimeout(total=10)
        ) as r:
            if r.status == 200:
                items = (await r.json()).get("items", [])
                for item in items:
                    same = (
                        item["owner"]["login"].lower() == owner.lower()
                        and item["name"].lower() == repo.lower()
                    )
                    if not same:
                        print(f"[Benchmark] Top competitor: {item['full_name']}")
                        return item["owner"]["login"], item["name"]
    except Exception as e:
        print(f"[Benchmark] Competitor search failed: {e}")
    return None, None


async def scrape_qualitative(session, owner, repo):
    """Use TinyFish to get strengths, weaknesses, unique features for one repo."""
    payload = {
        "url": f"https://github.com/{owner}/{repo}",
        "goal": f"""Visit the GitHub repo page for {owner}/{repo}.
Read the description, topics, and README preview visible on the page.
Return ONLY valid JSON with no extra text:
{{
  "strengths": ["strength 1", "strength 2", "strength 3"],
  "weaknesses": ["weakness 1", "weakness 2"],
  "unique_features": ["feature 1", "feature 2", "feature 3"]
}}"""
    }

    collected = {}
    try:
        async with session.post(
            TINYFISH_URL, headers=HEADERS, json=payload,
            timeout=aiohttp.ClientTimeout(total=90, connect=20)
        ) as resp:
            async for line in resp.content:
                decoded = line.decode("utf-8").strip()
                if not decoded.startswith("data: "):
                    continue
                try:
                    event = json.loads(decoded[6:])
                    etype = event.get("type", "")
                    if etype in ("STARTED", "STREAMING_URL", "PROGRESS"):
                        print(f"[Benchmark] {owner}/{repo} → {etype}")
                    elif etype == "COMPLETE":
                        result = event.get("result", {})
                        if isinstance(result, dict):
                            collected = result
                        elif isinstance(result, str):
                            try:
                                collected = json.loads(result)
                            except:
                                m = re.search(r'\{[\s\S]*\}', result)
                                if m:
                                    try:
                                        collected = json.loads(m.group())
                                    except:
                                        pass
                        print(f"[Benchmark] {owner}/{repo} qualitative ✅")
                        break
                except Exception:
                    pass
    except asyncio.TimeoutError:
        print(f"[Benchmark] {owner}/{repo} ⚠️ timed out — qualitative skipped")
    except Exception as e:
        print(f"[Benchmark] {owner}/{repo} ❌ {e}")

    return collected


async def run_competitor_benchmark(owner, repo):
    cache_key = f"{owner}/{repo}"
    if cache_key in _cache:
        print(f"[Benchmark] Cache hit for {cache_key}")
        return _cache[cache_key]

    connector = aiohttp.TCPConnector(limit=10)
    async with aiohttp.ClientSession(connector=connector) as session:

        # Step 1: get main repo stats from GitHub API (fast, never returns —)
        main_stats = await fetch_repo_stats_from_api(session, owner, repo)
        if not main_stats:
            return {"error": f"Could not fetch stats for {owner}/{repo} from GitHub API."}

        language = main_stats.get("language", "")
        if not language or language == "—":
            return {"error": f"No language detected for {owner}/{repo}."}

        print(f"[Benchmark] {owner}/{repo} | ⭐ {main_stats['stars']} | {language}")

        # Step 2: find #1 competitor via GitHub search API
        comp_owner, comp_repo = await get_top_competitor(session, owner, repo, language)
        if not comp_owner:
            return {"error": f"Could not find a {language} competitor on GitHub."}

        # Step 3: fetch competitor stats + qualitative for both in parallel
        comp_stats, main_qual, comp_qual = await asyncio.gather(
            fetch_repo_stats_from_api(session, comp_owner, comp_repo),
            scrape_qualitative(session, owner, repo),
            scrape_qualitative(session, comp_owner, comp_repo),
            return_exceptions=True
        )

    if isinstance(comp_stats, Exception) or not comp_stats:
        comp_stats = {}
    if isinstance(main_qual, Exception):
        main_qual = {}
    if isinstance(comp_qual, Exception):
        comp_qual = {}

    # Merge API stats (guaranteed) with TinyFish qualitative (best-effort)
    main_result = {**main_stats, **main_qual}
    comp_result = {**comp_stats, **comp_qual}

    main_stars = int(main_result.get("stars") or 0)
    comp_stars = int(comp_result.get("stars") or 0)

    def fmt(n):
        n = int(n or 0)
        return f"{n/1000:.1f}k" if n >= 1000 else str(n)

    result = {
        "main_repo": main_result,
        "competitors": [comp_result],
        "benchmark_table": {
            "headers": [
                main_result.get("name", f"{owner}/{repo}"),
                comp_result.get("name", f"{comp_owner}/{comp_repo}"),
            ],
            "rows": [
                {"metric": "Stars",        "values": [fmt(main_stars), fmt(comp_stars)]},
                {"metric": "Forks",        "values": [fmt(main_result.get("forks", 0)), fmt(comp_result.get("forks", 0))]},
                {"metric": "Language",     "values": [main_result.get("language", "—"), comp_result.get("language", "—")]},
                {"metric": "Maturity",     "values": [main_result.get("maturity", "—"), comp_result.get("maturity", "—")]},
                {"metric": "Last Updated", "values": [main_result.get("last_updated", "—"), comp_result.get("last_updated", "—")]},
            ]
        },
        "verdict": {
            "star_advantage": "ahead" if main_stars >= comp_stars else "behind",
            "star_gap": main_stars - comp_stars,
            "main_unique_strengths": main_qual.get("unique_features", main_qual.get("strengths", [])),
            "gaps_vs_competitors": [
                f"{comp_result.get('name', comp_owner+'/'+comp_repo)}: {f}"
                for f in comp_qual.get("unique_features", [])[:3]
            ]
        }
    }

    _cache[cache_key] = result
    return result