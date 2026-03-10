"""
Agent process detector — discovers running Claude Code / Codex / OpenClaw instances.

Each detector returns a list of DetectedAgent with a stable key, display name, and state.
"""

import os
import subprocess
import time
from dataclasses import dataclass
from typing import List


@dataclass
class DetectedAgent:
    """A detected agent process on the local machine."""
    key: str           # stable identifier, e.g. "claude_12345" or "openclaw_personal"
    name: str          # display name, e.g. "Claude Code (trading)"
    state: str         # "writing" | "idle"
    detail: str = ""   # extra info (e.g. project name)
    is_main: bool = False     # if True, sync to main sprite via /set_state instead of agent system


def _get_pids(process_name: str) -> List[str]:
    """Get PIDs for a given process name.

    Tries pgrep first, falls back to ps+awk (more reliable on macOS where
    pgrep sometimes can't see processes due to SIP/sandbox restrictions).
    Returns PIDs sorted numerically for deterministic ordering.
    """
    pid_set = set()

    # Source 1: pgrep (matches process name directly)
    try:
        result = subprocess.run(
            ["pgrep", "-x", process_name],
            capture_output=True, text=True, timeout=5,
        )
        for p in result.stdout.strip().split("\n"):
            if p.strip():
                pid_set.add(p.strip())
    except Exception:
        pass

    # Source 2: ps + basename match (catches cases pgrep misses, e.g.
    # macOS where COMM is the full binary path like /Users/.../codex)
    try:
        result = subprocess.run(
            ["ps", "-eo", "pid,comm"],
            capture_output=True, text=True, timeout=5,
        )
        for line in result.stdout.strip().split("\n"):
            parts = line.strip().split(None, 1)
            if len(parts) == 2 and os.path.basename(parts[1]) == process_name:
                pid_set.add(parts[0])
    except Exception:
        pass

    pids = list(pid_set)

    # Sort numerically so disambiguation labels are stable across cycles
    pids.sort(key=lambda p: int(p))
    return pids


def _get_cwd_for_pid(pid: str) -> str:
    """Get the current working directory for a PID (macOS/Linux)."""
    try:
        result = subprocess.run(
            ["lsof", "-a", "-d", "cwd", "-p", pid, "-Fn"],
            capture_output=True, text=True, timeout=5,
        )
        for line in result.stdout.split("\n"):
            if line.startswith("n/"):
                return line[1:]
    except Exception:
        pass
    return ""


def _basename_or_empty(path: str) -> str:
    return os.path.basename(path) if path else ""


def _detect_by_process(process_name: str, label_prefix: str) -> List[DetectedAgent]:
    """Detect running processes by name and return agents with disambiguated labels.

    Shared logic for Claude Code, Codex, and similar process-based agents.
    """
    agents = []
    seen_labels = {}

    for pid in _get_pids(process_name):
        cwd = _get_cwd_for_pid(pid)
        label = _basename_or_empty(cwd)

        # Disambiguate when multiple processes share the same cwd
        seen_labels[label] = seen_labels.get(label, 0) + 1
        if seen_labels[label] > 1:
            label_display = f"{label}#{seen_labels[label]}" if label else f"#{seen_labels[label]}"
        else:
            label_display = label

        name = f"{label_prefix} ({label_display})" if label_display else label_prefix
        agents.append(DetectedAgent(
            key=f"{process_name}_{pid}",
            name=name,
            state="writing",
            detail=label,
        ))

    return agents


def detect_claude_code() -> List[DetectedAgent]:
    """Detect running Claude Code processes."""
    return _detect_by_process("claude", "Claude Code")


def detect_codex() -> List[DetectedAgent]:
    """Detect running Codex processes."""
    return _detect_by_process("codex", "Codex")


def _log_modified_within(logfile: str, threshold_seconds: int = 120) -> bool:
    """Check if a log file was modified within the given threshold."""
    try:
        if not os.path.isfile(logfile):
            return False
        mtime = os.path.getmtime(logfile)
        return (time.time() - mtime) < threshold_seconds
    except Exception:
        return False


def detect_openclaw(busy_threshold: int = 120) -> List[DetectedAgent]:
    """Detect OpenClaw activity by checking gateway log modification time."""
    agents = []
    home = os.path.expanduser("~")

    variants = [
        ("openclaw_personal", "Lobster Personal", os.path.join(home, ".openclaw", "logs", "gateway.log"), False),
        ("openclaw_enterprise", "Lobster Enterprise", os.path.join(home, ".openclaw-enterprise", "logs", "gateway.log"), True),
    ]

    for key, name, logfile, main in variants:
        if not os.path.isfile(logfile):
            continue
        busy = _log_modified_within(logfile, busy_threshold)
        agents.append(DetectedAgent(
            key=key,
            name=name,
            state="writing" if busy else "idle",
            detail="active" if busy else "ready",
            is_main=main,
        ))

    return agents


def detect_all(busy_threshold: int = 120) -> List[DetectedAgent]:
    """Run all detectors and return combined list."""
    agents = []
    agents.extend(detect_claude_code())
    agents.extend(detect_codex())
    agents.extend(detect_openclaw(busy_threshold))
    return agents
