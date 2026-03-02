# Star Office UI — 功能说明（Overview）

Star Office UI 是一个“像素办公室”可视化界面，用来把 AI 助手/多个 OpenClaw 访客的状态，渲染成可在网页（含手机）查看的小办公室场景。

## 你能看到什么
- 像素办公室背景（俯视图）
- 角色（Star + 访客）会根据状态在不同区域移动
- 名字与气泡（bubble）展示当前状态/想法（可自定义映射）
- 手机端打开也能展示（适合作品展示/直播/对外演示）

## 核心能力

### 1) 单 Agent（本地 Star）状态渲染
- 后端读取 `state.json` 提供 `GET /status`
- 前端轮询 `/status`，根据 `state` 渲染 Star 所在区域
- 提供 `set_state.py` 快速切换状态

### 2) 多访客（多龙虾）加入办公室
- 访客通过 `POST /join-agent` 加入，获得 `agentId`
- 访客通过 `POST /agent-push` 持续推送自己的状态
- 前端通过 `GET /agents` 拉取访客列表并渲染

### 3) Join Key（接入密钥）机制
- 支持固定可复用 join key（如 `ocj_starteam01~08`）
- 支持每个 key 的并发在线上限（默认 3）
- 便于控制“谁能进办公室”和“同一个 key 同时可进几只龙虾”

### 4) 状态 → 区域映射（统一逻辑）
- idle → breakroom（休息区）
- writing / researching / executing / syncing → writing（工作区）
- error → error（故障区）

### 5) 访客动画与性能优化
- 访客角色使用动画精灵
- 支持 WebP 资源（体积更小、加载更快）

### 6) 名字/气泡不遮挡的布局
- 真实访客与 demo 访客分离逻辑
- 非 demo 访客名字与气泡整体上移
- bubble 锚定在名字上方，避免压住名字

### 7) Demo 模式（可选）
- `?demo=1` 才显示 demo 访客（默认不显示）
- demo 与真实访客互不影响

## 主要接口（Backend）
- `GET /`：前端页面
- `GET /status`：单 agent 状态（兼容旧版）
- `GET /agents`：多 agent 列表（访客渲染用）
- `POST /join-agent`：访客加入
- `POST /agent-push`：访客推送状态
- `POST /leave-agent`：访客离开
- `GET /health`：健康检查

## 安全与隐私注意
- 不要把隐私信息写进 `detail`（因为会被渲染/可被拉取）
- 开源前必须清理：日志、运行态文件、join keys、隧道输出等

## 美术资产使用声明（必须）
- 代码可开源，但美术素材（背景、角色、动画等）版权归原作者/工作室所有。
- 美术资产仅供学习与演示，**禁止商用**。
