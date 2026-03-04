#!/usr/bin/env python3
"""Star Office UI smoke test (non-destructive).

Usage:
  python3 scripts/smoke_test.py --base-url http://127.0.0.1:18791

Optional env:
  SMOKE_AUTH_BEARER=xxxx   # if your gateway/proxy requires bearer auth
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request


REQUIRED_ENDPOINTS = [
    ("GET", "/", 200),
    ("GET", "/health", 200),
    ("GET", "/status", 200),
    ("GET", "/agents", 200),
    ("GET", "/yesterday-memo", 200),
]


def req(method: str, url: str, body: dict | None = None, token: str = "") -> tuple[int, str]:
    data = None
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    r = urllib.request.Request(url=url, method=method, data=data, headers=headers)
    try:
        with urllib.request.urlopen(r, timeout=8) as resp:
            raw = resp.read().decode("utf-8", errors="ignore")
            return resp.status, raw
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="ignore") if hasattr(e, "read") else str(e)
        return e.code, raw
    except Exception as e:
        return 0, str(e)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="http://127.0.0.1:18791", help="Base URL of Star Office UI service")
    args = ap.parse_args()

    base = args.base_url.rstrip("/")
    token = os.getenv("SMOKE_AUTH_BEARER", "").strip()

    failures: list[str] = []
    print(f"[smoke] base={base}")

    for method, path, expected in REQUIRED_ENDPOINTS:
        code, body = req(method, base + path, token=token)
        if code != expected:
            failures.append(f"{method} {path}: expected {expected}, got {code}, body={body[:200]}")
        else:
            print(f"  OK  {method} {path} -> {code}")

    # non-destructive state update probe
    code, body = req("POST", base + "/set_state", {"state": "idle", "detail": "smoke-check"}, token=token)
    if code != 200:
        failures.append(f"POST /set_state failed: {code}, body={body[:200]}")
    else:
        print("  OK  POST /set_state -> 200")

    if failures:
        print("\n[smoke] FAIL")
        for f in failures:
            print(" -", f)
        return 1

    print("\n[smoke] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
