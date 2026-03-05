# Star Office UI

🌐 Language: [中文](./README.md) | **English** | [日本語](./README.ja.md)

![Star Office UI Cover 2](docs/screenshots/readme-cover-2.jpg)

A pixel office dashboard for multi-agent collaboration: visualize your AI assistants' (OpenClaw / "lobster") work status in real time, helping teams intuitively see "who is doing what, what they did yesterday, and whether they are online now."

> This is a **co-created project by Ring Hyacinth and Simon Lee**.

---

## What is this project? (In one sentence)

Star Office UI is a "multi-person collaboration status dashboard"—think of it as:
> A real-time "pixel office dashboard": your AI assistants (and other agents you invite) automatically move to different areas based on their status (breakroom / desk / bug area), and you can also see a micro-summary of their work from yesterday.

---

## ✨ 30-second Quick Start (Recommended)

```bash
# 1) Clone repository
git clone https://github.com/ringhyacinth/Star-Office-UI.git
cd Star-Office-UI

# 2) Install dependencies
python3 -m pip install -r backend/requirements.txt

# 3) Initialize state file (first run)
cp state.sample.json state.json

# 4) Start backend
cd backend
python3 app.py
```

Open: **http://127.0.0.1:18791**

Try changing states (run from project root):
```bash
python3 set_state.py writing "Organizing documents"
python3 set_state.py syncing "Syncing progress"
python3 set_state.py error "Found an issue, debugging"
python3 set_state.py idle "Standing by"
```
![Star Office UI Cover 1](docs/screenshots/readme-cover-1.jpg)
---

## I. What does this project do?

Star Office UI currently provides:

1. **Visualize lobster work status**
   - States: `idle`, `writing`, `researching`, `executing`, `syncing`, `error`
   - States map to different areas in the office and are shown with animations / bubbles.

2. **"Yesterday Memo" micro-summary**
   - A "Yesterday Memo" card in the UI.
   - Backend reads yesterday’s (or most recent available) records from `memory/*.md` and displays them after basic privacy sanitization.

3. **Support inviting other guests to join the office (feature ongoing)**
   - Join via join key.
   - Guests can continuously push their status to the office dashboard.
   - Currently usable, but overall interaction and onboarding experience are still being optimized.

4. **Mobile-friendly access**
   - Mobile devices can directly open and view status (great for quick checks on the go).

5. **Trilingual UI (Chinese / English / Japanese)**
   - CN / EN / JP language switching.
   - Language changes apply in real time to UI text, loading prompts, and character bubbles.

6. **Customizable art assets**
   - Replace character/scene assets via the asset sidebar.
   - Safe frame cuts and parameter sync (frame size / frame range) to avoid flickering.

7. **Bring-your-own image API (infinite background changes)**
   - Connect your own image-generation API for "move to new home / find agent" style background updates.
   - Recommended models: `nanobanana-pro` or `nanobanana-2` (more stable structure preservation).
   - Core dashboard functionality does not depend on an API; you can use the core status dashboard and asset management without connecting an API.

8. **Flexible public access options**
   - Skill defaults to using Cloudflare Tunnel for quick public access.
   - You can also use your own public domain / reverse proxy setup.

---

## II. Core changes in this rebuild (2026-03)

This version is not a patchwork update—it is a complete rebuild based on the original project. The core changes are focused on four areas:

1. **Added trilingual support (CN / EN / JP)**
   - Full UI localization in three languages.
   - State text, prompts, and asset display names switch together.

2. **Added asset management (full user customization of art assets)**
   - Asset sidebar supports selecting, replacing, and managing defaults.
   - Users can customize characters, scenes, decorations, buttons, and more.

3. **Integrated image generation API (smart room renovation + manual renovation)**
   - Supports workflows like "Move Home / Find Agent / DIY Decor."
   - OpenClaw can redesign rooms via image generation; users can also manually input themes.

4. **Art asset replacement & optimization (key focus)**
   - Core assets were replaced/redrawn at scale.
   - Rebuilt naming and index mapping for better stability and maintainability.
   - Optimized frame-cutting and rendering logic to reduce wrong-frame/cache interference.

---

## III. Quick Start

### 1) Install dependencies

```bash
cd star-office-ui
python3 -m pip install -r backend/requirements.txt
```

### 2) Initialize state file

```bash
cp state.sample.json state.json
```

### 3) Start backend

```bash
cd backend
python3 app.py
```

Open: `http://127.0.0.1:18791`

### 4) Switch main Agent status (example)

```bash
python3 set_state.py writing "Organizing documents"
python3 set_state.py syncing "Syncing progress"
python3 set_state.py error "Found an issue, debugging"
python3 set_state.py idle "Standing by"
```

---

## IV. Common APIs

- `GET /health`: Health check
- `GET /status`: Main Agent status
- `POST /set_state`: Set main Agent status
- `GET /agents`: Get multi-Agent list
- `POST /join-agent`: Guest joins
- `POST /agent-push`: Guest pushes status
- `POST /leave-agent`: Guest leaves
- `GET /yesterday-memo`: Yesterday memo

### Token Authentication

Some APIs require token authentication:

| Header | Usage |
|--------|-------|
| `X-API-Token` | User API Token (read/write status) |
| `X-Admin-Token` | Admin Token (management operations) |

Generate Token:
```bash
# Generate new Token
curl -X POST http://localhost:5000/api/v1/admin/token/generate \
  -H "X-Admin-Token: your-admin-token"

# List Tokens
curl http://localhost:5000/api/v1/admin/tokens \
  -H "X-Admin-Token: your-admin-token"
```

---

## V. OpenClaw Plugin (Auto State Sync)

Star Office UI provides an OpenClaw plugin for automatic Agent status sync. Supports two usage modes:

### 5.1 Two Usage Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| **Local Join** | Join office via Join Key | Multi-agent collaboration, local deployment |
| **Remote Connect** | Connect to remote office via plugin config | Public access, remote monitoring |

### 5.2 Installation

#### Option 1: CLI Installation (Recommended)

```bash
# Install local plugin
openclaw plugins install ./plugins/openclaw

# Or use --link to avoid copying
openclaw plugins install -l ./plugins/openclaw

# Install remote plugin (specific version)
openclaw plugins install star-office-ui@1.0.0
```

> ⚠️ **Security Note**: Treat plugin installation as running code. Prefer using fixed versions.

#### Option 2: Manual Configuration

Edit `~/.openclaw/openclaw.json`:

```json
{
  "plugins": {
    "allow": ["star-office"],
    "entries": {
      "star-office": {
        "enabled": true,
        "config": {
          "apiUrl": "http://localhost:5000",
          "apiToken": "your-api-token"
        }
      }
    }
  }
}
```

### 5.3 Configuration Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `apiUrl` | string | ✅ Required | `http://localhost:5000` | Star Office UI backend API URL |
| `apiToken` | string | ✅ Required | - | API Auth Token (generated from backend) |
| `agentId` | string | Optional | `openclaw-{timestamp}` | Agent unique identifier |
| `agentName` | string | Optional | - | Agent display name |
| `joinKey` | string | Optional | - | Can be empty for remote mode |
| `memoryDir` | string | Optional | `~/.openclaw/workspace/memory` | Memory files directory |
| `autoIdleSeconds` | number | Optional | `300` | Auto idle timeout (seconds) |

### 5.4 Generate API Token

```bash
# 1. Start backend
cd Star-Office-UI && docker-compose up -d

# 2. Generate Token (requires ADMIN_TOKEN first)
curl -X POST http://localhost:5000/api/v1/admin/token/generate \
  -H "X-Admin-Token: your-admin-token" \
  -H "Content-Type: application/json" \
  -d '{"name": "openclaw-agent", "type": "api"}'

# 3. Copy returned token to plugin config
```

### 5.5 Plugin Features

- ✅ `before_agent_start` - Show "working" when Agent starts
- ✅ `agent_end` - Show "idle" or "error" when Agent ends
- ✅ `agent_error` - Show error status on error
- ✅ Auto sync yesterday memo to office dashboard
- ✅ Daily sync at 8 AM (via cron or heartbeat)

---

## VI. Art asset usage notes (please read)

### Guest character asset source

Guest character animations use LimeZu’s free assets:
- **Animated Mini Characters 2 (Platformer) [FREE]**
- https://limezu.itch.io/animated-mini-characters-2-platform-free

Please keep attribution when redistributing/demoing, and follow the original license terms.

### Commercial restriction (important)

- Code logic can be used/extended under MIT.
- **All art assets in this repo (including main character/scene/full pack) are non-commercial.**
- For commercial use, please replace all assets with your own original art.

---

## VII. Open-source license & notice

- **Code / Logic: MIT** (see `LICENSE`)
- **Art Assets: non-commercial, learning/demo only**

Forks, idea sharing, and PRs are welcome. Please strictly respect asset-usage boundaries.

---

## VIII. Looking forward to more creative extensions

You can extend this framework with:
- richer state semantics and automation orchestration
- multi-room / multi-team collaboration maps
- task boards, timelines, auto daily reports
- more complete access control and permissions

If you build something cool, feel free to share!

---

## IX. Project authors

This project is co-created and maintained by **Ring Hyacinth** and **Simon Lee**.

- **X: Ring Hyacinth (@ring_hyacinth)**
  https://x.com/ring_hyacinth
- **X: Simon Lee (@simonxxoo)**
  https://x.com/simonxxoo

---

## X. 2026-03 Incremental Updates (added on top of the original version)

> This section records only new/changed items. Other parts keep the original structure.

### A) Recommended image models for room renovation (New)

For the “Move Home / Find Agent” workflow, it is recommended to connect your own Gemini API and prioritize:

1. **gemini nanobanana pro**
2. **gemini nanobanana 2**

Other models may be less stable for preserving room structure + style consistency.

Recommended config:

- `GEMINI_API_KEY`
- `GEMINI_MODEL` (recommend `nanobanana-pro` or `nanobanana-2`)

Runtime config endpoints are also supported:
- `GET /config/gemini`
- `POST /config/gemini`

If API key is missing, the sidebar will show an input entry so users can fill it in and retry directly.

### B) Asset drawer passcode (New)

The asset sidebar can modify layout, decoration, and default positions.

Current default:
- `ASSET_DRAWER_PASS=1234`

Suggested user-facing guidance:
1. Use default password `1234` for quick trial first;
2. Users can ask you to change the password anytime;
3. Recommend switching to a strong password as soon as possible.

Example:

```bash
export ASSET_DRAWER_PASS="your-strong-pass"
```

Why this matters:
- Prevents anyone with the public link from changing your room layout/assets.

### C) Three reminders for the owner after successful install (New)

1. **Temporary public link**
   - Send the `trycloudflare` temporary link to the owner.
   - Explain that you can later migrate to their own domain step by step.

2. **Room renovation entry**
   - Remind the owner to click “装修房间” to start.
   - Default password is `1234`.
   - If they want to change password, they can ask you anytime.
   - Recommend upgrading to a strong password.

3. **Image API setup**
   - Image generation uses the user’s own API.
   - Current integration uses Gemini official API format/address.
   - If switching to another API provider, ask for API docs first so you can adapt correctly.

### D) Runtime status usage recommendation (New)

Recommend that the Agent proactively maintains status:

1. Before taking a task, switch to a working state (`writing` / `researching` / `executing`) first;
2. After task completion, switch to `idle` first, then enter rest/waiting mode.

This makes the office dashboard feel more real-time and continuous.

### E) Art & copyright wording update (Important)

A major focus of this rebuild is the asset system upgrade (large-scale replacement + naming/index remapping).

Policy remains:

- Code logic: MIT
- Art assets: non-commercial (learning/demo/sharing only)

---


### F) 2026-03-04 P0/P1 Security & Stability Update (New)

This patch focuses on **production readiness + truthful status sync**, while preserving existing core features:

1. **P0 Security baseline**
   - Added production hardening checks (weak secret / weak password guard)
   - Hardened session cookie settings
   - Added `scripts/security_check.py` for pre-deploy checks

2. **P1 Refactor (no behavior change)**
   - Split backend helpers into `security_utils.py`, `memo_utils.py`, `store_utils.py`
   - Reduced `app.py` coupling and improved maintainability

3. **Status-sync & UX improvements**
   - Fixed state-source path priority
   - Added stale-state auto-idle to reduce false-working states
   - Improved first-screen UX (skeleton + deferred non-critical init)

4. **Service stability fixes**
   - Unified and stabilized `star-office-ui.service` on port 18888
   - Better coordination with `star-office-push.service` to reduce 502 risk

> Detailed notes: `docs/UPDATE_REPORT_2026-03-04_P0_P1.md`

## Project structure (simplified)

```text
star-office-ui/
  backend/
    app.py
    requirements.txt
    run.sh
  frontend/
    index.html
    join.html
    invite.html
    layout.js
    ...assets
  docs/
    screenshots/
  office-agent-push.py
  set_state.py
  state.sample.json
  join-keys.json
  SKILL.md
  README.md
  README.en.md
  README.ja.md
  LICENSE
```
