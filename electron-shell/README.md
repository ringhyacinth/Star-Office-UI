# Star Desktop Pet (Electron Shell)

这个目录是 Electron 版桌面壳，和现有 Tauri 版并行存在，方便逐步迁移。

## 已接入能力

- 复用原有前端：`http://127.0.0.1:18791/?desktop=1`
- 复用 mini 页面：`desktop-pet/src/minimized.html`
- 启动时自动拉起 Python backend（若未运行）
- 主窗口 / mini 窗口切换
- 托盘（menu bar）常驻菜单
- 通过 preload 注入 `window.__TAURI__` 兼容层，尽量少改现有前端逻辑

## 启动方式

```bash
cd "/Users/wangzhaohan/Documents/GitHub/Star-Office-UI/electron-shell"
npm install
npm run dev
```

## 可选环境变量

- `STAR_PROJECT_ROOT`：项目根目录（默认自动探测）
- `STAR_BACKEND_PYTHON`：后端 Python 可执行路径
- `STAR_BACKEND_HOST`：后端主机（默认 `127.0.0.1`）
- `STAR_BACKEND_PORT`：后端端口（默认 `18791`）

## 说明

- 当前阶段是“可运行迁移骨架”，目的是先替换桌面容器层。
- 现有 Tauri 目录不受影响，可随时回滚或并行对比。
