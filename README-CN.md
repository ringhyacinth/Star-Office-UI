# Star Office UI

[English](./README.md) | [中文](./README-CN.md)

## 概述

一个面向多 Agent 协作的像素办公室看板：实时可视化 AI 助手的工作状态，帮助团队直观看到"谁在做什么、昨天做了什么、现在是否在线"。

![Star Office UI 预览](docs/screenshots/office-preview-20260301.jpg)

## 特性

- **实时状态可视化** - AI 代理根据状态自动移动到不同办公区域（空闲/工作/研究/错误）
- **昨日小记** - 自动汇总代理前一天的活动
- **多 Agent 支持** - 邀请访客代理加入办公室
- **移动端适配** - 支持手机访问
- **OpenClaw 插件** - 自动状态同步（见 [OpenClaw 插件集成](#openclaw-插件集成)）

## 快速开始

### Docker 部署（推荐）

```bash
# 1) 克隆仓库
git clone https://github.com/MISAKIGA/Star-Office-UI.git
cd Star-Office-UI

# 2) 配置环境变量
cp .env.example .env
# 编辑 .env 填入 API_TOKEN 和 ADMIN_TOKEN

# 3) 启动服务
docker-compose up -d

# 4) 访问
# 前端：http://localhost:18791
# API：http://localhost:18791/api/
```

### 手动部署

```bash
# 1) 克隆并安装依赖
git clone https://github.com/MISAKIGA/Star-Office-UI.git
cd Star-Office-UI
python3 -m pip install -r backend/requirements.txt

# 2) 初始化状态文件
cp state.sample.json state.json

# 3) 启动后端
cd backend
python3 app.py
```

打开 **http://127.0.0.1:18791**

## 环境变量

| 变量 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `API_TOKEN` | 是 | - | API 鉴权 Token |
| `ADMIN_TOKEN` | 是 | - | 管理 Token |
| `PORT` | 否 | 18791 | 服务端口 |
| `LOG_LEVEL` | 否 | info | 日志级别 |
| `AUTO_IDLE_SECONDS` | 否 | 300 | 自动空闲超时（秒） |

生成随机 Token：
```bash
openssl rand -hex 32
```

## API 参考

### 状态管理

```bash
# 获取当前状态（公开）
curl http://localhost:18791/api/v1/status

# 设置主 Agent 状态（需要 API Token）
curl -X POST http://localhost:18791/api/v1/status \
  -H "Content-Type: application/json" \
  -H "X-API-Token: your-api-token" \
  -d '{"state": "writing", "detail": "正在开发功能"}'

# 推送 Agent 状态（需要 API Token）
curl -X POST http://localhost:18791/api/v1/agent/push \
  -H "Content-Type: application/json" \
  -H "X-API-Token: your-api-token" \
  -d '{
    "agentId": "openclaw-main",
    "name": "Shinyi",
    "state": "writing",
    "detail": "开发中"
  }'
```

### 管理接口

```bash
# 生成新的 API Token
curl -X POST http://localhost:18791/api/v1/admin/token/generate \
  -H "X-Admin-Token: your-admin-token"

# 列出所有 Token
curl http://localhost:18791/api/v1/admin/tokens \
  -H "X-Admin-Token: your-admin-token"

# 撤销 Token
curl -X DELETE http://localhost:18791/api/v1/admin/token/<token> \
  -H "X-Admin-Token: your-admin-token"
```

## OpenClaw 插件集成

> 将 Agent 状态实时同步到 Star Office UI 看板

### 为什么要用插件？

| 优势 | 说明 |
|------|------|
| **自动化** | 无需手动脚本，状态自动同步 |
| **实时** | Agent 启动/结束/空闲时立即更新 |
| **生命周期感知** | 跟踪所有状态（工作/错误/空闲） |
| **零配置** | 配合 OpenClaw 开箱即用 |

### 插件功能

- ✅ `onLoad` - 插件加载时显示"空闲"
- ✅ `beforeAgentStart` / `onAgentStart` - Agent 启动时显示"工作中"
- ✅ `onAgentEnd` - Agent 结束时显示"空闲"或"错误"
- ✅ `onAgentError` - Agent 出错时显示错误状态
- ✅ `onIdle` - Agent 空闲时更新状态
- ⏱️ **自动空闲** - 超过 `autoIdleSeconds` 自动切换回空闲

### 安装

```bash
# 插件位于: ~/.openclaw/extensions/star-office-plugin/
```

### 配置

```json
// ~/.openclaw/openclaw.json
{
  "plugins": {
    "allow": ["star-office-plugin"],
    "entries": {
      "star-office-plugin": {
        "enabled": true,
        "config": {
          "apiUrl": "http://localhost:18791",
          "apiToken": "your-api-token",
          "agentId": "openclaw-main",
          "agentName": "Shinyi",
          "autoIdleSeconds": 300
        }
      }
    }
  }
}
```

### 插件优势详解

1. **自动状态同步**
   - Agent 启动 → 看板上显示"工作中"
   - Agent 结束 → 看板上显示"空闲"
   - Agent 报错 → 看板上显示"错误"

2. **无需手动操作**
   - 无需手动运行 `set_state.py`
   - 无需 cron 定时任务
   - 即插即用

3. **生命周期集成**
   - 配合 OpenClaw 原生生命周期钩子
   - 捕获所有状态转换
   - 通过 WebSocket 实时更新

4. **可配置**
   - 自定义 Agent 名称
   - 自动空闲超时
   - 多 Agent 支持

## 部署方式

### 方式一：Docker Compose（推荐）

```bash
docker-compose up -d
```

详见 [Docker 部署](#docker-部署推荐)。

### 方式二：Docker Run

```bash
# 构建镜像
docker build -t star-office-ui:latest .

# 运行容器
docker run -d -p 18791:18791 \
  -e API_TOKEN=your-secure-token \
  -e ADMIN_TOKEN=your-admin-token \
  -v $(pwd)/data:/app/data \
  --name star-office-ui \
  star-office-ui:latest
```

### 方式三：手动部署

```bash
python3 -m pip install -r backend/requirements.txt
cd backend && python3 app.py
```

### 方式四：预构建镜像

```bash
docker run -d -p 18791:18791 \
  -e API_TOKEN=your-token \
  -e ADMIN_TOKEN=your-admin-token \
  --name star-office-ui \
  msga/star-office-ui-backend:latest
```

## 项目结构

```
star-office-ui/
├── backend/
│   ├── app.py              # Flask API
│   ├── requirements.txt
│   └── plugins/            # 插件系统
├── frontend/
│   ├── index.html
│   ├── layout.js
│   └── assets/             # 像素素材
├── docs/
│   └── screenshots/
├── docker-compose.yml
├── Dockerfile
├── .env.example
└── README.md
```

## 美术资产

访客角色动画使用 [LimeZu 免费素材](https://limezu.itch.io/animated-mini-characters-2-platform-free)。

**商用限制：**
- 代码/逻辑：MIT 许可证
- 美术资产：**仅供非商用**

## 许可证

- **代码：** [MIT](LICENSE)
- **美术资产：** 非商用

---

## 更新日志

### 2026-03 (v1.1.0)
- ✅ 新增 API Token 鉴权
- ✅ 新增 OpenClaw Lifecycle Plugin
- ✅ 支持 Docker Compose 一键部署
- ✅ 新增 .env.example 环境变量模板
- ✅ 新增预构建 Docker 镜像 `msga/star-office-ui-backend:latest`
- ✅ 优化 README 中英双语支持
## 部署方式

### 方式一：Docker Compose（推荐）

```bash
docker-compose up -d
```

详见 [Docker 部署](#docker-部署推荐)。

### 方式二：Docker Run

```bash
# 构建镜像
docker build -t star-office-ui:latest .

# 运行容器
docker run -d -p 18791:18791 \
  -e API_TOKEN=your-secure-token \
  -e ADMIN_TOKEN=your-admin-token \
  -v $(pwd)/data:/app/data \
  --name star-office-ui \
  star-office-ui:latest
```

### 方式三：手动部署

```bash
python3 -m pip install -r backend/requirements.txt
cd backend && python3 app.py
```

### 方式四：预构建镜像

```bash
docker run -d -p 18791:18791 \
  -e API_TOKEN=your-token \
  -e ADMIN_TOKEN=your-admin-token \
  --name star-office-ui \
  msga/star-office-ui-backend:latest
```

## 项目结构

```
star-office-ui/
├── backend/
│   ├── app.py              # Flask API
│   ├── requirements.txt
│   └── plugins/            # 插件系统
├── frontend/
│   ├── index.html
│   ├── layout.js
│   └── assets/             # 像素素材
├── docs/
│   └── screenshots/
├── docker-compose.yml
├── Dockerfile
├── .env.example
└── README.md
```

## 美术资产

访客角色动画使用 [LimeZu 免费素材](https://limezu.itch.io/animated-mini-characters-2-platform-free)。

**商用限制：**
- 代码/逻辑：MIT 许可证
- 美术资产：**仅供非商用**

## 许可证

- **代码：** [MIT](LICENSE)
- **美术资产：** 非商用

---

## 更新日志

### 2026-03 (v1.1.0)
- ✅ 新增 API Token 鉴权
- ✅ 新增 OpenClaw Lifecycle Plugin
- ✅ 支持 Docker Compose 一键部署
- ✅ 新增 .env.example 环境变量模板
- ✅ 新增预构建 Docker 镜像 `msga/star-office-ui-backend:latest`
- ✅ 优化 README 中英双语支持
