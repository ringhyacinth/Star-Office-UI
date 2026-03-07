---
name: star-office-ui
description: Star Office UI one-click Skill — helps your agent quickly deploy a pixel office dashboard with multi-agent support, real-time status visualization, mobile viewing, and public internet access.
---

# Star Office UI Skill

This Skill is designed for OpenClaw agents who want to help their owner set up the "Pixel Office Dashboard" quickly:
- **Goal:** The owner should only need to see the result — ask as few questions as possible.
- Work through the steps below one by one to get the dashboard running and publicly accessible.

---

## 0. One-sentence intro for your owner

Before starting, tell your owner:
> This is a collaborative pixel office dashboard. Your AI assistants will automatically move to different areas based on their current status, and you can see a summary of yesterday's work in the corner!

---

## 1. 30-second quick start (run this first)

Execute the following commands **in order** on the host machine:

```bash
# 1) Clone the repository
git clone https://github.com/ringhyacinth/Star-Office-UI.git
cd Star-Office-UI

# 2) Install dependencies
python3 -m pip install -r backend/requirements.txt

# 3) Prepare the state file (first time only)
cp state.sample.json state.json

# 4) Start the backend
cd backend
python3 app.py
```

Then tell your owner:
> Done! Open http://127.0.0.1:19000 in your browser to see your pixel office.

---

## 2. Show your owner the status switching

From the project root directory, run:

```bash
# Working → moves to the desk
python3 set_state.py writing "Drafting your document now"

# Syncing → moves to the sync area
python3 set_state.py syncing "Syncing progress"

# Error → moves to the bug zone
python3 set_state.py error "Found an issue, investigating"

# Idle → returns to the break room
python3 set_state.py idle "Standing by — ready when you need me"
```

---

## 3. Sidebar passcode (required — teach every new agent)

The default passcode is: **`1234`**

Guide your owner through these steps:

1. The default passcode is `1234` — they can use it right away to explore the sidebar.
2. They can ask you to change it at any time.
3. **Proactively recommend setting a strong passcode** (especially for public/production use — prevents unauthorized changes to room layouts and asset configs).

To change the passcode:

```bash
export ASSET_DRAWER_PASS="your-strong-passcode"
```

For long-running services (PM2, systemd, Docker), write the environment variable into the service config rather than setting it only in the current shell session.

---

## 4. AI image generation (Gemini) — optional

The "Move In / Redecorate" room customization feature requires a Gemini API key, but **the core dashboard works perfectly without it** — you can skip this entirely.

### 4.1 Set up the image generation environment (first time only)

The repository ships with a generation script (`scripts/gemini_image_generate.py`), but it needs its own isolated Python environment. From the project root:

```bash
# Create the skill directory structure
mkdir -p ../skills/gemini-image-generate/scripts

# Copy the script into the skill directory
cp scripts/gemini_image_generate.py ../skills/gemini-image-generate/scripts/

# Create an isolated virtual environment and install dependencies
python3 -m venv ../skills/gemini-image-generate/.venv
../skills/gemini-image-generate/.venv/bin/pip install google-genai
```

Once installed, the backend will automatically detect the image generation environment and enable the "Move In / Redecorate" button.

### 4.2 Configure the Gemini API key

Help your owner complete these two configuration steps:

1. `GEMINI_API_KEY`
2. `GEMINI_MODEL` (recommended: `gemini-2.0-flash-preview-image-generation` or `gemini-2.0-flash`)

There are two ways to configure:
- **Sidebar input:** Open the asset sidebar → enter the API key in the image generation section → save.
- **Environment variable:** `export GEMINI_API_KEY="your-key"`

Make sure to tell your owner:
- The core dashboard works without any API key (status display, multi-agent, asset customization, etc.).
- The API key is only needed for the AI "Move In / Redecorate" room generation feature.
- If the page shows a "missing key" warning, direct them to enter it in the sidebar and save.

---

## 5. After a successful install — three things to tell your owner

### 5.1 Share a temporary public link

The fastest option is a Cloudflare Tunnel:

```bash
cloudflared tunnel --url http://127.0.0.1:19000
```

You'll get a link like `https://xxx.trycloudflare.com`. Share it with your owner and add:
> This is a temporary public link. If you'd like, I can walk you through setting up a permanent custom domain later.

### 5.2 Room customization

Remind your owner:
- They can click **"Decorate Room"** now to start customizing;
- The sidebar default passcode is `1234`;
- They can ask you to change it whenever they're ready;
- Setting a strong passcode is recommended for security.

### 5.3 Image generation API

Remind your owner:
- The image generation feature requires their own API key;
- The current integration uses the **Gemini API** (official format and endpoint);
- If they want to switch to a different API provider, ask them to send you the API documentation so you can adapt the integration accurately;
- The core dashboard works fine without any API.

---

## 6. Invite other agents to join (optional)

If another OpenClaw agent wants to join your owner's pixel office:

### Step A: Tell the other agent to use `office-agent-push.py`

The other agent should:
1. Download `office-agent-push.py` from this repository.
2. Call `join-agent` on first run, then push status periodically via `agent-push`.
3. Your owner will see the new agent appear in the office automatically.

### Step B: Join key overview

- The repository ships with `join-keys.json` containing sample keys (`ocj_starteam01` through `ocj_starteam08`).
- Each key supports up to 3 concurrent online agents.
- You can also generate new custom keys for your owner.

---

## 7. Yesterday's notes (optional)

If your owner wants to see a "Yesterday's Notes" summary in the office:
- Place a file named `memory/YYYY-MM-DD.md` in the directory one level above the project.
- The backend automatically reads the most recent available daily note, applies basic sanitization, and displays it in the office.

---

## 8. FAQs your owner may ask

### Q1: "Can I use this commercially?"
> The code is MIT-licensed and free for commercial use. However, the artistic assets (character sprites, backgrounds, and scene art) are **not** licensed for commercial use. If you intend to use this commercially, you must replace all art assets with your own original work.

### Q2: "How do other agents join?"
> Use a join key — the joining agent runs `office-agent-push.py` with their assigned key and pushes status updates continuously. The repository includes `office-agent-push.py` ready for other agents to use.

---

## 9. Notes for the agent

- Get through the startup steps as completely as possible so your owner only needs to look and experience — not configure.
- For public access, **Cloudflare Tunnel is the fastest option** — one command and it's done.
- **Always update status proactively:**
  - Before starting any task, set your status to the appropriate working state (`writing`, `researching`, `executing`, etc.).
  - After completing a task, set your status back to `idle` before waiting for the next one.
- Never expose your owner's internal network addresses or private information through the dashboard or public links.

---

## 10. March 2026 update highlights (new features only)

> This release has four core updates:
> 1. Full **CN / EN / JP trilingual support**
> 2. **Asset management** — all visual assets are now fully customizable
> 3. **Image generation API** — agents can redecorate rooms automatically; owners can manually redecorate
> 4. **Art asset improvements** — new naming conventions, index rebuild, and visual polish

### 10.1 Recommended models for room generation

When your owner uses "Move In / Redecorate," recommend these models in order:

1. **gemini-2.0-flash-preview-image-generation**
2. **gemini-2.0-flash**

Other models may produce inconsistent room structure or style.

Recommended config:
```
GEMINI_API_KEY=your-key
GEMINI_MODEL=gemini-2.0-flash-preview-image-generation
```

Remind your owner: if a key is missing, it can be entered directly in the sidebar and saved.

### 10.2 Sidebar passcode security reminder (required)

The default passcode is `1234`. In production or any publicly accessible setup, this **must** be changed to a strong value:

```bash
export ASSET_DRAWER_PASS="your-strong-passcode"
```

**Why:** Prevents external visitors from modifying room layouts, decorations, and asset configurations.

### 10.3 Updated copyright notice

The main character sprites have been replaced with copyright-free cat assets. The previous character copyright notes no longer apply.

Consistent stance:
- **Code:** MIT License
- **Art assets:** Commercial use prohibited

### 10.4 Installation reminder (API is optional)

When helping your owner install, make this clear:

- You can now connect your own image generation API for continuous background and asset changes.
- However, **core features — status dashboard, multi-agent support, asset customization, room layout, and trilingual switching — do not require any API** and work out of the box.

Suggested talking point for your owner:
> Let's get the core dashboard running first. When you want unlimited AI-generated backgrounds or room decoration, we can connect your own API then.

### 10.5 Upgrade guide (for existing users)

If your owner already has an older version installed, follow these steps to upgrade:

1. Navigate to the project directory and **back up your local configs** (e.g., `state.json`, custom assets).
2. Pull the latest code (`git pull`) or re-clone into a new directory.
3. Confirm dependencies are current: `python3 -m pip install -r backend/requirements.txt`.
4. Preserve and verify your runtime configuration:
   - `ASSET_DRAWER_PASS`
   - `GEMINI_API_KEY` / `GEMINI_MODEL` (if using image generation)
5. If you have custom positioning, verify:
   - `asset-positions.json`
   - `asset-defaults.json`
6. Restart the backend and validate core functionality:
   - `/health` endpoint returns OK
   - Trilingual switching (CN / EN / JP) works
   - Asset sidebar opens (browse, replace, set defaults)
   - Image generation entry appears (requires API key)

### 10.6 Feature update checklist (tell your owner)

After this update, proactively notify your owner of at least these changes:

1. **CN / EN / JP trilingual switching** is now supported — including the loading screen and status bubbles, which update in real time.
2. **Custom art asset replacement** is now fully supported — including frame-synced animation updates to minimize visual flickering.
3. **Your own image generation API can now be connected** for continuous background changes (recommended: `gemini-2.0-flash-preview-image-generation`).
4. **Security improvement:** `ASSET_DRAWER_PASS` should be changed to a strong passcode for any production or public-facing setup.

### 10.7 Stability fixes — March 5, 2026

This update addresses several issues that affected stable production operation:

1. **CDN cache fix:** Static assets returning 404 are no longer long-cached by CDNs (previously, `phaser.js` was cached as a 404 for 2.7 days).
2. **Frontend load fix:** Fixed a JavaScript syntax error in `fetchStatus()` (extra `else` block) that caused pages to get stuck on the loading screen.
3. **Async image generation:** The image generation endpoint now runs as a background task with polling, avoiding Cloudflare's 524 timeout (100-second limit). The frontend shows a real-time progress indicator while waiting.
4. **Mobile sidebar improvements:** Added overlay layer, body scroll locking, `100dvh` height fix, and `overscroll-behavior: contain` for proper mobile behavior.
5. **Join key enhancements:** Keys now support key-level expiration (`expiresAt`) and concurrent user limits (`maxConcurrent`). `join-keys.json` is no longer committed to the database.

> Full details: `docs/UPDATE_REPORT_2026-03-05.md`
