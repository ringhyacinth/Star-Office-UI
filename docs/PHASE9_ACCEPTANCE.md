# Phase 9 验收单（生产严格模式开关）

本阶段目标（非破坏）：
- 给生产环境增加“强制安全基线”开关，但默认关闭，不影响当前运行

## 已做内容
1) 新增环境变量：`STAR_OFFICE_PROD_STRICT_MODE=false`
2) 当生产 + strict=true 时，启动前强制检查：
- `STAR_OFFICE_WRITE_API_BEARER_ENABLED=true`
- `STAR_OFFICE_WRITE_API_TOKENS` 非空
- `STAR_OFFICE_ASSET_READ_AUTH_ENABLED=true`
3) `security_check.py` 同步 strict 规则检查

## 你现在如何使用
- 先保持 false（不影响现网）
- 当你确认前面 phase 都稳定，再切 true 做“硬约束上线”

## 回滚
- 环境层：`STAR_OFFICE_PROD_STRICT_MODE=false`
- 代码层：`git revert <phase9_commit>`
