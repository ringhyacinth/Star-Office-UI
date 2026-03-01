# Office 重构 v2 合并执行清单（task1）

> 用途：今晚集成发布的“可执行”步骤卡。  
> 目标：保证**可构建、可回归、可回滚**。

---

## A. 合并前准备（Pre-Merge）

- [ ] 确认本次仅覆盖 `M1/M2/M3/M6`（见 integration plan）
- [ ] 确认 `frontend-app/` 改动不进入 release 分支
- [ ] 创建基线 tag：`office-v2-premerge-YYYYMMDD-HHMM`
- [ ] 记录发布负责人、回滚负责人、值班观察人

---

## B. 构建与静态检查（Build Gate）

在仓库根目录执行：

```bash
cd /Users/alshyib/Workspace/Next/conpay/star-office-ui
```

### B1. Python 语法检查（阻塞项）

```bash
python3 -m py_compile backend/app.py backend/feishu.py backend/task_sync.py set_state.py
```

通过标准：命令无报错输出。

### B2. Shell 脚本语法检查（阻塞项）

```bash
bash -n scripts/start-task-sync.sh
bash -n scripts/check-task-sync.sh
bash -n scripts/stop-task-sync.sh
bash -n scripts/open-dashboard.sh
```

通过标准：命令无报错输出。

### B3. React 实验工程构建（信息项，今晚非阻塞）

```bash
cd frontend-app && npm run build && cd ..
```

通过标准：构建成功即可；失败不阻塞本次发布（因不纳入今晚上线）。

---

## C. 合并顺序检查（Merge Order Gate）

- [ ] 先合并后端与同步链路：`backend/*`、`scripts/*task-sync*.sh`
- [ ] 后合并前端主界面：`frontend/index.html`
- [ ] 最后合并文档：`docs/office-v2/*`
- [ ] 每一步合并后先做一次快速冒烟，再继续下一步

---

## D. 回归验证（Regression Gate）

## D1. 服务启动与核心接口冒烟（阻塞项）

```bash
cd /Users/alshyib/Workspace/Next/conpay/star-office-ui
python3 backend/app.py
```

另开终端执行：

```bash
curl -s -o /tmp/office-health.json -w "%{http_code}\n" http://127.0.0.1:19800/health
curl -s -o /tmp/office-status.json -w "%{http_code}\n" http://127.0.0.1:19800/status
curl -s -o /tmp/office-live.json -w "%{http_code}\n" http://127.0.0.1:19800/live
curl -s -o /tmp/office-ollama.json -w "%{http_code}\n" http://127.0.0.1:19800/ollama
```

通过标准：HTTP 均为 `200`。

### D2. 前端主视图回归（阻塞项）

- [ ] 浏览器打开 `http://127.0.0.1:19800`
- [ ] 页面加载成功，无白屏
- [ ] 顶部在线数/进行中数有更新
- [ ] 日志面板有内容（或空态提示正常）
- [ ] 任务仪表盘右侧卡片渲染正常

### D3. 同步脚本回归（阻塞项）

```bash
cd /Users/alshyib/Workspace/Next/conpay/star-office-ui
bash scripts/start-task-sync.sh
bash scripts/check-task-sync.sh
bash scripts/stop-task-sync.sh
```

通过标准：可启动、可查看状态、可停止，无僵尸 PID。

### D4. 外部依赖退化验证（非阻塞但需记录）

- [ ] 未配置飞书时，`/tasks` 返回受控错误（不影响首页）
- [ ] 未运行 Ollama 时，页面显示“未运行”而非崩溃

---

## E. 发布动作（Release Gate）

- [ ] 所有阻塞项 PASS
- [ ] 打发布 tag：`office-v2-release-YYYYMMDD-HHMM`
- [ ] 发布后观察 30 分钟（每 5 分钟巡检一次 `/health` 与首页）

建议巡检命令：

```bash
for i in {1..6}; do
  date
  curl -s -o /dev/null -w "health=%{http_code}\n" http://127.0.0.1:19800/health
  sleep 300
done
```

---

## F. 回滚标准与步骤（Rollback Gate）

## F1. 触发回滚条件（任一满足即执行）

- [ ] `/health` 连续 2 分钟非 200
- [ ] 首页无法打开或主功能不可用持续 5 分钟
- [ ] 同步链路异常且 10 分钟内无法恢复
- [ ] 出现 P0 安全/稳定问题

## F2. 标准回滚步骤

1. 宣布回滚（团队同步：原因、执行人、预计完成时间）
2. 切回基线 tag（`office-v2-premerge-*` 或最近稳定 tag）

```bash
cd /Users/alshyib/Workspace/Next/conpay/star-office-ui
git checkout <stable-tag>
```

3. 重启服务并恢复同步器

```bash
pkill -f "python3 backend/app.py" || true
nohup python3 backend/app.py >/tmp/star-office-ui.log 2>&1 &
bash scripts/start-task-sync.sh
```

4. 回滚后验证

```bash
curl -s -o /tmp/office-rb-health.json -w "%{http_code}\n" http://127.0.0.1:19800/health
curl -s -o /tmp/office-rb-live.json -w "%{http_code}\n" http://127.0.0.1:19800/live
```

5. 观察 10 分钟无新增 P0/P1 后，宣布回滚完成。

---

## G. 记录留痕（必填）

- 发布版本（tag/commit）：
- 回滚版本（tag/commit）：
- 构建结果：PASS / FAIL
- 回归结果：PASS / FAIL
- 值班观察结论：
- 遗留风险与后续动作：

