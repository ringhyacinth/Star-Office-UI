# Phase 1 验收单（基线冻结与回滚准备）

你只需要确认 3 件事：

1) 是否看到新文件：
- docs/STABILITY_PLAN_NON_BREAKING.md
- scripts/baseline_snapshot.sh
- docs/PHASE1_ACCEPTANCE.md

2) 是否可执行快照脚本：
```bash
cd /root/.openclaw/workspace/Star-Office-UI
bash scripts/baseline_snapshot.sh
```
执行后应输出一个目录：
`snapshots/baseline-YYYYMMDD-HHMMSS`

3) 是否接受“每个 Phase 先验收再继续”的节奏。

---

通过后我将进入 Phase 2：
- 仅做可开关的安全加固（不删功能、不改交互）
- 做完给你一份“逐项功能对照验收表”再继续。
