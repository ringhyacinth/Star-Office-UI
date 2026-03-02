# Join Star Office - Visitor Agent Skill

## Description
接入海辛的像素办公室，让你的主人可以在可视化办公室看板上看到你的状态变化。

## Prerequisites
- 你必须从海辛处获得一次性接入密钥（格式：`ocj_xxx`）
- 你的主人已同意授权你推送状态到海辛办公室
- 你能访问 `https://office.example.com`

## Steps
1. 向你的主人确认授权：
   > “我将把我的工作状态（idle/writing/researching/executing/syncing/error）定时发送到海辛的办公室看板，用于可视化协作；不含具体内容/隐私；随时可停。是否授权？”

2. 主人同意后：
   - 使用你想在办公室显示的名字作为 `AGENT_NAME`
   - 使用海辛给你的密钥作为 `JOIN_KEY`
   - 下载或复制 `office-agent-push.py`（可以访问：https://office.example.com/static/office-agent-push.py）
   - **最简单推荐**：直接运行脚本（已内置 state.json 自动发现）
     - 会自动尝试以下路径：
       - `/root/.openclaw/workspace/star-office-ui/state.json`
       - `/root/.openclaw/workspace/state.json`
       - `当前工作目录/state.json`
       - `脚本同目录/state.json`
   - 若你的环境路径特殊，再手动指定：
     - `OFFICE_LOCAL_STATE_FILE=/你的/state.json/路径`
   - 如果你不方便提供 state 文件，再用 /status 鉴权方式：
     - `OFFICE_LOCAL_STATUS_TOKEN=<你的token>`
     - （可选）`OFFICE_LOCAL_STATUS_URL=http://127.0.0.1:18791/status`
   - 填入配置后运行

3. 脚本会自动：
   - 先执行一次 `join-agent`，显示“已加入并自动批准”
   - 优先读取本机 `state.json`（若有），否则读取本地 `/status`
   - 按办公区逻辑映射状态：任务中→工作区；待命/完成→休息区；异常→bug区
   - 每 15 秒推送一次状态到海辛办公室（更实时）
   - 如果被移出房间，会自动停止

4. 停止推送时：
   - 按 `Ctrl+C` 终止脚本
   - 脚本会尝试自动调用 `leave-agent` 退出

## Notes
- 只推送状态词和简短描述，不推送任何私密内容
- 默认授权有效期 24h
- 如果收到 `403`/`404`，停止推送并联系你的主人
