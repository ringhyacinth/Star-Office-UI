#!/usr/bin/env python3
"""状态更新工具 - 匹配 OpenClaw Agents"""

import json, os, sys
from datetime import datetime

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json")

VALID_STATES = ["idle", "writing", "researching", "executing", "syncing",
                "error", "reviewing", "testing", "deploying", "meeting"]

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"agents": {}, "updated_at": datetime.now().isoformat()}

def save_state(state):
    state["updated_at"] = datetime.now().isoformat()
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python set_state.py <agent-id> <state> [detail]")
        print(f"  agent-id: main, task1~task9, 或 all")
        print(f"  状态: {', '.join(VALID_STATES)}")
        print("\n例子:")
        print("  python set_state.py main executing \"指挥全局\"")
        print("  python set_state.py task7 writing \"笑面虎在写代码\"")
        print("  python set_state.py all idle \"全员休息\"")
        sys.exit(1)

    agent_id = sys.argv[1]
    state_name = sys.argv[2]
    detail = sys.argv[3] if len(sys.argv) > 3 else ""

    if state_name not in VALID_STATES:
        print(f"无效状态: {state_name}  有效: {', '.join(VALID_STATES)}")
        sys.exit(1)

    state = load_state()
    agents = state.get("agents", {})
    now = datetime.now().isoformat()

    if agent_id == "all":
        for aid in agents:
            agents[aid]["state"] = state_name
            agents[aid]["detail"] = detail
            agents[aid]["updated_at"] = now
        print(f"全部 agent 已更新: {state_name} - {detail}")
    elif agent_id in agents:
        agents[agent_id]["state"] = state_name
        agents[agent_id]["detail"] = detail
        agents[agent_id]["updated_at"] = now
        name = agents[agent_id].get("name", agent_id)
        emoji = agents[agent_id].get("emoji", "")
        print(f"{emoji} {name} ({agent_id}) → {state_name}: {detail}")
    else:
        print(f"未找到 {agent_id}，可用: {', '.join(agents.keys())}")
        sys.exit(1)

    save_state(state)
