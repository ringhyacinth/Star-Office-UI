# Star Office UI

一个面向多 Agent 协作的像素办公室看板：把 AI 助手（OpenClaw / 龙虾）的工作状态实时可视化，帮助团队直观看到“谁在做什么、昨天做了什么、现在是否在线”。

![Star Office UI 预览](docs/screenshots/office-preview-20260301.jpg)

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

## 2、本次更新相比上次的主要内容

本次发布相对早期基础版，新增/升级重点如下：

- 新增多 Agent 机制：`/join-agent`、`/agent-push`、`/leave-agent`、`/agents`
- 新增“昨日小记”接口与前端展示：`/yesterday-memo`
- 状态体系更完整：支持 `syncing`、`error` 等状态可视化
- 场景与角色动画升级：补充大量像素动画资产（含访客角色）
- 文档与 Skill 重写：更适合外部程序员快速上手
- 清理发布结构：去除临时文件 / 缓存 / 日志，降低阅读门槛
- 补充开源声明：代码 MIT、但美术资产禁止商用

---

## 3、快速开始

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

---

## 5、美术资产使用说明（请务必阅读）

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

## 6、开源许可与声明

- **Code / Logic：MIT**（见 `LICENSE`）
- **Art Assets：非商用，仅学习/演示用途**

欢迎 Fork、交流玩法、提 PR；但请严格遵守资产使用边界。

---

## 7、期待更多玩法交流

欢迎你基于这个框架扩展：
- 更丰富的状态语义与自动编排
- 多房间/多团队协作地图
- 任务看板、时间线、日报自动生成
- 更完整的访问控制与权限体系

如果你做了有趣改造，欢迎分享！

---

## 8、作者社交账号

- **X：Ring Hyacinth (@ring_hyacinth)**  
  https://x.com/ring_hyacinth
- **X：Simon Lee (@simonxxoo)**  
  https://x.com/simonxxoo

---

## 项目结构（简版）

```text
star-office-ui/
  backend/
    app.py
    requirements.txt
    run.sh
  frontend/
    index.html
    join.html
    invite.html
    layout.js
    ...assets
  docs/
    screenshots/
  office-agent-push.py
  set_state.py
  state.sample.json
  join-keys.json
  SKILL.md
  README.md
  LICENSE
```

---

---

---

# Star Office UI

A pixel office dashboard for multi-agent collaboration: visualize your AI assistants’ (OpenClaw / "lobster") work status in real-time, helping the team intuitively see "who is doing what, what they did yesterday, and whether they are online now."

![Star Office UI Preview](docs/screenshots/office-preview-20260301.jpg)

---

## What is this project? (In one sentence)

Star Office UI is a "multi-person collaboration status dashboard"—think of it as:
> A real-time "pixel office dashboard": your AI assistants (and other agents you invite) automatically move to different areas based on their status (breakroom / desk / bug area), and you can also see a micro-summary of their work from yesterday.

---

## ✨ 30-second Quick Start (Recommended)

```bash
# 1) Clone repository
git clone https://github.com/ringhyacinth/Star-Office-UI.git
cd Star-Office-UI

# 2) Install dependencies
python3 -m pip install -r backend/requirements.txt

# 3) Initialize state file (first run)
cp state.sample.json state.json

# 4) Start backend
cd backend
python3 app.py
```

Open: **http://127.0.0.1:18791**

Try changing states (run from project root):
```bash
python3 set_state.py writing "Organizing documents"
python3 set_state.py syncing "Syncing progress"
python3 set_state.py error "Found an issue, debugging"
python3 set_state.py idle "Standing by"
```

---

## I. What does this project do?

Star Office UI currently provides:

1. **Visualize lobster work status**
   - States: `idle`, `writing`, `researching`, `executing`, `syncing`, `error`
   - States map to different areas in the office and are shown with animations / bubbles.

2. **"Yesterday Memo" micro-summary**
   - A "Yesterday Memo" card in the UI.
   - Backend reads yesterday’s (or most recent available) records from `memory/*.md` and displays them after basic privacy sanitization.

3. **Support inviting other guests to join the office (feature ongoing)**
   - Join via join key.
   - Guests can continuously push their status to the office dashboard.
   - Currently usable, but overall interaction and onboarding experience are still being optimized.

4. **Mobile-friendly access**
   - Mobile devices can directly open and view status (great for quick checks on the go).

5. **Flexible public access options**
   - Skill defaults to using Cloudflare Tunnel for quick public access.
   - You can also use your own public domain / reverse proxy setup.

---

## II. Main changes in this update

This release adds/upgrades the following compared to the early base version:

- Added multi-agent mechanism: `/join-agent`, `/agent-push`, `/leave-agent`, `/agents`
- Added "Yesterday Memo" endpoint and UI: `/yesterday-memo`
- More complete state system: supports visualization for `syncing`, `error`, etc.
- Scene and character animation upgrade: added lots of pixel art assets (including guest roles)
- Rewrote docs and Skill: more beginner-friendly for external programmers
- Cleaned up release structure: removed temp files / cache / logs to lower comprehension barrier
- Added open-source notice: code under MIT, but art assets are non-commercial

---

## III. Quick Start

### 1) Install dependencies

```bash
cd star-office-ui
python3 -m pip install -r backend/requirements.txt
```

### 2) Initialize state file

```bash
cp state.sample.json state.json
```

### 3) Start backend

```bash
cd backend
python3 app.py
```

Open: `http://127.0.0.1:18791`

### 4) Switch main Agent status (example)

```bash
python3 set_state.py writing "Organizing documents"
python3 set_state.py syncing "Syncing progress"
python3 set_state.py error "Found an issue, debugging"
python3 set_state.py idle "Standing by"
```

---

## IV. Common APIs

- `GET /health`: Health check
- `GET /status`: Main agent status
- `POST /set_state`: Set main agent status
- `GET /agents`: Get multi-agent list
- `POST /join-agent`: Guest joins
- `POST /agent-push`: Guest pushes status
- `POST /leave-agent`: Guest leaves
- `GET /yesterday-memo`: Yesterday Memo

---

## V. Art Asset Usage Notes (Please Read)

### Guest character asset source

Guest character animations use LimeZu’s free assets:
- **Animated Mini Characters 2 (Platformer) [FREE]**
- https://limezu.itch.io/animated-mini-characters-2-platform-free

Please keep the source attribution and follow the original author’s license terms when redistributing / demonstrating.

### Other asset notes & disclaimer (Important)

- **Main character (Starmie) & homophone note:**
  - “Starmie” is an existing character IP from Nintendo/Pokémon, **not original to this project**.
  - This project is **non-commercial fan creation only**: this character was chosen because of a fun homophone between “Starmie” and the author’s Chinese name “海辛” (Hǎi Xīn).
  - All fan-created content in this project is for **learning, demonstration, and idea sharing only, with no commercial use**.
  - Nintendo, Pokémon, and “Starmie” are trademarks or registered trademarks of Nintendo/The Pokémon Company.
  - If you plan to use any content related to this project, please use your own original characters/art assets.

- **Office scene & other assets:** created by the project author team.

### Commercial restriction (Important)

- Code/logic may be used and modified under MIT.
- **All art assets in this repo (including main character / scene / full pack) are NOT for commercial use.**
- If you want to use this commercially, please create and replace with your own original art assets.

---

## VI. Open-source License & Notice

- **Code / Logic: MIT** (see `LICENSE`)
- **Art Assets: non-commercial, for learning / demo only**

Forks, idea sharing, and PRs are welcome; please strictly respect the asset usage boundaries.

---

## VII. Looking forward to more idea sharing

Feel free to extend this framework with:
- Richer state semantics and auto-orchestration
- Multi-room / multi-team collaboration maps
- Task boards, timelines, auto-generated daily reports
- More complete access control and permission systems

If you make an interesting modification, please share!

---

## VIII. Author social accounts

- **X: Ring Hyacinth (@ring_hyacinth)**  
  https://x.com/ring_hyacinth
- **X: Simon Lee (@simonxxoo)**  
  https://x.com/simonxxoo

---

## Project structure (simplified)

```text
star-office-ui/
  backend/
    app.py
    requirements.txt
    run.sh
  frontend/
    index.html
    join.html
    invite.html
    layout.js
    ...assets
  docs/
    screenshots/
  office-agent-push.py
  set_state.py
  state.sample.json
  join-keys.json
  SKILL.md
  README.md
  LICENSE
```

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

侧边栏可以修改布局、装饰、默认位置，建议务必设置强验证码：

- 默认：`ASSET_DRAWER_PASS=1234`
- 部署时建议覆盖：

```bash
export ASSET_DRAWER_PASS="your-strong-pass"
```

必要性：
- 防止拿到访问链接的人修改你的房间布局与素材。

### C) 角色素材版权口径更新（重要）

当前主角状态（Writing / Idle / Syncing / Error）已切换为无版权争议的小猫素材。

因此：
- README 中旧的任天堂/宝可梦角色说明不再作为当前版本口径。
- 保留原则仍不变：
  - 代码逻辑 MIT
  - 美术资产禁止商用（学习/演示/交流用途）
