"""
Auto-post tweet via TinyFish browser automation.
TinyFish navigates Twitter, logs in, and posts the tweet.
"""
import aiohttp
import os
import json
import re
# from dotenv import load_dotenv
# load_dotenv()

TINYFISH_API_KEY = os.getenv("TINYFISH_API_KEY")
TINYFISH_API_KEY="sk-tinyfish-9Kb06VX3aLaor0bIHuLS_9r5FJINIofj"
TINYFISH_URL     = "https://agent.tinyfish.ai/v1/automation/run-sse"
HEADERS          = {"X-API-Key": TINYFISH_API_KEY, "Content-Type": "application/json"}

# TWITTER_USERNAME = os.getenv("TWITTER_USERNAME", "")
# TWITTER_PASSWORD = os.getenv("TWITTER_PASSWORD", "")
TWITTER_USERNAME="MalathiVen61858"    
TWITTER_PASSWORD="LsoB49rfwgkk@" 



async def auto_post_tweet(tweet_text: str) -> dict:
    """
    TinyFish navigates Twitter/X, logs in, and posts the tweet.
    Real browser automation — not an API call.
    """
    if not TWITTER_USERNAME or not TWITTER_PASSWORD:
        return {
            "success": False,
            "error": "Twitter credentials not set. Add TWITTER_USERNAME and TWITTER_PASSWORD to your environment."
        }

    if not tweet_text or not tweet_text.strip():
        return {"success": False, "error": "No tweet text provided"}

    # Trim to 280 chars
    if len(tweet_text) > 280:
        tweet_text = tweet_text[:277] + "..."

    goal = f"""Go to https://twitter.com/login and log in with:
Username: {TWITTER_USERNAME}
Password: {TWITTER_PASSWORD}

After logging in successfully:
1. Click the compose tweet button (looks like a quill/pencil icon or says "Post")
2. Type exactly this text in the compose box:
{tweet_text}
3. Click the "Post" button to publish the tweet
4. Wait for confirmation that the tweet was posted

Return ONLY this JSON:
{{
  "success": true,
  "posted_text": "the tweet text that was posted",
  "error": null
}}

If login fails or posting fails, return:
{{
  "success": false,
  "posted_text": "",
  "error": "describe what went wrong"
}}"""

    payload = {
        "url": "https://twitter.com/login",
        "goal": goal,
        "browser_profile": "stealth"
    }

    collected = {}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                TINYFISH_URL, headers=HEADERS, json=payload,
                timeout=aiohttp.ClientTimeout(total=240, connect=30)
            ) as resp:
                async for line in resp.content:
                    decoded = line.decode("utf-8").strip()
                    if not decoded.startswith("data: "):
                        continue
                    try:
                        event = json.loads(decoded[6:])
                        etype = event.get("type", "")
                        print(f"[AutoPost] → {etype}")
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
                            print(f"[AutoPost] ✅ COMPLETE")
                            break
                    except: pass
    except Exception as e:
        return {"success": False, "error": str(e), "posted_text": ""}

    if not collected:
        return {
            "success": False,
            "error": "TinyFish did not return a result. Twitter may have blocked the login.",
            "posted_text": ""
        }

    return collected