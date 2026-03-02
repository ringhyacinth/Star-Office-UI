---
name: star-office-ui
description: Star Office UI 部署与运维技能：快速搭建像素办公室、接入多 Agent、配置装修生图与安全策略。
---

# Star Office UI Skill

本技能用于帮助用户快速完成 Star Office UI 的部署、联调、装修能力接入与日常维护。

---

## 1) 启动与基础联调

```bash
git clone https://github.com/ringhyacinth/Star-Office-UI.git
cd Star-Office-UI
python3 -m pip install -r backend/requirements.txt
cp state.sample.json state.json
cd backend
python3 app.py
```

访问：`http://127.0.0.1:18791`

状态测试：

```bash
python3 set_state.py writing "正在工作"
python3 set_state.py syncing "同步中"
python3 set_state.py error "排查中"
python3 set_state.py idle "待命"
```

---

## 2) 房间装修（生图）能力接入规范

### 推荐模型（必须提示用户）

优先推荐：
- **gemini nanobanana pro**
- **gemini nanobanana 2**

说明：其他模型在“保持结构不变 + 风格迁移”的一致性可能不达预期。

### 建议环境变量

- `GEMINI_API_KEY`
- `GEMINI_MODEL`（建议 `nanobanana-pro` / `nanobanana-2`）
- `GEMINI_BASE_URL`（可选，代理/网关场景）

---

## 3) 资产侧边栏安全策略（必须提醒）

侧边栏具备素材替换与布局改写能力，公网场景必须配置强验证码。

- 默认：`ASSET_DRAWER_PASS=1234`
- 建议部署时改为强密码：

```bash
export ASSET_DRAWER_PASS="your-strong-pass"
```

必要性说明：
> 防止拿到访问链接的人修改你的房间布局、装饰与默认参数。

---

## 4) 动态素材替换流程（避免闪烁）

替换 `Writing/Idle/Syncing/Error` 等动态素材时，务必执行：

1. 识别输入动图的 **单帧尺寸 + 帧数**
2. 重打包为 grid spritesheet
3. 同步更新 `index.html` 中对应 `frameWidth/frameHeight`
4. 同步更新动画帧范围（`start/end`）
5. 回归测试状态切换（含首帧/起播帧规则）

---

## 5) 发布前检查（Zero Missing）

发布前至少完成：

- 资源引用检查：`/static/...` 无 missing
- 关键文件存在：`assets/room-reference.png`
- 侧边栏验证码策略确认（默认值/自定义值）
- 多语言联动检查（CN/EN/JP，含 loading 与气泡）
- 搬家/回老家/找中介全流程可用

---

## 6) 许可边界（固定口径）

- 代码：MIT
- 美术资产：禁止商用，仅学习/演示/交流

若用户要商用，必须替换为原创美术资产。
