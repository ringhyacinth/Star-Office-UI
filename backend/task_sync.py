#!/usr/bin/env python3
"""OpenClaw Session -> 飞书任务自动同步"""

import json
import os
import glob
import time
from datetime import datetime

OPENCLAW_DIR = os.path.expanduser("~/.openclaw")

# 任务状态映射
SESSION_TO_TASK_STATUS = {
    "idle": "待办",
    "writing": "进行中",
    "researching": "进行中",
    "executing": "进行中",
    "syncing": "进行中",
    "reviewing": "进行中",
    "testing": "进行中",
    "deploying": "进行中",
    "meeting": "进行中",
    "error": "异常",
    "dead": "异常",
}

def get_active_sessions():
    """获取所有agent的活跃session"""
    sessions = {}
    agents_dir = os.path.join(OPENCLAW_DIR, "agents")
    
    if not os.path.isdir(agents_dir):
        return sessions
    
    for agent_name in os.listdir(agents_dir):
        agent_path = os.path.join(agents_dir, agent_name)
        sessions_dir = os.path.join(agent_path, "sessions")
        
        if not os.path.isdir(sessions_dir):
            continue
        
        # 获取最新的活跃session
        session_files = glob.glob(os.path.join(sessions_dir, "*.jsonl"))
        session_files = [f for f in session_files if not f.endswith(".deleted")]
        
        if not session_files:
            continue
        
        # 按修改时间排序，取最新的
        latest_session = max(session_files, key=os.path.getmtime)
        
        try:
            # 读取session信息
            with open(latest_session, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if not lines:
                continue
            
            # 解析第一行获取session元数据
            first_line = json.loads(lines[0])
            session_id = os.path.basename(latest_session).replace('.jsonl', '')
            
            # 提取用户的第一条消息作为任务描述
            task_description = ""
            for line in lines:
                try:
                    msg = json.loads(line)
                    if msg.get('type') == 'message':
                        role = msg.get('message', {}).get('role')
                        if role == 'user':
                            content = msg.get('message', {}).get('content', [])
                            for c in content:
                                if c.get('type') == 'text':
                                    task_description = c.get('text', '')[:200]
                                    break
                            if task_description:
                                break
                except:
                    continue
            
            # 计算进度（基于消息数量的简单估算）
            total_messages = len(lines)
            progress = min(int((total_messages / 20) * 100), 95)  # 最多95%，完成时才100%
            
            # 检查是否已完成
            is_completed = False
            last_line = json.loads(lines[-1]) if lines else {}
            if last_line.get('type') == 'message':
                stop_reason = last_line.get('message', {}).get('stopReason')
                if stop_reason in ('stop', 'endTurn'):
                    is_completed = True
                    progress = 100
            
            sessions[agent_name] = {
                'session_id': session_id,
                'task_description': task_description or f"{agent_name} 工作中",
                'progress': progress,
                'is_completed': is_completed,
                'message_count': total_messages,
                'last_update': os.path.getmtime(latest_session),
            }
        except Exception as e:
            print(f"解析 {agent_name} session 失败: {e}")
            continue
    
    return sessions

def sync_to_feishu(sessions):
    """同步session到飞书任务"""
    try:
        from feishu import add_task, update_task, complete_task, get_all_tasks, find_task_by_id
    except ImportError:
        print("飞书模块未安装")
        return
    
    # 获取现有任务
    existing_tasks = {t['task_id']: t for t in get_all_tasks()}
    
    for agent_name, session_info in sessions.items():
        task_id = f"session-{agent_name}-{session_info['session_id'][:8]}"
        
        # 检查任务是否已存在
        if task_id in existing_tasks:
            # 更新现有任务
            task = existing_tasks[task_id]
            record_id = task['record_id']
            
            updates = {
                '进度': session_info['progress'],
            }
            
            # 根据进度更新状态
            if session_info['is_completed']:
                updates['状态'] = '已完成'
                updates['完成时间'] = int(time.time()) * 1000
            elif session_info['progress'] > 0:
                updates['状态'] = '进行中'
            
            update_task(record_id, updates)
            print(f"✅ 更新任务: {agent_name} - {session_info['progress']}%", flush=True)
        else:
            # 创建新任务
            result = add_task(
                task_id=task_id,
                name=session_info['task_description'],
                agent_id=agent_name,
                priority="P2",
                description=f"Session: {session_info['session_id']}"
            )
            print(f"✅ 创建任务: {agent_name} - {session_info['task_description'][:50]}", flush=True)

def main():
    """主循环"""
    print("🚀 OpenClaw -> 飞书任务同步器启动", flush=True)
    
    while True:
        try:
            sessions = get_active_sessions()
            if sessions:
                print(f"\n📊 发现 {len(sessions)} 个活跃session", flush=True)
                sync_to_feishu(sessions)
            else:
                print(".", end="", flush=True)
            
            time.sleep(10)  # 每10秒检查一次
        except KeyboardInterrupt:
            print("\n👋 同步器已停止", flush=True)
            break
        except Exception as e:
            print(f"\n❌ 同步错误: {e}", flush=True)
            time.sleep(30)

if __name__ == "__main__":
    main()
