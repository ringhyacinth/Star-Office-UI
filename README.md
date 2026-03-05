# Star Office UI

🌐 Language: **中文** | [English](./README.en.md) | [日本語](./README.ja.md)

![Star Office UI 封面 2](docs/screenshots/readme-cover-2.jpg)

一个面向多 Agent 协作的像素办公室看板：把 AI 助手（OpenClaw / 龙虾）的工作状态实时可视化，帮助团队直观看到“谁在做什么、昨天做了什么、现在是否在线”。

> 本项目为 **Ring Hyacinth 与 Simon Lee 的共同项目（co-created project）**。

---

## 这是个什么项目？（一句话）

Star Office UI 是一个“多人协作状态看板”——你可以把它想象成：
> 一个实时更新的“像素办公室仪表盘”：你的 AI 助手（和你邀请的其他 Agent）会根据状态自动走到不同位置（休息区 / 工作区 / bug 区），你还能看到他们昨天的工作小记。

---

## ✨ 30 秒快速体验（推荐先看这里）

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

打开：**http://127.0.0.1:18791**

切状态试试（在项目根目录执行）：
```bash
python3 set_state.py writing "正在整理文档"
python3 set_state.py syncing "同步进度中"
python3 set_state.py error "发现问题，排查中"
python3 set_state.py idle "待命中"
```
![Star Office UI 封面 1](docs/screenshots/readme-cover-1.jpg)
---

## 1、这个项目实现了什么

Star Office UI 目前实现了：

1. **可视化龙虾工作状态**
   - 状态：`idle`（闲置）、`writing`（工作）、`researching`（研究）、`executing`（执行）、`syncing`（同步）、`error`（报 bug）
   - 状态会映射到办公室里的不同区域，并通过动画/气泡展示。

2. **“昨日小记”微型总结**
   - 前端展示“昨日小记”卡片。
   - 后端从 `memory/*.md` 中读取昨天（或最近可用）的记录，做基础脱敏后展示。

3. **支持邀请其他访客加入办公室（功能持续迭代中）**
   - 通过 join key 加入。
   - 访客可持续 push 自己状态到办公室看板。
   - 当前已可用，但整体仍在持续优化交互与接入体验。

4. **已适配手机端访问**
   - 移动端可直接打开与查看状态（适合外出时快速查看）。

5. **支持中英日三语切换**
   - 已支持 CN / EN / JP 三语切换。
   - 语言切换会实时作用于界面文案、加载提示与角色气泡。

6. **支持自定义美术资产**
   - 支持在资产侧边栏替换角色/场景素材。
   - 支持动态素材重切帧与参数同步（frame size / frame range）以避免闪烁。

7. **支持接入自己的生图 API（可无限换背景）**
   - 支持接入自有生图 API 进行“搬新家/找中介”式背景更新。
   - 推荐模型：`nanobanana-pro` 或 `nanobanana-2`（结构保持更稳定）。
   - 基础看板功能不依赖 API；不接入 API 也可正常使用核心状态看板与资产管理。

8. **公网访问方式灵活**
   - Skill 默认建议使用 Cloudflare Tunnel 快速公网化。
   - 也可以使用你自己的公网域名 / 反向代理方案。

---

## 2、本次重制（2026-03）核心变化

本次版本不是零散修补，而是基于原项目的一次完整重制。核心变化集中在以下 4 个方向：

1. **新增中英日三语（CN / EN / JP）**
   - 全局界面文案三语化
   - 状态文案、提示文案、资产显示名可联动切换

2. **新增资产管理功能（用户可自定义全量美术资产）**
   - 资产侧边栏支持选择、替换、默认值管理
   - 用户可自定义角色、场景、装饰、按钮等素材

3. **接入生图 API（支持房间智能装修 + 用户手动装修）**
   - 支持“搬新家 / 找中介 / 自己装”等装修流
   - 龙虾可基于生图能力更换房间设计，用户也可手动输入主题改造

4. **美术资产替换与优化（重点）**
   - 核心资产完成大规模替换与重绘
   - 重建资产命名与索引映射，提升替换稳定性与维护性
   - 动态素材切帧与展示逻辑优化，减少错帧/缓存干扰

---

## 3、快速开始

> 💡 推荐使用 Docker 部署，一行命令启动，无需手动安装依赖

### 方式一：Docker 部署（推荐）

```bash
# 1) 克隆
git clone https://github.com/MISAKIGA/Star-Office-UI.git
cd Star-Office-UI

# 2) 配置环境变量
cp .env.example .env
# 编辑 .env 填入 API_TOKEN 和 ADMIN_TOKEN

# 3) 启动（使用预构建镜像）
docker run -d \
  --name star-office-ui \
  -p 5000:18791 \
  -v /root/.openclaw/workspace/memory:/app/memory:ro \
  -e API_TOKEN=your-api-token \
  -e ADMIN_TOKEN=your-admin-token \
  msga/star-office-ui-backend:latest

# 或使用 docker-compose
docker-compose up -d

# 4) 访问
# http://localhost:5000
```

### 方式二：本地运行

### 1) 安装依赖

```bash
cd star-office-ui
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

打开：`http://127.0.0.1:18791`

### 4) 切换主 Agent 状态（示例）

```bash
python3 set_state.py writing "正在整理文档"
python3 set_state.py syncing "同步进度中"
python3 set_state.py error "发现问题，排查中"
python3 set_state.py idle "待命中"
```

---

## 4、常用 API

- `GET /health`：健康检查
- `GET /status`：主 Agent 状态
- `POST /set_state`：设置主 Agent 状态
- `GET /agents`：获取多 Agent 列表
- `POST /join-agent`：访客加入
- `POST /agent-push`：访客推送状态
- `POST /leave-agent`：访客离开
- `GET /yesterday-memo`：昨日小记

### Token 鉴权

部分接口需要 Token 鉴权：

| Header | 用途 |
|--------|------|
| `X-API-Token` | 用户 API Token（读写状态） |
| `X-Admin-Token` | 管理员 Token（管理操作） |

生成 Token：
```bash
# 生成新 Token
curl -X POST http://localhost:5000/api/v1/admin/token/generate \
  -H "X-Admin-Token: your-admin-token"

# 列出 Token
curl http://localhost:5000/api/v1/admin/tokens \
  -H "X-Admin-Token: your-admin-token"
```

---

## 5、OpenClaw 插件（自动状态同步）

Star Office UI 提供 OpenClaw 插件，实现 Agent 状态自动同步。支持两种使用方式：

### 5.1 两种使用方式

| 方式 | 描述 | 适用场景 |
|------|------|---------|
| **本地接入** | 通过 Join Key 加入办公室 | 多 Agent 协作、本地部署 |
| **远程连接** | 通过插件配置连接到远程办公室 | 公网访问、远程监控 |

### 5.2 安装方式

#### 方式一：命令行安装（推荐）

```bash
# 安装本地插件
openclaw plugins install ./plugins/openclaw

# 或使用 --link 避免复制
openclaw plugins install -l ./plugins/openclaw

# 安装远程插件（指定版本）
openclaw plugins install star-office-ui@1.0.0
```

> ⚠️ **安全提示**：将插件安装视为运行代码。优先使用固定版本。

#### 方式二：手动配置

编辑 `~/.openclaw/openclaw.json`：

```json
{
  "plugins": {
    "allow": ["star-office"],
    "entries": {
      "star-office": {
        "enabled": true,
        "config": {
          "apiUrl": "http://localhost:5000",
          "apiToken": "your-api-token"
        }
      }
    }
  }
}
```

### 5.3 配置参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `apiUrl` | string | ✅ 必填 | `http://localhost:5000` | Star Office UI 后端 API 地址 |
| `apiToken` | string | ✅ 必填 | - | API 鉴权 Token（需通过后端生成） |
| `agentId` | string | ❌ 可选 | `openclaw-{timestamp}` | Agent 唯一标识 |
| `agentName` | string | ❌ 可选 | - | Agent 显示名称 |
| `joinKey` | string | ❌ 可选 | - | 远程模式时可留空 |
| `memoryDir` | string | ❌ 可选 | `~/.openclaw/workspace/memory` | memory 文件目录 |
| `autoIdleSeconds` | number | ❌ 可选 | `300` | 自动空闲超时（秒） |

### 5.4 生成 API Token

```bash
# 1. 启动后端
cd Star-Office-UI && docker-compose up -d

# 2. 生成 Token（需要先设置 ADMIN_TOKEN）
curl -X POST http://localhost:5000/api/v1/admin/token/generate \
  -H "X-Admin-Token: your-admin-token" \
  -H "Content-Type: application/json" \
  -d '{"name": "openclaw-agent", "type": "api"}'

# 3. 复制返回的 token 到插件配置
```

### 5.5 插件功能

- ✅ `before_agent_start` - Agent 开始工作时显示"工作中"
- ✅ `agent_end` - Agent 结束时显示"空闲"或"错误"
- ✅ `agent_error` - Agent 报错时显示错误状态
- ✅ 自动同步昨日 memo 到办公室看板
- ✅ 每日 8 点自动同步（通过 cron 或 heartbeat）

---

## 6、美术资产使用说明（请务必阅读）

### 访客角色资产来源

访客角色动画使用了 LimeZu 的免费资产：
- **Animated Mini Characters 2 (Platformer) [FREE]**
- https://limezu.itch.io/animated-mini-characters-2-platform-free

请在二次发布/演示时保留来源说明，并遵守原作者许可条款。

### 商用限制（重要）

- 代码玩法可以基于 MIT 使用与二次开发。
- **本仓库所有美术资产（含主角色/场景/素材整包）禁止商用。**
- 若你要做商用，请务必制作并替换成你自己的原创美术资产。

---

## 7、开源许可与声明

- **Code / Logic：MIT**（见 `LICENSE`）
- **Art Assets：非商用，仅学习/演示用途**

欢迎 Fork、交流玩法、提 PR；但请严格遵守资产使用边界。

---

## 8、期待更多玩法交流

欢迎你基于这个框架扩展：
- 更丰富的状态语义与自动编排
- 多房间/多团队协作地图
- 任务看板、时间线、日报自动生成
- 更完整的访问控制与权限体系

如果你做了有趣改造，欢迎分享！

---

## 9、项目作者

本项目由 **Ring Hyacinth** 与 **Simon Lee** 共同创作与维护。

- **X：Ring Hyacinth (@ring_hyacinth)**  
  https://x.com/ring_hyacinth
- **X：Simon Lee (@simonxxoo)**  
  https://x.com/simonxxoo

---

## 9、2026-03 增量更新（在原版基础上补充）

> 本节仅记录“新增/变化”，其余内容保持原版结构不变。

### A) 房间装修生图模型推荐（新增）

在“搬新家 / 找中介”能力中，建议优先接入你自己的 Gemini 并使用：

1. **gemini nanobanana pro**
2. **gemini nanobanana 2**

其他模型在“保持原房间结构 + 风格迁移一致性”上可能不如预期。

建议配置：

- `GEMINI_API_KEY`
- `GEMINI_MODEL`（建议 `nanobanana-pro` 或 `nanobanana-2`）

此外，项目已支持运行时配置入口：
- `GET /config/gemini`
- `POST /config/gemini`

当 API key 缺失时，侧边栏会出现填写入口，用户可直接补填后重试。

### B) 资产编辑侧边栏验证码（新增）

侧边栏可以修改布局、装饰、默认位置。

当前默认值：
- `ASSET_DRAWER_PASS=1234`

推荐引导用户口径：
1. 默认密码 `1234` 可先用于体验；
2. 用户可随时和你沟通修改密码；
3. 建议尽快改成强密码，这样更安全。

示例：

```bash
export ASSET_DRAWER_PASS="your-strong-pass"
```

必要性：
- 防止拿到访问链接的人修改你的房间布局与素材。

### C) 安装成功后给主人的三条提醒（新增）

1. **临时公网链接**
   - 将 `trycloudflare` 临时链接发给主人；
   - 并告知后续可继续部署到本地域名，你可以一步步带他操作。

2. **装修房子入口**
   - 提醒主人可点击“装修房间”开始；
   - 默认密码 `1234`；
   - 主人若想改密码，可随时告诉你，你来协助修改；
   - 建议改成强密码。

3. **生图 API 配置**
   - 生图需要使用用户自己的 API；
   - 当前接入是 Gemini 官方 API 格式与地址；
   - 若需改为其他 API 类型，请先沟通并提供相关 API 文档，便于你适配。

### D) 运行状态使用建议（新增）

建议 Agent 主动维护自己的状态：

1. 接任务前，先切换到“工作中”（如 writing / researching / executing），再开始执行任务；
2. 完成任务后，先切换到“待命中（idle）”，再进入休息/等待下一任务。

这样主人在办公室看板里看到的状态会更真实、连续。

### E) 美术与版权口径更新（重要）

本次重制重点之一是美术资产系统升级（大规模替换 + 命名与索引重建）。

保留原则：
- 代码逻辑：MIT
- 美术资产：禁止商用（仅学习/演示/交流用途）


### F) 2026-03-04 P0/P1 安全与稳定性更新（新增）

本次补丁聚焦“可上线稳定运行 + 状态同步真实性”，在不减少既有功能前提下完成以下更新：

1. **P0 安全基线**
   - 增加生产模式安全校验（弱 secret / 弱口令阻止启动）
   - Session Cookie 安全参数加固
   - 新增 `scripts/security_check.py`（上线前安全自检）

2. **P1 结构优化（无行为变化）**
   - 后端拆分：`security_utils.py` / `memo_utils.py` / `store_utils.py`
   - 降低 `app.py` 耦合度，提升后续维护效率

3. **状态同步与体验优化**
   - 修复状态源读取路径优先级
   - stale 状态自动回 `idle`，减少“假工作中”
   - 优化首屏加载体感（骨架屏、非关键初始化延后）

4. **服务稳定性修复**
   - 修复并统一 `star-office-ui.service` 常驻运行（18888）
   - 与 `star-office-push.service` 联动，降低 502 风险

> 详细说明见：`docs/UPDATE_REPORT_2026-03-04_P0_P1.md`

## 项目结构

```text
star-office-ui/
  backend/
    app.py              # Flask API (含 Token 鉴权)
    requirements.txt
    plugins/            # OpenClaw 插件
  frontend/
    index.html         # 主页面
    layout.js
    ...assets          # 像素素材
  docs/
    screenshots/
  docker-compose.yml   # Docker 部署
  Dockerfile           # 镜像构建
  nginx.conf           # Nginx 配置
  .env.example         # 环境变量模板
  office-agent-push.py
  set_state.py
  state.sample.json
  join-keys.json
  SKILL.md
  README.md
  LICENSE
```
  README.md
  LICENSE
```
## Star History

[![Star History Chart](https://api.star-history.com/image?repos=ringhyacinth/Star-Office-UI&type=date&legend=top-left)](https://www.star-history.com/?repos=ringhyacinth%2FStar-Office-UI&type=date&legend=top-left)


