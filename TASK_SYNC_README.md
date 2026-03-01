# OpenClaw -> 飞书任务自动同步

## 功能说明

自动监控OpenClaw agent的session活动，并同步到飞书多维表格任务看板：

- 🔄 每10秒扫描一次所有agent的活跃session
- 📝 自动创建任务（基于session的第一条用户消息）
- 📊 实时更新任务进度（基于session消息数量）
- ✅ 自动标记任务完成（当session结束时）

## 使用方法

### 启动同步器

```bash
./star-office-ui/scripts/start-task-sync.sh
```

### 停止同步器

```bash
./star-office-ui/scripts/stop-task-sync.sh
```

### 检查状态

```bash
./star-office-ui/scripts/check-task-sync.sh
```

### 查看日志

```bash
tail -f /tmp/openclaw-task-sync.log
```

## 任务ID格式

`session-{agent_name}-{session_id前8位}`

例如：`session-task1-8fad612f`

## 状态映射

| OpenClaw状态 | 飞书任务状态 |
|-------------|------------|
| idle | 待办 |
| writing/researching/executing | 进行中 |
| error/dead | 异常 |

## 进度计算

- 基于session消息数量估算
- 每20条消息约等于100%进度
- session结束时自动设为100%

## 注意事项

1. 需要配置飞书API凭证（见`backend/feishu.py`）
2. 同步器会持续运行，建议配合systemd或launchd使用
3. 任务一旦创建不会自动删除，只会更新状态
