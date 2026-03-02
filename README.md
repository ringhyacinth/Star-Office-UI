# Star Office UI

面向多 Agent 协作的像素办公室看板：把 AI 助手的工作状态实时可视化，支持房间装修、资产替换、多语言切换与移动端访问。

![Star Office UI 预览](docs/screenshots/office-preview-20260301.jpg)

---

## 快速开始

```bash
git clone https://github.com/ringhyacinth/Star-Office-UI.git
cd Star-Office-UI
python3 -m pip install -r backend/requirements.txt
cp state.sample.json state.json
cd backend
python3 app.py
```

打开：`http://127.0.0.1:18791`

状态切换（项目根目录执行）：

```bash
python3 set_state.py writing "正在整理文档"
python3 set_state.py syncing "同步进度中"
python3 set_state.py error "发现问题，排查中"
python3 set_state.py idle "待命中"
```

---

## 核心能力

- 主 Agent 状态可视化：`idle / writing / researching / executing / syncing / error`
- 多 Agent 接入：`/join-agent`、`/agent-push`、`/leave-agent`、`/agents`
- 昨日小记：`/yesterday-memo`
- 资产侧边栏：替换素材、坐标/缩放调整、默认值写入
- 房间风格重绘：搬家/回老家/找中介（Prompt 生成）
- 多语言：CN / EN / JP 全链路联动（含 loading 与气泡）

---

## 房间装修与生图模型建议（重要）

项目支持“找中介/搬家”模式，建议接入你自己的 Gemini 图像能力。

### 推荐模型

优先推荐以下两个模型（效果更稳定）：

1. **gemini nanobanana pro**
2. **gemini nanobanana 2**

> 说明：其他模型可能在“保持房间结构 + 风格迁移一致性”上不如预期。

### 接入建议

在你的部署环境中配置 Gemini 相关凭据（示例）：

- `GEMINI_API_KEY`：你的 API Key
- `GEMINI_MODEL`：建议设为 `nanobanana-pro` 或 `nanobanana-2`
- `GEMINI_BASE_URL`：如需自建网关/代理可配置

具体调用逻辑在后端 `assets/generate-rpg-background` 相关流程中。

---

## 安全配置（强烈建议）

### 资产编辑侧边栏验证码

资产侧边栏用于修改房间布局、替换素材、改默认值，属于高风险操作入口。

- 默认验证码：`1234`
- 可通过环境变量自定义：

```bash
export ASSET_DRAWER_PASS="你的强密码"
```

**为什么必须改？**
如果你把看板公网分享，未设强验证码时，拿到链接的人可能改动你的房间布局与装饰。

---

## 关键文件与资源

- 参考底图（回老家恢复来源）：`assets/room-reference.png`
- 前端主文件：`frontend/index.html`
- 后端服务：`backend/app.py`
- 状态文件：`state.json`

---

## 常用 API

- `GET /health`
- `GET /status`
- `POST /set_state`
- `GET /agents`
- `POST /join-agent`
- `POST /agent-push`
- `POST /leave-agent`
- `GET /yesterday-memo`
- `POST /assets/generate-rpg-background`
- `POST /assets/restore-reference-background`
- `GET/POST /assets/positions`
- `GET/POST /assets/defaults`

---

## 开源许可与资产使用边界

- **Code / Logic：MIT**（见 `LICENSE`）
- **Art Assets：禁止商用，仅学习/演示/交流使用**

欢迎 Fork、提 PR、继续扩展玩法；商用请替换为你自己的原创美术资产。
