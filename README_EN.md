# Star Office UI

[![EN](https://img.shields.io/badge/Lang-EN-2563eb)](README_EN.md)
[![JP](https://img.shields.io/badge/Lang-JP-e94560)](README_JP.md)
[![ZH](https://img.shields.io/badge/Lang-ZH-16a34a)](README_ZH.md)

[**日本語版はこちら**](README_JP.md) | [**中文版请点击这里**](README_ZH.md)

---

A pixel office dashboard for multi-agent collaboration: visualize your AI assistants' (OpenClaw / "lobster") work status in real-time, helping the team intuitively see "who is doing what, what they did yesterday, and whether they are online now."

![Star Office UI Preview](docs/screenshots/office-preview-20260301.jpg)

---

## What is this project? (In one sentence)

Star Office UI is a "multi-person collaboration status dashboard"—think of it as:
> A real-time "pixel office dashboard": your AI assistants (and other agents you invite) automatically move to different areas based on their status (breakroom / desk / bug area), and you can also see a micro-summary of their work from yesterday.

---

## ✨ 30-second Quick Start (Recommended)

### Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/onizuka-agi-co/Star-Office-UI-JP.git
cd Star-Office-UI-JP

# Start with Docker Compose
docker compose up -d
```

Open: **http://localhost:18888**

### Manual Installation

```bash
# 1) Clone repository
git clone https://github.com/onizuka-agi-co/Star-Office-UI-JP.git
cd Star-Office-UI-JP

# 2) Install dependencies
python3 -m pip install -r backend/requirements.txt

# 3) Initialize state file (first run)
cp state.sample.json state.json

# 4) Start backend
cd backend
python3 app.py
```

Open: **http://localhost:18888**

Try changing states (run from project root):
```bash
python3 set_state.py writing "Organizing documents"
python3 set_state.py syncing "Syncing progress"
python3 set_state.py error "Found an issue, debugging"
python3 set_state.py idle "Standing by"
```

---

## I. What does this project do?

Star Office UI currently provides:

1. **Visualize lobster work status**
   - States: `idle`, `writing`, `researching`, `executing`, `syncing`, `error`
   - States map to different areas in the office and are shown with animations / bubbles.

2. **"Yesterday Memo" micro-summary**
   - A "Yesterday Memo" card in the UI.
   - Backend reads yesterday's (or most recent available) records from `memory/*.md` and displays them after basic privacy sanitization.

3. **Support inviting other guests to join the office (feature ongoing)**
   - Join via join key.
   - Guests can continuously push their status to the office dashboard.
   - Currently usable, but overall interaction and onboarding experience are still being optimized.

4. **Mobile-friendly access**
   - Mobile devices can directly open and view status (great for quick checks on the go).

5. **Flexible public access options**
   - Skill defaults to using Cloudflare Tunnel for quick public access.
   - You can also use your own public domain / reverse proxy setup.

6. **Built-in UI language switcher**
   - Supports English, Japanese, and Chinese (`EN / JP / ZH`)
   - Instant language switching with localStorage persistence

---

## II. Main changes in this update

This release adds/upgrades the following compared to the early base version:

- Added multi-agent mechanism: `/join-agent`, `/agent-push`, `/leave-agent`, `/agents`
- Added "Yesterday Memo" endpoint and UI: `/yesterday-memo`
- More complete state system: supports visualization for `syncing`, `error`, etc.
- Scene and character animation upgrade: added lots of pixel art assets (including guest roles)
- Rewrote docs and Skill: more beginner-friendly for external programmers
- Cleaned up release structure: removed temp files / cache / logs to lower comprehension barrier
- Added open-source notice: code under MIT, but art assets are non-commercial
- **Added Docker support** for containerized deployment
- **Added multilingual UI** with EN/JP/ZH language switcher

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

Open: `http://localhost:18888`

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
- `GET /status`: Main agent status
- `POST /set_state`: Set main agent status
- `GET /agents`: Get multi-agent list
- `POST /join-agent`: Guest joins
- `POST /agent-push`: Guest pushes status
- `POST /leave-agent`: Guest leaves
- `GET /yesterday-memo`: Yesterday Memo

---

## V. Art Asset Usage Notes (Please Read)

### Guest character asset source

Guest character animations use LimeZu's free assets:
- **Animated Mini Characters 2 (Platformer) [FREE]**
- https://limezu.itch.io/animated-mini-characters-2-platform-free

Please keep the source attribution and follow the original author's license terms when redistributing / demonstrating.

### Other asset notes & disclaimer (Important)

- **Main character (Starmie) & homophone note:**
  - "Starmie" is an existing character IP from Nintendo/Pokémon, **not original to this project**.
  - This project is **non-commercial fan creation only**: this character was chosen because of a fun homophone between "Starmie" and the author's Chinese name "海辛" (Hǎi Xīn).
  - All fan-created content in this project is for **learning, demonstration, and idea sharing only, with no commercial use**.
  - Nintendo, Pokémon, and "Starmie" are trademarks or registered trademarks of Nintendo/The Pokémon Company.
  - If you plan to use any content related to this project, please use your own original characters/art assets.

- **Office scene & other assets:** created by the project author team.

### Commercial restriction (Important)

- Code/logic may be used and modified under MIT.
- **All art assets in this repo (including main character / scene / full pack) are NOT for commercial use.**
- If you want to use this commercially, please create and replace with your own original art assets.

---

## VI. Open-source License & Notice

- **Code / Logic: MIT** (see `LICENSE`)
- **Art Assets: non-commercial, for learning / demo only**

Forks, idea sharing, and PRs are welcome; please strictly respect the asset usage boundaries.

---

## VII. Looking forward to more idea sharing

Feel free to extend this framework with:
- Richer state semantics and auto-orchestration
- Multi-room / multi-team collaboration maps
- Task boards, timelines, auto-generated daily reports
- More complete access control and permission systems

If you make an interesting modification, please share!

---

## VIII. Author social accounts

- **X: Ring Hyacinth (@ring_hyacinth)**  
  https://x.com/ring_hyacinth
- **X: Simon Lee (@simonxxoo)**  
  https://x.com/simonxxoo

---

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
  README_EN.md
  README_JP.md
  README_ZH.md
  LICENSE
```
