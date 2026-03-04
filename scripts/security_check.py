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
    write_api_guard_enabled = (os.getenv("STAR_OFFICE_WRITE_API_BEARER_ENABLED") or "").strip().lower() in {"1", "true", "yes", "on"}
    write_api_tokens = (os.getenv("STAR_OFFICE_WRITE_API_TOKENS") or "").strip()
    max_upload_mb_raw = (os.getenv("STAR_OFFICE_MAX_UPLOAD_MB") or "20").strip()
    write_rl_raw = (os.getenv("STAR_OFFICE_WRITE_RATE_LIMIT") or "60,60").strip()
    asset_read_auth_enabled = (os.getenv("STAR_OFFICE_ASSET_READ_AUTH_ENABLED") or "").strip().lower() in {"1", "true", "yes", "on"}
    gemini_timeout_raw = (os.getenv("STAR_OFFICE_GEMINI_TIMEOUT_SECONDS") or "240").strip()
    gemini_prompt_max_raw = (os.getenv("STAR_OFFICE_GEMINI_PROMPT_MAX_CHARS") or "1200").strip()
    request_log_enabled = (os.getenv("STAR_OFFICE_REQUEST_LOG_ENABLED") or "").strip().lower() in {"1", "true", "yes", "on"}
    request_log_path = (os.getenv("STAR_OFFICE_REQUEST_LOG_PATH") or "").strip()
    prod_strict_mode = (os.getenv("STAR_OFFICE_PROD_STRICT_MODE") or "").strip().lower() in {"1", "true", "yes", "on"}

    if in_prod:
        if not is_strong_secret(secret):
            failures.append("Weak/missing FLASK_SECRET_KEY (or STAR_OFFICE_SECRET) in production")
        if not is_strong_pass(drawer_pass):
            failures.append("Weak/missing ASSET_DRAWER_PASS in production")
        if not write_api_guard_enabled:
            warnings.append("STAR_OFFICE_WRITE_API_BEARER_ENABLED is OFF in production (write endpoints are publicly callable)")
        elif not write_api_tokens:
            failures.append("STAR_OFFICE_WRITE_API_BEARER_ENABLED is ON but STAR_OFFICE_WRITE_API_TOKENS is empty")
    else:
        if not secret:
            warnings.append("FLASK_SECRET_KEY not set (ok for local dev, not for production)")
        if not drawer_pass:
            warnings.append("ASSET_DRAWER_PASS not set (defaults may be unsafe for public exposure)")
        if write_api_guard_enabled and not write_api_tokens:
            failures.append("Write API bearer guard enabled but STAR_OFFICE_WRITE_API_TOKENS is empty")

    try:
        max_upload_mb = int(max_upload_mb_raw)
        if max_upload_mb < 1:
            failures.append("STAR_OFFICE_MAX_UPLOAD_MB must be >= 1")
        elif max_upload_mb > 200:
            warnings.append("STAR_OFFICE_MAX_UPLOAD_MB is very high (>200MB), consider lowering for DoS safety")
    except Exception:
        failures.append("STAR_OFFICE_MAX_UPLOAD_MB is invalid (must be integer)")

    try:
        a, b = [int(x.strip()) for x in write_rl_raw.split(",", 1)]
        if a < 1 or b < 1:
            failures.append("STAR_OFFICE_WRITE_RATE_LIMIT must be positive integers, e.g. 60,60")
    except Exception:
        failures.append("STAR_OFFICE_WRITE_RATE_LIMIT format invalid, expected <count>,<window_seconds> like 60,60")

    if in_prod and not asset_read_auth_enabled:
        warnings.append("STAR_OFFICE_ASSET_READ_AUTH_ENABLED is OFF in production (asset inventory endpoints are publicly readable)")

    try:
        gemini_timeout = int(gemini_timeout_raw)
        if gemini_timeout < 30:
            warnings.append("STAR_OFFICE_GEMINI_TIMEOUT_SECONDS is very low (<30), image generation may fail frequently")
        if gemini_timeout > 1800:
            warnings.append("STAR_OFFICE_GEMINI_TIMEOUT_SECONDS is very high (>1800), hung jobs may hold workers too long")
    except Exception:
        failures.append("STAR_OFFICE_GEMINI_TIMEOUT_SECONDS is invalid (must be integer)")

    try:
        gemini_prompt_max = int(gemini_prompt_max_raw)
        if gemini_prompt_max < 100:
            warnings.append("STAR_OFFICE_GEMINI_PROMPT_MAX_CHARS is very low (<100), prompts may be over-truncated")
        if gemini_prompt_max > 10000:
            warnings.append("STAR_OFFICE_GEMINI_PROMPT_MAX_CHARS is very high (>10000), consider lowering")
    except Exception:
        failures.append("STAR_OFFICE_GEMINI_PROMPT_MAX_CHARS is invalid (must be integer)")

    if request_log_enabled and request_log_path:
        low = request_log_path.lower()
        if any(x in low for x in [".ssh", ".gnupg", ".aws"]):
            failures.append("STAR_OFFICE_REQUEST_LOG_PATH points to a sensitive directory")

    if in_prod and prod_strict_mode:
        if not write_api_guard_enabled:
            failures.append("PROD_STRICT_MODE requires STAR_OFFICE_WRITE_API_BEARER_ENABLED=true")
        if write_api_guard_enabled and not write_api_tokens:
            failures.append("PROD_STRICT_MODE requires non-empty STAR_OFFICE_WRITE_API_TOKENS")
        if not asset_read_auth_enabled:
            failures.append("PROD_STRICT_MODE requires STAR_OFFICE_ASSET_READ_AUTH_ENABLED=true")

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
