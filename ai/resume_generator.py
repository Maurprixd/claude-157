"""
Claude-powered resume tailoring.
Uses claude-haiku-4-5 to rewrite bullets and emphasis for a specific job.
"""
import json
import os
import copy

import anthropic

from profile.mauricio import CANDIDATE_PROFILE
from scraper.models import Job

TAILOR_SYSTEM = """You are an expert resume writer for industrial designers.
Your task: tailor an existing resume for a specific job posting.

STRICT RULES:
- Never fabricate, invent, or exaggerate experience or skills
- Only reframe, reorder, and re-emphasize information that already exists
- Keep every bullet truthful and specific
- Adjust word choice to match the job's terminology when accurate
- Respond ONLY with valid JSON — no extra text"""


def _tailor_prompt(job: Job, profile: dict) -> str:
    exp_text = ""
    for exp in profile["experience"]:
        exp_text += f"\n**{exp['title']} — {exp['company']}** ({exp['dates']})\n"
        for b in exp["bullets"]:
            exp_text += f"  - {b}\n"

    skills_text = "\n".join(
        f"  {k}: {', '.join(v)}" for k, v in profile["skills"].items()
    )

    return f"""## Target Job
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

## Your Task
Return a JSON object with this exact structure — tailored for the job above:

{{
  "summary": "2-3 sentence summary targeting THIS specific role. Be specific.",
  "experience": [
    {{
      "title": "same title",
      "company": "same company",
      "location": "same location",
      "dates": "same dates",
      "bullets": ["rewritten bullet 1", "rewritten bullet 2", "..."]
    }}
  ],
  "skills_emphasis": ["skill1", "skill2", "skill3", "skill4", "skill5"],
  "tailoring_notes": "Brief note on what you emphasized and why"
}}

Rules:
- Rewrite up to 3 bullets per role to better match the job
- Keep bullets factually accurate to the original
- skills_emphasis: list the 5 most relevant skills for THIS job (from existing skills only)
- summary: mention the company name and role if natural"""


def generate_tailored_content(job: Job) -> dict:
    """Returns a tailored profile dict for PDF generation."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set.")

    client = anthropic.Anthropic(api_key=api_key)

    print(f"  [resume_gen] Tailoring resume for: {job.title} @ {job.company}")

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1500,
        system=TAILOR_SYSTEM,
        messages=[{"role": "user", "content": _tailor_prompt(job, CANDIDATE_PROFILE)}],
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

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
