# Star Office Auto-Detect Daemon

自动检测本机运行的 Claude Code / Codex / OpenClaw 实例，并同步到 Star Office。

## 快速开始

```bash
# 使用默认配置（localhost:28791）
python scripts/auto_detect/daemon.py

# 自定义配置
python scripts/auto_detect/daemon.py \
  --url https://office.hyacinth.im \
  --key ocj_your_key \
  --interval 15
```

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `STAR_OFFICE_URL` | `http://127.0.0.1:28791` | Office 后端地址 |
| `STAR_OFFICE_JOIN_KEY` | `ocj_example_team_01` | Join key |
| `STAR_OFFICE_INTERVAL` | `10` | 轮询间隔（秒） |

## 架构

```
detector.py   — 进程检测（pgrep + lsof 获取工作目录）
client.py     — Office API 客户端（join / push / leave）
daemon.py     — 主循环，协调检测与同步
```

## 检测方式

| Agent | 检测方法 | 状态判断 |
|-------|---------|---------|
| Claude Code | `pgrep -x claude` | 进程存在 → writing |
| Codex | `pgrep -x codex` | 进程存在 → writing |
| OpenClaw | `gateway.log` 修改时间 | 120s 内修改 → writing，否则 idle |

## 后台运行

```bash
# macOS launchd
nohup python scripts/auto_detect/daemon.py > /tmp/star-office-daemon.log 2>&1 &

# 或直接用 screen/tmux
screen -dmS star-office python scripts/auto_detect/daemon.py
```

## 相关

- Issue: [#65](https://github.com/ringhyacinth/Star-Office-UI/issues/65)
- PR: [#64](https://github.com/ringhyacinth/Star-Office-UI/pull/64)
