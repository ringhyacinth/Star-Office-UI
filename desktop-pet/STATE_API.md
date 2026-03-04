# 桌宠状态对接说明（openclaw 用）

桌宠通过读取 **state.json** 获取当前状态并刷新表现（头顶图标/emoji、气泡文案、角色动画、寻路目标）。openclaw 需要**写入或更新**该文件以驱动桌宠。

---

## 1. 文件位置

- **路径**：与桌宠工作目录下的 `state.json`（桌宠启动时会解析项目根目录，即包含 `state.json` 和 `layers/` 的目录）。
- **格式**：UTF-8 JSON。

---

## 2. state.json 结构

```json
{
  "state": "idle",
  "detail": "可选，状态说明，目前仅用于展示/调试",
  "progress": 0.0,
  "updated_at": "2025-02-27T12:00:00Z"
}
```

| 字段         | 类型    | 必填 | 说明 |
|--------------|---------|------|------|
| `state`      | string  | 是   | 当前状态，见下表。桌宠每 ~2s 轮询读取。 |
| `detail`     | string  | 否   | 可选描述，可被后续扩展用于气泡或调试。 |
| `progress`   | number  | 否   | 0~1，可选进度，可被后续扩展。 |
| `updated_at` | string  | 否   | ISO8601 时间，可选。 |

**只有 `state` 会影响桌宠行为**；其余字段可留空或省略。

---

## 3. 状态取值（openclaw 应写入的 `state`）

桌宠只认下面这些**标准状态名**（小写）。写别的值会被当成 `idle` 或按别名映射。

| state 值       | 含义           | 桌宠表现概要 |
|----------------|----------------|--------------|
| `idle`         | 摸鱼/无任务     | 💤 呼吸动画，随机闲逛 |
| `writing`      | 写作/记笔记     | Word 图标，走到 writing POI |
| `receiving`    | 收消息         | Hangouts 图标，走到 receiving POI |
| `replying`     | 回复消息       | Glovo 图标，走到 replying POI |
| `researching`  | 调研/查资料     | Google 图标，走到 researching POI |
| `executing`    | 执行任务/跑任务 | ⚡ emoji，走到 executing POI |
| `syncing`      | 同步/备份      | ☁️ emoji，走到 syncing POI |
| `error`        | 出错           | ❗ emoji，走到 error POI |

POI 在 `layers/map.json` 的 `pois` 里配置；状态变化时桌宠会寻路到对应格子。

---

## 4. 别名映射（可选）

若 openclaw 侧用不同名字，桌宠前端会先做一次**别名 → 标准状态**的映射，再按上表表现：

| openclaw 可写的 state | 映射为 |
|------------------------|--------|
| `working`              | `writing` |
| `run`                  | `executing` |
| `running`              | `executing` |
| `sync`                 | `syncing` |
| `research`             | `researching` |

未在上述列表中的 `state` 会视为 `idle`。

---

## 5. openclaw 需要“跳”什么

- **写 state.json**：在约定目录下创建/覆盖 `state.json`，保证 `state` 为上面 8 个标准状态之一（或 5 个别名之一）。
- **何时写**：状态变化时写一次即可；桌宠轮询间隔约 2 秒，无需高频写入。
- **示例**  
  - 开始写文档：`{ "state": "writing" }`  
  - 收到消息：`{ "state": "receiving" }`  
  - 正在回复：`{ "state": "replying" }`  
  - 查资料：`{ "state": "researching" }`  
  - 执行任务：`{ "state": "executing" }`  
  - 同步中：`{ "state": "syncing" }`  
  - 出错：`{ "state": "error" }`  
  - 摸鱼/无任务：`{ "state": "idle" }`

按上述方式更新 `state.json`，即可与当前桌宠状态和 POI 行为一致。
