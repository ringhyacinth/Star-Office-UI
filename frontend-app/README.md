# frontend-app

Star Office UI 的唯一前端入口（React + Vite + TypeScript）。

## Scripts

```bash
npm run dev        # 本地开发 (http://127.0.0.1:4173)
npm run lint       # ESLint
npm run test       # Vitest (jsdom)
npm run build      # tsc + vite build
npm run preview    # 本地预览构建产物
```

## API 对接约定

- 默认 `VITE_API_BASE_URL` 为空，使用相对路径（`/live`、`/health` 等）
- 开发态依赖 `vite.config.ts` 中的 proxy 转发到 `OFFICE_BACKEND_URL`（默认 `http://127.0.0.1:19800`）
- 生产态由 Flask 托管 `dist`，前端同源访问 API

## 环境变量

- `OFFICE_BACKEND_URL`：Vite dev proxy 的后端地址（仅开发态）
- `VITE_API_BASE_URL`：显式指定 API 基础地址（通常不需要）
- `VITE_API_DEV_PORT`：当检测到本地 dev 端口时，前端用于回退探测的后端端口（默认 `19800`）

## 质量门槛

提交前至少执行：

```bash
npm run lint
npm run test
npm run build
```
