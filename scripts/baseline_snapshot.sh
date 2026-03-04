#!/usr/bin/env bash
set -euo pipefail

# Star-Office-UI baseline snapshot (non-destructive)
# 用途：在改造前冻结当前可运行基线，便于随时回滚

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

TS="$(date +%Y%m%d-%H%M%S)"
SNAP_DIR="$ROOT_DIR/snapshots/baseline-$TS"
mkdir -p "$SNAP_DIR"

echo "[baseline] root=$ROOT_DIR"
echo "[baseline] snapshot=$SNAP_DIR"

# 1) 记录 git 元信息（仅记录，不修改）
{
  echo "branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"
  echo "commit=$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
  echo "created_at=$(date -Iseconds)"
} > "$SNAP_DIR/git-meta.txt"

# 2) 导出当前变更摘要
(git status --short || true) > "$SNAP_DIR/git-status.txt"
(git diff -- backend app.py frontend/index.html frontend/game.js 2>/dev/null || git diff -- .) > "$SNAP_DIR/git-diff.patch" || true

# 3) 复制关键运行态文件（如果存在）
copy_if_exists() {
  local f="$1"
  if [ -f "$f" ]; then
    mkdir -p "$SNAP_DIR/$(dirname "$f")"
    cp -a "$f" "$SNAP_DIR/$f"
    echo "copied: $f"
  else
    echo "skip: $f (not found)"
  fi
}

copy_if_exists "state.json"
copy_if_exists "agents-state.json"
copy_if_exists "join-keys.json"
copy_if_exists "runtime-config.json"
copy_if_exists "asset-positions.json"
copy_if_exists "asset-defaults.json"

# 4) 记录权限（便于回滚后复核）
(
  stat -c '%a %n' state.json agents-state.json join-keys.json runtime-config.json asset-positions.json asset-defaults.json 2>/dev/null || true
) > "$SNAP_DIR/file-perms.txt"

# 5) 产出可读说明
cat > "$SNAP_DIR/README.txt" <<EOF
This snapshot was created before stability hardening changes.

Restore hints:
1) Review git-status.txt and git-diff.patch.
2) Restore runtime files from this snapshot if needed.
3) Use git checkout/restore to roll back code changes.

Snapshot: baseline-$TS
EOF

echo "[baseline] done"
echo "$SNAP_DIR"
