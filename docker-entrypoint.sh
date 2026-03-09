#!/bin/sh
set -e

DATA_DIR="${STAR_OFFICE_DATA_DIR:-/data}"
mkdir -p "$DATA_DIR"

# Initialize state files from samples on first run
[ -f "$DATA_DIR/state.json" ]     || cp /app/state.sample.json     "$DATA_DIR/state.json"
[ -f "$DATA_DIR/join-keys.json" ] || cp /app/join-keys.sample.json "$DATA_DIR/join-keys.json"

exec python backend/app.py
