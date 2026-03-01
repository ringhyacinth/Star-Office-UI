# task11 自动化冒烟报告（办公室重构 v2）

## 1) 任务目标
为 `frontend-app` 增加最小冒烟自动化测试，覆盖：
- 页面可加载
- 关键卡片存在
- 日志区可见

## 2) 选型说明
本次采用 **Vitest + React Testing Library（RTL）**。

原因：
- 对 React 组件冒烟验证更轻量，执行速度快；
- 无需 Playwright 浏览器驱动下载，适合当前“最小可用”目标；
- 易于在本地/CI 中稳定运行。

## 3) 实施内容

### 3.1 测试基础设施
在 `frontend-app` 增加/更新：
- `package.json`
  - 新增脚本：
    - `test`: `vitest run`
    - `test:watch`: `vitest`
  - 新增 devDependencies：
    - `vitest`
    - `@testing-library/react`
    - `@testing-library/jest-dom`
    - `jsdom`
- `vite.config.ts`
  - 新增 `test` 配置：
    - `environment: 'jsdom'`
    - `setupFiles: './src/test/setup.ts'`
    - `css: true`

### 3.2 新增冒烟用例
- `src/test/setup.ts`
- `src/test/App.smoke.test.tsx`

用例覆盖：
1. **页面可加载**
   - 断言页面标题 `AI 特工队总部 · Office V2` 可见
   - 断言主内容容器 `#main-content` 存在
2. **关键卡片存在**
   - 断言关键卡片标题 `任务总览` 可见
   - 断言 `Agent 工作负载` 卡片可见
3. **日志区可见**
   - 断言日志容器 `#log-panel` 存在且可见
   - 断言日志筛选项 `全部日志` 可见

## 4) 如何运行
在仓库根目录执行：

```bash
cd frontend-app
npm install
npm run test
```

可选：

```bash
npm run build
```

## 5) 执行结果
本地执行结果：
- `npm run test`：✅ 通过（1 文件 / 3 用例）
- `npm run build`：✅ 通过

测试输出摘要：

```text
✓ src/test/App.smoke.test.tsx (3 tests)
Test Files  1 passed (1)
Tests       3 passed (3)
```

---

结论：`frontend-app` 已具备最小冒烟自动化能力，满足本任务 3 项覆盖要求。
