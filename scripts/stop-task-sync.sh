#!/bin/bash
# 停止OpenClaw -> 飞书任务同步器

PID_FILE="/tmp/openclaw-task-sync.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "⚠️  任务同步器未运行"
    exit 0
fi

PID=$(cat "$PID_FILE")

if ps -p "$PID" > /dev/null 2>&1; then
    echo "🛑 停止任务同步器 (PID: $PID)..."
    kill "$PID"
    rm "$PID_FILE"
    echo "✅ 已停止"
else
    echo "⚠️  进程不存在，清理PID文件"
    rm "$PID_FILE"
fi
