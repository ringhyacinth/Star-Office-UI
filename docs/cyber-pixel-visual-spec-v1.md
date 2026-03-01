# 赛博像素办公街区 · V1 视觉规范（草案）

- 版本：V1.0
- 状态：Draft（可直接用于前端落地）
- 适用范围：`star-office-ui`（Phaser 场景 + Web UI 面板）

---

## 0. 设计目标

1. **一眼识别“赛博像素办公”**：暗色底 + 霓虹强调 + 像素化信息层。  
2. **高密度信息可读**：小字号场景下仍保持层级清晰。  
3. **状态可视优先**：完成 / 失败 / 忙碌状态在 300ms 内可被用户识别。  
4. **可 token 化**：颜色、字号、动效可统一命名并可扩展到多主题。

---

## 1) 色板规范（主色 / 强调 / 状态色）

> 以当前项目变量为基线（`--bg-primary / --accent / --green ...`），补齐语义层。

### 1.1 主色（基础界面）

| Token | HEX | 用途 |
|---|---|---|
| `color.bg.canvas` | `#0D0D18` | 全局背景（页面底色） |
| `color.bg.surface` | `#111120` | 侧栏/次级容器 |
| `color.bg.card` | `#161628` | 卡片、列表项背景 |
| `color.bg.hover` | `#1C1C35` | Hover 态背景 |
| `color.border.default` | `#2A2A3A` | 分割线 / 边框 |
| `color.text.primary` | `#FFFFFF` | 高优先文字 |
| `color.text.secondary` | `#CCCCCC` | 常规文字 |
| `color.text.tertiary` | `#666666` | 次要说明 / 时间戳 |

### 1.2 强调色（品牌与交互）

| Token | HEX | 用途 |
|---|---|---|
| `color.accent.primary` | `#E94560` | 主 CTA、激活态标签、关键数字 |
| `color.accent.secondary` | `#6C5CE7` | 二级重点、数据高亮 |
| `color.accent.info` | `#42A5F5` | 链接/信息类视觉锚点 |
| `color.accent.gold` | `#FFD700` | 指挥/荣誉类元素（头衔、勋章） |

### 1.3 状态色（系统语义）

| 状态 | Token | HEX | 建议语义 |
|---|---|---|---|
| 成功 | `color.state.success` | `#4CAF50` | 完成、在线、健康 |
| 警告 | `color.state.warning` | `#FFC107` | 等待、需关注 |
| 失败 | `color.state.error` | `#F44336` | 错误、中断、告警 |
| 进行中 | `color.state.processing` | `#42A5F5` | 执行中、计算中 |
| 同步中 | `color.state.syncing` | `#9C27B0` | 同步、队列调度 |
| 离线/阵亡 | `color.state.dead` | `#333333` | 不可用、终止 |

### 1.4 对比度与使用规则

- 深色背景上正文文字建议不低于 **4.5:1** 对比度。  
- 强调色只用于“可操作”或“需立即识别”元素，避免整屏泛滥。  
- 同一块 UI 中，**主强调色 ≤ 2 个**，防止视觉噪音。

---

## 2) 字体与字号体系

### 2.1 字体族

1. **UI 主字体（中文优先）**  
   `-apple-system, "PingFang SC", "Helvetica Neue", sans-serif`
2. **主题装饰字体（店招/卷轴标题）**  
   `"MedievalSharp", serif`（建议仅用于标题，不用于密集正文）
3. **数据等宽字体（日志/时间/技术字段）**  
   `"Courier New", monospace`

### 2.2 字号阶梯（V1）

| 级别 | Token | px | 行高建议 | 场景 |
|---|---|---:|---:|---|
| XS | `font.size.xs` | 9 | 1.4 | 辅助标记、badge、时间戳 |
| SM | `font.size.sm` | 10 | 1.4 | 次级说明、标签 |
| MD | `font.size.md` | 11 | 1.45 | 列表主体文字 |
| LG | `font.size.lg` | 12 | 1.5 | 分组标题、按钮文字 |
| XL | `font.size.xl` | 14 | 1.5 | 模块标题、重点信息 |
| 2XL | `font.size.2xl` | 16 | 1.4 | 页面区块标题 |
| 3XL | `font.size.3xl` | 20 | 1.2 | 核心指标数字 |
| 4XL | `font.size.4xl` | 24 | 1.2 | 超大数据看板数值 |

### 2.3 字重规则

- `400`：正文默认  
- `600`：列表主信息/标签  
- `700`：模块标题  
- `800`：关键统计数字

---

## 3) 场景分层规范（前景 / 中景 / 远景 / UI 层）

> 结合 Phaser depth + DOM 叠层统一约束。

### 3.1 分层定义

1. **远景层（Background）**  
   - 内容：办公室静态底图（墙体、地板、分区基建）  
   - 建议深度：`depth 0–9`

2. **中景层（World Mid）**  
   - 内容：Agent 主体、角色配件、地面互动对象  
   - 建议深度：`depth 10–49`

3. **前景层（World Foreground FX）**  
   - 内容：气泡、告警弹层、局部特效、死亡提示  
   - 建议深度：`depth 50–299`

4. **UI 层（HUD / Panels）**  
   - 内容：顶部导航、右侧仪表盘、卷轴任务、日志面板  
   - 建议层级：DOM `z-index >= 1000`（统一管理）

### 3.2 分层规则

- 同一层内仅做局部排序，跨层不临时“抢层级”。  
- 战斗/告警类特效只允许进入前景层，不覆盖全局 HUD。  
- UI 层动效默认“轻量化”，避免遮挡场景核心路径。

---

## 4) 部门店铺招牌风格规则

> 目标：把“部门”做成可识别店铺门头，支持街区漫游感。

### 4.1 招牌结构（统一骨架）

每个店招由 4 部分组成：

1. `SignFrame`：边框（像素金属/木纹）  
2. `SignPanel`：底板（部门主色 15%~25% 明度范围）  
3. `SignIcon`：部门图标（emoji 或像素 icon）  
4. `SignText`：部门名（最多 6 个中文字符，超出截断）

### 4.2 六部门视觉识别

| 部门 | 主色 | 辅色 | 图形语义 | 文案语气 |
|---|---|---|---|---|
| 情报室 info | `#42A5F5` | `#80CBC4` | 雷达/报刊/信号 | 快、准、广 |
| 开发区 dev | `#4CAF50` | `#8D6E63` | 芯片/代码/扳手 | 稳、快、可交付 |
| 测试区 test | `#26C6DA` | `#8BC34A` | 扫描/刻度/靶心 | 严谨、可验证 |
| 金融区 fin | `#FFA726` | `#F44336` | K 线/硬币/算盘 | 收益、风控 |
| 策划产品 plan | `#AB47BC` | `#6C5CE7` | 蓝图/便签/灯泡 | 洞察、方案 |
| 指挥中心 cmd | `#FFD700` | `#B8860B` | 王冠/徽章/中枢 | 决策、统筹 |

### 4.3 状态态样式（店招）

- `normal`：100% 不透明，细边框光晕  
- `active`：增加 1 层外发光（alpha 0.35）+ 微呼吸（2.4s）  
- `alert`：红橙闪烁（0.6s）+ 轻微抖动（仅失败态）  
- `offline`：饱和度降到 20%，亮度降到 65%

---

## 5) 动效规范（完成 / 失败 / 忙碌）

### 5.1 动效总原则

- 短反馈：**200–400ms**（按钮、轻提示）  
- 状态反馈：**600–1200ms**（完成/失败/忙碌）  
- 循环动效：需低侵扰（振幅小、透明度变化优先）

### 5.2 三大状态动效

#### A. 完成（Success）
- 触发：任务从“进行中”进入“已完成”  
- 视觉：绿色 `#4CAF50` 扫光 + 图标 `✅` 弹入  
- 时长：`650ms`  
- 曲线：`cubic-bezier(0.2, 0.8, 0.2, 1)`  
- 禁止：大幅缩放（>1.12）

#### B. 失败（Error）
- 触发：任务失败、agent error/dead  
- 视觉：红色 `#F44336` 快速闪烁 + 横向抖动（2~4px）  
- 时长：`420ms`（单次），最多重复 2 次  
- 曲线：`ease-out`  
- 补充：抖动后必须回到静止态，避免持续干扰

#### C. 忙碌（Busy / Processing）
- 触发：writing/researching/executing 等工作态  
- 视觉：蓝/绿呼吸光环 + 点状脉冲  
- 周期：`1.2s`（与现有 dot-working 保持一致）  
- 振幅：透明度 1 → 0.35 → 1

### 5.3 动效 token（建议）

- `motion.duration.fast = 180ms`
- `motion.duration.normal = 320ms`
- `motion.duration.state = 650ms`
- `motion.duration.loop = 1200ms`
- `motion.easing.emphasized = cubic-bezier(0.2, 0.8, 0.2, 1)`
- `motion.easing.standard = ease`

---

## 6) 设计 Token 命名建议

> 推荐采用「Core → Semantic → Component」三层结构，便于主题切换。

### 6.1 命名格式

- `color.{group}.{role}[.{state}]`
- `font.{type}.{scale}`
- `space.{scale}`
- `radius.{scale}`
- `motion.{type}.{name}`
- `z.{layer}.{name}`

### 6.2 示例（可直接落地）

```json
{
  "color": {
    "bg": {
      "canvas": "#0D0D18",
      "surface": "#111120",
      "card": "#161628"
    },
    "accent": {
      "primary": "#E94560",
      "secondary": "#6C5CE7"
    },
    "state": {
      "success": "#4CAF50",
      "warning": "#FFC107",
      "error": "#F44336",
      "processing": "#42A5F5",
      "dead": "#333333"
    }
  },
  "font": {
    "family": {
      "ui": "-apple-system, PingFang SC, Helvetica Neue, sans-serif",
      "display": "MedievalSharp, serif",
      "mono": "Courier New, monospace"
    },
    "size": {
      "xs": "9px",
      "sm": "10px",
      "md": "11px",
      "lg": "12px",
      "xl": "14px",
      "2xl": "16px",
      "3xl": "20px"
    }
  },
  "motion": {
    "duration": {
      "fast": "180ms",
      "normal": "320ms",
      "state": "650ms",
      "loop": "1200ms"
    }
  },
  "z": {
    "scene": {
      "bg": 0,
      "agent": 20,
      "fx": 120
    },
    "ui": {
      "hud": 1000,
      "modal": 1200,
      "toast": 1400
    }
  }
}
```

### 6.3 与当前代码变量映射建议

- `--bg-primary` → `color.bg.canvas`  
- `--bg-secondary` → `color.bg.surface`  
- `--bg-card` → `color.bg.card`  
- `--accent` → `color.accent.primary`  
- `--accent2` → `color.accent.secondary`  
- `--green / --yellow / --red / --blue` → `color.state.*`

---

## V1 验收清单（建议）

- [ ] 颜色 token 已替换硬编码（至少 80%）  
- [ ] 字号统一到 9/10/11/12/14/16/20 阶梯  
- [ ] Phaser depth 按四层规范整理  
- [ ] 六部门店招具备统一骨架 + 部门差异化  
- [ ] 完成/失败/忙碌动效参数统一并可复用  
- [ ] token 命名在 CSS + JS 常量中一致
