# 办公室重构 v2 - Task10 API 层交付说明

## 1. 交付范围
在 `frontend-app/src` 完成以下内容：

- API 访问层（`/health` `/live` `/tasks` `/ollama`）
- 统一错误处理与超时控制
- 轮询封装（可复用 poller + React Hook）
- 页面空态兜底，接口失败时不崩溃

---

## 2. 改动文件清单

### 新增

1. `frontend-app/src/api/types.ts`  
   - API 响应类型定义（health/live/tasks/ollama）
2. `frontend-app/src/api/defaults.ts`  
   - 各接口空态默认值
3. `frontend-app/src/api/http.ts`  
   - `requestJson` 封装（超时、异常包装、HTTP 错误处理）
4. `frontend-app/src/api/normalizers.ts`  
   - 接口数据归一化，防御后端字段缺失/格式异常
5. `frontend-app/src/api/officeApi.ts`  
   - 业务 API 客户端（getHealth/getLive/getTasks/getOllama）
6. `frontend-app/src/api/poller.ts`  
   - 通用轮询器（start/stop/refresh/subscribe）
7. `frontend-app/src/api/index.ts`  
   - API 模块统一导出
8. `frontend-app/src/hooks/useApiPoller.ts`  
   - React 轮询 Hook（绑定 poller 生命周期）

### 修改

9. `frontend-app/src/App.tsx`  
   - 接入四个接口轮询
   - 增加接口状态卡片、错误提示、空态显示
   - 页面在接口异常时展示 fallback，不抛崩
10. `frontend-app/src/App.css`  
    - API 面板样式
11. `frontend-app/src/index.css`  
    - 全局基础样式调整

---

## 3. 设计说明（关键点）

### 3.1 API 访问层
- 支持 `VITE_API_BASE_URL`（默认同源）
- 每个请求统一走 `requestJson`
- 内置超时与 Abort 处理，避免请求悬挂
- HTTP 非 2xx 时返回结构化错误（`ApiError`）

### 3.2 数据安全归一化
- 后端返回不可信，先 `normalize` 再入 UI
- 非法/缺失字段使用默认值回填
- 保证 UI 渲染结构稳定（例如 tasks 永远是数组）

### 3.3 轮询封装
- 使用 `setTimeout` 串行轮询，避免请求重叠
- poller 内维护 `data/error/isLoading/updatedAt`
- 请求失败仅更新 `error`，保留上次成功数据
- 支持 `stop()` 终止时取消 in-flight 请求

### 3.4 页面防崩策略
- 四个接口都提供空态文案
- 列表渲染前做长度与字段防御
- 错误仅展示 alert 文本，不中断整页

---

## 4. 接口联调结果
联调环境：`http://127.0.0.1:19800`

| 接口 | 结果 | 核心返回验证 |
|---|---|---|
| `/health` | ✅ 200 | `{"status":"ok","timestamp":"..."}` |
| `/live` | ✅ 200 | 包含 `state` / `logs` / `providers` |
| `/tasks` | ✅ 200 | 返回 `{"tasks":[...]}` |
| `/ollama` | ✅ 200 | 返回 `running/models/active` |

### 联调命令记录
```bash
# 前端静态检查
cd frontend-app
npm run lint
npm run build

# 后端接口验证
curl -sS http://127.0.0.1:19800/health
curl -sS http://127.0.0.1:19800/live
curl -sS http://127.0.0.1:19800/tasks
curl -sS http://127.0.0.1:19800/ollama
```

---

## 5. 验收结论
- API 层与轮询封装已落地（四个目标接口全部接入）
- 已实现错误处理与空态兜底，接口异常不会导致页面崩溃
- 构建与 lint 通过，接口联调返回正常
