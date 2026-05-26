# Briefing for Local Claude Code Session
## How to connect your existing job hunter to the shared memory repo

Hey — I'm the cloud Claude session that built this job scraper repo.
Mauricio wants us to work as one team. Here's how.

---

## The Setup

We share data through one file: **`shared/jobs.json`** in this git repo.

- **You** (local) → scrape jobs from anywhere (Indeed, LinkedIn, Glassdoor, your
  existing bot, anywhere) → write results to `shared/jobs.json` → git push
- **Me** (cloud) → git pull → read `shared/jobs.json` → generate resumes,
  cover letters, plan strategy, score unscored jobs

The profile is also shared: **`profile/mauricio.py`** — read it before anything.

---

## What You Need To Do

### Step 1 — Pull the latest code
```bash
git pull origin claude/memory-form-clouds-access-bC5CO
```

### Step 2 — Connect your existing job hunter

Your existing bot/hunter saves jobs somewhere. Two options:

**Option A: Point it at shared/jobs.json directly**

Add this to your existing bot after it finds jobs:

```python
import json, pathlib, subprocess

REPO = pathlib.Path(__file__).parent  # adjust to actual repo path
SHARED = REPO / "shared" / "jobs.json"

# Load existing cache
jobs = json.loads(SHARED.read_text()) if SHARED.exists() else {}

# Add each job your bot found (minimum fields):
jobs["your_unique_job_id"] = {
    "job_id": "your_unique_job_id",        # e.g. "linkedin_1234567890"
    "title": "Junior Industrial Designer",
    "company": "Company Name",
    "location": "Toronto, ON",
    "url": "https://...",
    "description": "Full job description text",
    "source": "linkedin",                  # jobbank / indeed / linkedin / glassdoor / manual
    "match_score": None,                   # leave None — scoring happens via claude CLI
    "scraped_at": "2026-05-26T10:00:00",
    "is_active": "unknown",
    "applied": False,
}

# Save and push
SHARED.write_text(json.dumps(jobs, indent=2, default=str))
subprocess.run(["git", "-C", str(REPO), "add", "shared/jobs.json"], check=True)
subprocess.run(["git", "-C", str(REPO), "commit", "-m", "sync: jobs from local bot"], check=True)
subprocess.run(["git", "-C", str(REPO), "push"], check=True)
print("Pushed to shared repo — cloud Claude can now see these jobs")
```

**Option B: Run the built-in scraper + let it sync automatically**
```bash
python main.py scrape --sources jobbank,indeed,linkedin
# Auto-pushes shared/jobs.json when done
```

**Option C: Manual sync after any additions**
```bash
python main.py sync
```

---

## Scoring Unscored Jobs

After your bot pushes new jobs (with `match_score: null`), score them:

```bash
# This reads shared/jobs.json, scores unscored jobs via claude CLI, saves back
python main.py scrape --no-cache --sources jobbank
# Or just re-run list to see what's already scored:
python main.py list --min-score 0
```

To score a specific job that's already in the cache but unscored:
```python
from storage.cache import JobCache
from ai.matcher import score_job

cache = JobCache()
job = cache.get("your_job_id")
score_job(job)
cache.set(job)
cache.save()
# Then: python main.py sync
```

---

## The Scoring Prompt

Every job gets evaluated against Mauricio's full profile. The prompt reads
directly from `profile/mauricio.py` — so it always reflects his real experience,
never hallucinates. Key facts it knows:

- WIMTACH = real funded R&D, patent filed Feb 2026, shown at industry showcase
- VIV66 = apparel company → real soft goods / flexible materials experience
- Tools: SolidWorks (Expert), KeyShot, Rhino 3D, FDM 3D printing, DFM
- Sectors we want: medical devices, wearables, rehab, consumer electronics, sporting goods
- Sectors to skip: graphic design, interior design, software, civil/HVAC, retail
- Seniority: ~1.5 years professional, penalize if 3+ years strictly required
- Min score to surface: 50 (override with --min-score 40 to see more)

---

## Job Sources — Run Everything Here

| Source | Command / Method | Notes |
|--------|-----------------|-------|
| Job Bank Canada | `python main.py scrape --sources jobbank` | Most reliable |
| Indeed Canada | `python main.py scrape --sources indeed` | Works on your IP |
| LinkedIn Jobs | `python main.py scrape --sources linkedin` | Guest API |
| Glassdoor | Add playwright scraper (ask cloud Claude) | Needs chromium |
| Workopolis | Use WebFetch: workopolis.com/jobsearch/find-jobs?term=industrial+designer&job-location=Toronto | Canadian-only |
| Eluta.ca | Use WebFetch: eluta.ca/search?q=industrial+designer&l=Toronto | Aggregator |
| ZipRecruiter | RSS: ziprecruiter.com/candidate/search?search=industrial+designer&location=Toronto | |
| Your existing bot | Write results to shared/jobs.json + push | Any format, just map the fields |

---

## After Your Bot Finds Jobs → Tell Cloud Claude

Once you push `shared/jobs.json`, start a cloud session (claude.ai/code) and say:

> "Pull the latest shared/jobs.json and tell me the top new leads"

The cloud session will:
1. `git pull`
2. Read shared/jobs.json
3. Show you new jobs that haven't been reviewed
4. Generate resumes and cover letters on demand

---

## Key Commands

```bash
git pull origin claude/memory-form-clouds-access-bC5CO  # get latest
python main.py scrape                                    # full scrape + score + sync
python main.py list --min-score 40                       # see all leads
python main.py sync                                      # push cache to cloud
python main.py resume <job_id>                           # PDF resume
python main.py cover <job_id>                            # cover letter
python main.py apply <job_id>                            # log to Notion + sync
python bot.py                                            # Telegram phone bot
```

---

*Written by cloud session — 2026-05-26*
*Branch: claude/memory-form-clouds-access-bC5CO*
