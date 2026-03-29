# 🔭 RepoRadar — Top 3 Edition

> The only repo intelligence tool that doesn't just analyze — it **acts**.
> 100% TinyFish powered. Zero external LLM. One API key.

Built for the **TinyFish $2M Pre-Accelerator Hackathon**

---

## 🚀 3 Killer Features (What Makes This Top 3)

### Feature 1 — Auto-Post Tweet via TinyFish 🐦
TinyFish **navigates Twitter**, logs in, types the post, and hits send.
Not just generating text — **doing real work on the web**.

### Feature 2 — Competitor Benchmark 🏆
TinyFish **autonomously finds 3 competitors on GitHub**, scrapes all of them
in parallel, and returns a side-by-side comparison table. Multi-site orchestration.

### Feature 3 — Weekly Monitor + Email Diff 📡
A **recurring autonomous agent** — TinyFish checks your repo every week,
detects changes in stars/issues/activity, and emails you a diff report.
This is a real product people pay for.

---

## 🏗 Architecture

```
GitHub URL
    │
    ├── Core: 5 parallel TinyFish agents → intelligence dashboard
    │
    ├── Feature 1: TinyFish → Twitter login → compose → post
    │
    ├── Feature 2: TinyFish finds competitors → scrapes all 4 repos in parallel → benchmark table
    │
    └── Feature 3: Cron → TinyFish snapshot → diff → email report
```

---

## ✅ Setup

### 1. Get your free TinyFish API key
→ https://agent.tinyfish.ai/api-keys (no credit card, 500 free steps)

### 2. Configure
```bash
cp .env.example .env
# Fill in: TINYFISH_API_KEY (required)
# Optional: TWITTER_USERNAME, TWITTER_PASSWORD (for auto-tweet)
# Optional: SMTP_USER, SMTP_PASSWORD (for email monitor)
```

### 3. Run Backend
```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export $(cat ../.env | xargs)
uvicorn main:app --reload --port 8000
```

### 4. Run Frontend
```bash
cd frontend
npm create vite@latest . -- --template react
npm install
# Replace src/App.jsx with our App.jsx
npm run dev
```

---

## 📡 Weekly Monitor — Cron Setup

To run the monitor automatically every week:

```bash
# Add to crontab (runs every Monday at 9am)
0 9 * * 1 cd /path/to/reporadar/backend && python -c "
import asyncio
from monitor import run_monitor_cycle
asyncio.run(run_monitor_cycle())
"
```

Or call manually via API:
```bash
curl -X POST http://localhost:8000/monitor/run
```

---

## 📁 File Structure

```
reporadar/
├── .env.example
├── README.md
├── backend/
│   ├── main.py          ← FastAPI + all routes
│   ├── tinyfish.py      ← 5 core smart agents
│   ├── competitor.py    ← Feature 2: benchmark
│   ├── monitor.py       ← Feature 3: weekly monitor
│   ├── autopost.py      ← Feature 1: auto-tweet
│   └── requirements.txt
└── frontend/
    └── App.jsx          ← Full React dashboard
```

---

## 🏆 Why This Is Top 3

| Criteria | RepoRadar |
|---|---|
| Uses TinyFish for live browsing | ✅ 8+ agents total |
| Multi-step workflows | ✅ Login flows, parallel scraping |
| **Takes action on the web** | ✅ Posts tweets, sends emails |
| Real business value | ✅ Saves hours of research |
| Revenue potential | ✅ $20-50/mo SaaS |
| Zero external LLM | ✅ 100% TinyFish built-in |
| Impressive demo | ✅ Live results + auto-tweet moment |

**Unique pitch:**
> "Most hackathon projects read the web. RepoRadar reads it, analyzes it,
>  benchmarks against competitors, monitors it weekly, AND posts for you.
>  100% TinyFish. Zero external dependencies."

---

*RepoRadar · TinyFish $2M Pre-Accelerator Hackathon*
