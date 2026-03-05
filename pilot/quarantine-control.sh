#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT/pilot/quarantine.env"
FLAG_FILE="$ROOT/pilot/STAR_OFFICE_PILOT.flag"
PID_FILE="$ROOT/pilot/star-office-quarantine.pid"
LOG_FILE="$ROOT/pilot/star-office-quarantine.log"

load_env() {
  if [[ ! -f "$ENV_FILE" ]]; then
    echo "env missing: $ENV_FILE" >&2
    exit 1
  fi
  set -a
  source "$ENV_FILE"
  set +a
}

is_running() {
  [[ -f "$PID_FILE" ]] || return 1
  local pid
  pid="$(cat "$PID_FILE" 2>/dev/null || true)"
  [[ -n "$pid" ]] || return 1
  kill -0 "$pid" 2>/dev/null
}

cmd_enable() {
  touch "$FLAG_FILE"
  echo "FLAG=ON"
}

cmd_disable() {
  rm -f "$FLAG_FILE"
  echo "FLAG=OFF"
}

cmd_start() {
  [[ -f "$FLAG_FILE" ]] || { echo "Refusing start: feature flag OFF"; exit 2; }
  if is_running; then
    echo "already running (pid $(cat "$PID_FILE"))"
    exit 0
  fi
  load_env
  nohup "$ROOT/.venv-pilot/bin/python" "$ROOT/backend/app.py" >"$LOG_FILE" 2>&1 &
  echo $! > "$PID_FILE"
  sleep 1
  if is_running; then
    echo "started pid=$(cat "$PID_FILE") port=${STAR_BACKEND_PORT:-18991}"
  else
    echo "failed to start; check $LOG_FILE" >&2
    exit 1
  fi
}

cmd_stop() {
  if is_running; then
    kill "$(cat "$PID_FILE")" || true
    sleep 1
    if is_running; then
      kill -9 "$(cat "$PID_FILE")" || true
    fi
  fi
  rm -f "$PID_FILE"
  echo "stopped"
}

cmd_status() {
  load_env
  echo "feature_flag=$([[ -f "$FLAG_FILE" ]] && echo ON || echo OFF)"
  echo "rollback_switch=$([[ -f "$FLAG_FILE" ]] && echo ENABLED || echo READY_OFF)"
  if is_running; then
    echo "service=RUNNING pid=$(cat "$PID_FILE") port=${STAR_BACKEND_PORT:-18991}"
    curl -s -o /dev/null -w "health_http=%{http_code}\n" "http://127.0.0.1:${STAR_BACKEND_PORT:-18991}/health" || true
  else
    echo "service=STOPPED"
  fi
}

cmd_rollback() {
  cmd_stop
  cmd_disable
  echo "ROLLBACK=COMPLETE"
}

case "${1:-}" in
  enable) cmd_enable ;;
  disable) cmd_disable ;;
  start) cmd_start ;;
  stop) cmd_stop ;;
  status) cmd_status ;;
  rollback) cmd_rollback ;;
  *) echo "usage: $0 {enable|disable|start|stop|status|rollback}"; exit 1 ;;
esac
