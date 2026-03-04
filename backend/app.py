#!/usr/bin/env python3
"""Star Office UI - Backend State Service"""

from flask import Flask, jsonify, send_from_directory, make_response, request, session
from datetime import datetime, timedelta
import json
import os
import random
import math
import re
import shutil
import subprocess
import tempfile
import threading
from pathlib import Path
from security_utils import is_production_mode, is_strong_secret, is_strong_drawer_pass
from memo_utils import get_yesterday_date_str, sanitize_content, extract_memo_from_file
from store_utils import (
    load_agents_state as _store_load_agents_state,
    save_agents_state as _store_save_agents_state,
    load_asset_positions as _store_load_asset_positions,
    save_asset_positions as _store_save_asset_positions,
    load_asset_defaults as _store_load_asset_defaults,
    save_asset_defaults as _store_save_asset_defaults,
    load_runtime_config as _store_load_runtime_config,
    save_runtime_config as _store_save_runtime_config,
    load_join_keys as _store_load_join_keys,
    save_join_keys as _store_save_join_keys,
)

try:
    from PIL import Image
except Exception:
    Image = None

# Paths (project-relative, no hardcoded absolute paths)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEMORY_DIR = os.path.join(os.path.dirname(ROOT_DIR), "memory")
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")
FRONTEND_INDEX_FILE = os.path.join(FRONTEND_DIR, "index.html")
FRONTEND_ELECTRON_STANDALONE_FILE = os.path.join(FRONTEND_DIR, "electron-standalone.html")
STATE_FILE = os.path.join(ROOT_DIR, "state.json")
AGENTS_STATE_FILE = os.path.join(ROOT_DIR, "agents-state.json")
JOIN_KEYS_FILE = os.path.join(ROOT_DIR, "join-keys.json")
FRONTEND_PATH = Path(FRONTEND_DIR)
ASSET_ALLOWED_EXTS = {".png", ".webp", ".jpg", ".jpeg", ".gif", ".svg", ".avif"}
ASSET_TEMPLATE_ZIP = os.path.join(ROOT_DIR, "assets-replace-template.zip")
WORKSPACE_DIR = os.path.dirname(ROOT_DIR)
GEMINI_SCRIPT = os.path.join(WORKSPACE_DIR, "skills", "gemini-image-generate", "scripts", "gemini_image_generate.py")
GEMINI_PYTHON = os.path.join(WORKSPACE_DIR, "skills", "gemini-image-generate", ".venv", "bin", "python")
ROOM_REFERENCE_IMAGE = (
    os.path.join(ROOT_DIR, "assets", "room-reference.webp")
    if os.path.exists(os.path.join(ROOT_DIR, "assets", "room-reference.webp"))
    else os.path.join(ROOT_DIR, "assets", "room-reference.png")
)
BG_HISTORY_DIR = os.path.join(ROOT_DIR, "assets", "bg-history")
HOME_FAVORITES_DIR = os.path.join(ROOT_DIR, "assets", "home-favorites")
HOME_FAVORITES_INDEX_FILE = os.path.join(HOME_FAVORITES_DIR, "index.json")
HOME_FAVORITES_MAX = 30
ASSET_POSITIONS_FILE = os.path.join(ROOT_DIR, "asset-positions.json")

# 性能保护：默认关闭“每次打开页面随机换背景”，避免首页首屏被磁盘复制拖慢
AUTO_ROTATE_HOME_ON_PAGE_OPEN = (os.getenv("AUTO_ROTATE_HOME_ON_PAGE_OPEN", "0").strip().lower() in {"1", "true", "yes", "on"})
AUTO_ROTATE_MIN_INTERVAL_SECONDS = int(os.getenv("AUTO_ROTATE_MIN_INTERVAL_SECONDS", "60"))
_last_home_rotate_at = 0
ASSET_DEFAULTS_FILE = os.path.join(ROOT_DIR, "asset-defaults.json")
RUNTIME_CONFIG_FILE = os.path.join(ROOT_DIR, "runtime-config.json")


app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="/static")
app.secret_key = os.getenv("FLASK_SECRET_KEY") or os.getenv("STAR_OFFICE_SECRET") or "star-office-dev-secret-change-me"

# Session hardening
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=is_production_mode(),
    PERMANENT_SESSION_LIFETIME=timedelta(hours=12),
)

# Guard join-agent critical section to enforce per-key concurrency under parallel requests
join_lock = threading.Lock()

# Generate a version timestamp once at server startup for cache busting
VERSION_TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
ASSET_DRAWER_PASS_DEFAULT = os.getenv("ASSET_DRAWER_PASS", "1234")

if is_production_mode():
    hardening_errors = []
    if not is_strong_secret(str(app.secret_key)):
        hardening_errors.append("FLASK_SECRET_KEY / STAR_OFFICE_SECRET is weak (need >=24 chars, non-default)")
    if not is_strong_drawer_pass(ASSET_DRAWER_PASS_DEFAULT):
        hardening_errors.append("ASSET_DRAWER_PASS is weak (do not use default 1234; recommend >=8 chars)")
    if hardening_errors:
        raise RuntimeError("Security hardening check failed in production mode: " + "; ".join(hardening_errors))


def _is_asset_editor_authed() -> bool:
    return bool(session.get("asset_editor_authed"))


def _require_asset_editor_auth():
    if _is_asset_editor_authed():
        return None
    return jsonify({"ok": False, "code": "UNAUTHORIZED", "msg": "Asset editor auth required"}), 401


@app.after_request
def add_no_cache_headers(response):
    """Apply cache policy by path:
    - HTML/API/state: no-cache (always fresh)
    - /static assets: long cache (filenames are versioned with ?v=VERSION_TIMESTAMP)
    """
    path = (request.path or "")
    if path.startswith('/static/'):
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        response.headers.pop("Pragma", None)
        response.headers.pop("Expires", None)
    else:
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# Default state
DEFAULT_STATE = {
    "state": "idle",
    "detail": "等待任务中...",
    "progress": 0,
    "updated_at": datetime.now().isoformat()
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
                age = (datetime.now(timezone.utc) - dt.astimezone(timezone.utc)).total_seconds()
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


def ensure_electron_standalone_snapshot():
    """Create Electron standalone frontend snapshot once if missing.

    The snapshot is intentionally decoupled from the browser page:
    - browser uses frontend/index.html
    - Electron uses frontend/electron-standalone.html
    """
    if os.path.exists(FRONTEND_ELECTRON_STANDALONE_FILE):
        return
    try:
        shutil.copy2(FRONTEND_INDEX_FILE, FRONTEND_ELECTRON_STANDALONE_FILE)
        print(f"[standalone] created: {FRONTEND_ELECTRON_STANDALONE_FILE}")
    except Exception as e:
        print(f"[standalone] create failed: {e}")


# Initialize state
if not os.path.exists(STATE_FILE):
    save_state(DEFAULT_STATE)
ensure_electron_standalone_snapshot()


_INDEX_HTML_CACHE = None


@app.route("/", methods=["GET"])
def index():
    """Serve the pixel office UI with built-in version cache busting"""
    # 默认禁用页面打开即换背景，避免首屏慢
    # 如需启用，可配置 AUTO_ROTATE_HOME_ON_PAGE_OPEN=1
    _maybe_apply_random_home_favorite()

    global _INDEX_HTML_CACHE
    if _INDEX_HTML_CACHE is None:
        with open(FRONTEND_INDEX_FILE, "r", encoding="utf-8") as f:
            raw_html = f.read()
        _INDEX_HTML_CACHE = raw_html.replace("{{VERSION_TIMESTAMP}}", VERSION_TIMESTAMP)

    resp = make_response(_INDEX_HTML_CACHE)
    resp.headers["Content-Type"] = "text/html; charset=utf-8"
    return resp


@app.route("/electron-standalone", methods=["GET"])
def electron_standalone_page():
    """Serve Electron-only standalone frontend page."""
    ensure_electron_standalone_snapshot()
    target = FRONTEND_ELECTRON_STANDALONE_FILE
    if not os.path.exists(target):
        target = FRONTEND_INDEX_FILE
    with open(target, "r", encoding="utf-8") as f:
        html = f.read()
    html = html.replace("{{VERSION_TIMESTAMP}}", VERSION_TIMESTAMP)
    resp = make_response(html)
    resp.headers["Content-Type"] = "text/html; charset=utf-8"
    return resp

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
        "lastPushAt": None
    }
]


def load_agents_state():
    return _store_load_agents_state(AGENTS_STATE_FILE, DEFAULT_AGENTS)


def save_agents_state(agents):
    _store_save_agents_state(AGENTS_STATE_FILE, agents)


def load_asset_positions():
    return _store_load_asset_positions(ASSET_POSITIONS_FILE)


def save_asset_positions(data):
    _store_save_asset_positions(ASSET_POSITIONS_FILE, data)


def load_asset_defaults():
    return _store_load_asset_defaults(ASSET_DEFAULTS_FILE)


def save_asset_defaults(data):
    _store_save_asset_defaults(ASSET_DEFAULTS_FILE, data)


def load_runtime_config():
    return _store_load_runtime_config(RUNTIME_CONFIG_FILE)


def save_runtime_config(data):
    _store_save_runtime_config(RUNTIME_CONFIG_FILE, data)


def _ensure_home_favorites_index():
    os.makedirs(HOME_FAVORITES_DIR, exist_ok=True)
    if not os.path.exists(HOME_FAVORITES_INDEX_FILE):
        with open(HOME_FAVORITES_INDEX_FILE, "w", encoding="utf-8") as f:
            json.dump({"items": []}, f, ensure_ascii=False, indent=2)


def _load_home_favorites_index():
    _ensure_home_favorites_index()
    try:
        with open(HOME_FAVORITES_INDEX_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict) and isinstance(data.get("items"), list):
                return data
    except Exception:
        pass
    return {"items": []}


def _save_home_favorites_index(data):
    _ensure_home_favorites_index()
    with open(HOME_FAVORITES_INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _maybe_apply_random_home_favorite():
    """On page open, randomly apply one saved home favorite if available."""
    global _last_home_rotate_at

    if not AUTO_ROTATE_HOME_ON_PAGE_OPEN:
        return False, "disabled"

    try:
        now_ts = datetime.now().timestamp()
        if _last_home_rotate_at and (now_ts - _last_home_rotate_at) < AUTO_ROTATE_MIN_INTERVAL_SECONDS:
            return False, "throttled"

        idx = _load_home_favorites_index()
        items = idx.get("items") or []
        candidates = []
        for it in items:
            rel = (it.get("path") or "").strip()
            if not rel:
                continue
            abs_path = os.path.join(ROOT_DIR, rel)
            if os.path.exists(abs_path):
                candidates.append((rel, abs_path))

        if not candidates:
            return False, "no-favorites"

        rel, src = random.choice(candidates)
        target = FRONTEND_PATH / "office_bg_small.webp"
        if not target.exists():
            return False, "missing-office-bg"

        shutil.copy2(src, str(target))
        _last_home_rotate_at = now_ts
        return True, rel
    except Exception as e:
        return False, str(e)


def load_join_keys():
    return _store_load_join_keys(JOIN_KEYS_FILE)


def save_join_keys(data):
    _store_save_join_keys(JOIN_KEYS_FILE, data)


def _ensure_magick_or_ffmpeg_available():
    if shutil.which("magick"):
        return "magick"
    if shutil.which("ffmpeg"):
        return "ffmpeg"
    return None


def _probe_animated_frame_size(upload_path: str):
    """Return (w,h) from first frame if possible."""
    if Image is not None:
        try:
            with Image.open(upload_path) as im:
                w, h = im.size
                return int(w), int(h)
        except Exception:
            pass
    # ffprobe fallback
    if shutil.which("ffprobe"):
        try:
            cmd = [
                "ffprobe", "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height",
                "-of", "csv=p=0:s=x",
                upload_path,
            ]
            out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, timeout=5).decode().strip()
            if "x" in out:
                w, h = out.split("x", 1)
                return int(w), int(h)
        except Exception:
            pass
    return None, None


def _animated_to_spritesheet(
    upload_path: str,
    frame_w: int,
    frame_h: int,
    out_ext: str = ".webp",
    preserve_original: bool = True,
    pixel_art: bool = True,
    cols: int | None = None,
    rows: int | None = None,
):
    """Convert animated GIF/WEBP to spritesheet, return (out_path, columns, rows, frames, out_frame_w, out_frame_h)."""
    backend = _ensure_magick_or_ffmpeg_available()
    if not backend:
        raise RuntimeError("未检测到 ImageMagick/ffmpeg，无法自动转换动图")

    ext = (out_ext or ".webp").lower()
    if ext not in {".webp", ".png"}:
        ext = ".webp"

    out_fd, out_path = tempfile.mkstemp(suffix=ext)
    os.close(out_fd)

    with tempfile.TemporaryDirectory() as td:
        frames = 0
        out_fw, out_fh = int(frame_w), int(frame_h)
        if Image is not None:
            try:
                with Image.open(upload_path) as im:
                    n = getattr(im, "n_frames", 1)
                    # 默认保留用户原始帧尺寸（避免先压缩再放大导致像素糊）
                    if preserve_original:
                        out_fw, out_fh = im.size
                    for i in range(n):
                        im.seek(i)
                        fr = im.convert("RGBA")
                        if not preserve_original and (fr.size != (out_fw, out_fh)):
                            resample = Image.Resampling.NEAREST if pixel_art else Image.Resampling.LANCZOS
                            fr = fr.resize((out_fw, out_fh), resample)
                        fr.save(os.path.join(td, f"f_{i:04d}.png"), "PNG")
                    frames = n
            except Exception:
                frames = 0

        if frames <= 0:
            cmd1 = f"ffmpeg -y -i '{upload_path}' '{td}/f_%04d.png' >/dev/null 2>&1"
            if os.system(cmd1) != 0:
                raise RuntimeError("动图抽帧失败（Pillow/ffmpeg 都失败）")
            files = sorted([x for x in os.listdir(td) if x.startswith("f_") and x.endswith(".png")])
            frames = len(files)
            if frames <= 0:
                raise RuntimeError("动图无有效帧")

        if backend == "magick":
            # 像素风动图转精灵表默认无损，避免颜色/边缘被压缩糊掉
            quality_flag = "-define webp:lossless=true -define webp:method=6 -quality 100" if ext == ".webp" else ""
            # 允许按 cols/rows 排布；默认单行
            if cols is None or cols <= 0:
                cols_eff = frames
            else:
                cols_eff = max(1, int(cols))
            rows_eff = max(1, int(rows)) if (rows is not None and rows > 0) else max(1, math.ceil(frames / cols_eff))

            # 先规范单帧尺寸
            prep = ""
            if not preserve_original:
                magick_filter = "-filter point" if pixel_art else ""
                prep = f" {magick_filter} -resize {out_fw}x{out_fh}^ -gravity center -background none -extent {out_fw}x{out_fh}"

            cmd = (
                f"magick '{td}/f_*.png'{prep} "
                f"-tile {cols_eff}x{rows_eff} -background none -geometry +0+0 {quality_flag} '{out_path}'"
            )
            rc = os.system(cmd)
            if rc != 0:
                raise RuntimeError("ImageMagick 拼图失败")
            return out_path, cols_eff, rows_eff, frames, out_fw, out_fh

        ffmpeg_quality = "-lossless 1 -compression_level 6 -q:v 100" if ext == ".webp" else ""
        cols_eff = max(1, int(cols)) if (cols is not None and cols > 0) else frames
        rows_eff = max(1, int(rows)) if (rows is not None and rows > 0) else max(1, math.ceil(frames / cols_eff))
        if preserve_original:
            vf = f"tile={cols_eff}x{rows_eff}"
        else:
            scale_algo = "neighbor" if pixel_art else "lanczos"
            vf = (
                f"scale={out_fw}:{out_fh}:force_original_aspect_ratio=decrease:flags={scale_algo},"
                f"pad={out_fw}:{out_fh}:(ow-iw)/2:(oh-ih)/2:color=0x00000000,"
                f"tile={cols_eff}x{rows_eff}"
            )
        cmd2 = (
            f"ffmpeg -y -pattern_type glob -i '{td}/f_*.png' "
            f"-vf '{vf}' "
            f"{ffmpeg_quality} '{out_path}' >/dev/null 2>&1"
        )
        if os.system(cmd2) != 0:
            raise RuntimeError("ffmpeg 拼图失败")
        return out_path, frames, 1, frames, out_fw, out_fh


def normalize_agent_state(s):
    """归一化状态，提高兼容性。
    兼容输入：working/busy → writing; run/running → executing; sync → syncing; research → researching.
    未识别默认返回 idle.
    """
    if not s:
        return 'idle'
    s_lower = s.lower().strip()
    if s_lower in {'working', 'busy', 'write'}:
        return 'writing'
    if s_lower in {'run', 'running', 'execute', 'exec'}:
        return 'executing'
    if s_lower in {'sync'}:
        return 'syncing'
    if s_lower in {'research', 'search'}:
        return 'researching'
    if s_lower in {'idle', 'writing', 'researching', 'executing', 'syncing', 'error'}:
        return s_lower
    # 默认 fallback
    return 'idle'


# User-facing model aliases -> provider model ids
USER_MODEL_TO_PROVIDER_MODELS = {
    # 严格按用户要求：仅两种官方模型映射
    "nanobanana-pro": [
        "nano-banana-pro-preview",
    ],
    "nanobanana-2": [
        "gemini-2.5-flash-image",
    ],
}

PROVIDER_MODEL_TO_USER_MODEL = {
    provider: user
    for user, providers in USER_MODEL_TO_PROVIDER_MODELS.items()
    for provider in providers
}


def _normalize_user_model(model_name: str) -> str:
    m = (model_name or "").strip()
    if not m:
        return "nanobanana-pro"
    low = m.lower()
    if low in USER_MODEL_TO_PROVIDER_MODELS:
        return low
    if low in PROVIDER_MODEL_TO_USER_MODEL:
        return PROVIDER_MODEL_TO_USER_MODEL[low]
    return "nanobanana-pro"


def _provider_model_candidates(user_model: str):
    normalized = _normalize_user_model(user_model)
    return list(USER_MODEL_TO_PROVIDER_MODELS.get(normalized, USER_MODEL_TO_PROVIDER_MODELS["nanobanana-pro"]))


def _generate_rpg_background_to_webp(out_webp_path: str, width: int = 1280, height: int = 720, custom_prompt: str = "", speed_mode: str = "fast"):
    """Generate RPG-style room background and save as webp.

    speed_mode:
      - fast: use nanobanana-2 + 1024x576 intermediate + downscaled reference (faster)
      - quality: use configured model (fallback nanobanana-pro) + full 1280x720 path
    """
    runtime_cfg = load_runtime_config()
    api_key = (runtime_cfg.get("gemini_api_key") or "").strip()
    if not api_key:
        raise RuntimeError("MISSING_API_KEY")
    themes = [
        "8-bit dungeon guild room",
        "8-bit stardew-valley inspired cozy farm tavern",
        "8-bit nordic fantasy tavern",
        "8-bit magitech workshop",
        "8-bit elven forest inn",
        "8-bit pixel cyber tavern",
        "8-bit desert caravan inn",
        "8-bit snow mountain lodge",
    ]
    theme = random.choice(themes)

    if not (os.path.exists(GEMINI_PYTHON) and os.path.exists(GEMINI_SCRIPT)):
        raise RuntimeError("生图脚本环境缺失：gemini-image-generate 未安装")

    style_hint = (custom_prompt or "").strip()
    if not style_hint:
        style_hint = theme

    # 默认使用更稳妥的 quality 档，避免 fast 模型在部分 API 通道不可用
    mode = (speed_mode or "quality").strip().lower()
    if mode not in {"fast", "quality"}:
        mode = "quality"

    configured_user_model = _normalize_user_model(runtime_cfg.get("gemini_model") or "nanobanana-pro")
    if mode == "fast":
        preferred_user_model = "nanobanana-2"
        # fast 也提高基础清晰度：从 1024x576 提升到 1152x648（牺牲少量速度）
        gen_width, gen_height = 1152, 648
        ref_width, ref_height = 1152, 648
    else:
        preferred_user_model = configured_user_model
        gen_width, gen_height = width, height
        ref_width, ref_height = width, height

    # 同时规避可能触发 400 的特殊能力参数：
    # 仅 nanobanana-2 走 aspect-ratio，nanobanana-pro 交给模型默认比例（后续再标准化到 1280x720）
    allow_aspect_ratio = (preferred_user_model == "nanobanana-2")

    prompt = (
        "Use a top-down pixel room composition compatible with an office game scene. "
        "STRICTLY preserve the same room geometry, camera angle, wall/floor boundaries and major object placement as the provided reference image. "
        "Keep region layout stable (left work area, center lounge, right error area). "
        "Only change visual style/theme/material/lighting according to: " + style_hint + ". "
        "Do not add text or watermark. Retro 8-bit RPG style."
    )

    tmp_dir = tempfile.mkdtemp(prefix="rpg-bg-")
    cmd = [
        GEMINI_PYTHON,
        GEMINI_SCRIPT,
        "--prompt", prompt,
        "--model", configured_user_model,
        "--out-dir", tmp_dir,
        "--cleanup",
    ]
    if allow_aspect_ratio:
        cmd.extend(["--aspect-ratio", "16:9"])

    # 强约束：每次都带固定参考图，保持房间区域布局不漂移
    ref_for_call = None
    if os.path.exists(ROOM_REFERENCE_IMAGE):
        ref_for_call = ROOM_REFERENCE_IMAGE
        if mode == "fast" and Image is not None:
            try:
                ref_fast = os.path.join(tmp_dir, "room-reference-fast.webp")
                with Image.open(ROOM_REFERENCE_IMAGE) as rim:
                    rim = rim.convert("RGBA").resize((ref_width, ref_height), Image.Resampling.LANCZOS)
                    rim.save(ref_fast, "WEBP", quality=85, method=4)
                ref_for_call = ref_fast
            except Exception:
                ref_for_call = ROOM_REFERENCE_IMAGE

    if ref_for_call:
        cmd.extend(["--reference-image", ref_for_call])

    env = os.environ.copy()
    # 运行时配置优先：只保留 GEMINI_API_KEY，避免脚本因双 key 报错
    env.pop("GOOGLE_API_KEY", None)
    env["GEMINI_API_KEY"] = api_key

    def _run_cmd(cmd_args):
        return subprocess.run(cmd_args, capture_output=True, text=True, env=env, timeout=240)

    def _is_model_unavailable_error(text: str) -> bool:
        low = (text or "").strip().lower()
        return (
            ("not found" in low and "models/" in low)
            or ("model_not_available" in low)
            or ("model is not available" in low)
            or ("configured model is not available" in low)
            or ("this model is not available" in low)
            or ("not supported for generatecontent" in low)
        )

    def _with_model(cmd_args, model_name: str):
        m = cmd_args[:]
        if "--model" in m:
            idx = m.index("--model")
            if idx + 1 < len(m):
                m[idx + 1] = model_name
        else:
            m.extend(["--model", model_name])
        return m

    # 模型多级回退（仅允许两类用户模型：nanobanana-pro / nanobanana-2）
    # 每个用户模型映射到若干 provider 真实模型。
    user_model_order = [preferred_user_model, configured_user_model]
    user_model_order = [m for i, m in enumerate(user_model_order) if m and m not in user_model_order[:i]]

    model_candidates = []
    for um in user_model_order:
        model_candidates.extend(_provider_model_candidates(um))
    # 去重并清理空项
    model_candidates = [m for i, m in enumerate(model_candidates) if m and m not in model_candidates[:i]]

    proc = None
    last_err_text = ""
    model_unavailable_count = 0

    for mname in model_candidates:
        env["GEMINI_MODEL"] = mname
        try_cmd = _with_model(cmd, mname)
        proc = _run_cmd(try_cmd)
        if proc.returncode == 0:
            break

        err_text = (proc.stderr or proc.stdout or "").strip()
        last_err_text = err_text

        # key 失效/泄漏：立即终止，不继续尝试
        low = err_text.lower()
        if "your api key was reported as leaked" in low or "permission_denied" in low:
            raise RuntimeError("API_KEY_REVOKED_OR_LEAKED")

        if _is_model_unavailable_error(err_text):
            model_unavailable_count += 1
            continue

        # 非模型不可用错误，直接返回真实错误
        raise RuntimeError(f"生图失败: {err_text}")

    if proc is None or proc.returncode != 0:
        err_text = (last_err_text or "").strip()
        if model_unavailable_count >= len(model_candidates) or _is_model_unavailable_error(err_text):
            brief = (err_text or "").replace("\n", " ")[:240]
            raise RuntimeError(f"MODEL_NOT_AVAILABLE::{brief}")
        raise RuntimeError(f"生图失败: {err_text}")

    try:
        result = json.loads(proc.stdout.strip().splitlines()[-1])
    except Exception:
        raise RuntimeError("生图结果解析失败")

    files = result.get("files") or []
    if not files:
        raise RuntimeError("生图未返回文件")

    gen_path = files[0]
    if not os.path.exists(gen_path):
        raise RuntimeError("生图文件不存在")

    if Image is None:
        raise RuntimeError("Pillow 不可用，无法做尺寸标准化")

    with Image.open(gen_path) as im:
        im = im.convert("RGBA")
        # 质量模式优先保细节；快速模式优先速度
        if mode == "fast":
            im = im.resize((gen_width, gen_height), Image.Resampling.LANCZOS)
            if (gen_width, gen_height) != (width, height):
                # fast 的放大改为 LANCZOS，牺牲少量速度换更高细节
                im = im.resize((width, height), Image.Resampling.LANCZOS)
            im.save(out_webp_path, "WEBP", quality=96, method=6)
        else:
            # quality：确保输出标准尺寸，同时使用无损 webp，减少压缩损失
            if im.size != (width, height):
                im = im.resize((width, height), Image.Resampling.LANCZOS)
            im.save(out_webp_path, "WEBP", lossless=True, quality=100, method=6)


def state_to_area(state):
    area_map = {
        "idle": "breakroom",
        "writing": "writing",
        "researching": "writing",
        "executing": "writing",
        "syncing": "writing",
        "error": "error"
    }
    return area_map.get(state, "breakroom")


# Ensure files exist
if not os.path.exists(AGENTS_STATE_FILE):
    save_agents_state(DEFAULT_AGENTS)
if not os.path.exists(JOIN_KEYS_FILE):
    if os.path.exists(os.path.join(ROOT_DIR, "join-keys.sample.json")):
        try:
            with open(os.path.join(ROOT_DIR, "join-keys.sample.json"), "r", encoding="utf-8") as sf:
                sample = json.load(sf)
            save_join_keys(sample if isinstance(sample, dict) else {"keys": []})
        except Exception:
            save_join_keys({"keys": []})
    else:
        save_join_keys({"keys": []})

# Tighten runtime-config file perms if exists
if os.path.exists(RUNTIME_CONFIG_FILE):
    try:
        os.chmod(RUNTIME_CONFIG_FILE, 0o600)
    except Exception:
        pass


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
                        key_item = next((k for k in keys_data.get("keys", []) if k.get("key") == key), None)
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
        target = next((a for a in agents if a.get("agentId") == agent_id and not a.get("isMain")), None)
        if not target:
            return jsonify({"ok": False, "msg": "未找到 agent"}), 404

        target["authStatus"] = "approved"
        target["authApprovedAt"] = datetime.now().isoformat()
        target["authExpiresAt"] = (datetime.now() + timedelta(hours=24)).isoformat()  # 默认授权24h

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
        target = next((a for a in agents if a.get("agentId") == agent_id and not a.get("isMain")), None)
        if not target:
            return jsonify({"ok": False, "msg": "未找到 agent"}), 404

        target["authStatus"] = "rejected"
        target["authRejectedAt"] = datetime.now().isoformat()

        # Optionally free join key back to unused
        join_key = target.get("joinKey")
        keys_data = load_join_keys()
        if join_key:
            key_item = next((k for k in keys_data.get("keys", []) if k.get("key") == join_key), None)
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
        key_item = next((k for k in keys_data.get("keys", []) if k.get("key") == join_key), None)
        if not key_item:
            return jsonify({"ok": False, "msg": "接入密钥无效"}), 403
        # key 可复用：不再因为 used=true 拒绝

        with join_lock:
            # 在锁内重新读取，避免并发请求都基于同一旧快照通过校验
            keys_data = load_join_keys()
            key_item = next((k for k in keys_data.get("keys", []) if k.get("key") == join_key), None)
            if not key_item:
                return jsonify({"ok": False, "msg": "接入密钥无效"}), 403

            agents = load_agents_state()

            # 并发上限：同一个 key “同时在线”最多 3 个。
            # 在线判定：lastPushAt/updated_at 在 5 分钟内；否则视为 offline，不计入并发。
            now = datetime.now()
            existing = next((a for a in agents if a.get("name") == name and not a.get("isMain")), None)
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
                return jsonify({"ok": False, "msg": f"该接入密钥当前并发已达上限（{max_concurrent}），请稍后或换另一个 key"}), 429

            if existing:
                existing["state"] = state
                existing["detail"] = detail
                existing["updated_at"] = datetime.now().isoformat()
                existing["area"] = state_to_area(state)
                existing["source"] = "remote-openclaw"
                existing["joinKey"] = join_key
                existing["authStatus"] = "approved"
                existing["authApprovedAt"] = datetime.now().isoformat()
                existing["authExpiresAt"] = (datetime.now() + timedelta(hours=24)).isoformat()
                existing["lastPushAt"] = datetime.now().isoformat()  # join 视为上线，纳入并发/离线判定
                if not existing.get("avatar"):
                    import random
                    existing["avatar"] = random.choice(["guest_role_1", "guest_role_2", "guest_role_3", "guest_role_4", "guest_role_5", "guest_role_6"])
                agent_id = existing.get("agentId")
            else:
                # Use ms + random suffix to avoid collisions under concurrent joins
                import random
                import string
                agent_id = "agent_" + str(int(datetime.now().timestamp() * 1000)) + "_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
                agents.append({
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
                    "authExpiresAt": (datetime.now() + timedelta(hours=24)).isoformat(),
                    "lastPushAt": datetime.now().isoformat(),
                    "avatar": random.choice(["guest_role_1", "guest_role_2", "guest_role_3", "guest_role_4", "guest_role_5", "guest_role_6"])
                })

            key_item["used"] = True
            key_item["usedBy"] = name
            key_item["usedByAgentId"] = agent_id
            key_item["usedAt"] = datetime.now().isoformat()
            key_item["reusable"] = True

            # 拿到有效 key 直接批准，不再等待主人手动点击
            # （状态已在上面 existing/new 分支写入）
            save_agents_state(agents)
            save_join_keys(keys_data)

        return jsonify({"ok": True, "agentId": agent_id, "authStatus": "approved", "nextStep": "已自动批准，立即开始推送状态"})
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
            target = next((a for a in agents if a.get("agentId") == agent_id and not a.get("isMain")), None)
        if (not target) and name:
            # fallback: remove by name only if agentId not provided
            target = next((a for a in agents if a.get("name") == name and not a.get("isMain")), None)

        if not target:
            return jsonify({"ok": False, "msg": "没有找到要离开的 agent"}), 404

        join_key = target.get("joinKey")
        new_agents = [a for a in agents if a.get("isMain") or a.get("agentId") != target.get("agentId")]

        # Optional: free key back to unused after leave
        keys_data = load_join_keys()
        if join_key:
            key_item = next((k for k in keys_data.get("keys", []) if k.get("key") == join_key), None)
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

        valid_states = {"idle", "writing", "researching", "executing", "syncing", "error"}
        state = normalize_agent_state(state)

        keys_data = load_join_keys()
        key_item = next((k for k in keys_data.get("keys", []) if k.get("key") == join_key), None)
        if not key_item:
            return jsonify({"ok": False, "msg": "joinKey 无效"}), 403
        # key 可复用：不再做 used/usedByAgentId 绑定校验


        agents = load_agents_state()
        target = next((a for a in agents if a.get("agentId") == agent_id and not a.get("isMain")), None)
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
                files = [f for f in os.listdir(MEMORY_DIR) if f.endswith(".md") and re.match(r"\d{4}-\d{2}-\d{2}\.md", f)]
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
            return jsonify({
                "success": True,
                "date": target_date,
                "memo": memo_content
            })
        else:
            return jsonify({
                "success": False,
                "msg": "没有找到昨日日记"
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "msg": str(e)
        }), 500


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
            valid_states = {"idle", "writing", "researching", "executing", "syncing", "error"}
            if s in valid_states:
                state["state"] = s
        if "detail" in data:
            state["detail"] = data["detail"]
        state["updated_at"] = datetime.now().isoformat()
        save_state(state)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500


@app.route("/assets/template.zip", methods=["GET"])
def assets_template_download():
    if not os.path.exists(ASSET_TEMPLATE_ZIP):
        return jsonify({"ok": False, "msg": "模板包不存在，请先生成"}), 404
    return send_from_directory(ROOT_DIR, "assets-replace-template.zip", as_attachment=True)


@app.route("/assets/list", methods=["GET"])
def assets_list():
    items = []
    for p in FRONTEND_PATH.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(FRONTEND_PATH).as_posix()
        if rel.startswith("fonts/"):
            continue
        if p.suffix.lower() not in ASSET_ALLOWED_EXTS:
            continue
        st = p.stat()
        width = None
        height = None
        if Image is not None:
            try:
                with Image.open(p) as im:
                    width, height = im.size
            except Exception:
                pass
        items.append({
            "path": rel,
            "size": st.st_size,
            "ext": p.suffix.lower(),
            "width": width,
            "height": height,
            "mtime": datetime.fromtimestamp(st.st_mtime).isoformat(),
        })
    items.sort(key=lambda x: x["path"])
    return jsonify({"ok": True, "count": len(items), "items": items})


@app.route("/assets/generate-rpg-background", methods=["POST"])
def assets_generate_rpg_background():
    """Generate a new RPG-themed background and replace office_bg_small.webp."""
    guard = _require_asset_editor_auth()
    if guard:
        return guard
    try:
        req = request.get_json(silent=True) or {}
        custom_prompt = (req.get("prompt") or "").strip() if isinstance(req, dict) else ""
        speed_mode = (req.get("speed_mode") or "quality").strip().lower() if isinstance(req, dict) else "quality"
        if speed_mode not in {"fast", "quality"}:
            speed_mode = "fast"

        target = FRONTEND_PATH / "office_bg_small.webp"
        if not target.exists():
            return jsonify({"ok": False, "msg": "office_bg_small.webp 不存在"}), 404

        # 覆盖前保留最近一次备份
        bak = target.with_suffix(target.suffix + ".bak")
        shutil.copy2(target, bak)

        _generate_rpg_background_to_webp(
            str(target),
            width=1280,
            height=720,
            custom_prompt=custom_prompt,
            speed_mode=speed_mode,
        )

        # 每次生成都归档一份历史底图（可回溯风格演化）
        os.makedirs(BG_HISTORY_DIR, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        hist_file = os.path.join(BG_HISTORY_DIR, f"office_bg_small-{ts}.webp")
        shutil.copy2(target, hist_file)

        st = target.stat()
        return jsonify({
            "ok": True,
            "path": "office_bg_small.webp",
            "size": st.st_size,
            "history": os.path.relpath(hist_file, ROOT_DIR),
            "speed_mode": speed_mode,
            "msg": "已生成并替换 RPG 房间底图（已自动归档）",
        })
    except Exception as e:
        msg = str(e)
        if msg == "MISSING_API_KEY":
            return jsonify({"ok": False, "code": "MISSING_API_KEY", "msg": "Missing GEMINI_API_KEY or GOOGLE_API_KEY"}), 400
        if msg == "API_KEY_REVOKED_OR_LEAKED":
            return jsonify({"ok": False, "code": "API_KEY_REVOKED_OR_LEAKED", "msg": "API key is revoked or flagged as leaked. Please rotate to a new key."}), 400
        if msg.startswith("MODEL_NOT_AVAILABLE"):
            detail = ""
            if "::" in msg:
                detail = msg.split("::", 1)[1]
            return jsonify({
                "ok": False,
                "code": "MODEL_NOT_AVAILABLE",
                "msg": "Configured model is not available for this API key/channel.",
                "detail": detail,
            }), 400
        return jsonify({"ok": False, "msg": msg}), 500


@app.route("/assets/restore-reference-background", methods=["POST"])
def assets_restore_reference_background():
    """Restore office_bg_small.webp from fixed reference image."""
    guard = _require_asset_editor_auth()
    if guard:
        return guard
    try:
        target = FRONTEND_PATH / "office_bg_small.webp"
        if not target.exists():
            return jsonify({"ok": False, "msg": "office_bg_small.webp 不存在"}), 404
        if not os.path.exists(ROOM_REFERENCE_IMAGE):
            return jsonify({"ok": False, "msg": "参考图不存在"}), 404

        # 备份当前底图
        bak = target.with_suffix(target.suffix + ".bak")
        shutil.copy2(target, bak)

        # 快速路径：若参考图已是 1280x720 的 webp，直接拷贝（秒级）
        ref_ext = os.path.splitext(ROOM_REFERENCE_IMAGE)[1].lower()
        fast_copied = False
        if ref_ext == '.webp':
            try:
                with Image.open(ROOM_REFERENCE_IMAGE) as rim:
                    if rim.size == (1280, 720):
                        shutil.copy2(ROOM_REFERENCE_IMAGE, target)
                        fast_copied = True
            except Exception:
                fast_copied = False

        # 慢路径：仅在必要时重编码
        if not fast_copied:
            if Image is None:
                return jsonify({"ok": False, "msg": "Pillow 不可用"}), 500
            with Image.open(ROOM_REFERENCE_IMAGE) as im:
                im = im.convert("RGBA").resize((1280, 720), Image.Resampling.LANCZOS)
                im.save(target, "WEBP", quality=92, method=6)

        st = target.stat()
        return jsonify({
            "ok": True,
            "path": "office_bg_small.webp",
            "size": st.st_size,
            "msg": "已恢复初始底图",
        })
    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)}), 500


@app.route("/assets/restore-last-generated-background", methods=["POST"])
def assets_restore_last_generated_background():
    """Restore office_bg_small.webp from latest bg-history snapshot."""
    guard = _require_asset_editor_auth()
    if guard:
        return guard
    try:
        target = FRONTEND_PATH / "office_bg_small.webp"
        if not target.exists():
            return jsonify({"ok": False, "msg": "office_bg_small.webp 不存在"}), 404

        if not os.path.isdir(BG_HISTORY_DIR):
            return jsonify({"ok": False, "msg": "暂无历史底图"}), 404

        files = [
            os.path.join(BG_HISTORY_DIR, x)
            for x in os.listdir(BG_HISTORY_DIR)
            if x.startswith("office_bg_small-") and x.endswith(".webp")
        ]
        if not files:
            return jsonify({"ok": False, "msg": "暂无历史底图"}), 404

        latest = max(files, key=lambda p: os.path.getmtime(p))

        bak = target.with_suffix(target.suffix + ".bak")
        shutil.copy2(target, bak)
        shutil.copy2(latest, target)

        st = target.stat()
        return jsonify({
            "ok": True,
            "path": "office_bg_small.webp",
            "size": st.st_size,
            "from": os.path.relpath(latest, ROOT_DIR),
            "msg": "已回退到最近一次生成底图",
        })
    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)}), 500


@app.route("/assets/home-favorites/list", methods=["GET"])
def assets_home_favorites_list():
    guard = _require_asset_editor_auth()
    if guard:
        return guard
    try:
        data = _load_home_favorites_index()
        items = data.get("items") or []
        out = []
        for it in items:
            rel = (it.get("path") or "").strip()
            if not rel:
                continue
            abs_path = os.path.join(ROOT_DIR, rel)
            if not os.path.exists(abs_path):
                continue
            fn = os.path.basename(rel)
            out.append({
                "id": it.get("id"),
                "path": rel,
                "url": f"/assets/home-favorites/file/{fn}",
                "thumb_url": f"/assets/home-favorites/file/{fn}",
                "created_at": it.get("created_at") or "",
            })
        out.sort(key=lambda x: x.get("created_at") or "", reverse=True)
        return jsonify({"ok": True, "items": out})
    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)}), 500


@app.route("/assets/home-favorites/file/<path:filename>", methods=["GET"])
def assets_home_favorites_file(filename):
    guard = _require_asset_editor_auth()
    if guard:
        return guard
    return send_from_directory(HOME_FAVORITES_DIR, filename)


@app.route("/assets/home-favorites/save-current", methods=["POST"])
def assets_home_favorites_save_current():
    guard = _require_asset_editor_auth()
    if guard:
        return guard
    try:
        src = FRONTEND_PATH / "office_bg_small.webp"
        if not src.exists():
            return jsonify({"ok": False, "msg": "office_bg_small.webp 不存在"}), 404

        _ensure_home_favorites_index()
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        item_id = f"home-{ts}"
        fn = f"{item_id}.webp"
        dst = os.path.join(HOME_FAVORITES_DIR, fn)
        shutil.copy2(str(src), dst)

        idx = _load_home_favorites_index()
        items = idx.get("items") or []
        items.insert(0, {
            "id": item_id,
            "path": os.path.relpath(dst, ROOT_DIR),
            "created_at": datetime.now().isoformat(timespec="seconds"),
        })

        # 控制收藏数量上限，清理最旧项
        if len(items) > HOME_FAVORITES_MAX:
            extra = items[HOME_FAVORITES_MAX:]
            items = items[:HOME_FAVORITES_MAX]
            for it in extra:
                try:
                    p = os.path.join(ROOT_DIR, it.get("path") or "")
                    if os.path.exists(p):
                        os.remove(p)
                except Exception:
                    pass

        idx["items"] = items
        _save_home_favorites_index(idx)
        return jsonify({"ok": True, "id": item_id, "path": os.path.relpath(dst, ROOT_DIR), "msg": "已收藏当前地图"})
    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)}), 500


@app.route("/assets/home-favorites/delete", methods=["POST"])
def assets_home_favorites_delete():
    guard = _require_asset_editor_auth()
    if guard:
        return guard
    try:
        data = request.get_json(silent=True) or {}
        item_id = (data.get("id") or "").strip()
        if not item_id:
            return jsonify({"ok": False, "msg": "缺少 id"}), 400

        idx = _load_home_favorites_index()
        items = idx.get("items") or []
        hit = next((x for x in items if (x.get("id") or "") == item_id), None)
        if not hit:
            return jsonify({"ok": False, "msg": "收藏项不存在"}), 404

        rel = hit.get("path") or ""
        abs_path = os.path.join(ROOT_DIR, rel)
        if os.path.exists(abs_path):
            try:
                os.remove(abs_path)
            except Exception:
                pass

        idx["items"] = [x for x in items if (x.get("id") or "") != item_id]
        _save_home_favorites_index(idx)
        return jsonify({"ok": True, "id": item_id, "msg": "已删除收藏"})
    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)}), 500


@app.route("/assets/home-favorites/apply", methods=["POST"])
def assets_home_favorites_apply():
    guard = _require_asset_editor_auth()
    if guard:
        return guard
    try:
        data = request.get_json(silent=True) or {}
        item_id = (data.get("id") or "").strip()
        if not item_id:
            return jsonify({"ok": False, "msg": "缺少 id"}), 400

        idx = _load_home_favorites_index()
        items = idx.get("items") or []
        hit = next((x for x in items if (x.get("id") or "") == item_id), None)
        if not hit:
            return jsonify({"ok": False, "msg": "收藏项不存在"}), 404

        src = os.path.join(ROOT_DIR, hit.get("path") or "")
        if not os.path.exists(src):
            return jsonify({"ok": False, "msg": "收藏文件不存在"}), 404

        target = FRONTEND_PATH / "office_bg_small.webp"
        if not target.exists():
            return jsonify({"ok": False, "msg": "office_bg_small.webp 不存在"}), 404

        bak = target.with_suffix(target.suffix + ".bak")
        shutil.copy2(str(target), str(bak))
        shutil.copy2(src, str(target))

        st = target.stat()
        return jsonify({"ok": True, "path": "office_bg_small.webp", "size": st.st_size, "from": hit.get("path"), "msg": "已应用收藏地图"})
    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)}), 500


@app.route("/assets/auth", methods=["POST"])
def assets_auth():
    try:
        data = request.get_json(silent=True) or {}
        pwd = (data.get("password") or "").strip()
        if pwd and pwd == ASSET_DRAWER_PASS_DEFAULT:
            session["asset_editor_authed"] = True
            return jsonify({"ok": True, "msg": "认证成功"})
        return jsonify({"ok": False, "msg": "验证码错误"}), 401
    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)}), 500


@app.route("/assets/auth/status", methods=["GET"])
def assets_auth_status():
    return jsonify({
        "ok": True,
        "authed": _is_asset_editor_authed(),
        "drawer_default_pass": ASSET_DRAWER_PASS_DEFAULT == "1234",
    })


@app.route("/assets/positions", methods=["GET"])
def assets_positions_get():
    guard = _require_asset_editor_auth()
    if guard:
        return guard
    try:
        return jsonify({"ok": True, "items": load_asset_positions()})
    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)}), 500


@app.route("/assets/positions", methods=["POST"])
def assets_positions_set():
    guard = _require_asset_editor_auth()
    if guard:
        return guard
    try:
        data = request.get_json(silent=True) or {}
        key = (data.get("key") or "").strip()
        x = data.get("x")
        y = data.get("y")
        scale = data.get("scale")
        if not key:
            return jsonify({"ok": False, "msg": "缺少 key"}), 400
        if x is None or y is None:
            return jsonify({"ok": False, "msg": "缺少 x/y"}), 400
        x = float(x)
        y = float(y)
        if scale is None:
            scale = 1.0
        scale = float(scale)

        all_pos = load_asset_positions()
        all_pos[key] = {"x": x, "y": y, "scale": scale, "updated_at": datetime.now().isoformat()}
        save_asset_positions(all_pos)
        return jsonify({"ok": True, "key": key, "x": x, "y": y, "scale": scale})
    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)}), 500


@app.route("/assets/defaults", methods=["GET"])
def assets_defaults_get():
    guard = _require_asset_editor_auth()
    if guard:
        return guard
    try:
        return jsonify({"ok": True, "items": load_asset_defaults()})
    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)}), 500


@app.route("/assets/defaults", methods=["POST"])
def assets_defaults_set():
    guard = _require_asset_editor_auth()
    if guard:
        return guard
    try:
        data = request.get_json(silent=True) or {}
        key = (data.get("key") or "").strip()
        x = data.get("x")
        y = data.get("y")
        scale = data.get("scale")
        if not key:
            return jsonify({"ok": False, "msg": "缺少 key"}), 400
        if x is None or y is None:
            return jsonify({"ok": False, "msg": "缺少 x/y"}), 400
        x = float(x)
        y = float(y)
        if scale is None:
            scale = 1.0
        scale = float(scale)

        all_defaults = load_asset_defaults()
        all_defaults[key] = {"x": x, "y": y, "scale": scale, "updated_at": datetime.now().isoformat()}
        save_asset_defaults(all_defaults)
        return jsonify({"ok": True, "key": key, "x": x, "y": y, "scale": scale})
    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)}), 500


@app.route("/config/gemini", methods=["GET"])
def gemini_config_get():
    guard = _require_asset_editor_auth()
    if guard:
        return guard
    try:
        cfg = load_runtime_config()
        key = (cfg.get("gemini_api_key") or "").strip()
        masked = ("*" * max(0, len(key) - 4)) + key[-4:] if key else ""
        return jsonify({
            "ok": True,
            "has_api_key": bool(key),
            "api_key_masked": masked,
            "gemini_model": _normalize_user_model(cfg.get("gemini_model") or "nanobanana-pro"),
        })
    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)}), 500


@app.route("/config/gemini", methods=["POST"])
def gemini_config_set():
    guard = _require_asset_editor_auth()
    if guard:
        return guard
    try:
        data = request.get_json(silent=True) or {}
        api_key = (data.get("api_key") or "").strip()
        model = _normalize_user_model((data.get("model") or "").strip() or "nanobanana-pro")
        payload = {"gemini_model": model}
        if api_key:
            payload["gemini_api_key"] = api_key
        save_runtime_config(payload)
        return jsonify({"ok": True, "msg": "Gemini 配置已保存"})
    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)}), 500


@app.route("/assets/restore-default", methods=["POST"])
def assets_restore_default():
    guard = _require_asset_editor_auth()
    if guard:
        return guard
    try:
        data = request.get_json(silent=True) or {}
        rel_path = (data.get("path") or "").strip().lstrip("/")
        if not rel_path:
            return jsonify({"ok": False, "msg": "缺少 path"}), 400

        target = (FRONTEND_PATH / rel_path).resolve()
        try:
            target.relative_to(FRONTEND_PATH.resolve())
        except Exception:
            return jsonify({"ok": False, "msg": "非法 path"}), 400

        if not target.exists():
            return jsonify({"ok": False, "msg": "目标文件不存在"}), 404

        root, ext = os.path.splitext(str(target))
        default_path = root + ext + ".default"
        if not os.path.exists(default_path):
            return jsonify({"ok": False, "msg": "未找到默认资产快照"}), 404

        # 回滚前保留上一版
        bak = str(target) + ".bak"
        if os.path.exists(str(target)):
            shutil.copy2(str(target), bak)

        shutil.copy2(default_path, str(target))
        st = os.stat(str(target))
        return jsonify({"ok": True, "path": rel_path, "size": st.st_size, "msg": "已重置为默认资产"})
    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)}), 500


@app.route("/assets/restore-prev", methods=["POST"])
def assets_restore_prev():
    guard = _require_asset_editor_auth()
    if guard:
        return guard
    try:
        data = request.get_json(silent=True) or {}
        rel_path = (data.get("path") or "").strip().lstrip("/")
        if not rel_path:
            return jsonify({"ok": False, "msg": "缺少 path"}), 400

        target = (FRONTEND_PATH / rel_path).resolve()
        try:
            target.relative_to(FRONTEND_PATH.resolve())
        except Exception:
            return jsonify({"ok": False, "msg": "非法 path"}), 400

        bak = str(target) + ".bak"
        if not os.path.exists(bak):
            return jsonify({"ok": False, "msg": "未找到上一版备份"}), 404

        shutil.copy2(str(target), bak + ".tmp") if os.path.exists(str(target)) else None
        shutil.copy2(bak, str(target))
        st = os.stat(str(target))
        return jsonify({"ok": True, "path": rel_path, "size": st.st_size, "msg": "已回退到上一版"})
    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)}), 500


@app.route("/assets/upload", methods=["POST"])
def assets_upload():
    guard = _require_asset_editor_auth()
    if guard:
        return guard
    try:
        rel_path = (request.form.get("path") or "").strip().lstrip("/")
        backup = (request.form.get("backup") or "1").strip() != "0"
        f = request.files.get("file")

        if not rel_path or f is None:
            return jsonify({"ok": False, "msg": "缺少 path 或 file"}), 400

        target = (FRONTEND_PATH / rel_path).resolve()
        try:
            target.relative_to(FRONTEND_PATH.resolve())
        except Exception:
            return jsonify({"ok": False, "msg": "非法 path"}), 400

        if target.suffix.lower() not in ASSET_ALLOWED_EXTS:
            return jsonify({"ok": False, "msg": "仅允许上传图片/美术资源类型"}), 400

        if not target.exists():
            return jsonify({"ok": False, "msg": "目标文件不存在，请先从 /assets/list 选择 path"}), 404

        target.parent.mkdir(parents=True, exist_ok=True)

        # 首次上传前固化默认资产快照，供“重置为默认资产”使用
        default_snap = Path(str(target) + ".default")
        if not default_snap.exists():
            try:
                shutil.copy2(target, default_snap)
            except Exception:
                pass

        if backup:
            bak = target.with_suffix(target.suffix + ".bak")
            shutil.copy2(target, bak)

        auto_sheet = (request.form.get("auto_spritesheet") or "0").strip() == "1"
        ext_name = (f.filename or "").lower()

        if auto_sheet and target.suffix.lower() in {".webp", ".png"}:
            with tempfile.NamedTemporaryFile(suffix=os.path.splitext(ext_name)[1] or ".gif", delete=False) as tf:
                src_path = tf.name
                f.save(src_path)
            try:
                in_w, in_h = _probe_animated_frame_size(src_path)
                frame_w = int(request.form.get("frame_w") or (in_w or 64))
                frame_h = int(request.form.get("frame_h") or (in_h or 64))

                # 如果是静态图上传到精灵表目标，按网格切片而不是整图覆盖
                if not (ext_name.endswith(".gif") or ext_name.endswith(".webp")) and Image is not None:
                    try:
                        with Image.open(src_path) as sim:
                            sim = sim.convert("RGBA")
                            sw, sh = sim.size
                            if frame_w <= 0 or frame_h <= 0:
                                frame_w, frame_h = sw, sh
                            cols = max(1, sw // frame_w)
                            rows = max(1, sh // frame_h)
                            sheet_w = cols * frame_w
                            sheet_h = rows * frame_h
                            if sheet_w <= 0 or sheet_h <= 0:
                                raise RuntimeError("静态图尺寸与帧规格不匹配")

                            cropped = sim.crop((0, 0, sheet_w, sheet_h))
                            # 目标是 webp 仍按无损保存，避免像素损失
                            if target.suffix.lower() == ".webp":
                                cropped.save(str(target), "WEBP", lossless=True, quality=100, method=6)
                            else:
                                cropped.save(str(target), "PNG")

                            st = target.stat()
                            return jsonify({
                                "ok": True,
                                "path": rel_path,
                                "size": st.st_size,
                                "backup": backup,
                                "converted": {
                                    "from": ext_name.split(".")[-1] if "." in ext_name else "image",
                                    "to": "webp_spritesheet" if target.suffix.lower() == ".webp" else "png_spritesheet",
                                    "frame_w": frame_w,
                                    "frame_h": frame_h,
                                    "columns": cols,
                                    "rows": rows,
                                    "frames": cols * rows,
                                    "preserve_original": False,
                                    "pixel_art": True,
                                }
                            })
                    finally:
                        pass

                # 默认：优先保留输入帧尺寸；若前端传了强制值则按前端。
                preserve_original_val = request.form.get("preserve_original")
                if preserve_original_val is None:
                    preserve_original = True
                else:
                    preserve_original = preserve_original_val.strip() == "1"

                pixel_art = (request.form.get("pixel_art") or "1").strip() == "1"
                req_cols = int(request.form.get("cols") or 0)
                req_rows = int(request.form.get("rows") or 0)
                sheet_path, cols, rows, frames, out_fw, out_fh = _animated_to_spritesheet(
                    src_path,
                    frame_w,
                    frame_h,
                    out_ext=target.suffix.lower(),
                    preserve_original=preserve_original,
                    pixel_art=pixel_art,
                    cols=(req_cols if req_cols > 0 else None),
                    rows=(req_rows if req_rows > 0 else None),
                )
                shutil.move(sheet_path, str(target))
                st = target.stat()
                from_type = "gif" if ext_name.endswith(".gif") else "webp"
                to_type = "webp_spritesheet" if target.suffix.lower() == ".webp" else "png_spritesheet"
                return jsonify({
                    "ok": True,
                    "path": rel_path,
                    "size": st.st_size,
                    "backup": backup,
                    "converted": {
                        "from": from_type,
                        "to": to_type,
                        "frame_w": out_fw,
                        "frame_h": out_fh,
                        "columns": cols,
                        "rows": rows,
                        "frames": frames,
                        "preserve_original": preserve_original,
                        "pixel_art": pixel_art,
                    }
                })
            finally:
                try:
                    os.remove(src_path)
                except Exception:
                    pass

        f.save(str(target))
        st = target.stat()
        return jsonify({"ok": True, "path": rel_path, "size": st.st_size, "backup": backup})
    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)}), 500


if __name__ == "__main__":
    raw_port = os.environ.get("STAR_BACKEND_PORT", "18791")
    try:
        backend_port = int(raw_port)
    except ValueError:
        backend_port = 18791
    if backend_port <= 0:
        backend_port = 18791

    print("=" * 50)
    print("Star Office UI - Backend State Service")
    print("=" * 50)
    print(f"State file: {STATE_FILE}")
    print(f"Listening on: http://0.0.0.0:{backend_port}")
    mode = "production" if is_production_mode() else "development"
    print(f"Mode: {mode}")
    if is_production_mode():
        print("Security hardening: ENABLED (strict checks)")
    else:
        weak_flags = []
        if not is_strong_secret(str(app.secret_key)):
            weak_flags.append("weak FLASK_SECRET_KEY/STAR_OFFICE_SECRET")
        if not is_strong_drawer_pass(ASSET_DRAWER_PASS_DEFAULT):
            weak_flags.append("weak ASSET_DRAWER_PASS")
        if weak_flags:
            print("Security hardening: WARNING (dev mode) -> " + ", ".join(weak_flags))
        else:
            print("Security hardening: OK")
    print("=" * 50)

    app.run(host="0.0.0.0", port=backend_port, debug=False)

