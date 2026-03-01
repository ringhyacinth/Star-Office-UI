#!/bin/bash
# 检查OpenClaw任务同步器状态

PID_FILE="/tmp/openclaw-task-sync.pid"
LOG_FILE="/tmp/openclaw-task-sync.log"

echo "📊 OpenClaw任务同步器状态检查"
echo "================================"
echo ""

# 检查进程状态
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "✅ 同步器运行中 (PID: $PID)"
        
        # 显示运行时长
        START_TIME=$(ps -p "$PID" -o lstart=)
        echo "   启动时间: $START_TIME"
        
        # 显示最近日志
        echo ""
        echo "📝 最近日志 (最后10行):"
        echo "---"
        tail -10 "$LOG_FILE" 2>/dev/null || echo "   (日志文件为空)"
    else
        echo "❌ 同步器未运行 (PID文件存在但进程不存在)"
    fi
else
    echo "❌ 同步器未运行 (PID文件不存在)"
fi

echo ""
echo "================================"
echo "命令:"
echo "  启动: ./scripts/start-task-sync.sh"
echo "  停止: ./scripts/stop-task-sync.sh"
echo "  日志: tail -f $LOG_FILE"
