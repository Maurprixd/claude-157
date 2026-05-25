#!/usr/bin/env python3
"""
Telegram bot for Mauricio's job scraper.
Run this on your PC — then control everything from your phone via Telegram.

Setup (one-time):
  1. Message @BotFather on Telegram → /newbot → copy the token
  2. Add TELEGRAM_TOKEN=<your token> to your .env file
  3. Add TELEGRAM_CHAT_ID=<your chat ID> to .env (get it by messaging @userinfobot)
  4. pip install python-telegram-bot
  5. python bot.py

Commands from your phone:
  /scrape          — run full scrape + AI match + Notion filter
  /list            — show all cached jobs scored ≥50
  /resume <job_id> — generate tailored PDF and send it to you
  /apply <job_id>  — mark job as Applied in Notion
  /cover <job_id>  — generate cover letter and send it to you
  /help            — show this list
"""
import os
import sys
import pathlib
import asyncio
import subprocess
import time
import json
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

try:
    from telegram import Update, constants
    from telegram.ext import (
        Application,
        CommandHandler,
        ContextTypes,
    )
except ImportError:
    print("\n[ERROR] python-telegram-bot not installed.")
    print("  Run: pip install python-telegram-bot")
    sys.exit(1)

# ── Auth ──────────────────────────────────────────────────────────────────────

TOKEN = os.getenv("TELEGRAM_TOKEN")
ALLOWED_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # only you can use this bot

if not TOKEN:
    print("\n[ERROR] TELEGRAM_TOKEN not set in .env")
    print("  1. Message @BotFather on Telegram → /newbot → copy the token")
    print("  2. Add TELEGRAM_TOKEN=<token> to your .env file")
    sys.exit(1)

# ── Helpers ───────────────────────────────────────────────────────────────────

CACHE_PATH = pathlib.Path(__file__).parent / ".job_cache.json"
OUTPUTS_DIR = pathlib.Path(__file__).parent / "outputs"


def _auth_check(update: Update) -> bool:
    """Return True if message is from the allowed chat."""
    if ALLOWED_CHAT_ID and str(update.effective_chat.id) != ALLOWED_CHAT_ID:
        return False
    return True


def _load_cache() -> dict:
    if not CACHE_PATH.exists():
        return {}
    with open(CACHE_PATH) as f:
        return json.load(f)


def _format_job(job: dict, rank: int) -> str:
    score = job.get("match_score") or 0
    status = "✓ Active" if job.get("is_active") == "active" else "?"
    applied = " ✉️ Applied" if job.get("applied") else ""
    lines = [
        f"*#{rank} — {score}/100* {applied}",
        f"*{job.get('title', '?')}* @ {job.get('company', '?')}",
        f"📍 {job.get('location', '?')}  {status}",
        f"🎯 {job.get('odds_of_getting', 'N/A')}",
        f"🆔 `{job.get('job_id', '?')}`",
        f"🔗 {job.get('url', '')}",
    ]
    if job.get("key_strengths"):
        lines.append("✅ " + " | ".join(job["key_strengths"][:2]))
    if job.get("key_gaps"):
        lines.append("⚠️ " + " | ".join(job["key_gaps"][:2]))
    return "\n".join(lines)


# ── Command handlers ──────────────────────────────────────────────────────────

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _auth_check(update):
        return
    text = (
        "🤖 *Job Scraper Bot*\n\n"
        "/scrape — fresh scrape \\+ AI match \\+ Notion filter\n"
        "/list — show cached jobs \\(score ≥50\\)\n"
        "/resume `<job_id>` — tailored PDF resume\n"
        "/cover `<job_id>` — cover letter\n"
        "/apply `<job_id>` — log as Applied in Notion\n"
        "/help — this message"
    )
    await update.message.reply_text(text, parse_mode=constants.ParseMode.MARKDOWN_V2)


async def cmd_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _auth_check(update):
        return

    cache = _load_cache()
    if not cache:
        await update.message.reply_text("No cached jobs. Run /scrape first.")
        return

    jobs = sorted(
        cache.values(),
        key=lambda j: j.get("match_score") or 0,
        reverse=True,
    )
    qualified = [j for j in jobs if (j.get("match_score") or 0) >= 50]

    if not qualified:
        await update.message.reply_text(
            "No jobs with score ≥50 in cache. Run /scrape to refresh."
        )
        return

    await update.message.reply_text(
        f"📋 *{len(qualified)} jobs scored ≥50*",
        parse_mode=constants.ParseMode.MARKDOWN,
    )
    for i, job in enumerate(qualified[:10], 1):
        await update.message.reply_text(
            _format_job(job, i),
            parse_mode=constants.ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )


async def cmd_scrape(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _auth_check(update):
        return

    await update.message.reply_text(
        "🔍 Starting scrape... this takes 3-8 min. I'll message you when done."
    )

    try:
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "main.py", "scrape",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=str(pathlib.Path(__file__).parent),
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=600)
        output = stdout.decode("utf-8", errors="replace")

        # Extract summary line
        lines = output.splitlines()
        summary_lines = [l for l in lines if "Scored" in l or "Total" in l or "Removed" in l]
        summary = "\n".join(summary_lines) if summary_lines else "Done."

        await update.message.reply_text(f"✅ Scrape complete!\n\n{summary}\n\nRun /list to see results.")

    except asyncio.TimeoutError:
        await update.message.reply_text("⏱ Scrape timed out after 10 minutes. Try again.")
    except Exception as e:
        await update.message.reply_text(f"❌ Scrape failed: {e}")


async def cmd_resume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _auth_check(update):
        return

    if not context.args:
        await update.message.reply_text(
            "Usage: /resume <job_id>\nGet the job_id from /list"
        )
        return

    job_id = context.args[0].strip()
    await update.message.reply_text(f"📄 Generating resume for `{job_id}`...", parse_mode="Markdown")

    try:
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "main.py", "resume", job_id,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=str(pathlib.Path(__file__).parent),
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=300)
        output = stdout.decode("utf-8", errors="replace")

        # Find the PDF path in output
        pdf_path = None
        for line in output.splitlines():
            if line.strip().endswith(".pdf") and ("outputs/" in line or "Resume ready" in line):
                # Extract path from "Resume ready: outputs/resume_..."
                parts = line.strip().split()
                candidate = parts[-1]
                p = pathlib.Path(pathlib.Path(__file__).parent / candidate)
                if p.exists():
                    pdf_path = p
                    break

        # Fallback: search outputs dir
        if not pdf_path:
            company_slug = job_id.replace("jobbank_", "").replace("linkedin_", "")[:15]
            candidates = sorted(OUTPUTS_DIR.glob(f"resume_*{job_id[:12]}*.pdf"), reverse=True)
            if candidates:
                pdf_path = candidates[0]

        if pdf_path and pdf_path.exists():
            with open(pdf_path, "rb") as f:
                await update.message.reply_document(
                    document=f,
                    filename=pdf_path.name,
                    caption=f"✅ Tailored resume ready\nReview before sending!",
                )
        else:
            await update.message.reply_text(
                f"⚠️ Resume generated but PDF not found.\n\nOutput:\n```\n{output[-800:]}\n```",
                parse_mode="Markdown",
            )

    except asyncio.TimeoutError:
        await update.message.reply_text("⏱ Resume generation timed out (claude CLI may be slow).")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def cmd_cover(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _auth_check(update):
        return

    if not context.args:
        await update.message.reply_text("Usage: /cover <job_id>")
        return

    job_id = context.args[0].strip()
    await update.message.reply_text(f"✍️ Generating cover letter for `{job_id}`...", parse_mode="Markdown")

    try:
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "main.py", "cover", job_id,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=str(pathlib.Path(__file__).parent),
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=300)
        output = stdout.decode("utf-8", errors="replace")

        # Find txt file in outputs
        txt_candidates = sorted(
            OUTPUTS_DIR.glob(f"cover_*{job_id[:12]}*.txt"), reverse=True
        )

        if txt_candidates:
            text = txt_candidates[0].read_text()
            # Split into chunks (Telegram 4096 char limit)
            chunks = [text[i : i + 3900] for i in range(0, len(text), 3900)]
            for chunk in chunks:
                await update.message.reply_text(chunk)
        else:
            # Send raw output if no file found
            preview = output[:3900] if output else "No output."
            await update.message.reply_text(f"📝 Cover letter:\n\n{preview}")

    except asyncio.TimeoutError:
        await update.message.reply_text("⏱ Cover letter timed out.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def cmd_apply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _auth_check(update):
        return

    if not context.args:
        await update.message.reply_text("Usage: /apply <job_id>")
        return

    job_id = context.args[0].strip()
    await update.message.reply_text(f"📬 Logging `{job_id}` to Notion...", parse_mode="Markdown")

    try:
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "main.py", "apply", job_id,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=str(pathlib.Path(__file__).parent),
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=30)
        output = stdout.decode("utf-8", errors="replace")

        if proc.returncode == 0:
            await update.message.reply_text(f"✅ Logged as Applied!\n\n{output.strip()}")
        else:
            await update.message.reply_text(f"❌ Failed:\n{output.strip()}")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print(f"[bot] Starting Mauricio's Job Scraper Bot...")
    print(f"[bot] Token: {'set ✓' if TOKEN else 'MISSING ✗'}")
    print(f"[bot] Chat ID filter: {ALLOWED_CHAT_ID or 'none (open to anyone — set TELEGRAM_CHAT_ID)'}")
    print(f"[bot] Listening for commands...")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("start", cmd_help))
    app.add_handler(CommandHandler("list", cmd_list))
    app.add_handler(CommandHandler("scrape", cmd_scrape))
    app.add_handler(CommandHandler("resume", cmd_resume))
    app.add_handler(CommandHandler("cover", cmd_cover))
    app.add_handler(CommandHandler("apply", cmd_apply))

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
