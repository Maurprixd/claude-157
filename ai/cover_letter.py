"""
Claude-powered cover letter generator.
Uses the local claude CLI (your Pro subscription) — no API key needed.
Streams output to terminal so you see it as it writes.
"""
import pathlib
import time

from ai.claude_cli import call_claude_streaming, check_claude_cli
from profile.mauricio import CANDIDATE_PROFILE
from scraper.models import Job


def _cover_prompt(job: Job, profile: dict) -> str:
    exp = profile["experience"][0]
    bullets = "\n".join(f"  - {b}" for b in exp["bullets"][:3])

    return f"""You write compelling, specific cover letters for industrial designers.
Never use generic phrases like "I am excited to apply" or "I am a hard worker".
Be specific, confident, and brief. Target: 300-400 words.
Write in a direct, professional tone that reflects design-industry culture.

Write a cover letter for {profile['name']} applying to:

Role: {job.title}
Company: {job.company}
Location: {job.location}
{f"Salary: {job.salary}" if job.salary else ""}

Job Description (key parts):
{job.description[:2000]}

---

Candidate background:
- Graduating April 2026, Advanced Diploma in Industrial and Product Design, Centennial College
- Lead designer for BuddhaCalm — patent-pending wearable stress-relief device at WIMTACH
- SolidWorks expert, KeyShot, 3D printing (Bambu Lab P1S), DFM, BOM documentation
- Experience at VIV66 doing technical construction specs and manufacturing feasibility
- Bilingual: English (Fluent), Spanish (Native), French (basic)

Most relevant recent experience:
{bullets}

---

Structure:
1. Opening hook: something specific about THIS company/role (not generic excitement)
2. Paragraph 1: Connect Mauricio's most relevant project to this specific role
3. Paragraph 2: 2 concrete achievements that prove he can do this job
4. Paragraph 3: What makes him distinctive (bilingual, patent-pending project, Centennial Advanced Diploma expected 2026)
5. Closing: confident, professional call to action

Do NOT use:
- "I am excited to apply"
- "I am a team player"
- "I am passionate about design"
- Any cliché opener

Address to "Hiring Manager" unless the job description mentions a specific name.
Include contact at the end: {profile['email']} | {profile['phone']} | {profile['website']}"""


def generate_cover_letter(job: Job) -> str:
    """Stream a cover letter to the terminal and save it. Returns the file path."""
    check_claude_cli()

    print(f"\n{'='*60}")
    print(f"Cover Letter: {job.title} @ {job.company}")
    print(f"{'='*60}\n")

    full_text = call_claude_streaming(_cover_prompt(job, CANDIDATE_PROFILE))

    print(f"\n{'='*60}\n")

    pathlib.Path("outputs").mkdir(exist_ok=True)
    timestamp = int(time.time())
    output_path = f"outputs/cover_{job.job_id}_{timestamp}.txt"
    pathlib.Path(output_path).write_text(full_text, encoding="utf-8")
    print(f"Saved to: {output_path}")
    return output_path
