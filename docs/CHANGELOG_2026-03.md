# Changelog — 2026-03 Refresh

## Highlights

- Added robust asset editing workflow in drawer (select/deselect, highlight sync, default/override split)
- Added EN/JP/CN language buttons with real-time UI + loading + bubble text switching
- Added room loading overlay with emoji rotation and localized copy
- Fixed layering/layout issues (drawer overlap, detail overflow, canvas border fit)
- Completed multi-round state sprite replacement pipeline (Writing/Idle/Syncing/Error) with auto frame sync
- Updated syncing behavior: non-sync shows frame 0, syncing starts from frame 1
- Disabled error movement path (error anim stays in place)
- Removed GIF legacy assets and stale references
- Restored `assets/room-reference.png` for reference background restore
- Added configurable asset drawer password via env (`ASSET_DRAWER_PASS`, default `1234`)
- Improved startup performance:
  - static assets use long cache headers
  - local phaser vendor restored

## Security / Config

- Asset drawer default pass changed to `1234`
- Recommend deployment override:
  - `ASSET_DRAWER_PASS=<your-strong-pass>`
- Rationale: prevent unauthorized layout/asset modifications from shared links

## AI model recommendation for room generation

For best style-transfer quality (while preserving room structure), recommend:

1. gemini nanobanana pro
2. gemini nanobanana 2

Other models may produce unstable structure consistency.
