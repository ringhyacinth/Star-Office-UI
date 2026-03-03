#!/usr/bin/env python3
"""Star Office UI - Backend State Service"""

from flask import Flask, jsonify, send_from_directory, make_response, request
from datetime import datetime, timedelta
import json
import os
import re
import threading
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGINS_DIR = os.path.join(ROOT_DIR, "backend", "plugins")
sys.path.insert(0, os.path.join(ROOT_DIR, "backend"))
from plugins import PluginManager

plugin_manager = None
MEMORY_DIR = os.path.join(os.path.dirname(ROOT_DIR), "memory")
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")
STATE_FILE = os.path.join(ROOT_DIR, "state.json")
AGENTS_STATE_FILE = os.path.join(ROOT_DIR, "agents-state.json")
JOIN_KEYS_FILE = os.path.join(ROOT_DIR, "join-keys.json")


def get_yesterday_date_str():
    """获取昨天的日期字符串 YYYY-MM-DD"""
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.strftime("%Y-%m-%d")


def sanitize_content(text):
    """清理内容，保护隐私"""
    import re

    # 移除 OpenID、User ID 等
    text = re.sub(r"ou_[a-f0-9]+", "[用户]", text)
    text = re.sub(r'user_id="[^"]+"', 'user_id="[隐藏]"', text)

    # 移除具体的人名（如果有的话）
    # 这里可以根据需要添加更多规则

    # 移除 IP 地址、路径等敏感信息
    text = re.sub(r'/root/[^"\s]+', "[路径]", text)
    text = re.sub(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", "[IP]", text)

    # 移除电话号码、邮箱等
    text = re.sub(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "[邮箱]", text)
    text = re.sub(r"1[3-9]\d{9}", "[手机号]", text)

    return text


def extract_memo_from_file(file_path):
    """从 memory 文件中提取适合展示的 memo 内容（睿智风格的总结）"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 提取真实内容，不做过度包装
        lines = content.strip().split("\n")

        # 提取核心要点
        core_points = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                continue
            if line.startswith("- "):
                core_points.append(line[2:].strip())
            elif len(line) > 10:
                core_points.append(line)

        if not core_points:
            return "「昨日无事记录」\n\n若有恒，何必三更眠五更起；最无益，莫过一日曝十日寒。"

        # 从核心内容中提取 2-3 个关键点
        selected_points = core_points[:3]

        # 睿智语录库
        wisdom_quotes = [
            "「工欲善其事，必先利其器。」",
            "「不积跬步，无以至千里；不积小流，无以成江海。」",
            "「知行合一，方可致远。」",
            "「业精于勤，荒于嬉；行成于思，毁于随。」",
            "「路漫漫其修远兮，吾将上下而求索。」",
            "「昨夜西风凋碧树，独上高楼，望尽天涯路。」",
            "「衣带渐宽终不悔，为伊消得人憔悴。」",
            "「众里寻他千百度，蓦然回首，那人却在，灯火阑珊处。」",
            "「世事洞明皆学问，人情练达即文章。」",
            "「纸上得来终觉浅，绝知此事要躬行。」",
        ]

        import random

        quote = random.choice(wisdom_quotes)

        # 组合内容
        result = []

        # 添加核心内容
        if selected_points:
            for i, point in enumerate(selected_points):
                # 隐私清理
                point = sanitize_content(point)
                # 截断过长的内容
                if len(point) > 40:
                    point = point[:37] + "..."
                # 每行最多 20 字
                if len(point) <= 20:
                    result.append(f"· {point}")
                else:
                    # 按 20 字切分
                    for j in range(0, len(point), 20):
                        chunk = point[j : j + 20]
                        if j == 0:
                            result.append(f"· {chunk}")
                        else:
                            result.append(f"  {chunk}")

        # 添加睿智语录
        if quote:
            if len(quote) <= 20:
                result.append(f"\n{quote}")
            else:
                for j in range(0, len(quote), 20):
                    chunk = quote[j : j + 20]
                    if j == 0:
                        result.append(f"\n{chunk}")
                    else:
                        result.append(chunk)

        return "\n".join(result).strip()

    except Exception as e:
        print(f"提取 memo 失败: {e}")
        return "「昨日记录加载失败」\n\n「往者不可谏，来者犹可追。」"


app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="/static")

plugin_manager = PluginManager(PLUGINS_DIR)
plugin_manager.load(app)
print(f"[App] Loaded plugins: {plugin_manager.list_loaded()}")

# Guard join-agent critical section to enforce per-key concurrency under parallel requests
join_lock = threading.Lock()

# Generate a version timestamp once at server startup for cache busting
VERSION_TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")


@app.after_request
def add_no_cache_headers(response):
    """Aggressively prevent caching for all responses"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


# Default state
DEFAULT_STATE = {
    "state": "idle",
    "detail": "等待任务中...",
    "progress": 0,
    "updated_at": datetime.now().isoformat(),
}


def load_state():
    """Load state from file.

    Includes a simple auto-idle mechanism:
    - If the last update is older than ttl_seconds (default 25s)
      and the state is a "working" state, we fall back to idle.

    This avoids the UI getting stuck at the desk when no new updates arrive.
    """
    state = None
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
        except Exception:
            state = None

    if not isinstance(state, dict):
        state = dict(DEFAULT_STATE)

    # Auto-idle
    try:
        ttl = int(state.get("ttl_seconds", 300))
        updated_at = state.get("updated_at")
        s = state.get("state", "idle")
        working_states = {"writing", "researching", "executing"}
        if updated_at and s in working_states:
            # tolerate both with/without timezone
            dt = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
            # Use UTC for aware datetimes; local time for naive.
            if dt.tzinfo:
                from datetime import timezone

                age = (
                    datetime.now(timezone.utc) - dt.astimezone(timezone.utc)
                ).total_seconds()
            else:
                age = (datetime.now() - dt).total_seconds()
            if age > ttl:
                state["state"] = "idle"
                state["detail"] = "待命中（自动回到休息区）"
                state["progress"] = 0
                state["updated_at"] = datetime.now().isoformat()
                # persist the auto-idle so every client sees it consistently
                try:
                    save_state(state)
                except Exception:
                    pass
    except Exception:
        pass

    return state


def save_state(state: dict):
    """Save state to file"""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


# Initialize state
if not os.path.exists(STATE_FILE):
    save_state(DEFAULT_STATE)


@app.route("/", methods=["GET"])
def index():
    """Serve the pixel office UI with built-in version cache busting"""
    with open(os.path.join(FRONTEND_DIR, "index.html"), "r", encoding="utf-8") as f:
        html = f.read()
    html = html.replace("{{VERSION_TIMESTAMP}}", VERSION_TIMESTAMP)
    resp = make_response(html)
    resp.headers["Content-Type"] = "text/html; charset=utf-8"
    return resp


@app.route("/join", methods=["GET"])
def join_page():
    """Serve the agent join page"""
    with open(os.path.join(FRONTEND_DIR, "join.html"), "r", encoding="utf-8") as f:
        html = f.read()
    resp = make_response(html)
    resp.headers["Content-Type"] = "text/html; charset=utf-8"
    return resp


@app.route("/invite", methods=["GET"])
def invite_page():
    """Serve human-facing invite instruction page"""
    with open(os.path.join(FRONTEND_DIR, "invite.html"), "r", encoding="utf-8") as f:
        html = f.read()
    resp = make_response(html)
    resp.headers["Content-Type"] = "text/html; charset=utf-8"
    return resp


DEFAULT_AGENTS = [
    {
        "agentId": "star",
        "name": "Star",
        "isMain": True,
        "state": "idle",
        "detail": "待命中，随时准备为你服务",
        "updated_at": datetime.now().isoformat(),
        "area": "breakroom",
        "source": "local",
        "joinKey": None,
        "authStatus": "approved",
        "authExpiresAt": None,
        "lastPushAt": None,
    },
    {
        "agentId": "npc1",
        "name": "NPC 1",
        "isMain": False,
        "state": "writing",
        "detail": "在整理热点日报...",
        "updated_at": datetime.now().isoformat(),
        "area": "writing",
        "source": "demo",
        "joinKey": None,
        "authStatus": "approved",
        "authExpiresAt": None,
        "lastPushAt": None,
    },
]


def load_agents_state():
    if os.path.exists(AGENTS_STATE_FILE):
        try:
            with open(AGENTS_STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception:
            pass
    return list(DEFAULT_AGENTS)


def save_agents_state(agents):
    with open(AGENTS_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(agents, f, ensure_ascii=False, indent=2)


def load_join_keys():
    if os.path.exists(JOIN_KEYS_FILE):
        try:
            with open(JOIN_KEYS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and isinstance(data.get("keys"), list):
                    return data
        except Exception:
            pass
    return {"keys": []}


def save_join_keys(data):
    with open(JOIN_KEYS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def normalize_agent_state(s):
    """归一化状态，提高兼容性。
    兼容输入：working/busy → writing; run/running → executing; sync → syncing; research → researching.
    未识别默认返回 idle.
    """
    if not s:
        return "idle"
    s_lower = s.lower().strip()
    if s_lower in {"working", "busy", "write"}:
        return "writing"
    if s_lower in {"run", "running", "execute", "exec"}:
        return "executing"
    if s_lower in {"sync"}:
        return "syncing"
    if s_lower in {"research", "search"}:
        return "researching"
    if s_lower in {"idle", "writing", "researching", "executing", "syncing", "error"}:
        return s_lower
    # 默认 fallback
    return "idle"


def state_to_area(state):
    area_map = {
        "idle": "breakroom",
        "writing": "writing",
        "researching": "writing",
        "executing": "writing",
        "syncing": "writing",
        "error": "error",
    }
    return area_map.get(state, "breakroom")


# Ensure files exist
if not os.path.exists(AGENTS_STATE_FILE):
    save_agents_state(DEFAULT_AGENTS)
if not os.path.exists(JOIN_KEYS_FILE):
    save_join_keys({"keys": []})


@app.route("/agents", methods=["GET"])
def get_agents():
    """Get full agents list (for multi-agent UI), with auto-cleanup on access"""
    agents = load_agents_state()
    now = datetime.now()

    cleaned_agents = []
    keys_data = load_join_keys()

    for a in agents:
        if a.get("isMain"):
            cleaned_agents.append(a)
            continue

        auth_expires_at_str = a.get("authExpiresAt")
        auth_status = a.get("authStatus", "pending")

        # 1) 超时未批准自动 leave
        if auth_status == "pending" and auth_expires_at_str:
            try:
                auth_expires_at = datetime.fromisoformat(auth_expires_at_str)
                if now > auth_expires_at:
                    key = a.get("joinKey")
                    if key:
                        key_item = next(
                            (
                                k
                                for k in keys_data.get("keys", [])
                                if k.get("key") == key
                            ),
                            None,
                        )
                        if key_item:
                            key_item["used"] = False
                            key_item["usedBy"] = None
                            key_item["usedByAgentId"] = None
                            key_item["usedAt"] = None
                    continue
            except Exception:
                pass

        # 2) 超时未推送自动离线（超过5分钟）
        last_push_at_str = a.get("lastPushAt")
        if auth_status == "approved" and last_push_at_str:
            try:
                last_push_at = datetime.fromisoformat(last_push_at_str)
                age = (now - last_push_at).total_seconds()
                if age > 300:  # 5分钟无推送自动离线
                    a["authStatus"] = "offline"
            except Exception:
                pass

        cleaned_agents.append(a)

    save_agents_state(cleaned_agents)
    save_join_keys(keys_data)

    return jsonify(cleaned_agents)


@app.route("/agent-approve", methods=["POST"])
def agent_approve():
    """Approve an agent (set authStatus to approved)"""
    try:
        data = request.get_json()
        agent_id = (data.get("agentId") or "").strip()
        if not agent_id:
            return jsonify({"ok": False, "msg": "缺少 agentId"}), 400

        agents = load_agents_state()
        target = next(
            (a for a in agents if a.get("agentId") == agent_id and not a.get("isMain")),
            None,
        )
        if not target:
            return jsonify({"ok": False, "msg": "未找到 agent"}), 404

        target["authStatus"] = "approved"
        target["authApprovedAt"] = datetime.now().isoformat()
        target["authExpiresAt"] = (
            datetime.now() + timedelta(hours=24)
        ).isoformat()  # 默认授权24h

        save_agents_state(agents)
        return jsonify({"ok": True, "agentId": agent_id, "authStatus": "approved"})
    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)}), 500


@app.route("/agent-reject", methods=["POST"])
def agent_reject():
    """Reject an agent (set authStatus to rejected and optionally revoke key)"""
    try:
        data = request.get_json()
        agent_id = (data.get("agentId") or "").strip()
        if not agent_id:
            return jsonify({"ok": False, "msg": "缺少 agentId"}), 400

        agents = load_agents_state()
        target = next(
            (a for a in agents if a.get("agentId") == agent_id and not a.get("isMain")),
            None,
        )
        if not target:
            return jsonify({"ok": False, "msg": "未找到 agent"}), 404

        target["authStatus"] = "rejected"
        target["authRejectedAt"] = datetime.now().isoformat()

        # Optionally free join key back to unused
        join_key = target.get("joinKey")
        keys_data = load_join_keys()
        if join_key:
            key_item = next(
                (k for k in keys_data.get("keys", []) if k.get("key") == join_key), None
            )
            if key_item:
                key_item["used"] = False
                key_item["usedBy"] = None
                key_item["usedByAgentId"] = None
                key_item["usedAt"] = None

        # Remove from agents list
        agents = [a for a in agents if a.get("agentId") != agent_id or a.get("isMain")]

        save_agents_state(agents)
        save_join_keys(keys_data)
        return jsonify({"ok": True, "agentId": agent_id, "authStatus": "rejected"})
    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)}), 500


@app.route("/join-agent", methods=["POST"])
def join_agent():
    """Add a new agent with one-time join key validation and pending auth"""
    try:
        data = request.get_json()
        if not isinstance(data, dict) or not data.get("name"):
            return jsonify({"ok": False, "msg": "请提供名字"}), 400

        name = data["name"].strip()
        state = data.get("state", "idle")
        detail = data.get("detail", "")
        join_key = data.get("joinKey", "").strip()

        # Normalize state early for compatibility
        state = normalize_agent_state(state)

        if not join_key:
            return jsonify({"ok": False, "msg": "请提供接入密钥"}), 400

        keys_data = load_join_keys()
        key_item = next(
            (k for k in keys_data.get("keys", []) if k.get("key") == join_key), None
        )
        if not key_item:
            return jsonify({"ok": False, "msg": "接入密钥无效"}), 403
        # key 可复用：不再因为 used=true 拒绝

        with join_lock:
            # 在锁内重新读取，避免并发请求都基于同一旧快照通过校验
            keys_data = load_join_keys()
            key_item = next(
                (k for k in keys_data.get("keys", []) if k.get("key") == join_key), None
            )
            if not key_item:
                return jsonify({"ok": False, "msg": "接入密钥无效"}), 403

            agents = load_agents_state()

            # 并发上限：同一个 key “同时在线”最多 3 个。
            # 在线判定：lastPushAt/updated_at 在 5 分钟内；否则视为 offline，不计入并发。
            now = datetime.now()
            existing = next(
                (a for a in agents if a.get("name") == name and not a.get("isMain")),
                None,
            )
            existing_id = existing.get("agentId") if existing else None

            def _age_seconds(dt_str):
                if not dt_str:
                    return None
                try:
                    dt = datetime.fromisoformat(dt_str)
                    return (now - dt).total_seconds()
                except Exception:
                    return None

            # opportunistic offline marking
            for a in agents:
                if a.get("isMain"):
                    continue
                if a.get("authStatus") != "approved":
                    continue
                age = _age_seconds(a.get("lastPushAt"))
                if age is None:
                    age = _age_seconds(a.get("updated_at"))
                if age is not None and age > 300:
                    a["authStatus"] = "offline"

            max_concurrent = int(key_item.get("maxConcurrent", 3))
            active_count = 0
            for a in agents:
                if a.get("isMain"):
                    continue
                if a.get("agentId") == existing_id:
                    continue
                if a.get("joinKey") != join_key:
                    continue
                if a.get("authStatus") != "approved":
                    continue
                age = _age_seconds(a.get("lastPushAt"))
                if age is None:
                    age = _age_seconds(a.get("updated_at"))
                if age is None or age <= 300:
                    active_count += 1

            if active_count >= max_concurrent:
                save_agents_state(agents)
                return jsonify(
                    {
                        "ok": False,
                        "msg": f"该接入密钥当前并发已达上限（{max_concurrent}），请稍后或换另一个 key",
                    }
                ), 429

            if existing:
                existing["state"] = state
                existing["detail"] = detail
                existing["updated_at"] = datetime.now().isoformat()
                existing["area"] = state_to_area(state)
                existing["source"] = "remote-openclaw"
                existing["joinKey"] = join_key
                existing["authStatus"] = "approved"
                existing["authApprovedAt"] = datetime.now().isoformat()
                existing["authExpiresAt"] = (
                    datetime.now() + timedelta(hours=24)
                ).isoformat()
                existing["lastPushAt"] = (
                    datetime.now().isoformat()
                )  # join 视为上线，纳入并发/离线判定
                if not existing.get("avatar"):
                    import random

                    existing["avatar"] = random.choice(
                        [
                            "guest_role_1",
                            "guest_role_2",
                            "guest_role_3",
                            "guest_role_4",
                            "guest_role_5",
                            "guest_role_6",
                        ]
                    )
                agent_id = existing.get("agentId")
            else:
                # Use ms + random suffix to avoid collisions under concurrent joins
                import random
                import string

                agent_id = (
                    "agent_"
                    + str(int(datetime.now().timestamp() * 1000))
                    + "_"
                    + "".join(
                        random.choices(string.ascii_lowercase + string.digits, k=4)
                    )
                )
                agents.append(
                    {
                        "agentId": agent_id,
                        "name": name,
                        "isMain": False,
                        "state": state,
                        "detail": detail,
                        "updated_at": datetime.now().isoformat(),
                        "area": state_to_area(state),
                        "source": "remote-openclaw",
                        "joinKey": join_key,
                        "authStatus": "approved",
                        "authApprovedAt": datetime.now().isoformat(),
                        "authExpiresAt": (
                            datetime.now() + timedelta(hours=24)
                        ).isoformat(),
                        "lastPushAt": datetime.now().isoformat(),
                        "avatar": random.choice(
                            [
                                "guest_role_1",
                                "guest_role_2",
                                "guest_role_3",
                                "guest_role_4",
                                "guest_role_5",
                                "guest_role_6",
                            ]
                        ),
                    }
                )

            key_item["used"] = True
            key_item["usedBy"] = name
            key_item["usedByAgentId"] = agent_id
            key_item["usedAt"] = datetime.now().isoformat()
            key_item["reusable"] = True

            # 拿到有效 key 直接批准，不再等待主人手动点击
            # （状态已在上面 existing/new 分支写入）
            save_agents_state(agents)
            save_join_keys(keys_data)

        return jsonify(
            {
                "ok": True,
                "agentId": agent_id,
                "authStatus": "approved",
                "nextStep": "已自动批准，立即开始推送状态",
            }
        )
    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)}), 500


@app.route("/leave-agent", methods=["POST"])
def leave_agent():
    """Remove an agent and free its one-time join key for reuse (optional)

    Prefer agentId (stable). Name is accepted for backward compatibility.
    """
    try:
        data = request.get_json()
        if not isinstance(data, dict):
            return jsonify({"ok": False, "msg": "invalid json"}), 400

        agent_id = (data.get("agentId") or "").strip()
        name = (data.get("name") or "").strip()
        if not agent_id and not name:
            return jsonify({"ok": False, "msg": "请提供 agentId 或名字"}), 400

        agents = load_agents_state()

        target = None
        if agent_id:
            target = next(
                (
                    a
                    for a in agents
                    if a.get("agentId") == agent_id and not a.get("isMain")
                ),
                None,
            )
        if (not target) and name:
            # fallback: remove by name only if agentId not provided
            target = next(
                (a for a in agents if a.get("name") == name and not a.get("isMain")),
                None,
            )

        if not target:
            return jsonify({"ok": False, "msg": "没有找到要离开的 agent"}), 404

        join_key = target.get("joinKey")
        new_agents = [
            a
            for a in agents
            if a.get("isMain") or a.get("agentId") != target.get("agentId")
        ]

        # Optional: free key back to unused after leave
        keys_data = load_join_keys()
        if join_key:
            key_item = next(
                (k for k in keys_data.get("keys", []) if k.get("key") == join_key), None
            )
            if key_item:
                key_item["used"] = False
                key_item["usedBy"] = None
                key_item["usedByAgentId"] = None
                key_item["usedAt"] = None

        save_agents_state(new_agents)
        save_join_keys(keys_data)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)}), 500


@app.route("/status", methods=["GET"])
def get_status():
    """Get current main state (backward compatibility)"""
    state = load_state()
    return jsonify(state)


@app.route("/agent-push", methods=["POST"])
def agent_push():
    """Remote openclaw actively pushes status to office.

    Required fields:
    - agentId
    - joinKey
    - state
    Optional:
    - detail
    - name
    """
    try:
        data = request.get_json()
        if not isinstance(data, dict):
            return jsonify({"ok": False, "msg": "invalid json"}), 400

        agent_id = (data.get("agentId") or "").strip()
        join_key = (data.get("joinKey") or "").strip()
        state = (data.get("state") or "").strip()
        detail = (data.get("detail") or "").strip()
        name = (data.get("name") or "").strip()

        if not agent_id or not join_key or not state:
            return jsonify({"ok": False, "msg": "缺少 agentId/joinKey/state"}), 400

        valid_states = {
            "idle",
            "writing",
            "researching",
            "executing",
            "syncing",
            "error",
        }
        state = normalize_agent_state(state)

        keys_data = load_join_keys()
        key_item = next(
            (k for k in keys_data.get("keys", []) if k.get("key") == join_key), None
        )
        if not key_item:
            return jsonify({"ok": False, "msg": "joinKey 无效"}), 403
        # key 可复用：不再做 used/usedByAgentId 绑定校验

        agents = load_agents_state()
        target = next(
            (a for a in agents if a.get("agentId") == agent_id and not a.get("isMain")),
            None,
        )
        if not target:
            return jsonify({"ok": False, "msg": "agent 未注册，请先 join"}), 404

        # Auth check: only approved agents can push.
        # Note: "offline" is a presence state (stale), not a revoked authorization.
        # Allow offline agents to resume pushing and auto-promote them back to approved.
        auth_status = target.get("authStatus", "pending")
        if auth_status not in {"approved", "offline"}:
            return jsonify({"ok": False, "msg": "agent 未获授权，请等待主人批准"}), 403
        if auth_status == "offline":
            target["authStatus"] = "approved"
            target["authApprovedAt"] = datetime.now().isoformat()
            target["authExpiresAt"] = (datetime.now() + timedelta(hours=24)).isoformat()

        if target.get("joinKey") != join_key:
            return jsonify({"ok": False, "msg": "joinKey 不匹配"}), 403

        target["state"] = state
        target["detail"] = detail
        if name:
            target["name"] = name
        target["updated_at"] = datetime.now().isoformat()
        target["area"] = state_to_area(state)
        target["source"] = "remote-openclaw"
        target["lastPushAt"] = datetime.now().isoformat()

        save_agents_state(agents)
        return jsonify({"ok": True, "agentId": agent_id, "area": target.get("area")})
    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    """Health check"""
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})


@app.route("/yesterday-memo", methods=["GET"])
def get_yesterday_memo():
    """获取昨日小日记"""
    try:
        # 先尝试找昨天的文件
        yesterday_str = get_yesterday_date_str()
        yesterday_file = os.path.join(MEMORY_DIR, f"{yesterday_str}.md")

        target_file = None
        target_date = yesterday_str

        if os.path.exists(yesterday_file):
            target_file = yesterday_file
        else:
            # 如果昨天没有，找最近的一天
            if os.path.exists(MEMORY_DIR):
                files = [
                    f
                    for f in os.listdir(MEMORY_DIR)
                    if f.endswith(".md") and re.match(r"\d{4}-\d{2}-\d{2}\.md", f)
                ]
                if files:
                    files.sort(reverse=True)
                    # 跳过今天的（如果存在）
                    today_str = datetime.now().strftime("%Y-%m-%d")
                    for f in files:
                        if f != f"{today_str}.md":
                            target_file = os.path.join(MEMORY_DIR, f)
                            target_date = f.replace(".md", "")
                            break

        if target_file and os.path.exists(target_file):
            memo_content = extract_memo_from_file(target_file)
            return jsonify({"success": True, "date": target_date, "memo": memo_content})
        else:
            return jsonify({"success": False, "msg": "没有找到昨日日记"})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)}), 500


@app.route("/set_state", methods=["POST"])
def set_state_endpoint():
    """Set state via POST (for UI control panel)"""
    try:
        data = request.get_json()
        if not isinstance(data, dict):
            return jsonify({"status": "error", "msg": "invalid json"}), 400
        state = load_state()
        if "state" in data:
            s = data["state"]
            valid_states = {
                "idle",
                "writing",
                "researching",
                "executing",
                "syncing",
                "error",
            }
            if s in valid_states:
                state["state"] = s
        if "detail" in data:
            state["detail"] = data["detail"]
        state["updated_at"] = datetime.now().isoformat()
        save_state(state)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500


if __name__ == "__main__":
    print("=" * 50)
    print("Star Office UI - Backend State Service")
    print("=" * 50)
    print(f"State file: {STATE_FILE}")
    print("Listening on: http://0.0.0.0:18791")
    print("=" * 50)

    app.run(host="0.0.0.0", port=18791, debug=False)
