# Star-Office-UI Release Notes (2026-03-02)

## Summary
This package is a cleaned release snapshot for handoff/update.
It excludes runtime files, logs, and local backup artifacts.

## Included
- backend/
- frontend/
- docs/
- assets/room-reference.png
- core scripts and docs (README.md, SKILL.md, LICENSE, set_state.py, etc.)
- asset-defaults.json / asset-positions.json

## Excluded on purpose
- .git/
- .venv/
- __pycache__/
- *.log / *.out / *.pid
- *.bak (frontend image backups)
- assets/bg-history/ (historical generated backgrounds)
- runtime state files: state.json / agents-state.json / join-keys.json

## Artifact
- File: `dist/Star-Office-UI-release-20260302.tgz`
- SHA256: `bf52147b7664adc3c457eadd3748f969b1ad5ee7e8d3059ce9c8da4c6030f6ae`

## Pre-publish checklist
1. Confirm whether `asset-defaults.json` and `asset-positions.json` should be shipped as current defaults.
2. Confirm whether `assets/bg-history/` should remain local-only (currently excluded).
3. On target machine, create fresh `state.json` and `join-keys.json` if needed.
4. Start backend and validate:
   - `/health`
   - `/status`
   - language switches (EN/JP/CN)
   - loading overlay + sidebar layering
   - asset drawer selection / upload panel behavior
