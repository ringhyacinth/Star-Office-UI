# Star Office UI — 开源发布准备清单（仅准备，不上传）

## 0. 当前目标
- 本文档用于“发布前准备”，不执行实际上传。
- 所有 push 行为需海辛最终明确批准。

## 1. 隐私与安全审查结果（当前仓库）

### 发现高风险文件（必须排除）
- 运行日志：
  - `cloudflared.out`
  - `cloudflared-named.out`
  - `cloudflared-quick.out`
  - `healthcheck.log`
  - `backend.log`
  - `backend/backend.out`
- 运行状态：
  - `state.json`
  - `agents-state.json`
  - `backend/backend.pid`
- 备份/历史文件：
  - `index.html.backup.*`
  - `index.html.original`
  - `*.backup*` 目录与文件
- 本地虚拟环境与缓存：
  - `.venv/`
  - `__pycache__/`

### 发现潜在敏感内容
- 代码内含绝对路径 `/root/...`（建议改为相对路径或环境变量）
- 文档与脚本含私有域名 `office.example.com`（可保留为示例，但建议改成占位域名）

## 2. 必改项（提交前）

### A. .gitignore（需补齐）
建议新增：
```
*.log
*.out
*.pid
state.json
agents-state.json
join-keys.json
*.backup*
*.original
__pycache__/
.venv/
venv/
```

### B. README 版权声明（必须新增）
新增“美术资产版权与使用限制”章节：
- 代码按开源协议（如 MIT）
- 美术素材归原作者/工作室所有
- 素材仅供学习/演示，**禁止商用**

### C. 发布目录瘦身
- 清理运行日志、运行态文件、备份文件
- 仅保留“可运行最小集 + 必要素材 + 文档”

## 3. 准备中的发布包建议结构
```
star-office-ui/
  backend/
    app.py
    requirements.txt
    run.sh
  frontend/
    index.html
    game.js (若仍需要)
    layout.js
    assets/* (仅可公开素材)
  office-agent-push.py
  set_state.py
  state.sample.json
  README.md
  LICENSE
  SKILL.md
  docs/
```

## 4. 发布前最终核对（给海辛确认）
- [ ] 是否保留私有域名示例（`office.example.com`）
- [ ] 哪些美术资源允许公开（逐项确认）
- [ ] README 非商用声明是否满足你的预期措辞
- [ ] 是否需要将“阿文龙虾联调脚本”单独放 examples 目录

## 5. 当前状态
- ✅ 文档准备完成（总结、功能说明、Skill v2、发布检查清单）
- ⏳ 等待海辛确认“公开素材范围 + 声明文案 + 是否开始执行打包清理脚本”
- ⛔ 尚未执行 GitHub 上传
