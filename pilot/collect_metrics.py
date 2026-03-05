#!/usr/bin/env python3
from __future__ import annotations
import json, os, time, statistics, urllib.request, urllib.error

PORT = int(os.getenv("STAR_BACKEND_PORT", "18991"))
BASE = f"http://127.0.0.1:{PORT}"
FLAG = os.path.join(os.path.dirname(__file__), "STAR_OFFICE_PILOT.flag")

def req(method: str, path: str, body: dict | None = None):
    data = None
    headers = {}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    r = urllib.request.Request(BASE + path, method=method, data=data, headers=headers)
    t0 = time.perf_counter()
    code = 0
    err = ""
    size = 0
    try:
        with urllib.request.urlopen(r, timeout=5) as resp:
            raw = resp.read()
            size = len(raw)
            code = resp.status
    except urllib.error.HTTPError as e:
        code = e.code
        err = str(e)
    except Exception as e:
        err = str(e)
    ms = (time.perf_counter() - t0) * 1000
    return {"code": code, "ms": ms, "err": err, "bytes": size}

def ttfv_probe():
    url = BASE + "/"
    t0 = time.perf_counter()
    t_first = None
    total_bytes = 0
    code = 0
    err = ""
    try:
        with urllib.request.urlopen(url, timeout=8) as resp:
            code = resp.status
            first = resp.read(1)
            t_first = (time.perf_counter() - t0) * 1000
            total_bytes += len(first)
            rest = resp.read()
            total_bytes += len(rest)
    except Exception as e:
        err = str(e)
    full_ms = (time.perf_counter() - t0) * 1000
    return {
        "code": code,
        "ttfb_ms": round(t_first or 0, 2),
        "ttfv_proxy_ms": round(t_first or 0, 2),
        "full_load_ms": round(full_ms, 2),
        "bytes": total_bytes,
        "err": err,
    }

def summarize(samples):
    lat = [s["ms"] for s in samples]
    codes = [s["code"] for s in samples]
    errs = sum(1 for c in codes if c >= 400 or c == 0)
    return {
        "count": len(samples),
        "ok": sum(1 for c in codes if 200 <= c < 400),
        "errors": errs,
        "error_rate": round((errs / len(samples))*100, 2) if samples else 0,
        "avg_ms": round(statistics.mean(lat), 2) if lat else 0,
        "p95_ms": round(sorted(lat)[max(0, int(len(lat)*0.95)-1)], 2) if lat else 0,
    }

def run_endpoint(method, path, n, body=None):
    return [req(method, path, body=body) for _ in range(n)]

out = {
    "base_url": BASE,
    "feature_flag": "ON" if os.path.exists(FLAG) else "OFF",
    "rollback_switch_state": "ARMED" if os.path.exists(FLAG) else "DISARMED",
    "ttfv": ttfv_probe(),
}
health = run_endpoint("GET", "/health", 20)
status = run_endpoint("GET", "/status", 20)
agents = run_endpoint("GET", "/agents", 20)
set_state = run_endpoint("POST", "/set_state", 10, body={"state":"idle","detail":"pilot-probe"})
out["health_probe_stats"] = summarize(health)
out["status_probe_stats"] = summarize(status)
out["agents_probe_stats"] = summarize(agents)
out["set_state_probe_stats"] = summarize(set_state)
out["endpoint_error_stats"] = {
    "total_calls": 70,
    "total_errors": out["health_probe_stats"]["errors"] + out["status_probe_stats"]["errors"] + out["agents_probe_stats"]["errors"] + out["set_state_probe_stats"]["errors"],
}
out["endpoint_error_stats"]["error_rate"] = round(out["endpoint_error_stats"]["total_errors"] / out["endpoint_error_stats"]["total_calls"] * 100, 2)
print(json.dumps(out, ensure_ascii=False, indent=2))
