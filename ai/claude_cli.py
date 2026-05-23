"""
Shared helper that calls the local `claude` CLI (Claude Code).
Uses your Pro subscription — no separate API key needed.
"""
import shutil
import subprocess
import sys


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


def call_claude(prompt: str, timeout: int = 120) -> str:
    """
    Send a prompt to the claude CLI and return the response text.
    Uses your Claude Pro subscription via the locally installed CLI.
    """
    check_claude_cli()
    result = subprocess.run(
        ["claude", "-p", prompt],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Claude CLI returned error:\n{result.stderr.strip()}")
    return result.stdout.strip()


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
