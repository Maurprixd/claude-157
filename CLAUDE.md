# Job Scraper — Mauricio Mena
## Briefing for Claude Code (local PC session)

This file is auto-read by Claude Code at the start of every session.
It explains how the **cloud session** (claude.ai/code) and your **local session** (this terminal)
divide responsibilities — and what YOU specifically need to do that the cloud cannot.

---

## The Two-Claude Setup — Shared Memory via Git

```
┌─────────────────────────────────┐     ┌──────────────────────────────────┐
│  CLOUD SESSION (claude.ai/code) │     │  LOCAL SESSION (your PC terminal) │
│                                 │     │                                  │
│  • Builds & improves the code   │     │  • Actually RUNS the scraper     │
│  • Manages git / GitHub         │     │  • Calls claude CLI for AI match │
│  • Reviews Notion tracker       │     │  • Scrapes Indeed + LinkedIn     │
│  • Generates resumes (PDF)      │     │    (works here, blocked in cloud)│
│  • Plans job search strategy    │     │  • Runs your existing Telegram   │
│  • Reads shared/jobs.json to    │     │    bot + job hunter              │
│    see all your found jobs      │     │  • Auto-pushes results to git    │
│  • Answers questions            │     │    after every scrape            │
└─────────────────────────────────┘     └──────────────────────────────────┘
                    │                                   │
                    └──────────── git push/pull ────────┘
                                       │
                         ┌─────────────────────────┐
                         │   SHARED MEMORY (git)   │
                         │                         │
                         │  profile/mauricio.py    │  ← source of truth
                         │  shared/jobs.json       │  ← all scraped jobs
                         │  CLAUDE.md              │  ← session briefing
                         └─────────────────────────┘
```

**How it works:**
- Your local session scrapes → scores → saves to `shared/jobs.json` → auto git-pushes
- Cloud session does `git pull` → reads `shared/jobs.json` → can generate resumes,
  write cover letters, plan strategy, all based on YOUR real scraped data
- Profile changes go either way — edit `profile/mauricio.py`, push, both sessions see it

**Rule:** Code changes come from cloud. Job data comes from local. Both share through git.
Always `git pull origin claude/memory-form-clouds-access-bC5CO` before running.

---

## Your First Job Every Session

```bash
# 1. Pull latest code from cloud session
git pull origin claude/memory-form-clouds-access-bC5CO

# 2. Verify profile is loaded (do NOT search without this)
python3 -c "from profile.mauricio import CANDIDATE_PROFILE; print('Profile loaded:', CANDIDATE_PROFILE['name'])"

# 3. Run scraper
python main.py scrape
```

---

## ALWAYS Read profile/mauricio.py First

**Never search, score, or write resume bullets without reading `profile/mauricio.py` first.**
It is the single source of truth for:
- Mauricio's real experience (WIMTACH wearable, VIV66 soft goods)
- His skills (SolidWorks, KeyShot, Rhino, FDM, DFM, soft goods specs)
- Job search strategy (target roles, preferred sectors, boost/penalize keywords)
- Minimum match score threshold

Key facts the profile captures (don't hallucinate these):
- ~1.5 years professional + 3 years total design practice
- WIMTACH = real funded R&D program, not a class project. Patent filed Feb 2026.
- VIV66 = apparel company → real soft goods / flexible materials experience
- Portfolio is live: mauricio-mena.com + behance.net/gallery/217417729/Portfolio
- Languages: English (Fluent), Spanish (Native), French (Basic)

---

## Job Sources — What Works Where

| Source | Cloud | Local PC | Notes |
|--------|-------|----------|-------|
| Job Bank Canada | ✅ | ✅ | Most reliable, government site |
| Indeed Canada | ❌ (403 blocked) | ✅ | Works fine on your IP |
| LinkedIn Jobs | ❌ (blocked) | ✅ | Guest API works locally |
| Glassdoor | ❌ | ✅ (playwright) | Needs `playwright install chromium` |
| ZipRecruiter | ❌ | use WebFetch | RSS: ziprecruiter.com/candidate/search?search=industrial+designer&location=Toronto |
| Workopolis | ❌ | use WebFetch | Canadian-specific |
| Eluta.ca | ❌ | use WebFetch | Canadian job aggregator |

**To search a site not in the scraper yet**, use the WebFetch or WebSearch MCP tools
to manually retrieve listings, then add them to the cache:

```python
# Add a manually found job to cache
from storage.cache import JobCache
from scraper.models import Job, JobSource, VerificationStatus
import time

cache = JobCache()
job = Job(
    job_id="manual_<unique_id>",
    source=JobSource.LINKEDIN,   # or JOBBANK, INDEED
    title="Junior Industrial Designer",
    company="Company Name",
    location="Toronto, ON",
    url="https://...",
    description="Full job description text here...",
    scraped_at=time.strftime("%Y-%m-%dT%H:%M:%S"),
)
cache.set(job)
cache.save()
# Then score it: python main.py scrape --no-cache  (or score manually)
```

---

## How to Find Jobs Everywhere (Expanding Search)

When the user asks to "look everywhere" or finds the current results thin:

### 1. Run all sources
```bash
python main.py scrape --sources jobbank,indeed,linkedin
```

### 2. Search manually with WebFetch/WebSearch
Use these queries on sites the scraper doesn't cover yet:
- `site:glassdoor.ca "industrial designer" Toronto junior`
- `site:workopolis.com "product designer" Toronto`
- `site:eluta.ca "industrial designer" Toronto`
- `site:ziprecruiter.com "junior industrial designer" Toronto`
- `"junior industrial designer" OR "junior product designer" Toronto site:linkedin.com/jobs`

### 3. Add Glassdoor scraper (playwright)
If the user asks, the cloud session can write a Glassdoor scraper.
Run `playwright install chromium` first.

### 4. Broaden search queries
Current queries in `scraper/jobbank.py` → `SEARCH_QUERIES`. Add:
- "design technologist"
- "product development engineer"
- "CAD designer"
- "hardware designer"
- "wearable designer"

---

## Running the Telegram Bot (Phone Access)

```bash
# One-time setup:
# 1. Message @BotFather on Telegram → /newbot → copy token
# 2. Message @userinfobot → copy your chat ID
# 3. Add to .env: TELEGRAM_TOKEN=... and TELEGRAM_CHAT_ID=...
pip install python-telegram-bot

# Run (keep terminal open):
python bot.py
```

Commands from phone: `/scrape`, `/list`, `/resume <id>`, `/cover <id>`, `/apply <id>`

---

## Current Job Cache State (as of last cloud session, 2026-05-26)

Top cached jobs (run `/list` or `python main.py list --min-score 40` to refresh):

| Score | Job | Company | Status |
|-------|-----|---------|--------|
| 74 | Junior Industrial Designer | Sidekick | In Notion as Draft — apply now |
| 60 | Product Designer | Umbra | ✉️ Already applied (May 1) — skip |
| 53 | Industrial Designer | Pacific Smoke | Not in Notion — new lead |
| 53 | Industrial Designer (Orthopedic) | OssKin | ✉️ Already applied (May 6) — skip |
| 48 | Associate Product Designer | Mattel | Not in Notion — new lead |
| 33 | Industrial Designer | Bauer Hockey | Not in Notion — low odds |

**The scraper now auto-filters applied jobs** — Umbra and OssKin will not appear
in new results because they're in Notion with Applied status.

---

## .env File Required

```bash
# Copy the example and fill in your values
cp .env.example .env
```

Required:
- `NOTION_TOKEN` — from notion.so/my-integrations (for logging applied jobs)

Optional:
- `TELEGRAM_TOKEN` + `TELEGRAM_CHAT_ID` — for phone bot

NOT required: No Anthropic API key. The scraper uses `claude -p "..."` subprocess
calls which run through your Claude Pro subscription.

---

## Key Files

| File | Purpose |
|------|---------|
| `profile/mauricio.py` | **SOURCE OF TRUTH** — read before every session |
| `main.py` | CLI entry point (`scrape`, `list`, `resume`, `cover`, `apply`) |
| `ai/matcher.py` | Scoring prompt — reads live from profile |
| `ai/claude_cli.py` | Calls `claude -p "..."` subprocess (Pro subscription) |
| `ai/resume_generator.py` | Tailors resume bullets via claude CLI |
| `ai/cover_letter.py` | Streams cover letter via claude CLI |
| `pdf/builder.py` | Builds PDF resume with ReportLab |
| `bot.py` | Telegram bot for phone access |
| `notion/logger.py` | Logs applications + checks for duplicates |
| `storage/cache.py` | JSON cache with 24hr TTL |
| `scraper/jobbank.py` | Job Bank Canada scraper |
| `scraper/indeed.py` | Indeed Canada RSS scraper |
| `scraper/linkedin.py` | LinkedIn guest API scraper |
| `.job_cache.json` | Cached scored jobs (auto-created) |

---

## Commands Reference

```bash
python main.py scrape                          # Full scrape → AI score → Notion filter → report
python main.py scrape --min-score 40           # Lower threshold to see more results
python main.py scrape --sources jobbank        # Only Job Bank (faster)
python main.py scrape --no-cache               # Force fresh scrape ignoring cache
python main.py list                            # Show cached jobs
python main.py list --min-score 40             # Show more results from cache
python main.py resume <job_id>                 # Generate tailored PDF resume
python main.py cover <job_id>                  # Generate cover letter (streamed)
python main.py apply <job_id>                  # Log as Applied in Notion
python bot.py                                  # Start Telegram phone bot
```

---

## Git Workflow

Branch: `claude/memory-form-clouds-access-bC5CO`

```bash
git pull origin claude/memory-form-clouds-access-bC5CO   # get latest from cloud
git push -u origin claude/memory-form-clouds-access-bC5CO  # send changes back
```

---

## Connecting Your Existing Bot/Hunter to This Shared Memory

If you already have a job hunter running on your PC, point it at `shared/jobs.json`
and push to this repo — the cloud session will see everything it finds.

**Option A — Write directly to shared/jobs.json**
Your existing bot saves results in whatever format it uses.
After each run, convert them to the Job format and write to `shared/jobs.json`:

```python
# In your existing bot, after scraping:
import json, pathlib

SHARED = pathlib.Path("/path/to/claude-157/shared/jobs.json")
existing = json.loads(SHARED.read_text()) if SHARED.exists() else {}

# Add your jobs (minimum required fields):
existing["your_job_id"] = {
    "job_id": "your_job_id",
    "title": "Junior Industrial Designer",
    "company": "Company Name",
    "location": "Toronto, ON",
    "url": "https://...",
    "description": "Full job text...",
    "source": "linkedin",        # or "jobbank", "indeed", "glassdoor"
    "match_score": None,         # cloud session will score it
    "scraped_at": "2026-05-26T10:00:00",
}
SHARED.write_text(json.dumps(existing, indent=2))

# Then push:
import subprocess
subprocess.run(["git", "-C", "/path/to/claude-157", "add", "shared/jobs.json"])
subprocess.run(["git", "-C", "/path/to/claude-157", "commit", "-m", "sync: new jobs from local bot"])
subprocess.run(["git", "-C", "/path/to/claude-157", "push"])
```

**Option B — Just run python main.py sync**
After any manual additions to the cache:
```bash
python main.py sync
```

---

## If You Find a New Job Manually

1. Add it to cache (see "Add a manually found job" above)
2. Score it: `python main.py list` to verify it was cached
3. Run `python main.py resume <job_id>` to generate PDF
4. Run `python main.py apply <job_id>` after applying

---

*Last updated by cloud session: 2026-05-26*
*Branch: claude/memory-form-clouds-access-bC5CO*
