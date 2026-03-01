#!/usr/bin/env python3
"""飞书多维表格 API 封装 — AI特工队任务看板"""

import json, time, urllib.request, urllib.error

APP_ID = "cli_a92bf363c7ba1bd6"
APP_SECRET = "UuxWk8UGW9KdPS61VR2yubvHmAjrENEp"
APP_TOKEN = "FJwkbkGtma2QS7sIjlScMXHWnrb"
TABLE_ID = "tblZwTpj2jzTkdWB"

# 字段ID映射（从API获取的）
FIELD_MAP = {
    "任务ID": "fldQvQ7S43",
    "任务名称": "fldmKdJIPg",
    "负责Agent": "fld2nZExae",
    "状态": "fldiyu7Cav",
    "进度": "fldTbnAliE",
    "优先级": "fld7jEvCtq",
    "开始时间": "fldJdrJA8E",
    "完成时间": "fldkKRIqf8",
    "产出文档": "fld34FrZLs",
    "需求描述": "fldvjHx7U5",
    "备注": "fldwQOrkCj",
}

_token_cache = {"token": None, "expire": 0}


def _get_token():
    now = time.time()
    if _token_cache["token"] and now < _token_cache["expire"] - 60:
        return _token_cache["token"]
    data = json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode()
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    resp = json.loads(urllib.request.urlopen(req).read())
    if resp.get("code") == 0:
        _token_cache["token"] = resp["tenant_access_token"]
        _token_cache["expire"] = now + resp.get("expire", 7200)
        return _token_cache["token"]
    raise Exception(f"Failed to get token: {resp}")


def _api(method, path, body=None):
    token = _get_token()
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}{path}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = json.dumps(body, ensure_ascii=False).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        return {"code": e.code, "msg": err}


AGENT_NAMES = {
    "main": "🗡️宗主", "task1": "🫏拉磨驴", "task2": "🐴上等马",
    "task3": "🐕看门狗", "task4": "🐑领头羊", "task5": "🐦出头鸟",
    "task6": "🐔铁公鸡", "task7": "🐯笑面虎", "task8": "🔮妙法天尊",
    "task9": "⚡天地一子", "task10": "🐭探宝鼠", "task11": "🐦‍⬛知更鸟",
    "task12": "📈涨停板", "task13": "🐱哲学猫", "task14": "🧳旅行者",
    "task15": "🎀派蒙", "task16": "⚔️大根骑士",
}



def _to_int(v, default=0):
    """飞书字段值安全转 int，兼容 None/空串/浮点串。"""
    try:
        if v is None or v == "":
            return default
        return int(float(v))
    except Exception:
        return default



def add_task(task_id, name, agent_id, priority="P1", description=""):
    """添加一条任务记录"""
    agent_name = AGENT_NAMES.get(agent_id, agent_id)
    fields = {
        "任务ID": task_id,
        "任务名称": name,
        "负责Agent": agent_name,
        "状态": "待办",
        "进度": 0,
        "优先级": priority,
        "开始时间": int(time.time()) * 1000,
        "需求描述": description,
    }
    return _api("POST", "/records", {"fields": fields})


def update_task(record_id, updates):
    """更新任务记录
    updates: dict, 如 {"状态": "进行中", "进度": 50, "备注": "xxx"}
    """
    return _api("PUT", f"/records/{record_id}", {"fields": updates})


def complete_task(record_id, note=""):
    """标记任务完成"""
    fields = {
        "状态": "已完成",
        "进度": 100,
        "完成时间": int(time.time()) * 1000,
    }
    if note:
        fields["备注"] = note
    return _api("PUT", f"/records/{record_id}", {"fields": fields})


def list_tasks(filter_str=None, page_size=100):
    """查询任务列表"""
    path = f"/records?page_size={page_size}"
    if filter_str:
        import urllib.parse
        path += f"&filter={urllib.parse.quote(filter_str)}"
    return _api("GET", path)


def find_task_by_id(task_id):
    """根据任务ID查找记录"""
    result = list_tasks(f'CurrentValue.[任务ID]="{task_id}"')
    items = result.get("data", {}).get("items", [])
    return items[0] if items else None


def get_all_tasks():
    """获取所有任务，返回简化列表"""
    result = list_tasks()
    items = result.get("data", {}).get("items", [])
    tasks = []
    for item in items:
        f = item.get("fields", {})
        tasks.append({
            "record_id": item.get("record_id", ""),
            "task_id": f.get("任务ID", ""),
            "name": f.get("任务名称", ""),
            "agent": f.get("负责Agent", ""),
            "status": f.get("状态", ""),
            "progress": int(f.get("进度", 0) or 0),
            "priority": f.get("优先级", ""),
            "description": f.get("需求描述", ""),
            "note": f.get("备注", ""),
            # 供前端“最近完成”排序（毫秒时间戳）
            "start_time": _to_int(f.get("开始时间"), 0),
            "completed_time": _to_int(f.get("完成时间"), 0),
        })
    return tasks


def delete_task(record_id):
    """删除任务记录"""
    return _api("DELETE", f"/records/{record_id}")


# ============ 测试 ============
if __name__ == "__main__":
    print("Testing feishu API...")
    print("Token:", _get_token()[:20] + "...")
    result = add_task("test-001", "测试任务", "main", "P2", "这是一个测试任务")
    print("Add task:", result.get("msg", ""))
    if result.get("data", {}).get("record", {}).get("record_id"):
        rid = result["data"]["record"]["record_id"]
        print("Record ID:", rid)
        update_task(rid, {"状态": "进行中", "进度": 30})
        print("Updated to 进行中")
        tasks = get_all_tasks()
        print(f"Total tasks: {len(tasks)}")
        for t in tasks:
            print(f"  {t['task_id']}: {t['name']} [{t['status']}] {t['progress']}%")
