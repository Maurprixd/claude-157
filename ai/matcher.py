"""
Claude-powered job matching.
Uses the local claude CLI (your Pro subscription) — no API key needed.
"""
import json

from ai.claude_cli import call_claude, check_claude_cli
from profile.mauricio import CANDIDATE_PROFILE
from scraper.models import Job

MIN_SCORE = CANDIDATE_PROFILE["min_match_score"]

_CANDIDATE_CONTEXT = f"""
## Candidate: {CANDIDATE_PROFILE['name']}
Location: {CANDIDATE_PROFILE['location']} ({CANDIDATE_PROFILE['relocation_note']})

### Education
{CANDIDATE_PROFILE['education'][0]['degree']} — {CANDIDATE_PROFILE['education'][0]['school']}
Expected graduation: {CANDIDATE_PROFILE['education'][0]['graduation']}
Relevant courses: {CANDIDATE_PROFILE['education'][0]['courses']}

### Experience (~1.5 years total)
**Lead Industrial Designer — WIMTACH / Centennial College** (Sept 2024 – Present)
- Lead designer for BuddhaCalm, a patent-pending wearable stress-relief device
- Full product cycle: concept sketching → SolidWorks assemblies → pogo pin charging architecture → production-ready prototypes
- Bambu Lab P1S high-fidelity 3D printing, KeyShot renders, Adobe Suite presentations
- User research, ergonomic analysis, mood boards, competitive benchmarking

**Product & Technical Designer — VIV66** (2023 – 2024)
- Technical construction specs for manufacturing feasibility
- Material tolerances, BOM documentation, fit refinement

### Skills
CAD: SolidWorks (Expert), Rhino 3D
Rendering: KeyShot
Prototyping: 3D Printing (Bambu Lab P1S, Prusa XL), FDM
Engineering: DFM, BOM, technical drawings, assembly drawings
Design: Hand sketching, concept ideation, CMF exploration, mood boards
Software: Adobe Photoshop, Illustrator, InDesign
Research: User research, competitive benchmarking, ergonomic analysis

### Target Roles
{', '.join(CANDIDATE_PROFILE['target_roles'])}

### Preferred Sectors
{', '.join(CANDIDATE_PROFILE['preferred_sectors'])}

### Languages
{', '.join(CANDIDATE_PROFILE['languages'])}
"""


def _build_scoring_prompt(job: Job) -> str:
    return f"""You are a ruthlessly honest career counselor evaluating a job posting for a specific candidate.
Score the job 1-100 for fit. Be very strict — only score 70+ for genuine strong alignment.
Most jobs should score 30-65. Respond ONLY with valid JSON. No extra text before or after the JSON.

{_CANDIDATE_CONTEXT}

---

## Job to Evaluate

Title: {job.title}
Company: {job.company}
Location: {job.location}
Salary: {job.salary or 'Not specified'}
Posted: {job.posted_date or 'Unknown'}

### Job Description:
{job.description[:3500]}

---

Score this job strictly. Consider:
1. Seniority — penalize heavily if 3+ years required (candidate has ~1.5 yrs)
2. Required tools — must overlap with SolidWorks, KeyShot, Rhino, 3D printing, DFM
3. Location — Toronto/ON preferred; remote Canada ok; other provinces ok but note it
4. Sector — medical devices, wearables, consumer electronics = strong bonus
5. Role type — must involve physical product design (not pure graphic/UX/fashion/interior)
6. P.Eng or professional license required → penalize significantly (candidate is still a student)

Respond with this exact JSON (no markdown, no ```):
{{
  "score": <integer 1-100>,
  "reasoning": "<one paragraph explaining the score>",
  "odds_of_getting": "<realistic % range + brief reason, e.g. '25-35% — strong technical match but wants 2 yrs exp'>",
  "key_strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "key_gaps": ["<gap 1>", "<gap 2>"]
}}"""


def score_job(job: Job) -> Job:
    """Score a single job. Returns the job with scores filled in."""
    try:
        raw = call_claude(_build_scoring_prompt(job))

        # Strip markdown code fences if present
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.split("```")[0]

        # Find the JSON object in case there's stray text
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end > start:
            raw = raw[start:end]

        data = json.loads(raw)
        job.match_score = int(data.get("score", 0))
        job.match_reasoning = data.get("reasoning", "")
        job.odds_of_getting = data.get("odds_of_getting", "")
        job.key_strengths = data.get("key_strengths", [])
        job.key_gaps = data.get("key_gaps", [])
    except Exception as e:
        print(f"  [matcher] Error scoring {job.job_id}: {e}")
        job.match_score = 0
        job.match_reasoning = f"Scoring error: {e}"

    return job


def score_jobs_batch(jobs: list[Job], min_score: int = MIN_SCORE) -> list[Job]:
    """Score all jobs via claude CLI, return those meeting min_score."""
    check_claude_cli()
    scored = []

    for i, job in enumerate(jobs):
        print(f"  [matcher] Scoring {i+1}/{len(jobs)}: {job.title} @ {job.company}")
        score_job(job)
        print(f"    → Score: {job.match_score}/100")
        scored.append(job)

    qualified = [j for j in scored if (j.match_score or 0) >= min_score]
    print(f"  [matcher] {len(qualified)}/{len(scored)} jobs scored ≥{min_score}")
    return qualified
