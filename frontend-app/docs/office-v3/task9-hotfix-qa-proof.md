# task9 Hotfix QA Proof（快速验收）

- 验收时间：2026-03-01 20:04 (UTC+8)
- 验收范围：`/Users/alshyib/Workspace/Next/conpay/star-office-ui/frontend-app`
- 访问地址：`http://127.0.0.1:4173`

## 0) 运行前提

已检测到服务在跑：
- Frontend dev: `node ... vite --host 127.0.0.1 --port 4173 --strictPort`
- Backend API: `python ... star-office-ui/backend/app.py`（19800）

## 1) 验收项结果

### A. 画布可见且有 bot（非0）
- 结果：**FAIL**
- 证据（前端页面采样）
  - `docs/office-v3/evidence/task9-hotfix-qa-2026-03-01T12-03-50-984Z.json`
  - 字段：`canvasVisible=true`，但 `botCount=0`
  - 页面截图：`docs/office-v3/evidence/task9-hotfix-qa-2026-03-01T12-03-50-984Z.png`

### B. 日志区显示真实流
- 结果：**FAIL**
- 证据（前端页面采样）
  - 同上 JSON 证据中：`logCount=0`
  - API 状态条显示：`/live 0 agents · provider 0/0`
  - 同时出现空态与错误态文案（未注入 mock）

### C. 不含 mock/hardcode
- 结果：**PASS（代码层）**
- 证据
  - 代码检索：`rg -n "mock|hardcode|hard-code|fake data|假数据|模拟数据" src`
  - 命中仅为文案提示（`App.tsx`），未发现 mock 数据源注入逻辑
  - 默认数据仅为空态常量（`src/api/defaults.ts`），用于降级展示，不是伪造业务数据

## 2) 关键证据（接口返回摘要）

### 2.1 后端真实接口（19800）
- 摘要文件：`docs/office-v3/evidence/task9-hotfix-qa-live-summary.json`
- 核心摘要：
  - `/live`：`agent_count=17`，`agents_with_logs=15`，`total_log_entries_in_payload=76`
  - `/health`：`status=ok`
  - `/tasks`：`tasks=30`
  - `/ollama`：`running=true`，`models=2`

### 2.2 前端实际请求（4173）
- 证据文件：
  - `docs/office-v3/evidence/task9-hotfix-qa-20260301-200237.har`
  - `docs/office-v3/evidence/task9-hotfix-qa-2026-03-01T12-03-50-984Z.json`
- 观察到：
  - 前端请求 `http://127.0.0.1:4173/live`（而非 19800）
  - 返回 `text/html`（Vite 页面壳），不是 JSON 实时流
  - 导致前端轮询数据为空/超时，最终 bot=0、日志=0

## 3) 结论

**FAIL**

### 阻塞点
1. 前端 API 基址未指向后端（19800），当前在请求 4173 同源路径，`/live` 返回 HTML 非 JSON。  
2. 因接口未连通，无法满足“画布有 bot（非0）”和“日志区显示真实流”两项验收标准。
