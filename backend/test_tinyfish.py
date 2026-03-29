"""
Run this to test TinyFish directly and see raw response.
Usage: python test_tinyfish.py
"""
import asyncio
import aiohttp
import os
import json
# from dotenv import load_dotenv
# load_dotenv()

TINYFISH_API_KEY = os.getenv("TINYFISH_API_KEY")
TINYFISH_URL = "https://agent.tinyfish.ai/v1/automation/run-sse"

async def test():
    print(f"API Key present: {bool(TINYFISH_API_KEY)}")
    print(f"API Key starts with: {TINYFISH_API_KEY[:8] if TINYFISH_API_KEY else 'MISSING'}...")
    print("---")

    headers = {
        "X-API-Key": TINYFISH_API_KEY,
        "Content-Type": "application/json",
    }

    payload = {
        "url": "https://github.com/apache/airflow/issues",
        "goal": 'Look at this page and return ONLY this JSON: {"test": "success", "page_title": "the page title you see"}'
    }

    print("Sending request to TinyFish...")
    print(f"URL: {TINYFISH_URL}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("---")

    all_lines = []
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                TINYFISH_URL,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                print(f"Response status: {resp.status}")
                print(f"Response headers: {dict(resp.headers)}")
                print("--- RAW STREAM ---")
                async for line in resp.content:
                    decoded = line.decode("utf-8").strip()
                    if decoded:
                        print(f"LINE: {decoded}")
                        all_lines.append(decoded)
    except Exception as e:
        print(f"ERROR: {e}")

    print("--- END ---")
    print(f"Total lines received: {len(all_lines)}")

asyncio.run(test())