#!/usr/bin/env python3
"""Star Office UI - 10 Agents + 实时日志（对接 OpenClaw）"""

from flask import Flask, jsonify, send_from_directory, request, Response
from datetime import datetime, timezone
import json, os, glob, re, urllib.request, urllib.error

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")
STATE_FILE = os.path.join(ROOT_DIR, "state.json")
OPENCLAW_DIR = os.path.expanduser("~/.openclaw")
OPENCLAW_CONFIG = os.path.join(OPENCLAW_DIR, "openclaw.json")
NEWS_FILE = os.path.join(ROOT_DIR, "news.json")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="/static")

# ============ 模型提供商健康检查 + 模型 Ping ============
import threading, time as _time
_news_lock = threading.Lock()

_provider_health = {}       # provider_id -> {"online": bool, "last_check": float, "error": str}
_model_health = {}          # "provider/model_id" -> {"online": bool, "last_check": float, "error": str, "latency_ms": int}
_provider_health_lock = threading.Lock()
_HEALTH_CHECK_INTERVAL = 30   # provider 探测间隔
_MODEL_PING_INTERVAL = 60     # 模型 ping 间隔（秒）

def _load_providers():
    """从 openclaw.json 读取 provider 配置"""
    if not os.path.exists(OPENCLAW_CONFIG):
        return {}
    try:
        with open(OPENCLAW_CONFIG, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        return cfg.get("models", {}).get("providers", {})
    except Exception:
        return {}

def _load_agent_models():
    """从 openclaw.json 读取每个 agent 使用的模型"""
    if not os.path.exists(OPENCLAW_CONFIG):
        return {}
    try:
        with open(OPENCLAW_CONFIG, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        result = {}
        for a in cfg.get("agents", {}).get("list", []):
            aid = a.get("id", "")
            model = a.get("model", "")
            if aid and model:
                result[aid] = model
        return result
    except Exception:
        return {}

def _check_provider_health(provider_id, provider_cfg):
    """探测单个 provider 是否在线（发送轻量 models 列表请求）"""
    base_url = provider_cfg.get("baseUrl", "").rstrip("/")
    api_key = provider_cfg.get("apiKey", "")
    if not base_url:
        return False, "无 baseUrl"
    try:
        url = f"{base_url}/models"
        req = urllib.request.Request(url, method="GET")
        req.add_header("Authorization", f"Bearer {api_key}")
        req.add_header("Accept", "application/json")
        with urllib.request.urlopen(req, timeout=8) as resp:
            code = resp.getcode()
            if 200 <= code < 400:
                return True, ""
            return False, f"HTTP {code}"
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            return True, ""
        return False, f"HTTP {e.code}"
    except urllib.error.URLError as e:
        return False, str(e.reason)[:60]
    except Exception as e:
        return False, str(e)[:60]

def _ping_model(provider_cfg, model_id):
    """向模型发送极短的 completion 请求，测试推理层是否可用"""
    base_url = provider_cfg.get("baseUrl", "").rstrip("/")
    api_key = provider_cfg.get("apiKey", "")
    api_type = provider_cfg.get("api", "openai-completions")
    if not base_url:
        return False, "无 baseUrl", 0

    t0 = _time.time()
    try:
        # 根据 API 类型选择端点
        if "responses" in api_type:
            url = f"{base_url}/responses"
            body = json.dumps({
                "model": model_id,
                "input": "ping",
                "max_output_tokens": 1,
            }).encode("utf-8")
        else:
            url = f"{base_url}/chat/completions"
            body = json.dumps({
                "model": model_id,
                "messages": [{"role": "user", "content": "ping"}],
                "max_tokens": 1,
            }).encode("utf-8")

        req = urllib.request.Request(url, data=body, method="POST")
        req.add_header("Authorization", f"Bearer {api_key}")
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=15) as resp:
            latency = int((_time.time() - t0) * 1000)
            code = resp.getcode()
            if 200 <= code < 400:
                return True, "", latency
            return False, f"HTTP {code}", latency
    except urllib.error.HTTPError as e:
        latency = int((_time.time() - t0) * 1000)
        # 4xx 客户端错误 = 服务在线，只是请求有问题
        if 400 <= e.code < 500:
            return True, "", latency
        err_body = ""
        try:
            err_body = e.read().decode("utf-8", errors="replace")[:100]
        except Exception:
            pass
        short = f"HTTP {e.code}"
        if "502" in str(e.code):
            short = "502 Bad Gateway"
        elif "503" in str(e.code):
            short = "503 Service Unavailable"
        elif err_body:
            short = f"HTTP {e.code}: {err_body[:50]}"
        return False, short, latency
    except urllib.error.URLError as e:
        latency = int((_time.time() - t0) * 1000)
        return False, str(e.reason)[:60], latency
    except Exception as e:
        latency = int((_time.time() - t0) * 1000)
        return False, str(e)[:60], latency

def _health_check_loop():
    """后台线程：定期检查 provider + ping 各模型"""
    while True:
        try:
            providers = _load_providers()
            # 1) Provider 级别探测
            for pid, pcfg in providers.items():
                online, err = _check_provider_health(pid, pcfg)
                with _provider_health_lock:
                    _provider_health[pid] = {
                        "online": online,
                        "last_check": _time.time(),
                        "error": err,
                        "baseUrl": pcfg.get("baseUrl", ""),
                    }

            # 2) 模型级别 ping（收集所有在用的唯一 provider/model 组合）
            agent_models = _load_agent_models()
            pinged = set()
            for aid, model_str in agent_models.items():
                pid = model_str.split("/")[0] if "/" in model_str else ""
                mid = model_str.split("/", 1)[1] if "/" in model_str else model_str
                if not pid:
                    # 反查 provider
                    for ppid, pcfg in providers.items():
                        for m in pcfg.get("models", []):
                            if m.get("id") == mid or mid.startswith(m.get("id", "___")):
                                pid = ppid
                                break
                        if pid:
                            break
                if not pid or not mid:
                    continue
                key = f"{pid}/{mid}"
                if key in pinged:
                    continue
                pinged.add(key)
                pcfg = providers.get(pid, {})
                if not pcfg:
                    continue
                online, err, latency = _ping_model(pcfg, mid)
                with _provider_health_lock:
                    _model_health[key] = {
                        "online": online,
                        "last_check": _time.time(),
                        "error": err,
                        "latency_ms": latency,
                    }
        except Exception:
            pass
        _time.sleep(_MODEL_PING_INTERVAL)

# 启动后台健康检查线程
_health_thread = threading.Thread(target=_health_check_loop, daemon=True)
_health_thread.start()

def get_provider_for_model(model_str):
    """从 'provider/model-id' 格式中提取 provider 名，或通过配置反查"""
    if not isinstance(model_str, str):
        model_str = str(model_str) if model_str else ""
    if "/" in model_str:
        return model_str.split("/")[0]
    if not model_str:
        return ""
    providers = _load_providers()
    for pid, pcfg in providers.items():
        for m in pcfg.get("models", []):
            if m.get("id") == model_str or model_str.startswith(m.get("id", "___")):
                return pid
    return ""

def _resolve_model_key(model_str):
    """将模型字符串解析为 'provider/model_id' 格式"""
    if not isinstance(model_str, str):
        model_str = str(model_str) if model_str else ""
    if "/" in model_str:
        return model_str
    pid = get_provider_for_model(model_str)
    return f"{pid}/{model_str}" if pid else ""

def is_provider_online(provider_id):
    """检查 provider 是否在线"""
    with _provider_health_lock:
        info = _provider_health.get(provider_id)
    if not info:
        return True
    return info.get("online", True)

def is_model_online(model_str):
    """检查具体模型是否在线（基于 ping 结果）"""
    key = _resolve_model_key(model_str)
    if not key:
        return True  # 无法解析，默认在线
    with _provider_health_lock:
        info = _model_health.get(key)
    if not info:
        return True  # 未 ping 过，默认在线
    return info.get("online", True)

def get_model_error(model_str):
    """获取模型 ping 的错误信息"""
    key = _resolve_model_key(model_str)
    if not key:
        return ""
    with _provider_health_lock:
        info = _model_health.get(key)
    if not info:
        return ""
    return info.get("error", "")

def get_model_latency(model_str):
    """获取模型 ping 延迟"""
    key = _resolve_model_key(model_str)
    if not key:
        return 0
    with _provider_health_lock:
        info = _model_health.get(key)
    if not info:
        return 0
    return info.get("latency_ms", 0)

def get_provider_error(provider_id):
    """获取 provider 的错误信息"""
    with _provider_health_lock:
        info = _provider_health.get(provider_id)
    if not info:
        return ""
    return info.get("error", "")

VALID_STATES = ["idle", "writing", "researching", "executing", "syncing",
                "error", "dead", "reviewing", "testing", "deploying", "meeting"]

AGENT_DEFAULTS = {
    "main":  {"name": "宗主",     "emoji": "🗡️", "color": "#FFD700"},
    "task1": {"name": "拉磨驴",   "emoji": "🫏",  "color": "#8D6E63"},
    "task2": {"name": "上等马",   "emoji": "🐴",  "color": "#5C6BC0"},
    "task3": {"name": "看门狗",   "emoji": "🐕",  "color": "#FF7043"},
    "task4": {"name": "领头羊",   "emoji": "🐑",  "color": "#66BB6A"},
    "task5": {"name": "出头鸟",   "emoji": "🐦",  "color": "#42A5F5"},
    "task6": {"name": "铁公鸡",   "emoji": "🐔",  "color": "#FFA726"},
    "task7": {"name": "笑面虎",   "emoji": "🐯",  "color": "#EF5350"},
    "task8": {"name": "妙法天尊", "emoji": "🔮",  "color": "#AB47BC"},
    "task9":  {"name": "天地一子", "emoji": "⚡",  "color": "#26C6DA"},
    "task10": {"name": "探宝鼠",   "emoji": "🐭",  "color": "#8D6E63"},
    "task11": {"name": "知更鸟",   "emoji": "🐦‍⬛", "color": "#EC407A"},
    "task12": {"name": "涨停板",   "emoji": "📈",  "color": "#F44336"},
    "task13": {"name": "哲学猫",   "emoji": "🐱",  "color": "#7E57C2"},
    "task14": {"name": "旅行者",   "emoji": "🧳",  "color": "#26A69A"},
    "task15": {"name": "派蒙",     "emoji": "🎀",  "color": "#FF69B4"},
    "task16": {"name": "大根骑士", "emoji": "⚔️",  "color": "#4682B4"},
}

def _normalize_model(model_val):
    """将 model 字段统一为字符串（兼容 dict{primary,fallbacks} 和 str 两种格式）"""
    if isinstance(model_val, dict):
        return model_val.get("primary", "unknown")
    if isinstance(model_val, str):
        return model_val
    return "unknown"

def sync_from_openclaw():
    if not os.path.exists(OPENCLAW_CONFIG):
        return AGENT_DEFAULTS
    try:
        with open(OPENCLAW_CONFIG, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        agents = {}
        for a in cfg.get("agents", {}).get("list", []):
            aid = a.get("id", "")
            identity = a.get("identity", {})
            defaults = AGENT_DEFAULTS.get(aid, {"color": "#78909C"})
            agents[aid] = {
                "name": identity.get("name", aid),
                "emoji": identity.get("emoji", "🤖"),
                "color": defaults.get("color", "#78909C"),
                "model": _normalize_model(a.get("model", "unknown")),
            }
        return agents if agents else AGENT_DEFAULTS
    except Exception:
        return AGENT_DEFAULTS

def default_state():
    agents_info = sync_from_openclaw()
    agents = {}
    for aid, info in agents_info.items():
        agents[aid] = {
            "name": info["name"], "emoji": info["emoji"],
            "state": "idle", "detail": "等待任务中...",
            "color": info["color"],
            "model": info.get("model", "unknown"),
        }
    return {"agents": agents, "updated_at": datetime.now(timezone.utc).isoformat()}

def load_state():
    state = None
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
        except Exception:
            state = None
    if not isinstance(state, dict) or "agents" not in state:
        state = default_state()
    
    # 动态同步：检查OpenClaw配置中是否有新agent
    openclaw_agents = sync_from_openclaw()
    existing_agents = state.get("agents", {})
    
    # 添加新agent（保留现有agent的状态）
    for aid, info in openclaw_agents.items():
        if aid not in existing_agents:
            existing_agents[aid] = {
                "name": info["name"], 
                "emoji": info["emoji"],
                "state": "idle", 
                "detail": "等待任务中...",
                "color": info["color"],
                "model": info.get("model", "unknown"),
            }
    
    # 移除已删除的agent
    for aid in list(existing_agents.keys()):
        if aid not in openclaw_agents:
            del existing_agents[aid]
    
    state["agents"] = existing_agents
    return state

def save_state(state):
    state["updated_at"] = datetime.now().isoformat()
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

if not os.path.exists(STATE_FILE):
    save_state(default_state())

# ============ 日志读取 ============
def get_agent_latest_session(agent_id):
    """获取 agent 最新的活跃 session 文件"""
    session_dir = os.path.join(OPENCLAW_DIR, "agents", agent_id, "sessions")
    if not os.path.isdir(session_dir):
        return None
    files = glob.glob(os.path.join(session_dir, "*.jsonl"))
    files = [f for f in files if not f.endswith(".deleted")]
    if not files:
        return None
    return max(files, key=os.path.getmtime)

_BLOCK = "████"
_SYS_USER = os.environ.get("USER", "")

# 敏感信息正则列表
_SENSITIVE_PATTERNS = [
    # 文件路径中的用户名: /Users/xxx/ 或 /home/xxx/
    re.compile(r'(/(?:Users|home)/)([^/\s]+)(/?)'),
    # ~/ 开头的路径也遮掉用户目录标识
    re.compile(r'(?<!\w)(~/)'),
    # Telegram Bot Token: 数字:AAxxxx
    re.compile(r'\b\d{8,12}:[A-Za-z0-9_-]{30,50}\b'),
    # 通用 API Key / Secret (长随机串)
    re.compile(r'(?i)(?:api[_-]?key|api[_-]?secret|secret[_-]?key|access[_-]?key|auth[_-]?token|bearer)\s*[:=]\s*["\']?([A-Za-z0-9_\-/.+]{16,})["\']?'),
    # password / passwd / pwd = xxx
    re.compile(r'(?i)(?:password|passwd|pwd)\s*[:=]\s*["\']?(\S{4,})["\']?'),
    # token = "xxx" 或 token: "xxx"
    re.compile(r'(?i)(?:token|secret|credential)\s*[:=]\s*["\']([^"\']{8,})["\']'),
    # Bearer token in headers
    re.compile(r'(?i)Bearer\s+[A-Za-z0-9_\-/.+=]{16,}'),
    # 飞书 app secret / app_token 长串
    re.compile(r'(?i)(?:app[_-]?secret|app[_-]?id|cli_[a-z0-9]{12,})'),
    re.compile(r'[A-Za-z0-9_\-]{32,}'),  # 32+字符的连续字母数字串(大概率是密钥/hash)
    # 邮箱
    re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}'),
    # IP:Port 带端口的内网地址
    re.compile(r'\b(?:10|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.\d{1,3}\.\d{1,3}:\d{2,5}\b'),
    # Telegram 群组ID (负数长ID)
    re.compile(r'-\d{10,14}'),
    # Telegram/通用 数字ID字段: sender_id, chat_id, user_id, from_id, message_id, sender 等
    re.compile(r'(?i)(?:sender_id|chat_id|user_id|from_id|message_id|requester|sender)["\s:]+["\s]*(\d{5,})'),
    # Telegram bot username @xxx_bot
    re.compile(r'@[A-Za-z0-9_]{3,}_bot\b'),
]

def mask_sensitive(text):
    """将文本中的敏感信息替换为黑色方块"""
    if not text:
        return text
    for pat in _SENSITIVE_PATTERNS:
        # 路径用户名: /Users/xxx/ → /Users/████/
        if pat.pattern.startswith('(/(?:Users'):
            text = pat.sub(lambda m: m.group(1) + _BLOCK + (m.group(3) or ''), text)
        # ~/ → ████/
        elif pat.pattern.startswith('(?<!'):
            text = pat.sub(_BLOCK + '/', text)
        elif pat.groups:
            def _repl(m):
                s = m.start(1) - m.start(0)
                e = m.end(0) - m.end(1)
                return m.group(0)[:s] + _BLOCK + m.group(0)[len(m.group(0))-e:]
            text = pat.sub(_repl, text)
        else:
            text = pat.sub(_BLOCK, text)
    # 最后: 遮掉系统用户名(ls -la 输出等场景)
    if _SYS_USER and len(_SYS_USER) >= 3:
        text = text.replace(_SYS_USER, _BLOCK)
    return text

def parse_log_entry(line):
    """解析一行 JSONL 日志，返回简化的日志条目"""
    try:
        d = json.loads(line.strip())
    except Exception:
        return None

    def _as_str(v):
        if v is None:
            return ""
        if isinstance(v, str):
            return v
        if isinstance(v, (int, float, bool)):
            return str(v)
        return ""

    def _normalize_role(v):
        role_val = _as_str(v)
        if role_val in ("tool_result", "tool"):
            return "toolResult"
        return role_val

    def _normalize_stop(v):
        stop_val = _as_str(v)
        stop_map = {
            "tool_use": "toolUse",
            "end_turn": "stop",
            "completed": "stop",
        }
        return stop_map.get(stop_val, stop_val)

    def _to_channel(v):
        return _as_str(v).strip().lower()

    entry_type = _as_str(d.get("type"))
    ts = _as_str(d.get("timestamp"))
    raw_msg = d.get("message")
    msg = raw_msg if isinstance(raw_msg, dict) else {}
    provenance = msg.get("provenance") if isinstance(msg.get("provenance"), dict) else {}

    role = _normalize_role(msg.get("role") or d.get("role"))
    model = _as_str(msg.get("model") or msg.get("modelId") or d.get("model"))
    stop_reason = _normalize_stop(msg.get("stopReason") or msg.get("stop_reason"))
    error_msg = _as_str(msg.get("errorMessage") or msg.get("error_message") or d.get("error"))

    # 来源字段（优先用结构化字段）
    source_kind = _as_str(provenance.get("kind") or msg.get("kind") or d.get("kind")).strip().lower()
    source_channel = _to_channel(
        provenance.get("sourceChannel") or provenance.get("channel") or provenance.get("source")
        or msg.get("sourceChannel") or msg.get("channel") or msg.get("source")
        or d.get("sourceChannel") or d.get("channel") or d.get("source")
    )
    source_tool = _as_str(provenance.get("sourceTool") or msg.get("sourceTool") or d.get("sourceTool")).strip().lower()
    source_session = _as_str(provenance.get("sourceSessionKey") or msg.get("sourceSessionKey") or d.get("sourceSessionKey"))

    # 提取文本内容
    text = ""
    text_full = ""
    tool_name = ""
    raw_content = msg.get("content", [])
    if raw_content is None:
        content_items = []
    elif isinstance(raw_content, list):
        content_items = raw_content
    else:
        content_items = [raw_content]

    for c in content_items:
        piece = ""
        if isinstance(c, dict):
            ct = _as_str(c.get("type"))
            if ct in ("text", "input_text", "output_text"):
                piece = _as_str(c.get("text") or c.get("content") or c.get("output_text"))
            elif ct == "tool_use":
                tool_name = _as_str(c.get("name")) or "?"
                piece = f"调用工具: {tool_name}"
            elif ct in ("tool_result", "toolResult"):
                piece = _as_str(c.get("text")) or "工具返回结果"
            elif ct == "thinking":
                t = _as_str(c.get("thinking"))
                if t and len(t) > 5:
                    piece = f"💭 {t[:150]}"
        elif isinstance(c, str):
            piece = c
        elif c is not None:
            piece = _as_str(c)

        if piece and not text_full:
            text_full = piece
        if piece and not text:
            text = piece[:200]

    if not text_full:
        fallback = _as_str(msg.get("text") or msg.get("contentText") or d.get("text"))
        if fallback:
            text_full = fallback
            text = fallback[:200]

    if not text and error_msg:
        text = f"❌ {error_msg}"
        if not text_full:
            text_full = text

    # 从包装文本里的 metadata JSON 提取来源字段（兼容旧日志）
    queued_wrapper = False
    has_conversation_metadata = False
    if text_full:
        low_full = text_full.lower()
        queued_wrapper = low_full.startswith("[queued messages while agent was busy]")
        has_conversation_metadata = "conversation info (untrusted metadata):" in low_full

        if not source_channel and has_conversation_metadata:
            pattern = re.compile(
                r"conversation info \(untrusted metadata\):\s*```json\s*(\{.*?\})\s*```",
                flags=re.I | re.S,
            )
            for m in pattern.finditer(text_full):
                try:
                    meta = json.loads(m.group(1))
                except Exception:
                    continue
                if not isinstance(meta, dict):
                    continue
                for key in ("sourceChannel", "channel", "source", "conversation_label", "platform", "origin"):
                    raw_val = meta.get(key)
                    val = _to_channel(raw_val)
                    if not val:
                        continue
                    if "telegram" in val or val in ("tg", "channels/telegram", "channels.telegram"):
                        source_channel = "telegram"
                        break
                if source_channel:
                    break

    if entry_type == "compaction":
        text = "📦 上下文压缩"
        role = "system"

    if not text and not role:
        return None

    # 推断状态
    inferred_state = None
    death_reason = ""
    if role == "assistant" and stop_reason == "toolUse":
        inferred_state = "executing"
    elif role == "assistant" and stop_reason == "stop":
        inferred_state = "idle"  # 正常结束 = 空闲
    elif role == "assistant" and stop_reason == "error":
        inferred_state = "error"
        # 提取死亡原因
        if error_msg:
            death_reason = error_msg[:80]
        elif text and text.startswith("❌"):
            death_reason = text[2:].strip()[:80]
    elif role == "user":
        inferred_state = "researching"
    elif role == "toolResult":
        inferred_state = "executing"  # 工具返回结果 = 正在执行中
    elif entry_type == "compaction":
        inferred_state = "syncing"

    return {
        "ts": ts[:24] if ts else "",
        "type": entry_type,
        "role": role,
        "model": model,
        "stop": stop_reason,
        "text": mask_sensitive(text.replace("\n", " ").strip()[:200]),
        "tool": tool_name,
        "inferred_state": inferred_state,
        "death_reason": mask_sensitive(death_reason) if death_reason else "",
        "source_kind": source_kind,
        "source_channel": source_channel,
        "source_tool": source_tool,
        "source_session": source_session,
        "queued_wrapper": queued_wrapper,
        "has_conversation_metadata": has_conversation_metadata,
    }


def _is_owner_telegram_user_entry(entry):
    """仅隐藏来自 Telegram 的 user 包装消息；避免误伤 inter_session/assistant/tool。"""
    if not isinstance(entry, dict):
        return False
    if entry.get("role") != "user":
        return False

    source_kind = str(entry.get("source_kind") or "").strip().lower()
    source_channel = str(entry.get("source_channel") or "").strip().lower()
    source_tool = str(entry.get("source_tool") or "").strip().lower()

    # 明确不是 Telegram 用户输入：直接放行
    if source_kind == "inter_session" or source_tool == "sessions_send":
        return False

    # 优先按来源字段判定
    is_tg_source = (
        source_channel == "telegram"
        or "telegram" in source_channel
        or source_channel in ("tg", "channels/telegram", "channels.telegram")
    )
    if is_tg_source:
        return bool(entry.get("has_conversation_metadata") or entry.get("queued_wrapper"))

    # 兼容历史日志：来源字段缺失，但仍保留 Telegram 固定包装外形
    if not source_channel and not source_kind:
        text = (entry.get("text") or "").strip().lower()
        if text.startswith("conversation info (untrusted metadata):"):
            return True
        if text.startswith("[queued messages while agent was busy]") and "conversation info (untrusted metadata):" in text:
            return True

    return False


def read_agent_logs(agent_id, n=8):
    """读取 agent 最近 n 条有意义的日志"""
    session_file = get_agent_latest_session(agent_id)
    if not session_file:
        return []

    # 读最后 50 行，过滤出有意义的
    try:
        with open(session_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        lines = lines[-50:]
    except Exception:
        return []

    # 非宗主 agent: 只保留实际工作日志，过滤掉 TG 群聊对话
    _tg_block = (
        "Conversation info", "untrusted metadata", "telegram:",
        "message_id", "sender_id", "conversation_label",
        "group chat", "群聊", "BotFather", "/setprivacy",
        "chat_id", "openclaw message send", "channels/telegram",
        "channels.telegram", "groupPolicy",
    )
    # 群聊寒暄/自我介绍/等指令 的特征词
    _chat_block = (
        "大家好", "我在呢", "你喊", "你想让我", "你现在想",
        "给我一句话", "直接丢", "直接告诉我", "你这会儿",
        "先在这儿站岗", "先确认下", "把需求", "丢过来",
        "弟子", "到！", "到。", "已启动",
        "你发我", "发一下就行", "把下面任意一个",
        "帮你做哪件事", "帮你做什么", "让我做什么",
        "让我干啥", "让我帮你", "想让我现在",
        "陪聊", "查点资料", "设提醒", "设个提醒",
        "reply_to_current", "NO_REPLY",
        "把手头的事拆成", "偏好的输出形式",
        "越具体越好", "一句话目标",
        "主要能干", "打杂助理", "群里的", "在这儿。",
        "催介绍", "随便按这个格式", "各位随便",
        "我叫", "机器人。", "到位。", "谁点名",
        "啥事儿安排", "点名了",
    )

    entries = []
    for line in lines:
        entry = parse_log_entry(line)
        if entry and entry["text"]:
            # 对主界面日志统一隐藏“掌门人 Telegram 输入包装消息”
            if _is_owner_telegram_user_entry(entry):
                continue

            if agent_id != "main":
                text = entry["text"]
                # user 角色全部过滤(TG 传入)
                if entry["role"] == "user":
                    continue
                low = text.lower()
                # TG 关键词
                if any(kw.lower() in low for kw in _tg_block):
                    continue
                # 群聊寒暄
                if entry["role"] == "assistant" and any(kw in text for kw in _chat_block):
                    continue
            entries.append(entry)

    return entries[-n:]

# ============ 路由 ============
@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/status")
def get_status():
    return jsonify(load_state())

@app.route("/logs")
def get_all_logs():
    """获取所有 agent 的最新日志"""
    n = request.args.get("n", 5, type=int)
    n = min(n, 20)
    result = {}
    agents_info = sync_from_openclaw()
    for aid in agents_info:
        result[aid] = read_agent_logs(aid, n)
    return jsonify(result)

@app.route("/logs/<agent_id>")
def get_agent_log(agent_id):
    """获取单个 agent 的日志"""
    n = request.args.get("n", 10, type=int)
    return jsonify(read_agent_logs(agent_id, min(n, 30)))

@app.route("/live")
def live_status():
    """综合状态 + 日志，一次请求拿全"""
    state = load_state()
    logs = {}
    agents_info = sync_from_openclaw()

    for aid in agents_info:
        agent_logs = read_agent_logs(aid, 8)
        logs[aid] = agent_logs

        # 从日志中提取实际使用的模型名（取最新的 assistant 消息的 model）
        actual_model = ""
        for log in reversed(agent_logs):
            if log.get("role") == "assistant" and log.get("model"):
                actual_model = log["model"]
                break

        # 根据最新日志自动推断状态
        inferred = None
        ts = ""
        latest = None
        if agent_logs:
            latest = agent_logs[-1]
            inferred = latest.get("inferred_state")
            ts = latest.get("ts", "")

            # 时间衰减：如果最后日志超过5分钟
            if ts and inferred and inferred not in ("idle", "error"):
                try:
                    log_time = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    if log_time.tzinfo is None:
                        log_time = log_time.replace(tzinfo=timezone.utc)
                    now = datetime.now(timezone.utc)
                    age_seconds = (now - log_time).total_seconds()
                    if age_seconds > 300:  # 5分钟：工作状态衰减为idle
                        inferred = "idle"
                except Exception:
                    pass
            # error 状态超过10分钟 → 模型在线则降为idle，否则升级为dead
            if ts and inferred == "error":
                try:
                    log_time = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    if log_time.tzinfo is None:
                        log_time = log_time.replace(tzinfo=timezone.utc)
                    now = datetime.now(timezone.utc)
                    age_seconds = (now - log_time).total_seconds()
                    if age_seconds > 600:  # 10分钟
                        inferred = "idle"
                except Exception:
                    pass

        # 以下逻辑对所有 agent 执行（无论有无日志）
        if aid in state.get("agents", {}):
            agent = state["agents"][aid]
            # 用日志里的实际模型覆盖配置模型
            if actual_model:
                agent["model"] = actual_model

            # 检查模型是否在线（基于实际 ping 结果，用配置模型而非日志模型）
            model_str = agent.get("model", "")
            cfg_model = agents_info.get(aid, {}).get("model", "")
            check_model = cfg_model or model_str
            provider_id = get_provider_for_model(check_model)
            provider_offline = provider_id and not is_provider_online(provider_id)
            model_offline = not is_model_online(check_model)
            is_offline = model_offline or provider_offline
            if is_offline:
                offline_err = get_model_error(check_model) or get_provider_error(provider_id) or ""
            else:
                offline_err = ""

            # 提取死亡原因（从最近的 error 日志中）
            death_reason = ""
            for log in reversed(agent_logs):
                if log.get("death_reason"):
                    death_reason = log["death_reason"]
                    break
                if log.get("stop") == "error" and log.get("text"):
                    death_reason = log["text"][:80]
                    break

            # 模型离线 → 直接标记为 dead
            if is_offline:
                agent["state"] = "dead"
                short_model = check_model.split("/")[-1] if "/" in check_model else check_model
                agent["death_reason"] = f"模型不可用: {short_model} ({offline_err})" if offline_err else f"模型不可用: {short_model}"
                agent["detail"] = agent["death_reason"]
                agent["last_log_ts"] = ts if agent_logs else ""
            elif ts and latest:
                manual_ts = agent.get("updated_at", "")[:24]
                if ts[:19] > manual_ts[:19] and inferred:
                    agent["state"] = inferred
                    agent["death_reason"] = death_reason if inferred in ("error", "dead") else ""
                    text = latest.get("text", "")
                    if inferred == "idle" and agent.get("state") != "idle":
                        agent["detail"] = "等待任务中..."
                    elif inferred == "dead":
                        agent["detail"] = death_reason or "长时间无响应"
                    elif inferred == "error":
                        agent["detail"] = death_reason or text[:40]
                    elif len(text) > 40:
                        text = text[:37] + "..."
                        agent["detail"] = text
                    else:
                        agent["detail"] = text
                    agent["last_log_ts"] = ts

    # 附加 provider 健康状态
    provider_status = {}
    with _provider_health_lock:
        for pid, info in _provider_health.items():
            provider_status[pid] = {
                "online": info.get("online", False),
                "error": info.get("error", ""),
            }

    return jsonify({"state": state, "logs": logs, "providers": provider_status})

@app.route("/status/<agent_id>", methods=["POST"])
def update_agent(agent_id):
    data = request.get_json(force=True)
    state = load_state()
    if agent_id not in state.get("agents", {}):
        return jsonify({"error": f"Agent {agent_id} not found"}), 404
    new_s = data.get("state", "idle")
    if new_s not in VALID_STATES:
        return jsonify({"error": "Invalid state"}), 400
    agent = state["agents"][agent_id]
    agent["state"] = new_s
    agent["detail"] = data.get("detail", agent.get("detail", ""))
    agent["updated_at"] = datetime.now(timezone.utc).isoformat()
    save_state(state)
    return jsonify({"ok": True, "agent": agent})

@app.route("/status/batch", methods=["POST"])
def batch_update():
    data = request.get_json(force=True)
    state = load_state()
    updated = []
    now = datetime.now(timezone.utc).isoformat()
    for agent_id, updates in data.items():
        if agent_id in state.get("agents", {}):
            agent = state["agents"][agent_id]
            if "state" in updates and updates["state"] in VALID_STATES:
                agent["state"] = updates["state"]
            if "detail" in updates:
                agent["detail"] = updates["detail"]
            agent["updated_at"] = now
            updated.append(agent_id)
    save_state(state)
    return jsonify({"ok": True, "updated": updated})

@app.route("/health")
def health():
    return jsonify({"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()})

@app.route("/providers")
def providers_status():
    """返回模型提供商健康状态"""
    with _provider_health_lock:
        result = {}
        for pid, info in _provider_health.items():
            result[pid] = {
                "online": info.get("online", False),
                "error": info.get("error", ""),
                "baseUrl": info.get("baseUrl", ""),
                "last_check": datetime.fromtimestamp(info.get("last_check", 0)).isoformat() if info.get("last_check") else "",
            }
    return jsonify(result)

# ============ 飞书多维表格 API ============
try:
    from feishu import add_task, update_task, complete_task, get_all_tasks, find_task_by_id
    FEISHU_OK = True
except Exception:
    FEISHU_OK = False

@app.route("/tasks")
def tasks_list():
    if not FEISHU_OK:
        return jsonify({"error": "feishu module not available"}), 500
    try:
        tasks = get_all_tasks()
        return jsonify({"tasks": tasks})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/tasks", methods=["POST"])
def tasks_add():
    if not FEISHU_OK:
        return jsonify({"error": "feishu module not available"}), 500
    data = request.get_json(force=True)
    tid = data.get("task_id", f"task-{int(datetime.now().timestamp())}")
    result = add_task(
        tid, data.get("name", ""), data.get("agent", "main"),
        data.get("priority", "P1"), data.get("description", "")
    )
    return jsonify(result)

@app.route("/tasks/<record_id>", methods=["PUT"])
def tasks_update(record_id):
    if not FEISHU_OK:
        return jsonify({"error": "feishu module not available"}), 500
    data = request.get_json(force=True)
    result = update_task(record_id, data)
    return jsonify(result)

@app.route("/tasks/<record_id>/complete", methods=["POST"])
def tasks_complete(record_id):
    if not FEISHU_OK:
        return jsonify({"error": "feishu module not available"}), 500
    data = request.get_json(force=True) if request.data else {}
    result = complete_task(record_id, data.get("note", ""))
    return jsonify(result)

@app.route("/feishu-embed")
def feishu_embed():
    return jsonify({
        "url": "https://ycn7z9ux6s3s.feishu.cn/base/FJwkbkGtma2QS7sIjlScMXHWnrb",
        "app_token": "FJwkbkGtma2QS7sIjlScMXHWnrb",
        "table_id": "tblZwTpj2jzTkdWB"
    })

# ============ Ollama 本地模型状态 ============
OLLAMA_API = "http://localhost:11434"

@app.route("/ollama")
def ollama_status():
    """获取 Ollama 本地模型状态"""
    result = {"running": False, "models": [], "active": []}
    try:
        # 已安装模型
        req = urllib.request.Request(f"{OLLAMA_API}/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        result["running"] = True
        for m in data.get("models", []):
            result["models"].append({
                "name": m.get("name", ""),
                "size_mb": round(m.get("size", 0) / 1024 / 1024),
                "family": m.get("details", {}).get("family", ""),
                "params": m.get("details", {}).get("parameter_size", ""),
                "quant": m.get("details", {}).get("quantization_level", ""),
            })
        # 当前活跃模型
        req2 = urllib.request.Request(f"{OLLAMA_API}/api/ps", method="GET")
        with urllib.request.urlopen(req2, timeout=3) as resp2:
            ps_data = json.loads(resp2.read().decode("utf-8"))
        for m in ps_data.get("models", []):
            result["active"].append({
                "name": m.get("name", ""),
                "size_mb": round(m.get("size", 0) / 1024 / 1024),
                "expires": m.get("expires_at", ""),
            })
    except Exception:
        pass
    return jsonify(result)

# ============ Z-Image AI 绘图代理 ============
SILICONFLOW_API = "https://api.siliconflow.cn/v1/images/generations"

def _get_siliconflow_key():
    """从环境变量或 .env 文件读取 SiliconFlow API Key"""
    key = os.environ.get("SILICONFLOW_API_KEY", "")
    if key:
        return key
    env_file = os.path.join(ROOT_DIR, ".env")
    if os.path.exists(env_file):
        try:
            with open(env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("SILICONFLOW_API_KEY="):
                        return line.split("=", 1)[1].strip().strip("'\"")
        except Exception:
            pass
    return ""

@app.route("/api/zimage", methods=["POST"])
def zimage_generate():
    """代理 SiliconFlow Z-Image API，避免前端 CORS 问题"""
    api_key = _get_siliconflow_key()
    if not api_key:
        return jsonify({"error": "未配置 SILICONFLOW_API_KEY，请在 star-office-ui/.env 中添加 SILICONFLOW_API_KEY=sk-xxx"}), 500
    data = request.get_json(force=True)
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "prompt 不能为空"}), 400

    payload = json.dumps({
        "model": "Kwai-Kolors/Kolors",
        "prompt": prompt,
        "image_size": data.get("image_size", "1024x1024"),
        "num_inference_steps": data.get("steps", 25),
    }).encode("utf-8")

    req = urllib.request.Request(
        SILICONFLOW_API,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        return jsonify(result)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return jsonify({"error": f"API 错误 {e.code}", "detail": body}), e.code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============ 情报站 (News) ============
def _load_news():
    if os.path.exists(NEWS_FILE):
        with open(NEWS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def _save_news(items):
    with open(NEWS_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

@app.route("/news")
def news_list():
    """获取情报列表，支持 ?tag=xxx 过滤"""
    tag = request.args.get("tag", "").strip()
    with _news_lock:
        items = _load_news()
    if tag:
        items = [i for i in items if tag in i.get("tags", [])]
    # 按时间倒序
    items.sort(key=lambda x: x.get("ts", ""), reverse=True)
    return jsonify({"news": items, "total": len(items)})

@app.route("/news", methods=["POST"])
def news_add():
    """Bot 提交情报 — POST {title, summary, source, url, tags[], agent}"""
    data = request.get_json(force=True)
    title = data.get("title", "").strip()
    if not title:
        return jsonify({"error": "title required"}), 400
    item = {
        "id": f"news-{int(_time.time()*1000)}",
        "title": title,
        "summary": data.get("summary", ""),
        "source": data.get("source", ""),
        "url": data.get("url", ""),
        "tags": data.get("tags", []),
        "agent": data.get("agent", ""),
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    with _news_lock:
        items = _load_news()
        items.insert(0, item)
        # 最多保留 500 条
        if len(items) > 500:
            items = items[:500]
        _save_news(items)
    return jsonify({"ok": True, "item": item})

@app.route("/news/<news_id>", methods=["DELETE"])
def news_delete(news_id):
    """删除一条情报"""
    with _news_lock:
        items = _load_news()
        items = [i for i in items if i.get("id") != news_id]
        _save_news(items)
    return jsonify({"ok": True})

# ============ 情报自动抓取 ============
import xml.etree.ElementTree as _ET
import ssl as _ssl
_ssl_ctx = _ssl.create_default_context()

_NEWS_FETCH_INTERVAL = 600  # 10分钟抓一次

# RSS 源配置: (名称, URL, 标签列表, 最大条数)
_RSS_FEEDS = [
    ("IT之家",     "https://www.ithome.com/rss/",                          ["科技"],         15),
    ("虎嗅",       "https://www.huxiu.com/rss/0.xml",                      ["科技"],         10),
    ("少数派",     "https://sspai.com/feed",                                ["科技"],         10),
    ("V2EX",       "https://www.v2ex.com/index.xml",                       ["科技"],         10),
    ("TechCrunch", "https://techcrunch.com/feed/",                         ["科技", "AI"],   10),
    ("CoinDesk",   "https://www.coindesk.com/arc/outboundfeeds/rss/",      ["加密", "金融"], 10),
    ("BBC中文",    "https://feeds.bbci.co.uk/zhongwen/simp/rss.xml",       ["新闻"],         10),
]

def _fetch_rss(name, url, tags, max_items):
    """抓取单个 RSS 源，返回 news item 列表"""
    items = []
    try:
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)")
        with urllib.request.urlopen(req, timeout=10, context=_ssl_ctx) as resp:
            raw = resp.read()
        root = _ET.fromstring(raw)
        # RSS 2.0
        entries = root.findall(".//item")
        if not entries:
            # Atom
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            entries = root.findall(".//atom:entry", ns)
        for entry in entries[:max_items]:
            title_el = entry.find("title")
            if title_el is None:
                title_el = entry.find("{http://www.w3.org/2005/Atom}title")
            title = (title_el.text or "").strip() if title_el is not None else ""
            if not title:
                continue
            # 链接
            link_el = entry.find("link")
            if link_el is None:
                link_el = entry.find("{http://www.w3.org/2005/Atom}link")
            link = ""
            if link_el is not None:
                link = link_el.text or link_el.get("href", "")
            # 摘要
            desc_el = entry.find("description")
            if desc_el is None:
                desc_el = entry.find("{http://www.w3.org/2005/Atom}summary")
            desc = ""
            if desc_el is not None and desc_el.text:
                # 去 HTML 标签
                desc = re.sub(r"<[^>]+>", "", desc_el.text).strip()[:150]
            items.append({
                "title": title[:100],
                "summary": desc,
                "source": name,
                "url": link.strip(),
                "tags": tags,
            })
    except Exception:
        pass
    return items

def _fetch_hn_top(n=10):
    """抓取 Hacker News 热门"""
    items = []
    try:
        req = urllib.request.Request("https://hacker-news.firebaseio.com/v0/topstories.json")
        with urllib.request.urlopen(req, timeout=8, context=_ssl_ctx) as resp:
            ids = json.loads(resp.read().decode("utf-8"))[:n]
        for sid in ids:
            req2 = urllib.request.Request(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json")
            with urllib.request.urlopen(req2, timeout=5, context=_ssl_ctx) as resp2:
                story = json.loads(resp2.read().decode("utf-8"))
            title = story.get("title", "")
            if not title:
                continue
            items.append({
                "title": title[:100],
                "summary": f"Score: {story.get('score',0)} | Comments: {story.get('descendants',0)}",
                "source": "Hacker News",
                "url": story.get("url", f"https://news.ycombinator.com/item?id={sid}"),
                "tags": ["科技"],
            })
    except Exception:
        pass
    return items

def _news_fetch_loop():
    """后台线程：定期从 RSS 源抓取新闻"""
    _time.sleep(5)  # 启动延迟
    while True:
        try:
            all_new = []
            # RSS 源
            for name, url, tags, max_items in _RSS_FEEDS:
                all_new.extend(_fetch_rss(name, url, tags, max_items))
            # Hacker News
            all_new.extend(_fetch_hn_top(8))

            if all_new:
                with _news_lock:
                    existing = _load_news()
                    # 用 title+source 去重
                    existing_keys = {(i.get("title",""), i.get("source","")) for i in existing}
                    added = 0
                    now = datetime.now(timezone.utc).isoformat()
                    for item in all_new:
                        key = (item["title"], item["source"])
                        if key not in existing_keys:
                            item["id"] = f"news-{int(_time.time()*1000)}-{added}"
                            item["agent"] = "🤖自动抓取"
                            item["ts"] = now
                            existing.insert(0, item)
                            existing_keys.add(key)
                            added += 1
                    # 保留最新 500 条
                    if len(existing) > 500:
                        existing = existing[:500]
                    if added > 0:
                        _save_news(existing)
        except Exception:
            pass
        _time.sleep(_NEWS_FETCH_INTERVAL)

_news_thread = threading.Thread(target=_news_fetch_loop, daemon=True)
_news_thread.start()

if __name__ == "__main__":
    print("🏢 AI 特工队总部")
    print(f"   State: {STATE_FILE}")
    print(f"   OpenClaw: {OPENCLAW_DIR}")
    print("   http://127.0.0.1:19800")
    app.run(host="0.0.0.0", port=19800, debug=False)
