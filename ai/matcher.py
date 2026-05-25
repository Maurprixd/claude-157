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
Portfolio: mauricio-mena.com | behance.net/gallery/217417729/Portfolio
Languages: English (Fluent), Spanish (Native), French (Basic — actively studying)

### Education
{CANDIDATE_PROFILE['education'][0]['degree']} — {CANDIDATE_PROFILE['education'][0]['school']}
Expected graduation: {CANDIDATE_PROFILE['education'][0]['graduation']}
Relevant courses: {CANDIDATE_PROFILE['education'][0]['courses']}

### Experience (~1.5 years professional + 3 years total design practice)

**Lead Industrial Designer — WIMTACH / Centennial College** (Sept 2024 – Present)
- Lead designer on BuddhaCalm: a patent-pending wearable stress-relief device (patent application
  filed Feb 2026; device selected for WIMTACH industry showcase). Full ownership from first sketch
  to production-ready prototype — not a class project, a real funded R&D program.
- Generates 15-20+ distinct concepts per design sprint; iterates across mechanism variations,
  enclosure geometry, CMF, and ergonomic form factors before converging on a direction.
- Built multi-fidelity prototypes: foam and cardboard mockups for early ergonomic validation,
  iterative FDM prints (Bambu Lab P1S) for mechanism testing, final assemblies integrating rigid
  housing, flexible contact surfaces, and pogo-pin charging hardware.
- Created SolidWorks assemblies with complex constraint relationships; produced DFM-ready parts
  and technical drawings for external manufacturing partners.
- Led user research sessions and ergonomic testing with target users; synthesized feedback into
  documented design changes across 4 prototype iterations — experience equivalent to focus-group
  facilitation and usability validation.
- Produced KeyShot photorealistic renders and Adobe Suite stakeholder decks for client-facing
  design reviews. Visible portfolio of this work at mauricio-mena.com.

**Product & Technical Designer — VIV66** (2023 – 2024)
- Developed multi-material technical construction specifications for soft goods (apparel) product
  lines — documenting stitch types, fabric callouts, hardware assembly, and tolerance requirements.
  This is direct soft goods / flexible materials design experience.
- Collaborated with production teams on fit refinement and material tolerance validation across a
  5-month development cycle; iterating samples for comfort, durability, and manufacturability.
- Produced BOM documentation and shop drawings for manufacturing handoff.

### Hard Skills
CAD: SolidWorks (Expert — assemblies, parts, drawings, DFM-compliant design), Rhino 3D (surface modelling)
Rendering: KeyShot (photorealistic renders, lifestyle visuals, client presentations)
Prototyping: FDM 3D printing (Bambu Lab P1S, Prusa XL), foam mockups, multi-material assemblies
Engineering: Design for Manufacturing (DFM), BOM preparation, technical and assembly drawings
Concept Design: Hand sketching, digital ideation, CMF exploration, mood boards, benchmarking
Software: Adobe Photoshop, Illustrator, InDesign

### Soft Skills
High-volume concept generation | Cross-functional team coordination | User research & synthesis
Fast iteration under tight timelines | Bilingual client communication (English + Spanish)

### Target Roles
{', '.join(CANDIDATE_PROFILE['target_roles'])}

### Preferred Sectors (strongest fit)
{', '.join(CANDIDATE_PROFILE['preferred_sectors'])}
"""


def _build_scoring_prompt(job: Job) -> str:
    return f"""You are a ruthlessly honest career counselor scoring job fit for a specific candidate.
Use the full 1-100 range calibrated as follows:
  80-100 = exceptional fit — tools match, sector match, seniority appropriate, would strongly recommend applying
  60-79  = solid fit — most requirements met, 1-2 manageable gaps, worth applying
  40-59  = partial fit — meaningful overlap but notable gaps (experience, tools, sector) that hurt odds
  20-39  = weak fit — only surface-level overlap, significant mismatches
  1-19   = not a fit — wrong role type, wrong tools, or experience floor far exceeds candidate level

Be strict about seniority and must-have tools. Be generous when the role is explicitly junior/entry-level
or has no strict experience requirement. Respond ONLY with valid JSON — no markdown, no extra text.

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

Scoring criteria (weight each explicitly in your reasoning):
1. SENIORITY MATCH (high weight) — penalize heavily if 3+ years strictly required; candidate has ~1.5 yrs
   professional + 3 yrs practice. "No strict experience requirement" or "junior/entry-level" = strong boost.
2. TOOLS OVERLAP (high weight) — core stack: SolidWorks, KeyShot, Rhino, FDM 3D printing, DFM.
   Missing 1 core tool = moderate gap. Missing all = disqualifying.
3. ROLE TYPE (high weight) — must be physical product / industrial design. Graphic design, UX-only,
   interior design, software = wrong category, score ≤ 25.
4. SECTOR BONUS — medical devices, wearables, rehab products, consumer electronics, sporting goods,
   health tech = boost 5-10 pts. Commodity manufacturing or unrelated = neutral.
5. LOCATION — Toronto or Ontario = neutral (preferred). Remote Canada = slight positive. Other province
   = small penalty. Outside Canada = large penalty.
6. SOFT GOODS — candidate has apparel/soft goods construction experience (VIV66). Boost if role values
   fabric, foam, or flexible material experience.
7. PORTFOLIO REQUIRED — candidate has a visible portfolio (mauricio-mena.com + Behance). No penalty.
8. LANGUAGE BONUS — French language asset = small boost for Quebec or bilingual roles.
9. P.ENG / PROFESSIONAL LICENSE REQUIRED → penalize significantly (candidate is a student, not licensed).

Respond with this exact JSON (no markdown, no ```):
{{
  "score": <integer 1-100>,
  "reasoning": "<2-3 sentences covering the main score drivers>",
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
