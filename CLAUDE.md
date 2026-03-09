# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Star Office UI is a pixel-art AI office dashboard that visualizes AI agent work states in real time. It supports multi-agent collaboration, trilingual UI (CN/EN/JP), AI-generated backgrounds via Gemini, and an optional Tauri desktop pet mode.

## Commands

### Start Backend
```bash
cd backend
python3 app.py
# Serves on http://127.0.0.1:19000
```

### Install Backend Dependencies
```bash
python3 -m pip install -r backend/requirements.txt
# Dependencies: flask==3.0.2, pillow==10.4.0
```

### Set Agent State (CLI)
```bash
python3 set_state.py <state> "<detail>"
# States: idle | writing | researching | executing | syncing | error
```

### Smoke Test (non-destructive)
```bash
python3 scripts/smoke_test.py --base-url http://127.0.0.1:19000
```

### Security Check
```bash
python3 scripts/security_check.py
```

### Docker (recommended for server deployment)
```bash
cp .env.example .env          # fill in FLASK_SECRET_KEY, ASSET_DRAWER_PASS, MEMORY_HOST_PATH
docker compose up -d --build  # first build and start
docker compose up -d          # subsequent starts
docker compose logs -f        # follow logs
```

Set agent state via API (replaces `python3 set_state.py`):
```bash
curl -X POST http://localhost:19000/set_state \
  -H "Content-Type: application/json" \
  -d '{"state": "writing", "detail": "正在写代码"}'
```

Persistent data is stored in `./data/` (Volume mount, gitignored). On first start, `state.json` and `join-keys.json` are auto-initialized from their `.sample.json` counterparts.

### Desktop Pet (Tauri, optional)
```bash
cd desktop-pet
npm install
npm run dev
# Requires Tauri v2. Starts backend automatically. Points to http://127.0.0.1:19000/?desktop=1
```

## Architecture

### Backend (`backend/`)
Single Flask app (`app.py`) that serves both the API and the frontend static files. It is split into utility modules:

- **`app.py`** — All route definitions, state machine logic, asset management endpoints, and background task registry (`_bg_tasks` dict) for async image generation.
- **`store_utils.py`** — JSON load/save helpers for all persistent data files: `state.json`, `agents-state.json`, `join-keys.json`, `asset-positions.json`, `asset-defaults.json`, `runtime-config.json`.
- **`memo_utils.py`** — Reads `../memory/*.md` (relative to project root's parent), extracts and sanitizes a daily work memo for the `/yesterday-memo` API endpoint.
- **`security_utils.py`** — Production-mode detection and validation of `FLASK_SECRET_KEY` and `ASSET_DRAWER_PASS`.

**State machine:** Six valid agent states (`idle`, `writing`, `researching`, `executing`, `syncing`, `error`) map to three office areas. States in `WORKING_STATES` auto-revert to `idle` after `ttl_seconds` (default 300s) via `load_state()`.

**Key JSON files** (all at project root):
- `state.json` — Main agent state (copy from `state.sample.json` to initialize)
- `agents-state.json` — Guest agent list (auto-created)
- `join-keys.json` — Guest join keys (auto-created from `join-keys.sample.json`)
- `asset-positions.json`, `asset-defaults.json` — Asset layout overrides
- `runtime-config.json` — Gemini API key and model (chmod 0o600)

### Frontend (`frontend/`)
Vanilla JS + [Phaser 3](https://phaser.io/) game engine (loaded from `vendor/`). No build step required.

- **`index.html`** — Main office view
- **`game.js`** — Phaser scene logic: asset loading, sprite animation, state polling, multi-agent rendering, memo card, sidebar, Gemini image generation UI
- **`layout.js`** — All coordinates, z-depths, sprite paths, and canvas dimensions (1280×720). This is the single source of truth for layout — change positions here, not in `game.js`.
- **`join.html` / `invite.html`** — Guest join flow pages

**Asset format rule:** Transparent assets must use `.png`; non-transparent assets prefer `.webp`. The `getExt()` function in `game.js` applies WebP browser detection fallback.

**Depth (z-order) convention:**
```
sofa(10) → starWorking(900) → desk(1000) → flower(1100)
```

### Multi-Agent / Guest System
- Host creates join keys in `join-keys.json` (max concurrent agents per key is configurable)
- Guests run `office-agent-push.py` with `JOIN_KEY`, `AGENT_NAME`, and `OFFICE_URL` set
- Guest state uses the `/join-agent` → `/agent-push` → `/leave-agent` API flow
- Concurrent join requests are protected by `threading.Lock()` in `app.py`

### Desktop Pet (`desktop-pet/`)
Tauri v2 wrapper. `main.js` spawns the Python backend as a child process using `STAR_PROJECT_ROOT` env var (defaults to `..`). `STAR_PYTHON_PATH` can override the Python interpreter. Window loads `electron-standalone.html` (a self-contained copy of the frontend) for offline use.

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `FLASK_SECRET_KEY` / `STAR_OFFICE_SECRET` | Session signing | Dev placeholder (must change in prod) |
| `ASSET_DRAWER_PASS` | Sidebar lock password | `1234` (must change in prod) |
| `STAR_OFFICE_ENV` / `FLASK_ENV` | Set to `production` to enable hardening checks | — |
| `GEMINI_API_KEY` / `GOOGLE_API_KEY` | Gemini image generation | — |
| `GEMINI_MODEL` | Gemini model override | `nanobanana-pro` |
| `AUTO_ROTATE_HOME_ON_PAGE_OPEN` | Rotate background on each page load | `0` (off) |
| `STAR_OFFICE_STATE_FILE` | Override `state.json` path | `./state.json` |
| `STAR_OFFICE_DATA_DIR` | Directory for all runtime JSON files (Docker) | `ROOT_DIR` (project root) |
| `STAR_OFFICE_MEMORY_DIR` | Override memory directory path (Docker) | `../memory` relative to project root |

## Key API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/status` | Main agent state |
| POST | `/set_state` | Update main agent state |
| GET | `/agents` | Guest agent list |
| POST | `/join-agent` | Guest joins office |
| POST | `/agent-push` | Guest pushes state update |
| POST | `/leave-agent` | Guest leaves |
| GET | `/yesterday-memo` | Sanitized daily memo |
| GET/POST | `/config/gemini` | Gemini API key/model config |
| GET | `/assets/generate-rpg-background/poll` | Poll async image generation |
