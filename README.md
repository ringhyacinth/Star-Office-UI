# Star Office UI

[![EN](https://img.shields.io/badge/Lang-EN-2563eb)](#english)
[![JA](https://img.shields.io/badge/Lang-JA-e94560)](#日本語)
[![ZH](https://img.shields.io/badge/Lang-ZH-16a34a)](#中文)

A pixel office dashboard for multi-agent collaboration.

---

## English

### Overview

Star Office UI visualizes AI agent status in real-time.

- Main status: `idle`, `writing`, `researching`, `executing`, `syncing`, `error`
- Multi-agent guest join/leave flow
- Yesterday memo panel
- Mobile-friendly web UI
- Built-in UI language switcher (`EN / JA / ZH`)

### Quick Start

```bash
git clone https://github.com/ringhyacinth/Star-Office-UI.git
cd Star-Office-UI
python3 -m pip install -r backend/requirements.txt
cp state.sample.json state.json
cd backend
python3 app.py
```

Open: `http://127.0.0.1:18791`

### Change Main Agent State

```bash
cd /path/to/Star-Office-UI
python3 set_state.py writing "Organizing documents"
python3 set_state.py syncing "Syncing progress"
python3 set_state.py error "Found issue, debugging"
python3 set_state.py idle "Standing by"
```

### Main APIs

- `GET /health`
- `GET /status`
- `POST /set_state`
- `GET /agents`
- `POST /join-agent`
- `POST /agent-push`
- `POST /leave-agent`
- `GET /yesterday-memo`

### License

- Code / logic: MIT
- Art assets: non-commercial only

---

## 日本語

### 概要

Star Office UI は、複数のAIエージェントの作業状態をリアルタイム表示するピクセルオフィス看板です。

- メイン状態: `idle`, `writing`, `researching`, `executing`, `syncing`, `error`
- ゲストAgentの参加/退出フロー
- 昨日のメモ表示
- モバイル対応Web UI
- UI言語切替（`EN / JA / ZH`）

### クイックスタート

```bash
git clone https://github.com/ringhyacinth/Star-Office-UI.git
cd Star-Office-UI
python3 -m pip install -r backend/requirements.txt
cp state.sample.json state.json
cd backend
python3 app.py
```

アクセス先: `http://127.0.0.1:18791`

### メインAgentの状態変更

```bash
cd /path/to/Star-Office-UI
python3 set_state.py writing "文書を整理中"
python3 set_state.py syncing "進捗を同期中"
python3 set_state.py error "問題を検出、調査中"
python3 set_state.py idle "待機中"
```

### 主要API

- `GET /health`
- `GET /status`
- `POST /set_state`
- `GET /agents`
- `POST /join-agent`
- `POST /agent-push`
- `POST /leave-agent`
- `GET /yesterday-memo`

### ライセンス

- コード/ロジック: MIT
- アセット: 非商用のみ

---

## 中文

### 项目简介

Star Office UI 是一个多 Agent 协作的像素办公室状态看板。

- 主状态: `idle`, `writing`, `researching`, `executing`, `syncing`, `error`
- 支持访客 Agent 加入/退出
- 昨日备忘展示
- 支持移动端访问
- UI 语言切换（`EN / JA / ZH`）

### 快速开始

```bash
git clone https://github.com/ringhyacinth/Star-Office-UI.git
cd Star-Office-UI
python3 -m pip install -r backend/requirements.txt
cp state.sample.json state.json
cd backend
python3 app.py
```

打开: `http://127.0.0.1:18791`

### 切换主 Agent 状态

```bash
cd /path/to/Star-Office-UI
python3 set_state.py writing "正在整理文档"
python3 set_state.py syncing "同步进度中"
python3 set_state.py error "发现问题，排查中"
python3 set_state.py idle "待命中"
```

### 常用 API

- `GET /health`
- `GET /status`
- `POST /set_state`
- `GET /agents`
- `POST /join-agent`
- `POST /agent-push`
- `POST /leave-agent`
- `GET /yesterday-memo`

### 许可证

- 代码/逻辑: MIT
- 美术资源: 仅限非商用
