# 办公室重构 v2 - FPS 与遥测交付说明（task12）

## 1. 交付目标

本次在 `frontend-app` 内完成了轻量遥测能力，覆盖以下需求：

1. 增加 FPS / 刷新状态展示组件（轻量，不影响性能）
2. 提供开关（开发可见，生产可控）
3. 输出本交付文档

---

## 2. 实现内容

### 2.1 新增组件

- `frontend-app/src/components/telemetry/PerformanceTelemetry.tsx`
- `frontend-app/src/components/telemetry/performanceTelemetry.css`

组件能力：

- 展示 **FPS**（500ms 采样）
- 展示 **刷新状态**：
  - `刷新中`
  - `低频/停滞`
  - `后台暂停`
- 展示最近帧间隔（ms）
- 提供浮层按钮 `遥测 ON/OFF`，可随时开启/关闭面板

### 2.2 页面接入

- `frontend-app/src/App.tsx` 引入 `<PerformanceTelemetry />`
- `frontend-app/src/App.css` 更新为办公室重构 v2 的示例页面样式

---

## 3. 开关与可控策略

### 3.1 开发环境（开发可见）

- `import.meta.env.DEV === true` 时，遥测功能默认可用且默认显示

### 3.2 生产环境（生产可控）

生产环境下通过以下方式控制：

1. **构建时环境变量**
   - `VITE_TELEMETRY_ENABLED=true|false`
   - `VITE_TELEMETRY_DEFAULT_VISIBLE=true|false`

2. **URL 覆盖**
   - `?telemetry=1` / `?telemetry=true` / `?telemetry=on`
   - `?telemetry=0` / `?telemetry=false` / `?telemetry=off`

3. **本地记忆（localStorage）**
   - key: `office-v2:telemetry-visible`
   - 记录用户最近一次 ON/OFF 状态

> 优先级：URL 覆盖 > 本地记忆 > 环境变量默认值

---

## 4. 轻量性能设计

为避免遥测本身影响渲染性能，采用以下策略：

- 使用 `requestAnimationFrame` 仅做帧计数
- 每 `500ms` 汇总一次并更新 UI（非逐帧 setState）
- 面板关闭时停止监控循环（`RAF + interval` 全部清理）
- 状态变化不明显时避免重复 setState

---

## 5. 验证记录

在 `frontend-app` 执行：

- `npm run build` ✅ 通过
- `npm run lint` ⚠️ 失败（与本次改动无关）
  - 现有文件：`src/utils/sanitize.ts`
  - 问题：`no-control-regex`（历史遗留）

---

## 6. 变更文件清单

- `frontend-app/src/components/telemetry/PerformanceTelemetry.tsx`（新增）
- `frontend-app/src/components/telemetry/performanceTelemetry.css`（新增）
- `frontend-app/src/App.tsx`（修改，接入遥测组件）
- `frontend-app/src/App.css`（修改，页面样式整理）
- `docs/office-v2/task12-telemetry-delivery.md`（新增）

