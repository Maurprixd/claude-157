"""
Claude-powered job matching.
Uses claude-haiku-4-5 for fast batch scoring with prompt caching on profile.
"""
import json
import os
from typing import Optional

import anthropic

from profile.mauricio import CANDIDATE_PROFILE
from scraper.models import Job

MIN_SCORE = CANDIDATE_PROFILE["min_match_score"]

SYSTEM_PROMPT = """You are a ruthlessly honest career counselor evaluating job postings for a specific candidate.
Score each job 1-100 for fit. Be very strict — only score 70+ when there is genuine strong alignment.
Most jobs should score 30-65. Only genuinely great fits get 70+.
Respond ONLY with valid JSON matching the requested schema. No extra text."""

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

SCORE_SCHEMA = {
    "type": "object",
    "properties": {
        "score": {"type": "integer", "minimum": 1, "maximum": 100},
        "reasoning": {"type": "string"},
        "odds_of_getting": {
            "type": "string",
            "description": "Realistic % range + brief explanation, e.g. '25-35% — strong technical match but wants 2 yrs exp'"
        },
        "key_strengths": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Top 2-3 reasons candidate fits this role"
        },
        "key_gaps": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Top 1-3 gaps or concerns"
        },
    },
    "required": ["score", "reasoning", "odds_of_getting", "key_strengths", "key_gaps"],
    "additionalProperties": False,
}


def _render_job_prompt(job: Job) -> str:
    return f"""## Job to Evaluate

Title: {job.title}
Company: {job.company}
Location: {job.location}
Source: {job.source.value}
Salary: {job.salary or 'Not specified'}
Posted: {job.posted_date or 'Unknown'}

### Full Job Description:
{job.description[:3500]}

---

Score this job for the candidate. Consider strictly:
1. Seniority level — penalize heavily if 3+ years required (candidate has ~1.5 yrs)
2. Required tools — must overlap with SolidWorks, KeyShot, Rhino, 3D printing, DFM
3. Location — Toronto/ON preferred; remote Canada ok; other provinces ok but note it
4. Sector fit — medical devices, wearables, consumer electronics = strong bonus
5. Role type — must involve physical product design (not pure graphic/UX/fashion)
6. P.Eng or professional license required → penalize significantly (candidate is still a student)

Respond with JSON only."""


def score_job(job: Job, client: anthropic.Anthropic) -> Job:
    """Score a single job against Mauricio's profile. Returns the job with scores filled in."""
    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": _CANDIDATE_CONTEXT,
                            "cache_control": {"type": "ephemeral"},
                        }
                    ],
                },
                {
                    "role": "assistant",
                    "content": "Understood. I have reviewed the candidate profile. Please provide the job posting to evaluate.",
                },
                {
                    "role": "user",
                    "content": _render_job_prompt(job),
                },
            ],
        )

        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
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


def score_jobs_batch(
    jobs: list[Job],
    min_score: int = MIN_SCORE,
) -> list[Job]:
    """Score all jobs, return those meeting min_score. Uses Haiku with cached profile."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set in environment. Add it to your .env file.")

    client = anthropic.Anthropic(api_key=api_key)
    scored = []

    for i, job in enumerate(jobs):
        print(f"  [matcher] Scoring {i+1}/{len(jobs)}: {job.title} @ {job.company}")
        score_job(job, client)
        print(f"    → Score: {job.match_score}/100")
        scored.append(job)

    qualified = [j for j in scored if (j.match_score or 0) >= min_score]
    print(f"  [matcher] {len(qualified)}/{len(scored)} jobs scored ≥{min_score}")
    return qualified
