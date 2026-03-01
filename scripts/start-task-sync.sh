#!/bin/bash
# 启动OpenClaw -> 飞书任务同步器

cd "$(dirname "$0")/.."
SYNC_SCRIPT="backend/task_sync.py"
PID_FILE="/tmp/openclaw-task-sync.pid"
LOG_FILE="/tmp/openclaw-task-sync.log"

# 检查是否已运行
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "⚠️  任务同步器已在运行 (PID: $OLD_PID)"
        exit 0
    fi
fi

# 启动同步器
echo "🚀 启动OpenClaw任务同步器..."
nohup python3 "$SYNC_SCRIPT" > "$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"

sleep 1

if ps -p $(cat "$PID_FILE") > /dev/null 2>&1; then
    echo "✅ 任务同步器已启动 (PID: $(cat "$PID_FILE"))"
    echo "📝 日志文件: $LOG_FILE"
else
    echo "❌ 启动失败，查看日志: $LOG_FILE"
    exit 1
fi
