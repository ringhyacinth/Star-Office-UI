# PR Artifact Index — Quarantine / Hardening Track

## In-repo artifacts
- Quarantine gate evidence:
  - `pilot/OPS-020-gate-evidence-2026-03-05-0921.md`
- AuthZ implementation options:
  - `pilot/AUTHZ_IMPLEMENTATION_OPTIONS.md`
- Quarantine metrics snapshot:
  - `pilot/metrics-baseline-2026-03-05.json`
  - `pilot/metrics-latest.json` (runtime-generated)

## Cross-workspace artifact (Obsidian)
- C1-BUILD checkpoint (required path):
  - `/home/tekron/.openclaw/workspace-obsidian/artifacts/ops-020/gallium-build-checkpoint.md`

## Verification commands
```bash
# Quarantine status
./pilot/quarantine-control.sh status

# Security preflight
set -a && source pilot/quarantine.env && set +a && .venv-pilot/bin/python scripts/security_check.py

# Probe metrics
python3 pilot/collect_metrics.py

# Smoke
python3 scripts/smoke_test.py --base-url http://127.0.0.1:18991
```
