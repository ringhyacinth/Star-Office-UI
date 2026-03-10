#!/usr/bin/env python3
"""
Star Office Auto-Detect Daemon

Polls for running Claude Code / Codex / OpenClaw processes every N seconds,
auto-joins new instances to the office, pushes state updates, and removes
agents when their process exits.

Usage:
    python daemon.py                           # use defaults
    python daemon.py --interval 15             # poll every 15s
    python daemon.py --url http://host:28791   # custom office URL

Environment variables:
    STAR_OFFICE_URL       Office backend URL (default: http://127.0.0.1:28791)
    STAR_OFFICE_JOIN_KEY  Join key (default: ocj_example_team_01)
"""

import argparse
import hashlib
import json
import os
import signal
import sys
import time
from typing import Dict, List

try:
    from detector import DetectedAgent, detect_all
    from client import OfficeClient
except ImportError:
    from .detector import DetectedAgent, detect_all
    from .client import OfficeClient


_state_file_path: str = ""


def _make_state_file(url: str, key: str) -> str:
    """Generate a unique state file path per url+key combination."""
    token = hashlib.md5(f"{url}|{key}".encode()).hexdigest()[:8]
    return f"/tmp/star-office-daemon-{token}.json"


def load_tracked() -> Dict[str, dict]:
    """Load tracked agents from state file."""
    try:
        with open(_state_file_path, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_tracked(tracked: Dict[str, dict]):
    """Persist tracked agents to state file (atomic write)."""
    tmp_path = _state_file_path + ".tmp"
    with open(tmp_path, "w") as f:
        json.dump(tracked, f, indent=2)
    os.replace(tmp_path, _state_file_path)


def sync_agents(client: OfficeClient, tracked: Dict[str, dict], detected: List[DetectedAgent]) -> Dict[str, dict]:
    """Sync detected agents with the office backend.

    - Join new agents
    - Push state updates for existing agents
    - Leave agents whose processes have exited
    """
    active_keys = set()

    for agent in detected:
        active_keys.add(agent.key)

        # Main agent (e.g. Enterprise Lobster) — drive the main sprite directly
        if agent.is_main:
            ok = client.set_state(agent.state, detail=agent.detail)
            if ok:
                tracked[agent.key] = {"name": agent.name, "is_main": True, "persistent": True}
            else:
                print(f"[set_state-failed] {agent.name}")
            continue

        if agent.key not in tracked:
            # New agent — join the office
            agent_id = client.join(agent.name, state=agent.state, detail=agent.detail)
            if agent_id:
                tracked[agent.key] = {
                    "agentId": agent_id,
                    "name": agent.name,
                }
                print(f"[join] {agent.name} -> {agent_id}")
            else:
                print(f"[join-failed] {agent.name}")
                continue

        # Push current state
        entry = tracked[agent.key]
        if not entry.get("agentId"):
            # Corrupted entry without agentId — force re-join next cycle
            del tracked[agent.key]
            continue
        ok = client.push(entry["agentId"], agent.state, detail=agent.detail, name=agent.name)
        if ok:
            entry["name"] = agent.name
            entry["_fail_count"] = 0
        else:
            fail_count = entry.get("_fail_count", 0) + 1
            entry["_fail_count"] = fail_count
            print(f"[push-failed] {agent.name} ({entry['agentId']}) attempt {fail_count}")
            # After 3 consecutive failures, drop stale agentId so next cycle re-joins
            if fail_count >= 3:
                print(f"[re-join] dropping stale agentId for {agent.name}")
                del tracked[agent.key]

    # Remove agents that are no longer detected
    gone_keys = [k for k in tracked if k not in active_keys]
    for key in gone_keys:
        entry = tracked[key]
        if entry.get("is_main"):
            client.set_state("idle", detail="agent no longer detected")
            print(f"[idle] {entry['name']} (main, no longer detected)")
        else:
            agent_id = entry.get("agentId")
            if agent_id:
                client.leave(agent_id)
                print(f"[leave] {entry['name']} ({agent_id})")
        del tracked[key]

    return tracked


def main():
    parser = argparse.ArgumentParser(description="Star Office Auto-Detect Daemon")
    parser.add_argument(
        "--url",
        default=os.environ.get("STAR_OFFICE_URL", "http://127.0.0.1:28791"),
        help="Office backend URL",
    )
    parser.add_argument(
        "--key",
        default=os.environ.get("STAR_OFFICE_JOIN_KEY", "ocj_example_team_01"),
        help="Join key",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=int(os.environ.get("STAR_OFFICE_INTERVAL", "10")),
        help="Poll interval in seconds (default: 10)",
    )
    parser.add_argument(
        "--busy-threshold",
        type=int,
        default=120,
        help="OpenClaw busy threshold in seconds (default: 120)",
    )
    args = parser.parse_args()

    global _state_file_path
    _state_file_path = _make_state_file(args.url, args.key)

    client = OfficeClient(args.url, args.key)
    tracked = load_tracked()

    print(f"Star Office Auto-Detect Daemon started")
    print(f"  URL:      {args.url}")
    print(f"  Key:      {args.key[:8]}...")
    print(f"  Interval: {args.interval}s")

    running = True

    def shutdown(signum, frame):
        nonlocal running
        running = False

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    while running:
        try:
            detected = detect_all(busy_threshold=args.busy_threshold)
            tracked = sync_agents(client, tracked, detected)
            save_tracked(tracked)
        except Exception as e:
            print(f"[error] {e}")

        # Sleep in small increments so we can exit quickly
        for _ in range(args.interval * 2):
            if not running:
                break
            time.sleep(0.5)

    # Graceful cleanup
    print("Shutting down, removing tracked agents...")
    for key, entry in list(tracked.items()):
        if entry.get("is_main"):
            client.set_state("idle", detail="daemon stopped")
            print(f"[idle] {entry['name']} (main)")
        elif entry.get("agentId"):
            client.leave(entry["agentId"])
            print(f"[leave] {entry['name']}")
    save_tracked({})
    print("Done.")


if __name__ == "__main__":
    main()
