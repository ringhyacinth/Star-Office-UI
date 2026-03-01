# Star Office UI「更有人味 / 游戏感」替代配色方案（不改布局）

> 目标：替换当前偏“AI 霓虹感”的视觉，保留现有结构与布局，仅通过颜色 Token 完成风格转向。  
> 适用文件：`frontend/index.html`（`:root` 与少量硬编码颜色处）

---

## 1) 三套主题方案

## A. 工业复古（推荐默认）
- 风格关键词：铁锈金属、工坊灯光、任务大厅
- 体验倾向：更“人味”，弱化赛博霓虹，保留沉浸式游戏质感

### 颜色定义
- **主色**：`#CD8455`（铜橙）
- **辅色**：`#7A9E7E`（苔绿）
- **状态色**：
  - Success `#72B36F`
  - Warning `#D8A351`
  - Danger `#D6766E`
  - Info `#5A87A1`
- **文本色**：
  - 主文本 `#E9DFCF`
  - 次文本 `#B7A892`
  - 高亮文本 `#FFF7EA`
- **背景层级**：
  - BG0 `#1A1714`
  - BG1 `#231F1A`
  - BG2 `#2B251E`
  - Surface1 `#312920`
  - Surface2 `#3A3025`
  - Border `#5A4734`

---

## B. 城市夜景（平衡款）
- 风格关键词：雨夜街道、暖窗灯、深蓝城市
- 体验倾向：现代但不“AI 冷感”，对数据看板友好

### 颜色定义
- **主色**：`#D07B55`（暖砖橙）
- **辅色**：`#6C8FBF`（雾蓝）
- **状态色**：
  - Success `#57B38A`
  - Warning `#E0B14A`
  - Danger `#D95D63`
  - Info `#4F8AC9`
- **文本色**：
  - 主文本 `#DCE5F2`
  - 次文本 `#9EACC2`
  - 高亮文本 `#F8FBFF`
- **背景层级**：
  - BG0 `#0E1117`
  - BG1 `#131A24`
  - BG2 `#1A2433`
  - Surface1 `#1D2838`
  - Surface2 `#243246`
  - Border `#34455D`

---

## C. 温暖像素（游戏感最强）
- 风格关键词：像素酒馆、木质 UI、轻奇幻
- 体验倾向：最有“游戏大厅”气质，亲和感强

### 颜色定义
- **主色**：`#CE7F52`（陶土橙）
- **辅色**：`#B790D6`（柔紫）
- **状态色**：
  - Success `#7DB06D`
  - Warning `#E5B45A`
  - Danger `#DE7E76`
  - Info `#6F94C6`
- **文本色**：
  - 主文本 `#F0E2CE`
  - 次文本 `#C7B49A`
  - 高亮文本 `#FFF6E8`
- **背景层级**：
  - BG0 `#2A1F1B`
  - BG1 `#332722`
  - BG2 `#3D2F28`
  - Surface1 `#46362D`
  - Surface2 `#524036`
  - Border `#6A5345`

---

## 2) 可读性对比（日志区 / 右侧面板 / 按钮）

> 对比值为 WCAG 对比度（越大越清晰）。正文建议 ≥ 4.5，辅助文本建议 ≥ 3。

| 主题 | 日志区 主文本 | 日志区 次文本 | 右侧面板 主文本 | 右侧面板 次文本 | 按钮默认文本 | 按钮激活文本 |
|---|---:|---:|---:|---:|---:|---:|
| 工业复古 | 13.08 | 7.42 | 12.35 | 7.00 | 10.65 | 11.59 |
| 城市夜景 | 14.00 | 7.74 | 12.71 | 7.02 | 10.50 | 11.69 |
| 温暖像素 | 11.83 | 7.48 | 10.41 | 6.58 | 8.45 | 10.24 |

### 说明
- 三套都满足日志区、右侧面板、按钮核心可读性要求。
- **城市夜景**对比度最高，适合长时间看数据。
- **工业复古**在保证对比度的同时，风格最“去 AI 化”。
- **温暖像素**风格最强，但在高亮色大面积使用时要注意不过度“发灰”。

---

## 3) 默认推荐：工业复古

### 推荐理由
1. **最能解决“太 AI 风格”问题**：从霓虹青紫切到铜橙 + 苔绿，更像“有人在用的系统”，不是“机器在发光”。
2. **与现有游戏元素兼容**：当前已有卷轴/中世纪元素，工业复古不会割裂，反而把“任务大厅”气氛串起来。
3. **可读性稳**：日志、右侧信息卡、按钮状态都高于可读性阈值。
4. **落地成本低**：主要替换 Token，布局和组件结构不用动。

---

## 4) 可直接替换的 CSS Token 建议

> 用法：直接替换 `frontend/index.html` 里现有 `:root` 的颜色 Token；再应用下面“补丁映射”以覆盖部分硬编码颜色。

### 4.1 推荐默认（工业复古）Token（可直接粘贴）

```css
:root {
  /* ===== Humanized Theme: Industrial Retro ===== */
  --theme-bg-0: #1A1714;
  --theme-bg-1: #231F1A;
  --theme-bg-2: #2B251E;
  --theme-surface-1: #312920;
  --theme-surface-2: #3A3025;
  --theme-border: #5A4734;

  --theme-accent: #CD8455;
  --theme-accent-2: #7A9E7E;

  --theme-success: #72B36F;
  --theme-warning: #D8A351;
  --theme-danger: #D6766E;
  --theme-info: #5A87A1;

  --theme-text-main: #E9DFCF;
  --theme-text-dim: #B7A892;
  --theme-text-bright: #FFF7EA;

  /* 区域语义色 */
  --log-bg: #1F1A16;
  --panel-bg: #251F1A;
  --btn-bg: #332A22;
  --btn-border: #5A4734;
  --btn-text: #D7C7B1;
  --btn-active-bg: #4A2E21;
  --btn-active-text: #FFF7EA;

  --log-user: #8FB5D8;
  --log-assistant: #8EBE8A;
  --log-tool: #D2A374;
  --log-error: #D6766E;
  --log-system: #B4A88D;

  /* 兼容旧变量（保留原工程逻辑） */
  --bg-primary: var(--theme-bg-0);
  --bg-secondary: var(--theme-bg-1);
  --bg-card: var(--theme-surface-1);
  --bg-hover: var(--theme-surface-2);
  --border: var(--theme-border);

  --accent: var(--theme-accent);
  --accent2: var(--theme-accent-2);

  --green: var(--theme-success);
  --yellow: var(--theme-warning);
  --red: var(--theme-danger);
  --blue: var(--theme-info);

  --text: var(--theme-text-main);
  --text-dim: var(--theme-text-dim);
  --text-bright: var(--theme-text-bright);
}
```

### 4.2 补丁映射（建议一并加上，确保“日志区/右侧/按钮”统一）

```css
/* 背景与顶部（减少霓虹感） */
body {
  background:
    radial-gradient(120% 140% at 0% 0%, rgba(205,132,85,0.12), transparent 48%),
    radial-gradient(100% 120% at 100% 100%, rgba(122,158,126,0.10), transparent 52%),
    linear-gradient(180deg, var(--theme-bg-2), var(--theme-bg-0));
}
#top-bar {
  background: linear-gradient(90deg, rgba(43,37,30,0.96), rgba(35,31,26,0.96));
  box-shadow: 0 2px 16px rgba(205,132,85,0.08), inset 0 -1px 0 rgba(122,158,126,0.12);
}

/* 日志区 */
#log-panel { background: var(--log-bg); }
.log-line { color: var(--text-dim); }
.log-line.r-user .lx { color: var(--log-user); }
.log-line.r-assistant .lx { color: var(--log-assistant); }
.log-line.r-tool .lx { color: var(--log-tool); }
.log-line.r-error .lx { color: var(--log-error); }
.log-line.r-system .lx { color: var(--log-system); }

/* 右侧面板 */
#office-right {
  background: var(--panel-bg);
  border-left: 1px solid var(--border);
}
.dash-header {
  background: rgba(58,48,37,0.72);
  border: 1px solid rgba(205,132,85,0.25);
}

/* 按钮 */
.log-action-btn,
.fx-toggle,
.log-chip {
  background: var(--btn-bg);
  border-color: var(--btn-border);
  color: var(--btn-text);
}
.log-action-btn.active,
.log-chip.active,
.fx-toggle:hover {
  background: var(--btn-active-bg);
  color: var(--btn-active-text);
  border-color: var(--accent);
}
```

---

## 5) 另外两套主题的 Token（便于快速切换）

> 只给核心变量，直接替换对应值即可。

### 城市夜景（核心 Token）
```css
--theme-bg-0:#0E1117; --theme-bg-1:#131A24; --theme-bg-2:#1A2433;
--theme-surface-1:#1D2838; --theme-surface-2:#243246; --theme-border:#34455D;
--theme-accent:#D07B55; --theme-accent-2:#6C8FBF;
--theme-success:#57B38A; --theme-warning:#E0B14A; --theme-danger:#D95D63; --theme-info:#4F8AC9;
--theme-text-main:#DCE5F2; --theme-text-dim:#9EACC2; --theme-text-bright:#F8FBFF;
--log-bg:#121823; --panel-bg:#182131; --btn-bg:#223044; --btn-active-bg:#4B2F24;
```

### 温暖像素（核心 Token）
```css
--theme-bg-0:#2A1F1B; --theme-bg-1:#332722; --theme-bg-2:#3D2F28;
--theme-surface-1:#46362D; --theme-surface-2:#524036; --theme-border:#6A5345;
--theme-accent:#CE7F52; --theme-accent-2:#B790D6;
--theme-success:#7DB06D; --theme-warning:#E5B45A; --theme-danger:#DE7E76; --theme-info:#6F94C6;
--theme-text-main:#F0E2CE; --theme-text-dim:#C7B49A; --theme-text-bright:#FFF6E8;
--log-bg:#2F241F; --panel-bg:#3A2D26; --btn-bg:#4B3A31; --btn-active-bg:#5B3127;
```

---

## 6) 落地顺序建议（10 分钟版本）
1. 替换 `:root` 为“工业复古”Token。
2. 加入“补丁映射”覆盖日志区/右侧面板/按钮硬编码颜色。
3. 本地检查 3 个重点场景：
   - 日志快速滚动时是否刺眼
   - 右侧卡片层级是否清晰
   - 按钮 hover/active 是否足够可辨识
4. 如需更现代一点，直接切到“城市夜景”核心 Token。
