#!/bin/bash
# Star Office UI Health Check
# Checks if backend is responding, restarts if not

BACKEND_URL="http://127.0.0.1:18791/health"
LOG_FILE="/root/.openclaw/workspace/star-office-ui/healthcheck.log"

# Log timestamp
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Health check starting..." >> "$LOG_FILE"

# Check backend
if curl -sS "$BACKEND_URL" > /dev/null 2>&1; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Backend is healthy" >> "$LOG_FILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Backend is NOT healthy - restarting..." >> "$LOG_FILE"
    systemctl restart star-office-backend.service
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Backend restarted" >> "$LOG_FILE"
fi
