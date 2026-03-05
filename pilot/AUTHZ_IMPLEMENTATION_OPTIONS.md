# AuthZ Implementation Options — OPS-020 Quarantine Pilot

## Context
Current pilot keeps network exposure constrained (loopback bind + feature flag), but write endpoints (e.g. `/set_state`) should be explicitly authorized before any broader internal exposure.

## Option A — In-App RBAC (service-level authz)

### Design
- Add API key/JWT middleware in Flask app.
- Define roles/scopes:
  - `viewer`: read-only endpoints (`/health`, `/status`, `/agents`)
  - `operator`: state mutation (`/set_state`, `/agent-push`)
  - `admin`: asset/config mutation endpoints
- Enforce scope checks per route.
- Emit audit logs per denied/allowed write request.

### Pros
- Defense in depth even if gateway policy misconfigured.
- Fine-grained control at route level.
- Portable across environments.

### Cons
- Higher implementation/maintenance complexity.
- Secret/key lifecycle must be managed in app.
- Requires test matrix expansion.

### Effort
- Medium (1–2 days to implement + test + docs for pilot scope).

## Option B — Strict Gateway-Only Policy (external authz)

### Design
- Keep Flask service private (loopback/internal network only).
- Route all access through trusted gateway/reverse proxy.
- Gateway enforces:
  - authentication
  - allowlisted principals
  - method/path policy (deny public write paths)
  - optional mTLS/internal-token headers for write routes
- App remains mostly unchanged; no in-app RBAC complexity.

### Pros
- Fastest path for 48h sprint.
- Centralized policy and credential handling.
- Minimal app changes, lower near-term regression risk.

### Cons
- Relies on gateway correctness.
- Less portable if moved outside managed gateway perimeter.
- Weaker defense-in-depth than dual-layer model.

### Effort
- Small (hours, assuming gateway policy pipeline is available).

## Recommendation (Pilot horizon)
- **Pilot (48h): Option B strict gateway-only policy** to hit speed + safety constraints.
- **Post-pilot hardening:** add Option A in-app RBAC for defense-in-depth before broader rollout.

## Minimum acceptance criteria for either option
- No unauthenticated write path exposed externally.
- Audit trail exists for every write success/failure.
- Negative tests prove unauthorized write requests are rejected.
- Rollback path documented and tested.
