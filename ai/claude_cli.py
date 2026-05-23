"""
Shared helper that calls the local `claude` CLI (Claude Code).
Uses your Pro subscription — no separate API key needed.
"""
import shutil
import subprocess
import sys
import time


def check_claude_cli() -> None:
    """Raise a clear error if the claude CLI is not installed/authenticated."""
    if not shutil.which("claude"):
        print(
            "\n[ERROR] Claude CLI not found on this machine.\n"
            "  1. Install Claude Code: https://claude.ai/code\n"
            "  2. Sign in with your Claude Pro account\n"
            "  3. Run this script again"
        )
        sys.exit(1)


def call_claude(prompt: str, timeout: int = 120, retries: int = 3) -> str:
    """
    Send a prompt to the claude CLI and return the response text.
    Uses your Claude Pro subscription via the locally installed CLI.
    Retries up to `retries` times with exponential backoff on failure.
    """
    check_claude_cli()
    last_error = None
    for attempt in range(retries):
        try:
            result = subprocess.run(
                ["claude", "-p", prompt],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            if result.returncode == 0:
                return result.stdout.strip()
            last_error = result.stderr.strip() or f"exit code {result.returncode}"
        except subprocess.TimeoutExpired:
            last_error = "timeout"

        if attempt < retries - 1:
            wait = 10 * (2 ** attempt)  # 10s, 20s, 40s
            print(f"  [claude_cli] Retrying in {wait}s (attempt {attempt + 1}/{retries})...")
            time.sleep(wait)

    raise RuntimeError(f"Claude CLI failed after {retries} attempts: {last_error}")


def call_claude_streaming(prompt: str, timeout: int = 120) -> str:
    """
    Send a prompt to the claude CLI and stream the output to the terminal.
    Returns the full response text when done.
    """
    check_claude_cli()
    proc = subprocess.Popen(
        ["claude", "-p", prompt],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    full_text = ""
    for char in iter(lambda: proc.stdout.read(1), ""):
        print(char, end="", flush=True)
        full_text += char
    proc.wait(timeout=timeout)
    return full_text
