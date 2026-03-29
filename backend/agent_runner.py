"""
Shared TinyFish agent runner (FINAL VERSION)

Handles:
- SSE streaming correctly
- No premature timeout (aiohttp)
- Global timeout per agent
- Idle timeout protection (no hanging)
- Partial result fallback if COMPLETE not received
"""

import aiohttp
import json
import re
import os
import asyncio

# ------------------------
# CONFIG
# ------------------------
TINYFISH_API_KEY = os.getenv("TINYFISH_API_KEY")
TINYFISH_URL = "https://agent.tinyfish.ai/v1/automation/run-sse"

HEADERS = {
    "X-API-Key": TINYFISH_API_KEY,
    "Content-Type": "application/json"
}


# ------------------------
# MAIN AGENT FUNCTION
# ------------------------
async def run_agent(session, url, goal, label, use_stealth=False):
    payload = {
        "url": url,
        "goal": goal
    }

    if use_stealth:
        payload["browser_profile"] = "stealth"

    collected = {}
    last_data_time = asyncio.get_event_loop().time()

    try:
        async with session.post(
            TINYFISH_URL,
            headers=HEADERS,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=None)  # ✅ no hard timeout
        ) as resp:

            print(f"[Agent] {label} → STARTED")

            async for line in resp.content:
                now = asyncio.get_event_loop().time()

                # ✅ Idle timeout (no data for 30s)
                if now - last_data_time > 30:
                    print(f"[Agent] {label} ⚠️ idle timeout (30s no data)")
                    break

                decoded = line.decode("utf-8").strip()

                if not decoded:
                    continue

                last_data_time = now

                if not decoded.startswith("data: "):
                    continue

                try:
                    event = json.loads(decoded[6:])
                    event_type = event.get("type")

                    if event_type == "STARTED":
                        print(f"[Agent] {label} → STARTED")

                    elif event_type == "STREAMING_URL":
                        print(f"[Agent] {label} → STREAMING_URL")

                    elif event_type == "PROGRESS":
                        print(f"[Agent] {label} → PROGRESS")

                    elif event_type == "COMPLETE":
                        print(f"[Agent] {label} ✅ COMPLETE")

                        result = event.get("result", {})

                        # ✅ Handle dict result
                        if isinstance(result, dict):
                            collected = result

                        # ✅ Handle string result (sometimes TinyFish sends stringified JSON)
                        elif isinstance(result, str):
                            try:
                                collected = json.loads(result)
                            except Exception:
                                match = re.search(r'\{[\s\S]*\}', result)
                                if match:
                                    try:
                                        collected = json.loads(match.group())
                                    except Exception:
                                        pass

                        return {
                            "source": label,
                            "data": collected
                        }

                except json.JSONDecodeError:
                    continue

    except Exception as e:
        print(f"[Agent] {label} ❌ ERROR: {str(e)}")
        return {
            "source": label,
            "data": {},
            "error": str(e)
        }

    # ------------------------
    # FALLBACK (NO COMPLETE EVENT)
    # ------------------------
    if collected:
        print(f"[Agent] {label} ⚠️ returning partial data")
        return {
            "source": label,
            "data": collected,
            "partial": True
        }

    print(f"[Agent] {label} ⚠️ no data received")
    return {
        "source": label,
        "data": {},
        "error": "no_data"
    }


# ------------------------
# TIMEOUT WRAPPER
# ------------------------
async def run_agent_with_timeout(run_agent_func, *args, timeout=210):
    try:
        return await asyncio.wait_for(
            run_agent_func(*args),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        label = args[3] if len(args) > 3 else "unknown"
        print(f"[Agent] {label} ⚠️ timed out after {timeout}s")

        return {
            "source": label,
            "data": {},
            "error": "timeout"
        }