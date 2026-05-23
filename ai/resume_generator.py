"""
Claude-powered resume tailoring.
Uses the local claude CLI (your Pro subscription) — no API key needed.
"""
import copy
import json

from ai.claude_cli import call_claude, check_claude_cli
from profile.mauricio import CANDIDATE_PROFILE
from scraper.models import Job


def _tailor_prompt(job: Job, profile: dict) -> str:
    exp_text = ""
    for exp in profile["experience"]:
        exp_text += f"\n**{exp['title']} — {exp['company']}** ({exp['dates']})\n"
        for b in exp["bullets"]:
            exp_text += f"  - {b}\n"

    skills_text = "\n".join(
        f"  {k}: {', '.join(v)}" for k, v in profile["skills"].items()
    )

    return f"""You are an expert resume writer for industrial designers.
Tailor the candidate's resume for the specific job below.

STRICT RULES:
- Never fabricate, invent, or exaggerate experience or skills
- Only reframe, reorder, and re-emphasize information that already exists
- Keep every bullet truthful and specific
- Adjust word choice to match the job's terminology when accurate
- Respond ONLY with valid JSON — no markdown, no extra text

## Target Job
Title: {job.title}
Company: {job.company}
Location: {job.location}
Salary: {job.salary or 'Not specified'}

### Job Description:
{job.description[:3000]}

---

## Current Resume Content

### Summary:
{profile['summary']}

### Experience:
{exp_text}

### Skills:
{skills_text}

---

Return this exact JSON structure (no markdown fences):
{{
  "summary": "<2-3 sentence summary targeting THIS specific role and company>",
  "experience": [
    {{
      "title": "<same title as original>",
      "company": "<same company>",
      "location": "<same location>",
      "dates": "<same dates>",
      "bullets": ["<rewritten bullet 1>", "<rewritten bullet 2>", "..."]
    }}
  ],
  "skills_emphasis": ["<skill1>", "<skill2>", "<skill3>", "<skill4>", "<skill5>"],
  "tailoring_notes": "<brief note on what you emphasized and why>"
}}

Rules:
- Rewrite up to 3 bullets per role to better match the job
- Keep bullets factually accurate to the original
- skills_emphasis: list the 5 most relevant skills for THIS job (from existing skills only)
- summary: naturally mention the role or company if it fits"""


def generate_tailored_content(job: Job) -> dict:
    """Returns a tailored profile dict ready for PDF generation."""
    check_claude_cli()
    print(f"  [resume_gen] Tailoring resume for: {job.title} @ {job.company}")

    raw = call_claude(_tailor_prompt(job, CANDIDATE_PROFILE), timeout=180)

    # Strip markdown fences if present
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.split("```")[0]

    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start != -1 and end > start:
        raw = raw[start:end]

    data = json.loads(raw)

    tailored = copy.deepcopy(CANDIDATE_PROFILE)
    tailored["summary"] = data.get("summary", CANDIDATE_PROFILE["summary"])

    for i, exp_data in enumerate(data.get("experience", [])):
        if i < len(tailored["experience"]):
            tailored["experience"][i]["bullets"] = exp_data.get(
                "bullets", tailored["experience"][i]["bullets"]
            )

    emphasized = data.get("skills_emphasis", [])
    if emphasized:
        tailored["_skills_emphasis"] = emphasized

    print(f"  [resume_gen] Tailoring notes: {data.get('tailoring_notes', '')}")
    return tailored
