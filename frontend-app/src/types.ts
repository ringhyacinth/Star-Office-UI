export type AgentStatus = 'idle' | 'working' | 'error' | 'dead'

export interface Agent {
  id: string
  name: string
  emoji: string
  team: string
  status: AgentStatus
  highlightColor: string
}

export type LogRole = 'user' | 'assistant' | 'tool' | 'system'

export interface LogEntry {
  id: string
  agentId: string
  ts: string
  role: LogRole
  text: string
  isError?: boolean
  isDone?: boolean
}

export type TaskStatus = '进行中' | '待办' | '已完成'

export interface TaskItem {
  id: string
  title: string
  summary: string
  ownerAgentId: string
  priority: 'P0' | 'P1' | 'P2' | 'P3'
  status: TaskStatus
}

export type LogQuickFilter = 'all' | 'error' | 'done'
