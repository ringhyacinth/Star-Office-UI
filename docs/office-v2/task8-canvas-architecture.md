# 办公室重构 v2：Canvas 展示架构方案（Task8）

> 目标：将“像素办公室”明确定位为**展示型可视化系统**（非游戏控制），在 React 外壳下运行 Canvas/Phaser 场景，保证可维护、可扩展、可降级。

---

## 1. 设计目标与边界

### 1.1 目标
- 将当前单文件 `frontend/index.html` 的展示逻辑升级为可模块化架构。
- 保留现有数据源（`/live`、`/tasks`），重点优化前端“渲染与通信”。
- 让像素场景承担“视觉表达”，让 React 承担“业务状态与交互编排”。

### 1.2 非目标（明确不是）
- 不做玩家控制、角色操控、键盘移动等“游戏玩法”。
- 不以 Canvas 作为业务状态真源（source of truth）。
- 不让 Phaser 直接操作右侧 DOM 面板。

### 1.3 约束
- 继续兼容桌面与移动端。
- 长时间展示稳定（大屏场景）。
- 支持高/低特效自动切换。

---

## 2. 方案对比与推荐

### 方案 A：Phaser 继续做“大一统”
- **做法**：延续现在的单页思路，所有数据、动画、DOM 操作都在 Phaser 周边处理。
- **优点**：改动快。
- **缺点**：耦合高，维护成本继续上升，React 价值无法发挥。

### 方案 B：React 主控 + Canvas 子系统（推荐）
- **做法**：React 负责数据状态、布局和面板；Canvas 负责像素世界渲染；两者通过事件总线与共享 Store 通信。
- **优点**：边界清晰、可测试、便于拆分迭代。
- **缺点**：初期需要做事件协议和组件分层设计。

### 方案 C：纯 React DOM 动画替代 Canvas
- **做法**：不再用 Phaser，全部改 CSS/SVG/DOM。
- **优点**：前端工程化统一。
- **缺点**：像素场景性能、层级和特效能力下降，重做成本高。

**推荐结论：方案 B。**
此方案妙在：保留当前视觉资产与动效沉淀，同时引入 React 的可维护性，风险最低。

---

## 3. 总体架构（展示系统）

```text
Backend APIs
  ├─ GET /live
  └─ GET /tasks
        │
        ▼
Data Gateway (polling/SSE)
        │ normalize
        ▼
Office Store (single source of truth)
  ├─ agents/tasks/logs/providers
  ├─ derived selectors (dept status, KPIs, alerts)
  └─ ui state (selectedDept, highlightedAgent, filters)
        │
  ┌─────┴───────────────┐
  ▼                     ▼
React UI Tree      Canvas Renderer (Phaser)
(HUD/Panel/Drawer) (scene + layers + fx)
  ▲                     │
  └────── Event Bus ────┘
      (typed events)
```

### 关键原则
1. **单向数据流**：后端数据 → Store → UI/Canvas。
2. **Canvas 只消费状态，不拥有业务状态**。
3. **交互回传必须事件化**：Canvas 点击部门后，发事件给 React，由 React 决定打开抽屉/筛选任务。

---

## 4. Canvas 图层架构（非游戏控制）

> 以“展示层次 + 更新频率 + 性能预算”来组织，而不是按游戏玩法组织。

| 层级 | 建议 depth | 内容 | 更新频率 | 说明 |
|---|---:|---|---|---|
| L0 背景底图层 | 0-5 | `office_bg`、远景底色、地面网格 | 仅初始化 | 静态，不参与逐帧计算 |
| L1 建筑与街区层 | 6-15 | 等距建筑、道路霓虹、分区底座 | 低频（8-15fps感知） | 可在低配模式减少数量 |
| L2 部门招牌层 | 16-30 | 店招、状态灯、部门铭牌 | 状态变化/低频 | 承担“部门健康”表达 |
| L3 Agent 实体层 | 31-60 | 小人精灵、昵称、emoji、阴影 | 逐帧 | 按状态驱动，不支持玩家输入 |
| L4 事件特效层 | 61-90 | 完成/失败提示、脉冲、短时扫光 | 事件触发 | 必须可快速回收（池化） |
| L5 前景信息层 | 91-130 | 气泡、死亡原因顶栏等 | 低频 + 按需 | 优先可读性，不遮挡关键 UI |
| L6 交互热区层 | 131-150 | 透明 hit area | 事件驱动 | 仅点选、hover，不接管全局手势 |

### 分层约束
- Canvas 内允许“点击部门/点击角色”，但**不提供 WASD/摇杆/拖拽移动角色**。
- UI 面板（React）永远在 Canvas 之上，避免 z-index 争夺。
- 动态对象必须可销毁或复用，避免长时间泄漏。

---

## 5. 动效策略（状态驱动 + 分级降载）

## 5.1 动效类型
1. **常驻微动效**：呼吸光、轻微浮动、霓虹闪烁（低振幅）。
2. **状态动效**：Agent 状态变化（idle/writing/error/dead）触发表现切换。
3. **事件动效**：任务完成/失败、部门告警（短时 burst）。

## 5.2 状态到动效映射（建议）

| 业务状态 | 视觉语言 | 节奏 |
|---|---|---|
| idle | 弱光常亮、轻微浮动 | 慢（1.8~2.4s） |
| working（writing/researching/executing/testing...） | 亮度增强 + 呼吸 + 小范围移动 | 中（0.9~1.3s） |
| syncing | 双脉冲或环形扫描 | 中快（0.8~1.1s） |
| error | 红色快闪 + 抖动（限制次数） | 快（0.4~0.6s） |
| dead | 去饱和 + 低亮 + 低频闪断 | 慢（1.8~2.6s） |

## 5.3 性能分档策略
- **High**：全量雨雾、扫光、更多建筑窗灯随机。
- **Low**：关闭雨滴/减少雾层/降低更新频率/减少并行动画数。
- 自动降档建议：平均 FPS 持续低于阈值（如 40）若干周期后切换。

## 5.4 动效治理规则
- 事件特效持续时间建议 `< 1200ms`。
- 同屏高亮目标不超过 2 个，避免“全屏都在闪”。
- 文字类提示优先稳定、少抖动。

---

## 6. React 组件边界设计

> 原则：React 负责“数据与交互编排”，Canvas 负责“渲染执行”。

```text
OfficeApp
├─ OfficeDataProvider         # 数据拉取 + 归一化 + Store 注入
├─ OfficeLayout
│  ├─ TopHUD                  # 时间、KPI、模式切换
│  ├─ OfficeCanvasShell       # Phaser 生命周期容器（唯一入口）
│  ├─ RightPanel
│  │  ├─ AgentGrid
│  │  ├─ TaskList
│  │  └─ LogPanel
│  ├─ DeptDrawer              # 部门详情（点击店铺后打开）
│  └─ OverlayFxLayer          # DOM 级提示（非核心）
└─ Devtools/Diagnostics (可选)
```

### 6.1 组件职责
- **OfficeDataProvider**：
  - 拉取 `/live`、`/tasks`；
  - 统一 normalize；
  - 写入 `OfficeStore`；
  - 管理轮询节奏与失败重试。

- **OfficeCanvasShell**：
  - 只做 Phaser mount/unmount；
  - 将“可渲染快照”传给 Scene Adapter；
  - 不直接做业务判断。

- **RightPanel / DeptDrawer**：
  - 全部基于 Store selector 渲染；
  - 不直接读 Phaser 对象。

- **TopHUD**：
  - 展示性能档位、主题、全局筛选；
  - 发出 UI 命令事件（如 `ui/filter.changed`）。

---

## 7. 事件通信方案（React ↔ Canvas）

## 7.1 通信原则
1. **事件有类型、有来源、有负载 schema**。
2. **状态更新走 Store，瞬时交互走 EventBus**。
3. **禁止跨层直接调用**（例如 React 直接改 scene internals）。

## 7.2 事件总线分层

### A. Domain Events（数据域）
- 由数据网关或 Store 触发。
- 示例：
  - `domain/live.updated`
  - `domain/tasks.updated`
  - `domain/task.transition`

### B. UI Command Events（UI -> Canvas）
- React 发给 Canvas 的渲染命令。
- 示例：
  - `ui/agent.highlight` `{ agentId }`
  - `ui/dept.focus` `{ deptId }`
  - `ui/fx.mode.set` `{ mode: 'high'|'low' }`
  - `ui/theme.set` `{ theme }`

### C. Scene Interaction Events（Canvas -> UI）
- Canvas 将点击/hover等交互回传给 React。
- 示例：
  - `scene/dept.clicked` `{ deptId }`
  - `scene/agent.clicked` `{ agentId }`
  - `scene/fps.low` `{ avgFps }`
  - `scene/object.hovered` `{ kind, id }`

## 7.3 事件信封（建议）

```ts
{
  id: string,          // 唯一ID
  type: string,        // 事件类型
  source: 'ui' | 'scene' | 'domain',
  ts: number,          // 时间戳
  payload: object
}
```

## 7.4 典型链路
1. 用户点击店铺（Canvas）
2. Scene 发 `scene/dept.clicked`
3. React 监听后更新 `selectedDept`
4. `DeptDrawer` 打开并展示该部门 Agent/任务/日志
5. 同时 React 发 `ui/dept.focus` 给 Canvas，做店铺高亮

---

## 8. 数据与渲染同步策略

### 8.1 数据节奏
- `live`：高频（例如 2~3s）
- `tasks`：中低频（例如 10~15s）
- 前端内部对高频抖动做合并（batched update）

### 8.2 渲染策略
- Canvas 不直接消费原始接口数据，统一消费 `RenderSnapshot`。
- `RenderSnapshot` 建议结构：
  - `agentsView[]`（含位置目标、状态、高亮）
  - `deptView[]`（部门灯、聚合状态）
  - `fxQueue[]`（任务完成/失败事件）
  - `overlayView`（气泡/提示）

### 8.3 一致性规则
- 业务真相在 Store；Canvas 对象是投影。
- 当 Scene 与 Store 不一致，以 Store 为准进行回收/重建。

---

## 9. 可实施目录建议（面向 frontend-app）

```text
frontend-app/src/
├─ app/
│  ├─ OfficeApp.tsx
│  ├─ OfficeLayout.tsx
│  └─ routes.ts
├─ data/
│  ├─ gateways/liveGateway.ts
│  ├─ gateways/taskGateway.ts
│  ├─ normalize/
│  └─ pollingScheduler.ts
├─ store/
│  ├─ officeStore.ts
│  ├─ selectors.ts
│  └─ eventBus.ts
├─ canvas/
│  ├─ OfficeCanvasShell.tsx
│  ├─ phaser/config.ts
│  ├─ phaser/scenes/OfficeScene.ts
│  ├─ phaser/layers/
│  ├─ phaser/entities/
│  └─ adapters/renderSnapshotAdapter.ts
├─ ui/
│  ├─ TopHUD/
│  ├─ RightPanel/
│  ├─ DeptDrawer/
│  └─ LogPanel/
└─ shared/
   ├─ types/
   └─ constants/
```

---

## 10. 迁移与落地顺序（不改业务接口）

1. 先建立 Store + EventBus + 数据 normalize（不改视觉）。
2. 抽离 Canvas 壳层（`OfficeCanvasShell`），把现有 Phaser 初始化纳入生命周期。
3. 将“部门点击/Agent 高亮/特效触发”迁移到事件通信。
4. 再拆 UI 面板为 React 组件，替换内联 DOM 拼接。
5. 最后做性能分档、异常恢复、长时稳定性压测。

---

## 11. 风险与规避

- **风险 1：状态双写（React 与 Scene 各自持有）**  
  规避：业务状态只保留 Store 一份，Scene 只读快照。

- **风险 2：事件风暴导致卡顿**  
  规避：事件节流、同类事件合并、关键事件优先级。

- **风险 3：长时运行内存上涨**  
  规避：对象池 + 定时清理 + 统一 destroy 流程。

- **风险 4：UI/Canvas 职责再次混乱**  
  规避：代码评审强制边界（禁止跨层直接操作）。

---

## 12. 验收要点（v2 架构层）

- [ ] Canvas 完全作为展示引擎，不包含游戏操控逻辑。
- [ ] React 组件边界清晰，UI 与渲染引擎解耦。
- [ ] 事件通信有统一协议，核心链路可追踪。
- [ ] 图层与动效具备高/低档策略，可自动降级。
- [ ] 长时间展示（8h+）无明显卡顿和内存异常。

---

**结论**：
办公室 v2 的最优解是“React 主控 + Canvas 展示子系统 + 事件化通信”。
该方案能在不改后端接口的前提下，完成从“单文件脚本”到“可维护展示架构”的升级。
