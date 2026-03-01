import type {
  LiveAgent,
  LiveLogEntry,
  LiveResponse,
  TaskItem as ApiTaskItem,
  TasksResponse,
} from '../api/types'
import type { Agent, AgentStatus, LogEntry, LogRole, TaskItem, TaskStatus } from '../types'

const FALLBACK_HIGHLIGHT_COLOR = '#7f9fc3'
const FALLBACK_EMOJI = '🤖'

const TEAM_BY_AGENT_ID: Record<string, string> = {
  main: '指挥中心',
  task1: '开发区',
  task2: '开发区',
  task3: '开发区',
  task4: '策划产品',
  task5: '情报室',
  task6: '金融区',
  task7: '指挥中心',
  task8: '策划产品',
  task9: '测试区',
  task10: '情报室',
  task11: '测试区',
  task12: '金融区',
  task13: '指挥中心',
  task14: '情报室',
  task15: '情报室',
  task16: '开发区',
}


const AGENT_NAME_TO_ID: Record<string, string> = {
  宗主: 'main',
  拉磨驴: 'task1',
  上等马: 'task2',
  看门狗: 'task3',
  领头羊: 'task4',
  出头鸟: 'task5',
  铁公鸡: 'task6',
  笑面虎: 'task7',
  妙法天尊: 'task8',
  天地一子: 'task9',
  探宝鼠: 'task10',
  知更鸟: 'task11',
  涨停板: 'task12',
  哲学猫: 'task13',
  旅行者: 'task14',
  派蒙: 'task15',
  大根骑士: 'task16',
}

function cleanupAgentDisplayName(value: string): string {
  return value
    .replace(/\p{Extended_Pictographic}|️|‍/gu, '')
    .replace(/\s+/g, '')
    .trim()
}

function normalizeHexColor(color: string | undefined): string {
  if (!color) {
    return FALLBACK_HIGHLIGHT_COLOR
  }

  const text = color.trim()
  if (/^#[0-9a-fA-F]{6}$/.test(text) || /^#[0-9a-fA-F]{3}$/.test(text)) {
    return text
  }

  return FALLBACK_HIGHLIGHT_COLOR
}

function toAgentStatus(rawStatus: string | undefined): AgentStatus {
  const normalized = (rawStatus ?? '').trim().toLowerCase()

  if (normalized === 'dead' || normalized === 'offline') {
    return 'dead'
  }

  if (normalized === 'error' || normalized === 'failed') {
    return 'error'
  }

  if (
    normalized === 'working'
    || normalized === 'busy'
    || normalized === 'executing'
    || normalized === 'researching'
    || normalized === 'syncing'
    || normalized === 'writing'
    || normalized === 'reviewing'
    || normalized === 'testing'
    || normalized === 'deploying'
    || normalized === 'meeting'
    || normalized === 'running'
    || normalized === 'in_progress'
    || normalized === 'processing'
  ) {
    return 'working'
  }

  return 'idle'
}

function toLogRole(rawRole: string | undefined): LogRole {
  const normalized = (rawRole ?? '').trim().toLowerCase()

  if (normalized === 'user') {
    return 'user'
  }

  if (normalized === 'assistant') {
    return 'assistant'
  }

  if (normalized === 'system') {
    return 'system'
  }

  return 'tool'
}

function resolveTaskStatus(raw: string | undefined): TaskStatus {
  const normalized = (raw ?? '').trim().toLowerCase()

  if (normalized.includes('完成') || normalized === 'done' || normalized === 'completed') {
    return '已完成'
  }

  if (
    normalized.includes('进行')
    || normalized === 'doing'
    || normalized === 'in_progress'
    || normalized === 'running'
  ) {
    return '进行中'
  }

  return '待办'
}

function resolveTaskPriority(raw: string | undefined): TaskItem['priority'] {
  const normalized = (raw ?? '').trim().toUpperCase()
  if (normalized === 'P0' || normalized === 'P1' || normalized === 'P2' || normalized === 'P3') {
    return normalized
  }

  return 'P2'
}

function parseTimestamp(value: string): number {
  const epoch = Date.parse(value)
  return Number.isFinite(epoch) ? epoch : Number.NaN
}

function formatTimestamp(value: string): string {
  if (!value.trim()) {
    return '--'
  }

  const epoch = parseTimestamp(value)
  if (Number.isNaN(epoch)) {
    return value.replace('T', ' ').slice(0, 19)
  }

  return new Date(epoch).toLocaleString('zh-CN', {
    hour12: false,
  })
}

function resolveOwnerAgentId(task: ApiTaskItem): string {
  const directId = typeof task.agent === 'string' ? task.agent.trim() : ''
  if (/^(main|task\d+)$/.test(directId)) {
    return directId
  }

  const richName = typeof task.agent === 'string' ? task.agent : ''
  const byEmbeddedId = Object.keys(TEAM_BY_AGENT_ID).find((id) => richName.includes(id))
  if (byEmbeddedId) {
    return byEmbeddedId
  }

  const normalizedDisplayName = cleanupAgentDisplayName(richName)
  const byDisplayName = Object.entries(AGENT_NAME_TO_ID).find(([displayName]) => normalizedDisplayName.includes(displayName))
  if (byDisplayName) {
    return byDisplayName[1]
  }

  return 'main'
}

function toTaskItem(task: ApiTaskItem, index: number): TaskItem {
  const id = (task.id ?? task.task_id ?? '').trim() || `task-${index}`
  const title = (task.task_name ?? task.name ?? '').trim() || `任务 ${index + 1}`
  const summary = (task.description ?? task.desc ?? '').trim() || '暂无描述'

  return {
    id,
    title,
    summary,
    ownerAgentId: resolveOwnerAgentId(task),
    priority: resolveTaskPriority(task.priority),
    status: resolveTaskStatus(task.status),
  }
}

function toLogEntry(agentId: string, log: LiveLogEntry, index: number): LogEntry {
  const stop = (log.stop ?? '').toLowerCase()
  const inferredState = (log.inferred_state ?? '').toLowerCase()
  const type = (log.type ?? '').toLowerCase()

  const isError = stop === 'error' || inferredState === 'error' || inferredState === 'dead' || type === 'error'
  const isDone = stop === 'stop' || inferredState === 'idle'

  return {
    id: `${agentId}:${log.ts || 'no-ts'}:${index}`,
    agentId,
    ts: formatTimestamp(log.ts),
    role: toLogRole(log.role),
    text: log.text?.trim() || '（空日志）',
    isError,
    isDone: isError ? false : isDone,
  }
}

function toAgent(agentId: string, liveAgent: LiveAgent): Agent {
  const name = liveAgent.name?.trim() || agentId
  const emoji = liveAgent.emoji?.trim() || FALLBACK_EMOJI
  const team = (typeof liveAgent.team === 'string' ? liveAgent.team : TEAM_BY_AGENT_ID[agentId]) || '未分组'

  return {
    id: agentId,
    name,
    emoji,
    team,
    status: toAgentStatus(liveAgent.state),
    highlightColor: normalizeHexColor(liveAgent.color),
  }
}

export function mapLiveAgents(live: LiveResponse): Agent[] {
  return Object.entries(live.state.agents)
    .map(([agentId, liveAgent]) => toAgent(agentId, liveAgent))
    .sort((left, right) => left.id.localeCompare(right.id))
}

export function mapLiveLogs(logsByAgent: Record<string, LiveLogEntry[]>): LogEntry[] {
  const entries: Array<{ rawTs: string; log: LogEntry }> = []

  Object.entries(logsByAgent).forEach(([agentId, logs]) => {
    logs.forEach((log, index) => {
      entries.push({
        rawTs: log.ts,
        log: toLogEntry(agentId, log, index),
      })
    })
  })

  entries.sort((left, right) => {
    const leftEpoch = parseTimestamp(left.rawTs)
    const rightEpoch = parseTimestamp(right.rawTs)

    if (!Number.isNaN(leftEpoch) && !Number.isNaN(rightEpoch)) {
      return leftEpoch - rightEpoch
    }

    return left.rawTs.localeCompare(right.rawTs)
  })

  return entries.map((entry) => entry.log)
}

export function mapTasks(tasksResponse: TasksResponse): TaskItem[] {
  return tasksResponse.tasks.map((task, index) => toTaskItem(task, index))
}
