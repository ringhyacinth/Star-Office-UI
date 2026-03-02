# PR Draft — Star Office UI March Refresh

## Title
feat: asset editor + i18n + loading UX + sprite pipeline + security/perf refinements

## Summary
This PR delivers a full refresh of Star Office UI across UX, asset pipeline, localization, stability, and deployment security.

### What changed

#### 1) Asset editor / room decoration
- Improved drawer selection UX (select/deselect + dual highlight sync)
- Upload panel now appears only when an asset is selected
- Added defaults/overrides split:
  - `GET/POST /assets/defaults`
  - `GET/POST /assets/positions`
- Added “Set Default” flow for persistent base placement

#### 2) Localization (CN/EN/JP)
- Replaced language toggles with EN / JP / CN buttons
- Active language button highlighted in green
- Real-time language switching for:
  - UI labels
  - loading texts
  - role/cat/guest bubbles
  - initial boot loading sentence

#### 3) Loading overlay and UX polish
- Added room-bound loading overlay with emoji rotation
- Updated copy to voyage-themed localized sets
- Trigger timing fixed: overlay shows immediately on click
- Overlay and detail placement bound to canvas rect for consistency

#### 4) Layout and layering fixes
- Fixed canvas border fit and theme color unification (#64477d)
- Ensured status/detail stays inside canvas and single-line clipped
- Drawer open now shifts main stage to avoid overlap and large gaps
- Drawer kept above room loading overlay

#### 5) Sprite replacement pipeline hardening
- Reworked replacement flow to detect frame size/count from incoming animated webp
- Synced loader + animation frame ranges to avoid flicker
- Applied across Writing / Idle / Syncing / Error replacements
- Syncing behavior adjusted:
  - non-sync state shows frame 0
  - syncing animation starts from frame 1
- Error animation movement path removed (fixed in place)

#### 6) Cleanup / reliability / perf
- Removed legacy GIF assets
- Removed stale asset references (zero missing static refs)
- Restored `assets/room-reference.png` for restore-reference endpoint
- Added configurable drawer pass via env:
  - `ASSET_DRAWER_PASS` (default `1234`)
- Performance improvements:
  - static assets served with long cache headers
  - local phaser vendor restored to reduce cold-load latency

## Documentation updates included
- README rewritten for latest behavior/config
- SKILL updated with deployment + safety + replacement SOP
- LICENSE updated to remove old third-party character disclaimer and keep:
  - code MIT
  - art assets non-commercial
- Added `docs/CHANGELOG_2026-03.md`

## Deployment notes
- Recommended model for room generation:
  1. gemini nanobanana pro
  2. gemini nanobanana 2
- Security recommendation:
  - always override `ASSET_DRAWER_PASS` in production/public deployments

## Test checklist
- [ ] Open page cold + warm load
- [ ] Switch CN/EN/JP at any state
- [ ] Trigger Move Home/Broker and observe local status text + loading overlay
- [ ] Replace one animated asset and verify frame sync/no flicker
- [ ] Verify Error is fixed in place
- [ ] Verify `/assets/restore-reference-background` works with `assets/room-reference.png`
- [ ] Verify no missing `/static/*` refs in runtime logs

## How to create PR
1. `git checkout -b feat/march-refresh`
2. `git push -u origin feat/march-refresh`
3. Open PR to `ringhyacinth/Star-Office-UI:main`
4. Paste this document as PR description
