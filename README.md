# Star Office UI

🌐 Language: **中文** | [English](./README.en.md) | [日本語](./README.ja.md)

![Star Office UI 封面](docs/screenshots/readme-cover-2.jpg)

**一个像素风格的 AI 办公室看板** —— 把 AI 助手的工作状态实时可视化，让你直观看到"谁在做什么、昨天做了什么、现在是否在线"。

支持多 Agent 协作、中英日三语、AI 生图装修、桌面宠物模式。
与 [OpenClaw](https://github.com/openclaw/openclaw) 深度集成时体验最佳，也可以独立部署作为状态看板使用。

> 本项目由 **[Ring Hyacinth](https://x.com/ring_hyacinth)** 与 **[Simon Lee](https://x.com/simonxxoo)** 共同创建（co-created project），并与社区开发者（[@Zhaohan-Wang](https://github.com/Zhaohan-Wang)、[@Jah-yee](https://github.com/Jah-yee)、[@liaoandi](https://github.com/liaoandi)）一起持续维护和共建。
> 欢迎提交 Issue 和 PR，也感谢每一位贡献者的支持。

---

## ✨ 快速体验

### 方式一：让龙虾帮你部署（推荐给 OpenClaw 用户）

如果你正在使用 [OpenClaw](https://github.com/openclaw/openclaw)，直接把下面这句话发给你的龙虾：

```text
请按照这个 SKILL.md 帮我完成 Star Office UI 的部署：
https://github.com/ringhyacinth/Star-Office-UI/blob/master/SKILL.md
```

龙虾会自动完成 clone、安装依赖、启动后端、配置状态同步，并把访问地址发给你。

### 方式二：30 秒手动部署

```bash
# 1) 下载仓库
git clone https://github.com/ringhyacinth/Star-Office-UI.git
cd Star-Office-UI

# 2) 安装依赖
python3 -m pip install -r backend/requirements.txt

# 3) 准备状态文件（首次）
cp state.sample.json state.json

# 4) 启动后端
cd backend
python3 app.py
```

打开 **http://127.0.0.1:19000**，然后试试切状态：

```bash
python3 set_state.py writing "正在整理文档"
python3 set_state.py error "发现问题，排查中"
python3 set_state.py idle "待命中"
```

![Star Office UI 预览](docs/screenshots/readme-cover-1.jpg)

---

## 🤔 适合谁用？

### 有 OpenClaw / AI Agent 的用户
这是**完整体验**。Agent 在工作时自动切换状态，办公室里的像素角色会实时走到对应区域——你只需要打开网页，就能看到 AI 此刻在做什么。

### 没有 OpenClaw 的用户
也完全可以部署。你可以：
- 用 `set_state.py` 或 API 手动 / 脚本推送状态
- 把它当成一个像素风的个人状态页 / 远程办公看板
- 接入任何能发 HTTP 请求的系统来驱动状态


---

## 📋 功能一览

1. **状态可视化** —— 6 种状态（`idle` / `writing` / `researching` / `executing` / `syncing` / `error`）自动映射到办公室不同区域，动画 + 气泡实时展示
2. **昨日小记** —— 自动从 `memory/*.md` 读取最近一天的工作记录，脱敏后展示为"昨日小记"卡片
3. **多 Agent 协作** —— 通过 join key 邀请其他 Agent 加入你的办公室，实时查看多人状态
4. **中英日三语** —— CN / EN / JP 一键切换，界面文案、气泡、加载提示全部联动
5. **美术资产自定义** —— 侧边栏管理角色 / 场景 / 装饰素材，支持动态帧同步，避免闪烁
6. **AI 生图装修** —— 接入 Gemini API，用 AI 给办公室换背景；不接入 API 也能正常使用核心功能
7. **移动端适配** —— 手机直接打开即可查看，适合外出时快速瞄一眼
8. **安全加固** —— 侧边栏密码保护、生产环境弱密码拦截、Session Cookie 加固
9. **灵活公网访问** —— 推荐 Cloudflare Tunnel 一键公网化，也可用自有域名 / 反向代理
10. **桌面宠物版** —— 可选的 Tauri 桌面封装，把办公室变成透明窗口的桌面宠物（见下方说明）

---

## 🚀 详细部署指南

### 1) 安装依赖

```bash
cd Star-Office-UI
python3 -m pip install -r backend/requirements.txt
```

### 2) 初始化状态文件

```bash
cp state.sample.json state.json
```

### 3) 启动后端

```bash
cd backend
python3 app.py
```

打开 `http://127.0.0.1:19000`

> ✅ 首次部署可以先保留默认配置；在生产环境中，请复制 `.env.example` 为 `.env` 并设置强随机的 `FLASK_SECRET_KEY` 与 `ASSET_DRAWER_PASS`，避免弱密码和会话泄露。

### 4) 切换状态

```bash
python3 set_state.py writing "正在整理文档"
python3 set_state.py syncing "同步进度中"
python3 set_state.py error "发现问题，排查中"
python3 set_state.py idle "待命中"
```

### 5) 公网访问（可选）

```bash
cloudflared tunnel --url http://127.0.0.1:19000
```

拿到 `https://xxx.trycloudflare.com` 链接即可分享。

### 6) 验证安装（可选）

```bash
python3 scripts/smoke_test.py --base-url http://127.0.0.1:19000
```

所有检查显示 `OK` 即表示部署成功。

---

## 🐳 Docker 部署（可选）

如果你希望用 Docker 运行，无需手动安装 Python 依赖，重启自动恢复。

### 1) 准备配置文件

```bash
cp .env.example .env
```

编辑 `.env`，至少填写 `MEMORY_HOST_PATH`（你本机 memory 目录的绝对路径）：

```bash
FLASK_SECRET_KEY=replace_with_a_long_random_secret
ASSET_DRAWER_PASS=replace_with_strong_drawer_password
MEMORY_HOST_PATH=/absolute/path/to/your/memory
```

### 2) 启动

```bash
docker compose up -d --build
```

打开 `http://127.0.0.1:19000`

首次启动会自动从 `state.sample.json` 和 `join-keys.sample.json` 初始化数据文件，持久化到 `./data/` 目录。

### 3) 切换状态（API 方式）

Docker 部署时，用 HTTP API 替代 `set_state.py`：

```bash
curl -X POST http://127.0.0.1:19000/set_state \
  -H "Content-Type: application/json" \
  -d '{"state": "writing", "detail": "正在整理文档"}'
```

可用状态：`idle` / `writing` / `researching` / `executing` / `syncing` / `error`

### 4) 常用命令

```bash
docker compose up -d          # 启动（已构建过）
docker compose up -d --build  # 重新构建并启动
docker compose logs -f        # 查看日志
docker compose down           # 停止
```

---

## 🦞 OpenClaw 深度集成

> 以下内容面向 [OpenClaw](https://github.com/openclaw/openclaw) 用户。如果你不使用 OpenClaw，可以跳过这一节。

### 状态自动同步

在你的 `SOUL.md`（或 Agent 规则文件）中加入以下规则，让 Agent 自觉维护状态：

```markdown
## Star Office 状态同步规则
- 接到任务时：先执行 `python3 set_state.py <状态> "<描述>"` 再开始工作
- 完成任务后：执行 `python3 set_state.py idle "待命中"` 再回复
```

**6 种状态 → 3 个区域的映射：**

| 状态 | 办公室区域 | 触发场景 |
|------|-----------|---------|
| `idle` | 🛋 休息区（沙发） | 待命 / 任务完成 |
| `writing` | 💻 工作区（办公桌） | 写代码 / 写文档 |
| `researching` | 💻 工作区 | 搜索 / 调研 |
| `executing` | 💻 工作区 | 执行命令 / 跑任务 |
| `syncing` | 💻 工作区 | 同步数据 / 推送 |
| `error` | 🐛 Bug 区 | 报错 / 异常排查 |

### 邀请其他 Agent 加入办公室

**Step 1：准备 join key**

首次启动后端时，如果当前目录下不存在 `join-keys.json`，服务会自动根据 `join-keys.sample.json` 生成一个运行时的 `join-keys.json`（内含示例 key，例如 `ocj_example_team_01`）。你可以在生成后的 `join-keys.json` 中自行添加、修改或删除 key，每个 key 默认支持最多 3 人同时在线。

**Step 2：让访客 Agent 运行推送脚本**

访客只需下载 `office-agent-push.py`，填写 3 个变量即可：

```python
JOIN_KEY = "ocj_starteam02"          # 你分配的 key
AGENT_NAME = "小明的龙虾"            # 显示名称
OFFICE_URL = "https://office.hyacinth.im"  # 你的办公室地址
```

```bash
python3 office-agent-push.py
```

脚本会自动加入办公室并每 15 秒推送一次状态。访客会出现在看板上，根据状态自动走到对应区域。

**Step 3（可选）：访客安装 Skill**

访客也可以把 `frontend/join-office-skill.md` 作为 Skill 使用，Agent 会自动完成配置和推送。

> 详细的访客接入说明见 [`frontend/join-office-skill.md`](./frontend/join-office-skill.md)

---

## 📡 常用 API

| 端点 | 说明 |
|------|------|
| `GET /health` | 健康检查 |
| `GET /status` | 获取主 Agent 状态 |
| `POST /set_state` | 设置主 Agent 状态 |
| `GET /agents` | 获取多 Agent 列表 |
| `POST /join-agent` | 访客加入办公室 |
| `POST /agent-push` | 访客推送状态 |
| `POST /leave-agent` | 访客离开 |
| `GET /yesterday-memo` | 获取昨日小记 |
| `GET /config/gemini` | 获取 Gemini API 配置 |
| `POST /config/gemini` | 设置 Gemini API 配置 |
| `GET /assets/generate-rpg-background/poll` | 轮询生图进度 |

---

## 🖥 桌面宠物版（可选）

`desktop-pet/` 目录提供了一个基于 **Tauri** 的桌面封装版本，可以把像素办公室变成一个透明窗口的桌面宠物。

```bash
cd desktop-pet
npm install
npm run dev
```

- 启动时自动拉起 Python 后端
- 窗口默认指向 `http://127.0.0.1:19000/?desktop=1`
- 支持通过环境变量自定义项目路径和 Python 路径

> ⚠️ 这是一个**可选的实验性功能**，目前主要在 macOS 上开发测试。详见 [`desktop-pet/README.md`](./desktop-pet/README.md)。
>
> 🙏 桌面宠物版由 [@Zhaohan-Wang](https://github.com/Zhaohan-Wang) 独立开发，感谢他的贡献！

---

## 🎨 美术资产与开源许可

### 资产来源

访客角色动画使用了 **LimeZu** 的免费资产：
- [Animated Mini Characters 2 (Platformer) [FREE]](https://limezu.itch.io/animated-mini-characters-2-platform-free)

请在二次发布 / 演示时保留来源说明，并遵守原作者许可条款。

### 许可协议

- **代码 / 逻辑：MIT**（见 [`LICENSE`](./LICENSE)）
- **美术资产：禁止商用**（仅学习 / 演示 / 交流用途）

> 如需商用，请将所有美术资产替换为你自己的原创素材。

---

## 📝 更新日志

| 日期 | 概要 | 详情 |
|------|------|------|
| 2026-03-06 | 🔌 默认端口调整 — 默认后端端口从 18791 调整为 19000，以避开 OpenClaw Browser Control 端口冲突；同步更新脚本、桌面壳与文档默认值 | [`docs/CHANGELOG_2026-03.md`](./docs/CHANGELOG_2026-03.md) |
| 2026-03-05 | 📱 稳定性修复 — CDN 缓存修复、生图异步化、移动端侧边栏优化、Join Key 过期与并发控制 | [`docs/UPDATE_REPORT_2026-03-05.md`](./docs/UPDATE_REPORT_2026-03-05.md) |
| 2026-03-04 | 🔒 P0/P1 安全加固 — 弱密码拦截、后端模块拆分、stale 状态自动回 idle、首屏骨架屏优化 | [`docs/UPDATE_REPORT_2026-03-04_P0_P1.md`](./docs/UPDATE_REPORT_2026-03-04_P0_P1.md) |
| 2026-03-03 | 📋 开源发布检查清单完成 | [`docs/OPEN_SOURCE_RELEASE_CHECKLIST.md`](./docs/OPEN_SOURCE_RELEASE_CHECKLIST.md) |
| 2026-03-01 | 🎉 **v2 重制发布** — 新增三语支持、资产管理系统、AI 生图装修、美术资产全面替换 | [`docs/FEATURES_NEW_2026-03-01.md`](./docs/FEATURES_NEW_2026-03-01.md) |

---

## 📁 项目结构

```text
Star-Office-UI/
├── backend/            # Flask 后端
│   ├── app.py
│   ├── requirements.txt
│   └── run.sh
├── frontend/           # 前端页面与资产
│   ├── index.html
│   ├── join.html
│   ├── invite.html
│   └── layout.js
├── desktop-pet/        # Tauri 桌面宠物版（可选）
├── docs/               # 文档与截图
│   └── screenshots/
├── office-agent-push.py  # 访客推送脚本
├── set_state.py          # 状态切换脚本
├── state.sample.json     # 状态文件模板
├── join-keys.sample.json # Join Key 模板（启动时生成 join-keys.json）
├── SKILL.md              # OpenClaw Skill
└── LICENSE               # MIT 许可
```

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/image?repos=ringhyacinth/Star-Office-UI&type=date&legend=top-left)](https://www.star-history.com/?repos=ringhyacinth%2FStar-Office-UI&type=date&legend=top-left)
