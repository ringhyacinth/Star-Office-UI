#!/usr/bin/env python3
"""Star Office UI security preflight checker (non-destructive).

Checks:
- weak/default secrets in env
- risky tracked files in git index
- known API key patterns in tracked files
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(cmd: list[str]) -> tuple[int, str, str]:
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def is_strong_secret(v: str) -> bool:
    if not v:
        return False
    s = v.strip()
    if len(s) < 24:
        return False
    low = s.lower()
    for token in ("change-me", "default", "example", "test", "dev"):
        if token in low:
            return False
    return True


def is_strong_pass(v: str) -> bool:
    if not v:
        return False
    s = v.strip()
    if s == "1234":
        return False
    return len(s) >= 8


def tracked_files() -> list[str]:
    code, out, _ = run(["git", "ls-files"])
    if code != 0:
        return []
    return [x for x in out.splitlines() if x.strip()]


def file_has_secret_pattern(path: Path) -> list[str]:
    hits: list[str] = []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return hits

    patterns = [
        (r"AIza[0-9A-Za-z\-_]{20,}", "Google/Gemini API key-like token"),
        (r"sk-[A-Za-z0-9]{16,}", "Generic sk-* token"),
        (r"AKIA[0-9A-Z]{16}", "AWS access key-like token"),
    ]
    for pat, label in patterns:
        if re.search(pat, text):
            hits.append(label)
    return hits


def main() -> int:
    print("[security-check] Star Office UI preflight")

    failures: list[str] = []
    warnings: list[str] = []

    env_mode = (os.getenv("STAR_OFFICE_ENV") or os.getenv("FLASK_ENV") or "").strip().lower()
    in_prod = env_mode in {"prod", "production"}

    secret = os.getenv("FLASK_SECRET_KEY") or os.getenv("STAR_OFFICE_SECRET") or ""
    drawer_pass = os.getenv("ASSET_DRAWER_PASS") or ""

    if in_prod:
        if not is_strong_secret(secret):
            failures.append("Weak/missing FLASK_SECRET_KEY (or STAR_OFFICE_SECRET) in production")
        if not is_strong_pass(drawer_pass):
            failures.append("Weak/missing ASSET_DRAWER_PASS in production")
    else:
        if not secret:
            warnings.append("FLASK_SECRET_KEY not set (ok for local dev, not for production)")
        if not drawer_pass:
            warnings.append("ASSET_DRAWER_PASS not set (defaults may be unsafe for public exposure)")

    tracked = tracked_files()
    risky_tracked = [
        "runtime-config.json",
        "join-keys.json",
        "office-agent-state.json",
    ]
    for f in risky_tracked:
        if f in tracked:
            failures.append(f"Risky runtime file is tracked by git: {f}")

    # scan tracked text-ish files for common secret patterns
    for rel in tracked:
        if rel.startswith(".git/"):
            continue
        p = ROOT / rel
        if not p.exists() or p.is_dir():
            continue
        if p.stat().st_size > 2_000_000:
            continue
        hits = file_has_secret_pattern(p)
        for h in hits:
            failures.append(f"Potential secret pattern in tracked file: {rel} ({h})")

    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  - {w}")

    if failures:
        print("\nFAIL:")
        for f in failures:
            print(f"  - {f}")
        print("\nResult: FAILED")
        return 1

    print("\nResult: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
