# Office v2 冲突审计报告（task7）

> 审计时间：2026-03-01 19:2x（GMT+8）  
> 审计负责人：task7（笑面虎）  
> 审计范围：`/Users/alshyib/Workspace/Next/conpay/star-office-ui`（同 inode 路径别名：`/Users/alshyib/WorkSpace/...`）

---

## 0) 结论先行

**存在明显冲突风险（有）**，且已出现“后写覆盖先写”迹象。  
高危集中在：`frontend-app/src/App.tsx`、`frontend/index.html`、`backend/app.py`。

---

## 1) 审计依据（基于当前实际文件与变更）

1. 工作区实际变更：`git status --short`
   - 已跟踪修改：`backend/app.py`、`frontend/index.html`、`set_state.py`、`state.sample.json`
   - 大量未跟踪新增：`frontend-app/**`、`backend/feishu.py`、`backend/task_sync.py`、`scripts/**`、`docs/**`
2. 交付文档中的文件声明（`docs/office-v2/task*.md`）与现有文件交叉核对。
3. 关键冲突文件内容签名核验（是否保留前序任务功能点）。

---

## 2) 冲突清单

## 2.1 高冲突文件（被多个任务修改）

> 统计口径：同一文件被 >=2 个 task 在交付文档中声明涉及，且文件当前存在。

| 文件 | 涉及任务数 | 涉及任务 | 当前状态 | 风险级别 |
|---|---:|---|---|---|
| `frontend-app/src/App.tsx` | 7 | task2/task3/task7/task9/task10/task12/task16 | 未跟踪（新文件） | **极高** |
| `frontend/index.html` | 6 | task1/task5/task6/task8/task13/task14 | 已修改（tracked） | **极高** |
| `backend/app.py` | 4 | task1/task6/task13/task14 | 已修改（tracked） | **高** |
| `frontend-app/src/App.css` | 4 | task2/task10/task12/task16 | 未跟踪（新文件） | **高** |
| `frontend-app/src/components/CanvasShell.tsx` | 2 | task2/task16 | 未跟踪（新文件） | 中高 |
| `frontend-app/src/components/LogPanel.tsx` | 2 | task2/task16 | 未跟踪（新文件） | 中高 |
| `frontend-app/src/data/mockData.ts` | 2 | task2/task16 | 未跟踪（新文件） | 中 |
| `frontend-app/src/index.css` | 2 | task2/task10 | 未跟踪（新文件） | 中 |
| `backend/task_sync.py` | 2 | task1/task13 | 未跟踪（新文件） | 中 |

---

## 2.2 覆盖风险（后写覆盖先写）

### R-1 `frontend-app/src/App.tsx` 已出现功能覆盖

- task3（稳态/安全）与 task10（API 轮询）均声明修改 `App.tsx`。
- **当前 `App.tsx` 仅保留 mock 数据 + 画布交互 + telemetry 挂载**，未发现以下签名：
  - `useApiPoller`
  - `officeApi`
  - `fetchJsonWithTimeout`
  - `sanitizeForDisplay`
- 说明：前序“API 接入/降级/清洗”逻辑大概率被后续重写冲掉。

### R-2 `frontend-app/src/App.css` / `index.css` 存在样式覆盖风险

- task10 声明加入 API 面板样式；task12/task16 又连续改样式。
- 当前样式以画布与布局样式为主，API 相关样式痕迹不足，存在“后写吞并前写”概率。

### R-3 `frontend/index.html` 连续手工改写链长，覆盖窗口大

- 同文件涉及 6 个任务，且存在多份快照备份：
  - `frontend/index.html.bak.v2`
  - `frontend/index.html.bak.right-panel-redesign-20260301`
  - `frontend/index.html.bak.color-retheme-v1-pre`
- 当前仍可见“占位特效/术语不一致/task_id 回退”等点，说明并行意见未完整整合。

### R-4 `backend/app.py` 超大单文件并行改，回归覆盖风险高

- `/live` 聚合、provider 健康、tasks/news/ollama 等集中在同一文件。
- 多任务并改时容易出现“局部修复互相覆盖、回归遗漏”。

---

## 2.3 依赖顺序风险（先后不当会坏）

| 风险ID | 依赖关系 | 若顺序错误的后果 |
|---|---|---|
| D-1 | `backend/app.py` -> `frontend/index.html`（`/live`/`/tasks` 字段契约） | 前端渲染空白、状态/任务卡片错位 |
| D-2 | `backend/feishu.py` + `backend/task_sync.py` -> `scripts/*task-sync*.sh` | 同步进程启动失败或“假在线” |
| D-3 | `task2骨架` -> `task3稳态` -> `task10 API` -> `task16画布交互`（同在 `frontend-app/src/App.tsx`） | 先合后写会把 API/降级/安全或交互任一侧覆盖掉 |
| D-4 | `frontend-app/src/App.tsx` -> `src/test/App.smoke.test.tsx` | 先改测试后改页面会导致测试漂移/误绿 |
| D-5 | 运行数据文件（`news.json`/`state.sample.json`）与代码提交混包 | 代码审查噪声增大，回滚困难 |

---

## 3) 建议动作

## 3.1 立即冻结（只允许单人整合）

建议立刻冻结以下文件（进入“单写者”模式）：

1. `backend/app.py`
2. `frontend/index.html`
3. `frontend-app/src/App.tsx`
4. `frontend-app/src/App.css`
5. `frontend-app/src/index.css`
6. `backend/task_sync.py`
7. `scripts/start-task-sync.sh`
8. `scripts/check-task-sync.sh`
9. `scripts/stop-task-sync.sh`

---

## 3.2 关键文件唯一 owner（建议）

| 关键文件 | 唯一 owner（taskX） | 说明 |
|---|---|---|
| `backend/app.py` | **task1** | 集成主负责人，统一后端契约 |
| `frontend/index.html` | **task2** | 前端主界面整合入口 |
| `frontend-app/src/App.tsx` | **task10** | 负责把 API/降级/稳态与交互能力合并到单入口 |
| `frontend-app/src/App.css` | **task12** | 样式与遥测表现统一口径 |
| `frontend-app/src/components/CanvasShell.tsx` | **task16** | 画布交互主实现 |
| `frontend-app/src/components/LogPanel.tsx` | **task16** | 与点名/筛选联动同源维护 |
| `backend/task_sync.py` | **task16** | 稳定性维护与同步链路执行 |
| `scripts/*task-sync*.sh` | **task16** | 与同步器代码同 owner 降低断链风险 |
| `docs/office-v2/*`（集成/发布清单类） | **task1** | 发布文档单点收口 |

---

## 3.3 合并顺序（建议执行序列）

1. **打基线快照并冻结高冲突文件**（禁止并行直改）。
2. **先后端同步链路**：`backend/feishu.py` + `backend/task_sync.py` + `scripts/*task-sync*.sh`（owner: task16）。
3. **再后端主接口**：`backend/app.py`（owner: task1），确保 `/health` `/live` `/tasks` 契约稳定。
4. **再旧前端主视图**：`frontend/index.html`（owner: task2），只按既定契约接入。
5. **若要推进 React 线**：
   - 5.1 `frontend-app/src/App.tsx` 由 task10 先做“API+稳态主干”；
   - 5.2 task16 以 patch 方式并入画布交互；
   - 5.3 task12 收敛 `App.css/index.css`；
   - 5.4 最后更新 `src/test/App.smoke.test.tsx` 并回归。
6. **统一回归**：`py_compile`、`npm run lint/test/build`、`/health /live /tasks /ollama` 冒烟。
7. **文档收口与解冻**：由 task1 更新上线清单后再开放并行修改。

---

## 4) 一句话判断

当前不是“是否会冲突”的问题，而是**已经出现覆盖痕迹**。建议先冻结高冲突文件，按 owner + 顺序串行整合，再恢复并行开发。
