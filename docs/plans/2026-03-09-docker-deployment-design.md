# Docker 部署设计方案

**日期：** 2026-03-09
**目标：** 本机个人服务器 Docker 部署，外部脚本通过 HTTP API 转换 Agent 状态

---

## 架构概览

单一容器 + docker-compose，代码打包进镜像，运行时数据通过 Volume 持久化。

```
Host 本机
├── Star-Office-UI/
│   ├── data/                ← Volume 挂载点（持久化 JSON）
│   │   ├── state.json
│   │   ├── agents-state.json
│   │   ├── join-keys.json
│   │   └── runtime-config.json
│   └── docker-compose.yml
│
├── memory/                  ← 现有 memory 目录（只读挂载）
│
└── Docker Container /app
    ├── backend/             ← 代码打包进镜像（不可变）
    ├── frontend/            ← 静态资源打包进镜像
    ├── /data  → ./data/     ← 运行时数据（可写 Volume）
    └── /memory → memory/    ← 昨日小记（只读 Volume）
```

---

## 需要修改的文件

### `backend/app.py`（仅改路径常量，8 行）

新增 `DATA_DIR` 变量，支持通过 `STAR_OFFICE_DATA_DIR` 环境变量覆盖数据文件路径：

```python
# 修改前
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEMORY_DIR = os.path.join(os.path.dirname(ROOT_DIR), "memory")
STATE_FILE = os.path.join(ROOT_DIR, "state.json")
AGENTS_STATE_FILE = os.path.join(ROOT_DIR, "agents-state.json")
JOIN_KEYS_FILE = os.path.join(ROOT_DIR, "join-keys.json")
ASSET_POSITIONS_FILE = os.path.join(ROOT_DIR, "asset-positions.json")
ASSET_DEFAULTS_FILE = os.path.join(ROOT_DIR, "asset-defaults.json")
RUNTIME_CONFIG_FILE = os.path.join(ROOT_DIR, "runtime-config.json")

# 修改后
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.getenv("STAR_OFFICE_DATA_DIR") or ROOT_DIR
MEMORY_DIR = os.getenv("STAR_OFFICE_MEMORY_DIR") or os.path.join(os.path.dirname(ROOT_DIR), "memory")
STATE_FILE = os.path.join(DATA_DIR, "state.json")
AGENTS_STATE_FILE = os.path.join(DATA_DIR, "agents-state.json")
JOIN_KEYS_FILE = os.path.join(DATA_DIR, "join-keys.json")
ASSET_POSITIONS_FILE = os.path.join(DATA_DIR, "asset-positions.json")
ASSET_DEFAULTS_FILE = os.path.join(DATA_DIR, "asset-defaults.json")
RUNTIME_CONFIG_FILE = os.path.join(DATA_DIR, "runtime-config.json")
```

**向后兼容**：不传环境变量时回退到 `ROOT_DIR`，`python3 app.py` 直接运行行为不变。

---

## 新增文件

### `Dockerfile`

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY . .
EXPOSE 19000
ENV STAR_OFFICE_DATA_DIR=/data
ENV STAR_OFFICE_MEMORY_DIR=/memory
ENTRYPOINT ["sh", "docker-entrypoint.sh"]
```

### `docker-entrypoint.sh`

首次启动自动从 sample 文件初始化数据目录：

```bash
#!/bin/sh
mkdir -p "$STAR_OFFICE_DATA_DIR"
[ -f "$STAR_OFFICE_DATA_DIR/state.json" ]     || cp /app/state.sample.json     "$STAR_OFFICE_DATA_DIR/state.json"
[ -f "$STAR_OFFICE_DATA_DIR/join-keys.json" ] || cp /app/join-keys.sample.json "$STAR_OFFICE_DATA_DIR/join-keys.json"
exec python backend/app.py
```

### `docker-compose.yml`

```yaml
services:
  star-office:
    build: .
    ports:
      - "19000:19000"
    volumes:
      - ./data:/data
      - ${MEMORY_HOST_PATH:-../memory}:/memory:ro
    environment:
      STAR_OFFICE_DATA_DIR: /data
      STAR_OFFICE_MEMORY_DIR: /memory
      FLASK_SECRET_KEY: ${FLASK_SECRET_KEY:-star-office-dev-secret-change-me}
      ASSET_DRAWER_PASS: ${ASSET_DRAWER_PASS:-1234}
    restart: unless-stopped
```

### `.dockerignore`

```
data/
desktop-pet/
dist/
docs/
*.pyc
__pycache__/
.venv/
uv.lock
```

### `.env.example`

```bash
FLASK_SECRET_KEY=your-strong-random-key-here
ASSET_DRAWER_PASS=your-password
MEMORY_HOST_PATH=/absolute/path/to/your/memory
```

---

## API 使用方式

启动容器后，通过 HTTP 调用替代原来的 `python3 set_state.py`：

```bash
# 切换状态
curl -X POST http://localhost:19000/set_state \
  -H "Content-Type: application/json" \
  -d '{"state": "writing", "detail": "正在写代码"}'

# 查询当前状态
curl http://localhost:19000/status
```

可用状态值：`idle` / `writing` / `researching` / `executing` / `syncing` / `error`

---

## 改动清单

| 文件 | 动作 | 说明 |
|------|------|------|
| `backend/app.py` | 修改 | 添加 `DATA_DIR` 变量，8 行 |
| `Dockerfile` | 新建 | 镜像构建配置 |
| `docker-entrypoint.sh` | 新建 | 首次启动初始化逻辑 |
| `docker-compose.yml` | 新建 | 容器编排 + Volume + 环境变量 |
| `.dockerignore` | 新建 | 排除不必要文件 |
| `.env.example` | 新建 | 环境变量模板 |
