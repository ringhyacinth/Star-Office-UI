# Star Office UI（frontend-app 单入口版）

星办公室重构后的统一入口：

- **前端唯一入口：`frontend-app`（React + Vite + TypeScript）**
- **后端：`backend/app.py`（Flask，提供 `/live` 等实时接口）**
- **生产态由 Flask 直接托管 `frontend-app/dist`**

> 旧版 `frontend/` Phaser 页面已下线，不再作为入口。

---

## 目录结构

```text
star-office-ui/
  backend/                # Flask API + 生产态静态托管
  frontend-app/           # React 前端（唯一 UI 入口）
  scripts/                # 运维脚本
  state.sample.json
```

---

## 开发模式（推荐）

### 1) 启动后端（19800）

```bash
cd backend
python3 app.py
```

### 2) 启动前端开发服务（4173）

```bash
cd frontend-app
npm ci
npm run dev
```

### 3) 打开页面

- 开发入口：`http://127.0.0.1:4173`
- 前端默认通过 Vite Proxy 转发 `/health`、`/live`、`/tasks`、`/ollama` 等接口到 `http://127.0.0.1:19800`

---

## 生产/部署模式

### 1) 构建前端

```bash
cd frontend-app
npm ci
npm run build
```

### 2) 启动后端

```bash
cd backend
python3 app.py
```

### 3) 访问

- 统一入口：`http://127.0.0.1:19800`
- Flask 将自动托管 `frontend-app/dist`

> 若 `dist` 不存在，访问根路径会返回明确提示，指导先执行 `npm run build`。

---

## 前端质量门槛

在 `frontend-app` 目录执行：

```bash
npm run lint
npm run test
npm run build
```

---

## CI

已提供 GitHub Actions：`.github/workflows/frontend-app-ci.yml`

- 触发：push / pull_request
- 执行：`npm ci` + `npm run lint` + `npm run test` + `npm run build`

---

## 常见问题

### 1) `/live` 返回 HTML 而不是 JSON？

重构后默认不会把 API 未命中回退成 HTML：

- API 路径未命中时返回 **JSON 404**
- 前端请求层会对 HTML 响应做显式报错（提示检查 API base/proxy）

### 2) 本地只想看前端，不想构建 dist？

直接使用开发入口：`http://127.0.0.1:4173`。

