# OPS-020 — Gallium C1-BUILD Checkpoint

- Owner: Gallium
- Checkpoint: C1-BUILD (Quarantine Pilot)
- Timestamp: 2026-03-05 09:39 ET
- Scope: Star-Office-UI quarantine pilot (internal-only)

## 1) Quarantine build plan

- Isolation model:
  - Run Star-Office-UI in quarantine runtime with feature flag gate.
  - Bind service to loopback only (`127.0.0.1:18991`) to prevent external exposure.
  - Separate control harness (`pilot/quarantine-control.sh`) for enable/start/status/rollback.
- Hardening controls:
  - Production-mode env checks enabled (`STAR_OFFICE_ENV=production`).
  - Strong secret + drawer pass in quarantine env.
  - Security preflight command executed: `scripts/security_check.py` => OK.
- Runtime posture:
  - No production cutover.
  - Internal/staging route only.
  - Rollback always armed.

## 2) Integration sequence

1. Initialize quarantine env + runtime files from samples.
2. Enable feature flag (`pilot/STAR_OFFICE_PILOT.flag`).
3. Start service in quarantine mode (loopback bind).
4. Verify health endpoints (`/health`, `/status`, `/agents`, `/set_state`).
5. Capture baseline metrics (TTFV, health probes, endpoint error rate).
6. Run smoke test (`scripts/smoke_test.py --base-url http://127.0.0.1:18991`).
7. Hold in internal-only pilot state pending security gate closure for broader exposure.

## 3) Rollback triggers

- Trigger immediate rollback if any of the following occur:
  - Endpoint error rate > 2% over probe window.
  - Health probe failures >= 2 consecutive checks.
  - Unexpected external bind (anything other than `127.0.0.1:18991`).
  - Security preflight failure or Sentinel gate regression.
  - Functional regressions impacting primary dashboard operations.
- Rollback command:
  - `./pilot/quarantine-control.sh rollback`
  - Effect: stop service + disable feature flag.

## 4) Recommendation

- Recommendation: **CONDITIONAL**
- Rationale:
  - Build/instrumentation and quarantine controls are operational (internal pilot viable).
  - Broader exposure remains blocked until unresolved security/legal/dependency gates close.
  - Production/commercial remains NO-GO under current gate state.
