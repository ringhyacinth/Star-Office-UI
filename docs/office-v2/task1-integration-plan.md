# Office 重构 v2 集成说明与冲突规约（task1）

> 目标：让多名弟子并行开发时**不互相覆盖**，并保证今晚上线可控。
> 
> 适用仓库：`/Users/alshyib/Workspace/Next/conpay/star-office-ui`
> 
> 版本：v2.0（今晚集成版）

---

## 1. 结论先行（今晚执行口径）

1. **主运行栈保持不变**：继续以 `backend/app.py + frontend/index.html` 为唯一上线链路。  
2. **`frontend-app/` 不纳入今晚上线**：仅作为实验/后续迁移分支，不参与生产合并。  
3. **单文件高冲突区单主负责**：`frontend/index.html`、`backend/app.py` 今晚只能有 1 位主改人，其他人通过 PR/patch 交由主改人落地。  
4. **按模块顺序合并**：先后端契约，再前端视图，再脚本与文档，最后回归和发布。  
5. **不做数据结构迁移**：`state.json`、任务字段、接口返回结构保持兼容，避免夜间联动风险。

---

## 2. 模块边界（并行开发拆分单位）

> 并行单位按“目录/模块”划分，**不按同一文件内区域并行**。

| 模块 | 边界（目录/文件） | 职责 | 今晚状态 |
|---|---|---|---|
| M1 后端运行时 | `backend/app.py` | `/health` `/status` `/live` `/logs` `/tasks` `/news` `/ollama` `/api/zimage` | **纳入上线** |
| M2 任务同步链路 | `backend/task_sync.py` `backend/feishu.py` `scripts/start-task-sync.sh` `scripts/check-task-sync.sh` `scripts/stop-task-sync.sh` | OpenClaw ↔ 飞书任务同步 | **纳入上线（仅稳定性修补）** |
| M3 前端主界面 | `frontend/index.html` `frontend/office_bg.png` | 指挥中心 UI、日志面板、看板视图 | **纳入上线** |
| M4 React 迁移实验 | `frontend-app/**` | 新前端技术栈验证 | **不纳入今晚上线** |
| M5 运行数据/配置 | `state.json` `state.sample.json` `.env` `news.json` | 状态、样例、环境变量、资讯数据 | **只读/谨慎改** |
| M6 文档与规约 | `docs/**` | 集成规则、清单、验收与回滚说明 | **纳入上线** |

---

## 3. 文件所有权（避免互踩）

> 原则：一个高冲突文件只允许一个主负责人直接改。

| 文件/路径 | 主负责人（建议） | 备援 | 其他人规则 |
|---|---|---|---|
| `backend/app.py` | task1（集成主） | task16 | 不直接改主干；提交差异说明/patch，由主负责人吸收 |
| `frontend/index.html` | task2（UI主改） | task1 | 禁止多人同时改；所有 UI 变更先过主改人整合 |
| `backend/task_sync.py` `backend/feishu.py` | task16（稳定性） | task3 | 只改同步与容错，不改业务展示逻辑 |
| `scripts/*task-sync*.sh` | task16 | task1 | shell 变更需附“启动-检查-停止”验证输出 |
| `frontend-app/**` | task8（预研） | task2 | 今晚不进 release 分支 |
| `docs/office-v2/**` | task1 | task4 | 可并行补充，但不得改上述所有权定义 |

### 高冲突文件特别规约

- `frontend/index.html` 与 `backend/app.py` 采用**串行合并**，不能平行抢同一文件。  
- 若出现冲突：按“主负责人版本优先 + 需求提交者补丁重放”处理。  
- 禁止直接在主分支临时手改（必须走 PR/合并记录）。

---

## 4. 合并顺序（今晚上线序列）

### Phase 0：冻结与基线（5 分钟）
- 冻结并行提交窗口，确认本次 release 的目标分支。
- 打一个基线标签（示例）：`office-v2-premerge-YYYYMMDD-HHMM`。

### Phase 1：后端契约先行（M1 + M2）
- 先合并 `backend/*` 与 `scripts/*task-sync*.sh`。
- 要求：不破坏现有接口字段，不改端口，不改状态机关键枚举。

### Phase 2：前端主界面（M3）
- 再合并 `frontend/index.html` 相关改动。
- 要求：不新增后端必填字段，不依赖未上线接口。

### Phase 3：文档与执行清单（M6）
- 合并 `docs/office-v2/*`，固化操作手册。

### Phase 4：联调回归 + 发布
- 统一执行构建与回归清单（见 `task1-merge-checklist.md`）。
- 满足通过条件后再发布。

---

## 5. 今晚上线最小范围（MVP Release Slice）

### 必须包含
1. `/health`、`/status`、`/live` 三条核心接口可用；
2. `frontend/index.html` 指挥中心主视图可打开、可轮询更新；
3. 任务同步脚本可启动/检查/停止；
4. 文档清单齐备（本目录两份文档）。

### 明确排除
1. `frontend-app/` React 产物接管生产；
2. 新增外部依赖导致的部署步骤变化；
3. 数据格式变更（state/tasks/news schema）；
4. 大规模视觉重构（仅修 bug/稳定性）。

---

## 6. 冲突处理与升级机制

### 冲突判定（任一即触发）
- 两个 PR 同时改 `backend/app.py` 或 `frontend/index.html`；
- 前端改动依赖未合并的后端字段；
- 回归出现 P0（页面打不开、核心接口 5xx、同步链路中断）。

### 处理流程
1. 先暂停后入 PR；
2. 由主负责人产出冲突合并版本；
3. 再跑完整回归；
4. 若仍失败，回退至基线 tag，拆小后重提。

---

## 7. 交付物映射

- 本文档：`docs/office-v2/task1-integration-plan.md`
- 执行清单：`docs/office-v2/task1-merge-checklist.md`

> 本规约今晚优先级最高；如与历史习惯冲突，以本文件为准。
