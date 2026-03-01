# 办公室重构 v2 - Task3 稳定性/安全加固报告

## 任务范围
在 `frontend-app` 完成以下硬化：
1. 增加 Error Boundary，防止渲染异常导致整页白屏。
2. 增加请求失败降级 UI 与超时处理。
3. 对日志/任务文本渲染做基础安全处理，避免危险 HTML 注入风险。
4. 不做视觉样式重构，只做稳态与安全能力补强。

---

## 改动文件
- `frontend-app/src/components/ErrorBoundary.tsx` **(新增)**
- `frontend-app/src/utils/request.ts` **(新增)**
- `frontend-app/src/utils/sanitize.ts` **(新增)**
- `frontend-app/src/App.tsx` **(重写为稳态数据面板 + 降级逻辑 + 安全文本渲染)**
- `frontend-app/src/main.tsx` **(接入全局 ErrorBoundary)**
- `docs/office-v2/task3-hardening-report.md` **(新增，本报告)**

---

## 关键实现说明

### 1) ErrorBoundary（渲染层兜底）
- 在 `main.tsx` 中用 `<ErrorBoundary>` 包裹 `<App />`。
- `ErrorBoundary` 捕获 render 生命周期异常（`getDerivedStateFromError` + `componentDidCatch`）。
- 出错后显示兜底卡片和“重试渲染”按钮，避免全页崩溃白屏。

### 2) 请求失败降级 UI + 超时处理
- 新增 `fetchJsonWithTimeout()`：
  - 默认超时 6 秒（可配置）；
  - 超时抛 `RequestTimeoutError`；
  - 非 2xx 抛 `HttpRequestError`；
  - 统一 `toReadableRequestError()` 输出可读报错。
- `App.tsx` 中并发请求 `/live` 与 `/tasks`，用 `Promise.allSettled` 做“部分可用”策略：
  - 任一接口成功：保留并展示可用数据；
  - 任一接口失败：显示“已启用降级展示”提示；
  - 首次加载且全失败：展示 fatal fallback，并提供“重新请求”。
- 支持手动“立即刷新”与后台定时刷新（10s）。

### 3) 日志/任务文本基础安全处理
- 新增 `sanitizeForDisplay()`：
  - 去除控制字符；
  - 去除 HTML tag 片段（`<...>`）；
  - 替换危险协议前缀（`javascript:` / `vbscript:` / `data:`）；
  - 限长截断，避免异常超长文本撑爆 UI。
- 所有任务标题/描述、日志文本、异常提示均在渲染前走 `sanitizeForDisplay()`。
- 未使用 `dangerouslySetInnerHTML`，保持 React 默认安全转义路径。

### 4) 视觉样式控制
- **未改动** `App.css` / `index.css` 的现有样式定义。
- 仅在结构与交互逻辑层完成加固，不做视觉皮肤改版。

---

## 验证结果
在 `frontend-app` 执行：
- `npm run lint` ✅ 通过
- `npm run build` ✅ 通过

构建产物正常生成，TypeScript 校验、ESLint 与 Vite 打包均通过。

---

## 风险评估与残余风险

### 已降低风险
1. **高概率可用性风险（白屏）**：由 ErrorBoundary 降低。
2. **接口抖动导致整页不可用**：通过超时 + allSettled 降级策略降低。
3. **日志/任务文本注入风险（基础层）**：通过文本清洗 + 不使用危险 HTML 渲染降低。

### 残余风险（需后续增强）
1. 当前 `sanitizeForDisplay` 是**基础清洗**，并非完整 HTML 解析级 sanitizer；若后续引入富文本，需要专业 sanitizer（如 DOMPurify）和白名单策略。
2. ErrorBoundary 仅覆盖渲染生命周期错误；事件回调/异步链错误仍需配合全局错误上报与请求重试策略。
3. 超时阈值（6s）为保守默认值，生产环境建议按网络与后端 SLA 调参。
4. 前端已做输出清洗，但后端输入源仍应继续做服务端校验与日志入库清洗，形成端到端防护。

---

七弟子看门狗，守好门！本次加固已完成并可构建验证。
