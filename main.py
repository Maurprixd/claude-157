#!/usr/bin/env python3
"""
Job Scraper — Mauricio Mena
Always reads profile/mauricio.py before any search to stay grounded in your actual experience.

Usage:
  python main.py scrape              # Scrape + AI match + verify + report
  python main.py list                # Show cached scored jobs
  python main.py resume <job_id>     # Generate custom tailored PDF resume
  python main.py cover <job_id>      # Generate cover letter (streams to terminal)
  python main.py apply <job_id>      # Log job to Notion as Applied
"""
import os
import pathlib
import subprocess
import sys
import time

from dotenv import load_dotenv

load_dotenv()

import click

from profile.mauricio import CANDIDATE_PROFILE
from scraper.models import Job, VerificationStatus
from storage.cache import JobCache

SHARED_DIR = pathlib.Path("shared")
BRANCH = "claude/memory-form-clouds-access-bC5CO"


def _git_sync(message: str = "sync: update job cache") -> bool:
    """
    Commit and push shared/jobs.json so the cloud session can read it.
    Returns True if push succeeded, False if git is not available or push failed.
    Both Claude sessions share data through this file in the git repo.
    """
    try:
        SHARED_DIR.mkdir(exist_ok=True)
        cache_file = SHARED_DIR / "jobs.json"
        if not cache_file.exists():
            return False

        # Check if there's anything to commit
        status = subprocess.run(
            ["git", "status", "--porcelain", str(cache_file)],
            capture_output=True, text=True
        )
        if not status.stdout.strip():
            return True  # nothing changed, no need to push

        subprocess.run(["git", "add", str(cache_file)], check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", message],
            check=True, capture_output=True
        )
        subprocess.run(
            ["git", "push", "-u", "origin", BRANCH],
            check=True, capture_output=True
        )
        print(f"  [sync] Pushed shared/jobs.json → cloud session can now see these results")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  [sync] Git push failed (working offline): {e}")
        return False
    except FileNotFoundError:
        return False  # git not available


def _print_job(rank: int, job: Job) -> None:
    active_icon = {
        VerificationStatus.ACTIVE: "✓ ACTIVE",
        VerificationStatus.EXPIRED: "✗ EXPIRED",
        VerificationStatus.UNKNOWN: "? UNVERIFIED",
    }[job.is_active]
    print(f"\n#{rank}  SCORE: {job.match_score}/100  {active_icon}")
    print(f"    {job.title} — {job.company}")
    print(f"    Location: {job.location}")
    if job.salary:
        print(f"    Salary: {job.salary}")
    print(f"    Source: {job.source.value} | ID: {job.job_id}")
    print(f"    URL: {job.url}")
    print(f"    Odds: {job.odds_of_getting or 'N/A'}")
    if job.key_strengths:
        print(f"    Strengths: {' | '.join(job.key_strengths)}")
    if job.key_gaps:
        print(f"    Gaps: {' | '.join(job.key_gaps)}")


def _print_report(jobs: list[Job], sources: list[str], min_score: int) -> None:
    active_jobs = [j for j in jobs if j.is_active != VerificationStatus.EXPIRED]
    print(f"\n{'='*65}")
    print(f" JOB MATCH REPORT — {CANDIDATE_PROFILE['name']}")
    print(f" Sources: {', '.join(sources)} | Min score: {min_score}")
    print(f"{'='*65}")

    if not active_jobs:
        print("\n  No matching jobs found this run. Try again later or broaden sources.")
    else:
        for i, job in enumerate(active_jobs, 1):
            _print_job(i, job)

    print(f"\n{'='*65}")
    print(f"Total scraped: {len(jobs)} | Scored ≥{min_score}: {len(jobs)} | Active: {len(active_jobs)}")
    print(f"\nNext steps:")
    print(f"  python main.py resume <job_id>   → tailored PDF resume")
    print(f"  python main.py cover  <job_id>   → cover letter (streamed)")
    print(f"  python main.py apply  <job_id>   → log to Notion")
    print(f"{'='*65}\n")


@click.group()
def cli():
    """Job scraper and application assistant for Mauricio Mena.

    Always reads profile/mauricio.py before searching — no hallucinations about your background.
    """
    pass


@cli.command()
@click.option(
    "--sources",
    default="jobbank,indeed,linkedin",
    show_default=True,
    help="Comma-separated sources: jobbank,indeed,linkedin",
)
@click.option(
    "--min-score",
    default=CANDIDATE_PROFILE["min_match_score"],
    show_default=True,
    help="Minimum AI match score (1-100) to include in report",
)
@click.option(
    "--no-verify",
    is_flag=True,
    default=False,
    help="Skip liveness verification (faster but may include expired listings)",
)
@click.option(
    "--no-cache",
    is_flag=True,
    default=False,
    help="Force fresh scrape, ignore cached results",
)
def scrape(sources: str, min_score: int, no_verify: bool, no_cache: bool):
    """Scrape jobs, score with AI, verify active, print report."""
    source_list = [s.strip() for s in sources.split(",")]
    cache = JobCache()

    print(f"\n[profile] Loaded: {CANDIDATE_PROFILE['name']}")
    print(f"[profile] Target roles: {', '.join(CANDIDATE_PROFILE['target_roles'][:3])}...")
    print(f"[profile] Min match score: {min_score}\n")

    # --- Scrape ---
    all_raw: list[Job] = []

    if "jobbank" in source_list:
        print("[scraper] Job Bank Canada...")
        from scraper import jobbank
        try:
            all_raw.extend(jobbank.scrape())
        except Exception as e:
            print(f"  [jobbank] Failed: {e}")

    if "indeed" in source_list:
        print("\n[scraper] Indeed Canada...")
        from scraper import indeed
        try:
            all_raw.extend(indeed.scrape())
        except Exception as e:
            print(f"  [indeed] Failed: {e}")

    if "linkedin" in source_list:
        print("\n[scraper] LinkedIn Jobs...")
        from scraper import linkedin
        try:
            all_raw.extend(linkedin.scrape())
        except Exception as e:
            print(f"  [linkedin] Failed: {e}")

    # Deduplicate
    seen: set[str] = set()
    unique_jobs: list[Job] = []
    for job in all_raw:
        if job.job_id not in seen:
            seen.add(job.job_id)
            unique_jobs.append(job)

    print(f"\n[scraper] {len(unique_jobs)} unique jobs after deduplication")

    # Check cache for already-scored jobs
    if not no_cache:
        to_score = []
        for job in unique_jobs:
            cached = cache.get(job.job_id)
            if cached and cached.match_score is not None:
                unique_jobs[unique_jobs.index(job)] = cached
            else:
                to_score.append(job)
        print(f"[cache] {len(unique_jobs) - len(to_score)} from cache, {len(to_score)} to score")
    else:
        to_score = unique_jobs

    # --- AI Matching ---
    if to_score:
        print(f"\n[matcher] Scoring {len(to_score)} jobs with Claude AI (via your Pro subscription)...")
        from ai.matcher import score_jobs_batch
        qualified = score_jobs_batch(to_score, min_score=min_score)
    else:
        qualified = [j for j in unique_jobs if (j.match_score or 0) >= min_score]

    # --- Filter against Notion tracker (skip already-applied companies) ---
    if os.getenv("NOTION_TOKEN") and qualified:
        try:
            print("\n[notion] Checking tracker for already-applied jobs...")
            from notion.logger import NotionLogger
            notion = NotionLogger()
            applied_companies, applied_job_ids = notion.get_applied_entries()
            before = len(qualified)
            filtered = []
            for job in qualified:
                if job.job_id in applied_job_ids:
                    print(f"  [notion] Skip (applied): {job.title} @ {job.company}")
                    continue
                if job.company.lower().strip() in applied_companies:
                    print(f"  [notion] Skip (company already applied): {job.company}")
                    continue
                filtered.append(job)
            if before > len(filtered):
                print(f"  [notion] Removed {before - len(filtered)} already-applied job(s)")
            qualified = filtered
        except Exception as e:
            print(f"  [notion] Could not check tracker (skipping filter): {e}")

    # --- Verify ---
    if not no_verify and qualified:
        print(f"\n[verifier] Checking {len(qualified)} jobs are still active...")
        from verifier.checker import verify_jobs_batch
        qualified = verify_jobs_batch(qualified)

    # --- Cache all scored jobs ---
    for job in unique_jobs:
        cache.set(job)
    for job in qualified:
        cache.set(job)
    cache.save()

    # --- Sync to git so cloud session sees the same results ---
    from datetime import datetime
    _git_sync(f"sync: scrape {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} — {len(unique_jobs)} jobs, {len(qualified)} matched")

    # --- Report ---
    qualified_sorted = sorted(qualified, key=lambda j: j.match_score or 0, reverse=True)
    _print_report(qualified_sorted, source_list, min_score)


@cli.command(name="list")
@click.option("--min-score", default=0, help="Filter by minimum score")
def list_jobs(min_score: int):
    """Show previously scraped and scored jobs from cache."""
    cache = JobCache()
    jobs = cache.get_all_scored_sorted()
    if min_score > 0:
        jobs = [j for j in jobs if (j.match_score or 0) >= min_score]

    if not jobs:
        print("No scored jobs in cache. Run: python main.py scrape")
        return

    print(f"\nCached jobs (sorted by match score):")
    for i, job in enumerate(jobs, 1):
        _print_job(i, job)
    print(f"\nTotal: {len(jobs)} jobs\n")


@cli.command()
@click.argument("job_id")
@click.option("--output-dir", default="outputs", show_default=True)
def resume(job_id: str, output_dir: str):
    """Generate a custom tailored PDF resume for JOB_ID."""
    cache = JobCache()
    job = cache.get(job_id)
    if not job:
        print(f"Job '{job_id}' not found in cache. Run scrape first.")
        sys.exit(1)

    print(f"\nGenerating tailored resume for: {job.title} @ {job.company}")

    from ai.resume_generator import generate_tailored_content
    from pdf.builder import build_resume

    tailored_profile = generate_tailored_content(job)

    pathlib.Path(output_dir).mkdir(exist_ok=True)
    company_slug = job.company.lower().replace(" ", "_")[:20]
    output_path = f"{output_dir}/resume_{company_slug}_{job_id[:10]}.pdf"

    build_resume(tailored_profile, output_path)
    print(f"\nResume ready: {output_path}")
    print("Tip: Open and review before sending. Always double-check for accuracy.")


@cli.command()
@click.argument("job_id")
@click.option("--output-dir", default="outputs", show_default=True)
def cover(job_id: str, output_dir: str):
    """Generate a cover letter for JOB_ID. Streams to terminal and saves."""
    cache = JobCache()
    job = cache.get(job_id)
    if not job:
        print(f"Job '{job_id}' not found in cache. Run scrape first.")
        sys.exit(1)

    from ai.cover_letter import generate_cover_letter
    generate_cover_letter(job)


@cli.command()
@click.argument("job_id")
def apply(job_id: str):
    """Log JOB_ID as 'Applied' in your Notion database."""
    cache = JobCache()
    job = cache.get(job_id)
    if not job:
        print(f"Job '{job_id}' not found in cache. Run scrape first.")
        sys.exit(1)

    if not os.getenv("NOTION_TOKEN"):
        print("[ERROR] NOTION_TOKEN not set. Add it to your .env file.")
        print("Get it from: https://www.notion.so/my-integrations")
        sys.exit(1)

    print(f"\nLogging to Notion: {job.title} @ {job.company}")

    from notion.logger import NotionLogger
    logger = NotionLogger()
    logger.mark_applied(job)

    job.applied = True
    job.applied_at = time.strftime("%Y-%m-%dT%H:%M:%S")
    cache.set(job)
    cache.save()

    # Sync so cloud session knows this job is now applied (won't recommend it again)
    _git_sync(f"sync: applied {job.company} — {job.title}")

    print(f"\nDone! Check your Notion database:")
    print(f"  https://www.notion.so/{os.getenv('NOTION_DATABASE_ID', 'fcadfa0f55a54b6f99b5e2fadfdf1ad9')}")


@cli.command()
def sync():
    """Push shared/jobs.json to git so the cloud session sees your latest results."""
    print("\n[sync] Pushing job cache to shared repository...")
    ok = _git_sync("sync: manual push from local session")
    if ok:
        print("[sync] Done — cloud session can now see all your scraped jobs.")
    else:
        print("[sync] Nothing to push (cache unchanged or git unavailable).")


if __name__ == "__main__":
    cli()
