"""
Star Office API client — handles join / push / leave calls.
"""

import json
import urllib.request
import urllib.error
from typing import Optional


class OfficeClient:
    """Lightweight HTTP client for Star Office backend API."""

    def __init__(self, office_url: str, join_key: str, timeout: int = 5):
        self.office_url = office_url.rstrip("/")
        self.join_key = join_key
        self.timeout = timeout

    def _post(self, endpoint: str, data: dict) -> dict:
        try:
            req = urllib.request.Request(
                f"{self.office_url}{endpoint}",
                data=json.dumps(data).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            resp = urllib.request.urlopen(req, timeout=self.timeout)
            return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            try:
                body = json.loads(e.read())
            except Exception:
                body = {"error": str(e)}
            return body
        except Exception as e:
            return {"error": str(e)}

    def join(self, name: str, state: str = "idle", detail: str = "") -> Optional[str]:
        """Join the office. Returns agentId on success, None on failure."""
        payload = {
            "name": name,
            "joinKey": self.join_key,
            "state": state,
            "detail": detail,
        }
        result = self._post("/join-agent", payload)
        return result.get("agentId")

    def push(self, agent_id: str, state: str, detail: str = "", name: str = "") -> bool:
        """Push agent state update. Returns True on success."""
        payload = {
            "agentId": agent_id,
            "joinKey": self.join_key,
            "state": state,
            "detail": detail,
        }
        if name:
            payload["name"] = name
        result = self._post("/agent-push", payload)
        return result.get("ok", False)

    def set_state(self, state: str, detail: str = "") -> bool:
        """Set the main agent (Star) state via /set_state."""
        payload = {"state": state, "detail": detail}
        result = self._post("/set_state", payload)
        return result.get("ok", False) or result.get("status") == "ok"

    def leave(self, agent_id: str) -> bool:
        """Leave the office. Returns True on success."""
        payload = {
            "agentId": agent_id,
            "joinKey": self.join_key,
        }
        result = self._post("/leave-agent", payload)
        return result.get("ok", False)
