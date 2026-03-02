# Star Office UI

[![EN](https://img.shields.io/badge/Lang-EN-2563eb)](README_EN.md)
[![JP](https://img.shields.io/badge/Lang-JP-e94560)](README_JP.md)
[![ZH](https://img.shields.io/badge/Lang-ZH-16a34a)](README_ZH.md)

A pixel office dashboard for multi-agent collaboration.

![Star Office UI Preview](docs/screenshots/office-preview-20260301.jpg)

## Overview

Star Office UI visualizes AI agent status in real-time.

- Main status: `idle`, `writing`, `researching`, `executing`, `syncing`, `error`
- Multi-agent guest join/leave flow
- Yesterday memo panel
- Mobile-friendly web UI
- Built-in UI language switcher (`EN / JP / ZH`)

## Quick Start

### Docker (Recommended)

```bash
docker compose up -d
```

Open: `http://localhost:18888`

### Manual

```bash
git clone https://github.com/onizuka-agi-co/Star-Office-UI-JP.git
cd Star-Office-UI-JP
python3 -m pip install -r backend/requirements.txt
cp state.sample.json state.json
cd backend
python3 app.py
```

Open: `http://localhost:18888`

## License

- **Code**: MIT
- **Art Assets**: Non-commercial use only

For full documentation, select your language above.
