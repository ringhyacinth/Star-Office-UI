#!/bin/bash
# 等待 staroffice 后端就绪后自动打开任务大厅
MAX_WAIT=60
WAITED=0
URL="http://localhost:19800"

while [ $WAITED -lt $MAX_WAIT ]; do
    if curl -s -o /dev/null -w "%{http_code}" "$URL/health" 2>/dev/null | grep -q "200"; then
        open "$URL"
        exit 0
    fi
    sleep 2
    WAITED=$((WAITED + 2))
done

# 超时也尝试打开
open "$URL"
