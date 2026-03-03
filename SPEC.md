# Star Office UI 改进方案 SPEC.md

> 版本: 1.0  
> 日期: 2026-03-03  
> 目标: 降低用户使用门槛，支持 Docker 一键部署，封装 OpenClaw Plugin

---

## 1. 背景与目标

### 1.1 当前痛点

| 问题 | 影响 |
|------|------|
| 无 API Token 鉴权 | 安全性低，任何人可随意修改状态 |
| 无 Docker 支持 | 部署依赖 Python 环境，用户门槛高 |
| join-key 机制复杂 | 普通用户难以理解和使用 |
| 无官方 Plugin | 与 OpenClaw 集成需要手动开发 |
| 状态文件路径硬编码 | 多实例部署时路径冲突 |

### 1.2 改进目标

- ✅ **降低部署门槛**: Docker Compose 一键启动
- ✅ **简化接入**: API Token 鉴权，告别复杂的 join-key
- ✅ **开箱即用**: 提供 OpenClaw Lifecycle Plugin
- ✅ **生产可用**: 健康检查、日志、低资源占用
- ✅ **多实例支持**: 支持远程 Agent 状态推送

---

## 2. 系统架构

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        Star Office UI                            │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│  │   Frontend     │◄──►│   Flask API     │◄──►│  State      │ │
│  │  (Pixel Art)   │    │  (Token Auth)   │    │  Storage    │ │
│  └─────────────────┘    └─────────────────┘    └─────────────┘ │
│                                  ▲                               │
│                                  │                               │
│         ┌────────────────────────┼────────────────────────┐     │
│         │                        │                        │     │
│  ┌──────┴──────┐        ┌───────┴───────┐        ┌──────┴─────┐│
│  │ OpenClaw   │        │  Remote Agent  │        │  Manual   ││
│  │ Plugin     │        │  (REST API)    │        │  (Browser) ││
│  └─────────────┘        └────────────────┘        └────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 部署架构 (Docker)

```yaml
# docker-compose.yml
services:
  star-office:
    image: star-office-ui:latest
    ports:
      - "18791:18791"
    volumes:
      - ./state:/app/state
      - ./memory:/app/memory
    environment:
      - API_TOKEN=${API_TOKEN}           # 鉴权 Token
      - ADMIN_TOKEN=${ADMIN_TOKEN}        # 管理 Token
      - STATE_FILE=/app/state/state.json
      - FLASK_ENV=production
      - LOG_LEVEL=info
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:18791/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

---

## 3. API 设计

### 3.1 认证机制

| Header | 说明 |
|--------|------|
| `X-API-Token` | 用户 API Token (读写状态) |
| `X-Admin-Token` | 管理员 Token (管理配置) |

> **设计理念**: Token 存环境变量，容器启动时注入，无需用户接触代码

### 3.2 API 端点

#### 3.2.1 状态管理

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | `/api/v1/status` | 公开 | 获取当前状态 |
| POST | `/api/v1/status` | API Token | 设置主 Agent 状态 |
| POST | `/api/v1/agent/push` | API Token | 推送 Agent 状态 |
| GET | `/api/v1/agents` | API Token | 获取所有 Agent |

#### 3.2.2 管理接口

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| POST | `/api/v1/admin/token/generate` | Admin Token | 生成新的 API Token |
| DELETE | `/api/v1/admin/token/<token>` | Admin Token | 撤销 Token |
| GET | `/api/v1/admin/tokens` | Admin Token | 列出所有 Token |

#### 3.2.3 健康与配置

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | `/health` | 公开 | 健康检查 |
| GET | `/api/v1/config` | API Token | 获取前端配置 |

### 3.3 请求/响应示例

#### 推送状态

```bash
# 请求
curl -X POST http://localhost:18791/api/v1/agent/push \
  -H "Content-Type: application/json" \
  -H "X-API-Token: your-token-here" \
  -d '{
    "agentId": "openclaw-main",
    "name": "Shinyi",
    "state": "writing",
    "detail": "正在分析项目结构"
  }'

# 响应
{
  "ok": true,
  "agentId": "openclaw-main",
  "state": "writing",
  "area": "writing",
  "updatedAt": "2026-03-03T17:10:00+08:00"
}
```

---

## 4. Docker 部署方案

### 4.1 一键启动

```bash
# 方式 1: 使用默认配置 (测试用)
docker run -d -p 18791:18791 --name star-office \
  star-office-ui:latest

# 方式 2: 生产部署 (自定义 Token)
docker run -d -p 18791:18791 \
  -e API_TOKEN=your-secure-token \
  -e ADMIN_TOKEN=your-admin-token \
  -v $(pwd)/data:/app/data \
  --name star-office \
  star-office-ui:latest
```

### 4.2 Docker Compose (推荐)

```yaml
# docker-compose.yml
version: '3.8'

services:
  star-office:
    image: star-office-ui:latest
    container_name: star-office-ui
    ports:
      - "18791:18791"
    environment:
      - API_TOKEN=${API_TOKEN:-dev-token-12345}
      - ADMIN_TOKEN=${ADMIN_TOKEN:-admin-token-67890}
      - FLASK_ENV=production
      - LOG_LEVEL=info
    volumes:
      - ./data:/app/data
      - ./memory:/app/memory
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:18791/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

networks:
  default:
    name: star-office-network
```

```bash
# 启动命令
git clone https://github.com/MISAKIGA/Star-Office-UI.git
cd Star-Office-UI
cp .env.example .env  # 编辑配置
docker compose up -d
```

### 4.3 环境变量

| 变量 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `API_TOKEN` | 是 | - | API 鉴权 Token |
| `ADMIN_TOKEN` | 是 | - | 管理Token |
| `PORT` | 否 | 18791 | 服务端口 |
| `STATE_FILE` | 否 | /app/data/state.json | 状态文件路径 |
| `MEMORY_DIR` | 否 | /app/memory | 昨日小记目录 |
| `AUTO_IDLE_SECONDS` | 否 | 300 | 自动空闲超时 |
| `LOG_LEVEL` | 否 | info | 日志级别 |

---

## 5. OpenClaw Plugin 设计

### 5.1 插件结构

```
~/.openclaw/extensions/star-office-plugin/
├── package.json
├── openclaw.plugin.json
├── src/
│   └── index.ts          # 插件主逻辑
├── config.schema.json    # 配置Schema
└── README.md
```

### 5.2 插件配置 (openclaw.plugin.json)

```json
{
  "id": "star-office-plugin",
  "name": "Star Office UI Plugin",
  "description": "将 Agent 状态实时同步到 Star Office UI 像素办公室",
  "version": "1.0.0",
  "kind": "lifecycle",
  "main": "./dist/index.js",
  "configSchema": {
    "type": "object",
    "properties": {
      "apiUrl": {
        "type": "string",
        "description": "Star Office UI 服务地址",
        "default": "http://localhost:18791"
      },
      "apiToken": {
        "type": "string",
        "description": "API Token"
      },
      "agentId": {
        "type": "string",
        "description": "Agent ID",
        "default": "openclaw-main"
      },
      "agentName": {
        "type": "string",
        "description": "显示名称",
        "default": "Shinyi"
      },
      "autoIdleSeconds": {
        "type": "number",
        "description": "无活动自动变空闲",
        "default": 300
      }
    },
    "required": ["apiUrl", "apiToken"]
  }
}
```

### 5.3 插件逻辑

```typescript
// src/index.ts
import { Plugin, LifecycleEvents } from "@openclaw/core";

interface Config {
  apiUrl: string;
  apiToken: string;
  agentId: string;
  agentName: string;
  autoIdleSeconds: number;
}

export default class StarOfficePlugin implements Plugin {
  id = "star-office-plugin";
  name = "Star Office UI Plugin";
  kind = "lifecycle";

  private config: Config;
  private idleTimer?: NodeJS.Timeout;

  constructor(config: Config) {
    this.config = config;
  }

  async onLoad() {
    console.log("[star-office] 插件已加载");
    await this.pushState("idle", "待命中");
  }

  async beforeAgentStart(event: LifecycleEvents.BeforeAgentStart) {
    await this.pushState("writing", "工作中");
  }

  async onAgentEnd(event: LifecycleEvents.AgentEnd) {
    const state = event.success ? "idle" : "error";
    const detail = event.success ? "任务完成" : "执行失败";
    await this.pushState(state, detail);
  }

  private async pushState(state: string, detail: string) {
    // 清除之前的空闲定时器
    if (this.idleTimer) {
      clearTimeout(this.idleTimer);
    }

    try {
      const response = await fetch(`${this.config.apiUrl}/api/v1/agent/push`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Token": this.config.apiToken,
        },
        body: JSON.stringify({
          agentId: this.config.agentId,
          name: this.config.agentName,
          state,
          detail,
        }),
      });

      if (!response.ok) {
        console.error("[star-office] 状态推送失败:", await response.text());
      }
    } catch (error) {
      console.error("[star-office] 请求失败:", error);
    }

    // 设置自动空闲
    if (state === "writing" && this.config.autoIdleSeconds > 0) {
      this.idleTimer = setTimeout(async () => {
        await this.pushState("idle", "自动回到休息区");
      }, this.config.autoIdleSeconds * 1000);
    }
  }
}
```

### 5.4 OpenClaw 配置

```json
// ~/.openclaw/openclaw.json
{
  "plugins": {
    "allow": ["star-office-plugin"],
    "entries": {
      "star-office-plugin": {
        "enabled": true,
        "config": {
          "apiUrl": "http://192.168.1.100:18791",
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

---

## 6. 多 Agent 支持

### 6.1 远程 Agent 接入

任何支持 HTTP 的 Agent 都可以通过 REST API 接入：

```python
# office-agent-push.py (改进版)
import requests
import os
import sys
import json

API_URL = os.environ.get("STAR_OFFICE_URL", "http://localhost:18791")
API_TOKEN = os.environ.get("STAR_OFFICE_TOKEN", "")

def push_state(agent_id: str, name: str, state: str, detail: str = ""):
    """推送 Agent 状态"""
    response = requests.post(
        f"{API_URL}/api/v1/agent/push",
        headers={
            "Content-Type": "application/json",
            "X-API-Token": API_TOKEN
        },
        json={
            "agentId": agent_id,
            "name": name,
            "state": state,
            "detail": detail
        }
    )
    return response.json()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python push.py <state> <detail>")
        sys.exit(1)
    
    result = push_state(
        agent_id="remote-agent-01",
        name="Remote Bot",
        state=sys.argv[1],
        detail=sys.argv[2]
    )
    print(result)
```

### 6.2 Agent 注册

首次使用自动注册，无需手动操作：

```bash
# 首次推送会自动创建 Agent
curl -X POST http://localhost:18791/api/v1/agent/push \
  -H "X-API-Token: xxx" \
  -d '{"agentId": "new-agent", "name": "New Bot", "state": "idle"}'
```

---

## 7. 安全设计

### 7.1 认证流程

```
┌─────────┐     X-API-Token      ┌─────────┐
│  Client │────────────────────►│ Server  │
│         │    (Header)         │         │
│         │◄────────────────────│         │
└─────────┘   200 OK / 403      └─────────┘
```

### 7.2 Token 管理

- **API Token**: 用于日常状态推送，最小权限原则
- **Admin Token**: 用于管理操作 (生成/撤销 Token)
- Token 存储在环境变量，不存入代码仓库
- 支持 Token 轮换 (通过 Admin Token 生成新 Token)

### 7.3 网络隔离

- 默认只监听 `127.0.0.1` (Docker 内部)
- 对外暴露需配合 Nginx 反向代理 + HTTPS
- 生产环境建议使用 Docker Network 隔离

---

## 8. 实施计划

### Phase 1: 核心改进 (Week 1)

- [ ] 改造 Flask API，添加 Token 鉴权中间件
- [ ] 重构状态存储，支持环境变量配置路径
- [ ] 编写 Dockerfile 和 .dockerignore

### Phase 2: Docker 生态 (Week 2)

- [ ] 编写 docker-compose.yml
- [ ] 编写 .env.example 配置模板
- [ ] 编写部署文档
- [ ] CI/CD 自动构建 (GitHub Actions)

### Phase 3: Plugin 开发 (Week 3)

- [ ] 开发 OpenClaw Lifecycle Plugin
- [ ] 配置Schema 定义
- [ ] 本地测试验证

### Phase 4: 文档与发布 (Week 4)

- [ ] 更新 README.md
- [ ] 编写 API 文档
- [ ] 编写快速开始指南
- [ ] GitHub Release

---

## 9. 验收标准

| 序号 | 验收项 | 成功条件 |
|------|--------|----------|
| 1 | Docker 部署 | `docker compose up -d` 后服务可访问 |
| 2 | Token 鉴权 | 无 Token 请求返回 403 |
| 3 | 状态推送 | Plugin 触发后 UI 正确显示状态 |
| 4 | 多实例支持 | 多个 Agent 可同时推送状态 |
| 5 | 自动空闲 | 超过设定时间自动切换 idle |
| 6 | 健康检查 | `/health` 端点正常响应 |

---

## 10. 风险与对策

| 风险 | 影响 | 对策 |
|------|------|------|
| Token 泄露 | 状态被恶意修改 | 定期轮换、限制 IP |
| Docker 资源 | 占用过多资源 | 限制 CPU/内存 |
| 网络延迟 | 状态更新不及时 | 本地缓存 + 重试机制 |
| 状态文件损坏 | 服务异常 | 定时备份 + 启动校验 |

---

## 11. 附录

### A. 快速验证脚本

```bash
#!/bin/bash
# 验证部署是否成功

API_URL="http://localhost:18791"
TOKEN="test-token-123"

echo "1. 健康检查..."
curl -s $API_URL/health | jq .

echo "2. 无 Token 访问 (应失败)..."
curl -s -X POST $API_URL/api/v1/status \
  -H "Content-Type: application/json" \
  -d '{"state":"writing"}' | jq .

echo "3. Token 访问 (应成功)..."
curl -s -X POST $API_URL/api/v1/status \
  -H "Content-Type: application/json" \
  -H "X-API-Token: $TOKEN" \
  -d '{"state":"writing","detail":"测试中"}' | jq .

echo "4. 查看状态..."
curl -s $API_URL/api/v1/status | jq .
```

### B. 环境变量模板

```bash
# .env
API_TOKEN=your-secure-random-token
ADMIN_TOKEN=your-admin-random-token
PORT=18791
LOG_LEVEL=info
AUTO_IDLE_SECONDS=300
```

---

> **文档版本**: 1.0  
> **维护人**: Shinyi (AI 架构师)  
> **更新日志**:
> - 2026-03-03: 初始版本
