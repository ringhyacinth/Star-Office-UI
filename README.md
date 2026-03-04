# Star Office UI

[English](./README.md) | [中文](./README-CN.md)

---

<!-- ENGLISH VERSION -->

# English

## Overview

A pixel office dashboard for multi-agent collaboration: visualize your AI assistants' work status in real-time, helping teams see "who is doing what, what they did yesterday, and whether they are online."

![Star Office UI Preview](docs/screenshots/office-preview-20260301.jpg)

## Features

- **Real-time Status Visualization** - AI agents move to different office areas based on their status (idle/working/researching/error)
- **Yesterday Memo** - Automatic summary of agent activities from the previous day
- **Multi-Agent Support** - Invite guest agents to join the office
- **Mobile Friendly** - Access on any device
- **OpenClaw Plugin** - Automatic state synchronization (see [OpenClaw Plugin](#openclaw-plugin-integration))

## Quick Start

### Docker (Recommended)

```bash
# 1) Clone repository
git clone https://github.com/MISAKIGA/Star-Office-UI.git
cd Star-Office-UI

# 2) Configure environment
cp .env.example .env
# Edit .env with your API_TOKEN and ADMIN_TOKEN

# 3) Start services
docker-compose up -d

# 4) Access
# Frontend: http://localhost:18791
# API: http://localhost:18791/api/
```

### Manual Deployment

```bash
# 1) Clone and install
git clone https://github.com/MISAKIGA/Star-Office-UI.git
cd Star-Office-UI
python3 -m pip install -r backend/requirements.txt

# 2) Initialize
cp state.sample.json state.json

# 3) Start
cd backend
python3 app.py
```

Open **http://127.0.0.1:18791**

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `API_TOKEN` | Yes | - | API authentication token |
| `ADMIN_TOKEN` | Yes | - | Admin token for management |
| `PORT` | No | 18791 | Service port |
| `LOG_LEVEL` | No | info | Log level |
| `AUTO_IDLE_SECONDS` | No | 300 | Auto idle timeout (seconds) |

Generate a random token:
```bash
openssl rand -hex 32
```

## API Reference

### Status Management

```bash
# Get current status (public)
curl http://localhost:18791/api/v1/status

# Set main agent status (requires API Token)
curl -X POST http://localhost:18791/api/v1/status \
  -H "Content-Type: application/json" \
  -H "X-API-Token: your-api-token" \
  -d '{"state": "writing", "detail": "Developing feature"}'

# Push agent status (requires API Token)
curl -X POST http://localhost:18791/api/v1/agent/push \
  -H "Content-Type: application/json" \
  -H "X-API-Token: your-api-token" \
  -d '{
    "agentId": "openclaw-main",
    "name": "Shinyi",
    "state": "writing",
    "detail": "Developing"
  }'
```

### Admin APIs

```bash
# Generate new API Token
curl -X POST http://localhost:18791/api/v1/admin/token/generate \
  -H "X-Admin-Token: your-admin-token"

# List all tokens
curl http://localhost:18791/api/v1/admin/tokens \
  -H "X-Admin-Token: your-admin-token"

# Revoke token
curl -X DELETE http://localhost:18791/api/v1/admin/token/<token> \
  -H "X-Admin-Token: your-admin-token"
```

## OpenClaw Plugin Integration

> Automatically synchronize agent status to Star Office UI dashboard

### Why Use the Plugin?

| Benefit | Description |
|---------|-------------|
| **Automatic** | No manual scripts - status syncs automatically |
| **Real-time** | Updates when agent starts/ends/idle |
| **Lifecycle Aware** | Tracks all agent states (working, error, idle) |
| **Zero Config** | Works out of the box with OpenClaw |

### Plugin Features

- ✅ `onLoad` - Shows "idle" when plugin loads
- ✅ `beforeAgentStart` / `onAgentStart` - Shows "working" when agent starts
- ✅ `onAgentEnd` - Shows "idle" or "error" when agent ends
- ✅ `onAgentError` - Shows error state when agent fails
- ✅ `onIdle` - Updates status when agent is idle
- ⏱️ **Auto Idle** - Automatically returns to idle after `autoIdleSeconds`

### Installation

```bash
# Plugin is located at: ~/.openclaw/extensions/star-office-plugin/
```

### Configuration

```json
// ~/.openclaw/openclaw.json
{
  "plugins": {
    "allow": ["star-office-plugin"],
    "entries": {
      "star-office-plugin": {
        "enabled": true,
        "config": {
          "apiUrl": "http://localhost:18791",
          "apiToken": "your-api-token",
          "agentId": "openclaw-main",
          "agentName": "Shinyi",
          "autoIdleSeconds": 300
        }
      }
    }
  }
}
```

### Plugin Benefits Detail

1. **Automatic State Sync**
   - Agent starts → Shows "working" on dashboard
   - Agent ends → Shows "idle" on dashboard
   - Agent errors → Shows "error" on dashboard

2. **Zero Manual Work**
   - No need to run `set_state.py` manually
   - No cron jobs required
   - Pure plug-and-play

3. **Lifecycle Integration**
   - Works with OpenClaw's native lifecycle hooks
   - Captures all state transitions
   - Real-time updates via WebSocket

4. **Configurable**
   - Custom agent names
   - Auto idle timeout
   - Multiple agent support

## Deployment Options

### Option 1: Docker Compose (Recommended)

```bash
docker-compose up -d
```

See [Docker Deployment](#docker-recommended) for details.

### Option 2: Docker Run

```bash
# Build image
docker build -t star-office-ui:latest .

# Run container
docker run -d -p 18791:18791 \
  -e API_TOKEN=your-secure-token \
  -e ADMIN_TOKEN=your-admin-token \
  -v $(pwd)/data:/app/data \
  --name star-office-ui \
  star-office-ui:latest
```

### Option 3: Manual

```bash
python3 -m pip install -r backend/requirements.txt
cd backend && python3 app.py
```

### Option 4: Pre-built Image

```bash
docker run -d -p 18791:18791 \
  -e API_TOKEN=your-token \
  -e ADMIN_TOKEN=your-admin-token \
  --name star-office-ui \
  msga/star-office-ui-backend:latest
```

## Project Structure

```
star-office-ui/
├── backend/
│   ├── app.py              # Flask API
│   ├── requirements.txt
│   └── plugins/            # Plugin system
├── frontend/
│   ├── index.html
│   ├── layout.js
│   └── assets/             # Pixel art
├── docs/
│   └── screenshots/
├── docker-compose.yml
├── Dockerfile
├── .env.example
└── README.md
```

## Art Assets

Guest character animations use [LimeZu's free assets](https://limezu.itch.io/animated-mini-characters-2-platform-free).

**Commercial Restriction:**
- Code/Logic: MIT License
- Art Assets: **Non-commercial use only**

## License

- **Code:** [MIT](LICENSE)
- **Art Assets:** Non-commercial

---

