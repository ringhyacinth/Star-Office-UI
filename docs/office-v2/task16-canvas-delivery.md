# 办公室重构 v2 - Task16 交付说明（画布交互实现）

> 日期：2026-03-01  
> 目标：在 `frontend-app` 画布模块落地“点名高亮 + 角色绿色呼吸态 + 非游戏控制交互”，并与 React 状态联动。

---

## 1) 本次改动文件

### 核心实现
- `frontend-app/src/components/CanvasShell.tsx`
  - 将原占位 `CanvasShell` 改为真实 `<canvas>` 渲染模块。
  - 新增角色节点动画、点名高亮圈、工作中绿色呼吸波。
  - 新增指针交互（点击角色触发点名），不接入键盘控制。
  - 保留兼容挂载点：`#game-container`、`#v2-fx-overlays`、`#agent-highlight-mount`。

- `frontend-app/src/App.tsx`
  - 用 React 状态统一管理 `selectedAgentId` 与日志筛选。
  - 画布、顶部点名条、右侧 Agent 卡片使用同一状态源联动。
  - 补充页面结构（`office-v2-page`、`office-key-card`）便于稳定回归。

### 关联样式与展示
- `frontend-app/src/App.css`
  - 新增画布区域、高亮、状态点、呼吸动画、布局样式。
  - 加入 `.sr-only` 等辅助样式，保留可访问性与挂载兼容。

- `frontend-app/src/components/LogPanel.tsx`
  - 补充日志区标题与测试标识，保证页面语义/回归稳定。

- `frontend-app/src/data/mockData.ts`
  - 补充基础日志数据（包含 `[INFO] 页面加载完成`），便于空接口场景稳定展示。

### 测试更新
- `frontend-app/src/test/App.smoke.test.tsx`
  - 增加点名联动与“非游戏控制”文案存在性测试。

---

## 2) 功能效果说明

### A. 点名高亮（已落实）
- 可通过以下入口点名：
  1. 画布下方 `agent-chip` 按钮；
  2. 右侧 `Agent 工作负载` 卡片；
  3. 画布内直接点击角色。
- 点名后：
  - 画布角色出现外圈高亮脉冲（使用该角色 `highlightColor`）；
  - 顶部出现“点名：xx ×”清除按钮；
  - 日志面板可按点名对象联动筛选。

### B. 角色绿色呼吸态（已落实）
- `status === working` 的角色在画布上有绿色双层呼吸波纹（动态脉冲）。
- 同时保留 chip/card 上的 `status-breathing` 视觉提示。

### C. 非游戏控制交互（已落实）
- 只支持“展示型交互”：点击点名、查看状态。
- 未实现键盘移动 / WASD / 手柄控制 / 角色操控逻辑。
- 画布提示文案明确标注：`展示交互：点击角色点名高亮（非游戏控制）`。

---

## 3) React 状态联动说明

当前联动链路：

`CanvasShell / RightPanel / AgentBar 点击`  
→ `App.tsx: selectedAgentId`（单一状态源）  
→ 同步更新 `TopBar` 点名状态、`CanvasShell` 高亮绘制、`LogPanel` 点名筛选。

这保证了“画布只是展示层，状态由 React 控制”的边界。

---

## 4) 稳定性与可运行验证

已执行：

```bash
cd frontend-app
npm test
npm run lint
npm run build
```

结果：
- `npm test`：通过（5/5）
- `npm run lint`：通过
- `npm run build`：通过

---

## 5) 取舍说明（按“稳定可跑优先”）

- 本次采用 Canvas 2D 直接渲染实现，不引入键盘玩法逻辑，避免“展示页游戏化控制”风险。
- 在测试环境（jsdom）下主动跳过 Canvas runtime 绘制循环，避免无效告警，确保 CI 稳定。
- 优先保证页面可跑、状态联动一致、结构挂载点兼容。
