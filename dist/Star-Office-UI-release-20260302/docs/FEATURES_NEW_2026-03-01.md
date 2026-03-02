# Star Office UI — 新增功能说明（本阶段）

## 1. 多龙虾访客系统
- 支持多个远端 OpenClaw 同时加入同一办公室。
- 访客支持独立头像、名字、状态、区域、气泡。
- 支持动态上下线与实时刷新。

## 2. Join Key 机制升级
- 从“一次性 key”升级为“固定可复用 key”。
- 默认 key：`ocj_starteam01` ~ `ocj_starteam08`。
- 保留安全控制：每个 key 的并发上限 `maxConcurrent`（默认 3）。

## 3. 并发控制（已修复竞态）
- 修复并发 join 的竞态问题（race condition）。
- 同 key 第 4 个并发 join 会被正确拒绝（HTTP 429）。

## 4. 访客状态映射与区域渲染
- `idle -> breakroom`
- `writing/researching/executing/syncing -> writing`
- `error -> error`
- 访客气泡文案与状态同步，不再错位。

## 5. 访客动画与资源优化
- 访客由静态图升级为动画精灵（像素风）。
- `guest_anim_1~6` 已提供 webp 版本，减少加载体积。

## 6. 名字与气泡显示优化
- 非 demo 访客名字与气泡位置上移，避免角色遮挡。
- 气泡锚点改为基于名字定位，保障“气泡在名字上方”。

## 7. 移动端展示
- 页面可在手机端直接访问与展示。
- 布局已进行基础移动端适配，满足演示场景。

## 8. 远端推送脚本联调改进
- 支持从状态文件读取并推送状态到 office。
- 增加状态来源诊断日志（用于定位“为何一直 idle”）。
- 修复 AGENT_NAME 环境变量覆盖时序问题。
