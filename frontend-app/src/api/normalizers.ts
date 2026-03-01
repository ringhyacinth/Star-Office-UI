import { HEALTH_EMPTY, LIVE_EMPTY, TASKS_EMPTY } from './defaults'
import type {
  HealthResponse,
  LiveAgent,
  LiveLogEntry,
  LiveResponse,
  OllamaActiveModel,
  OllamaModel,
  OllamaResponse,
  ProviderStatus,
  TaskItem,
  TasksResponse,
} from './types'

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : {}
}

function asArray(value: unknown): unknown[] {
  return Array.isArray(value) ? value : []
}

function asString(value: unknown, fallback = ''): string {
  if (typeof value === 'string') {
    return value
  }

  if (typeof value === 'number' || typeof value === 'boolean') {
    return String(value)
  }

  return fallback
}

function asBoolean(value: unknown, fallback = false): boolean {
  if (typeof value === 'boolean') {
    return value
  }

  if (typeof value === 'number') {
    return value !== 0
  }

  if (typeof value === 'string') {
    const normalized = value.trim().toLowerCase()
    if (['true', '1', 'yes', 'ok', 'online', 'up', 'healthy', 'running'].includes(normalized)) {
      return true
    }

    if (['false', '0', 'no', 'offline', 'down', 'error'].includes(normalized)) {
      return false
    }
  }

  return fallback
}

function asNumber(value: unknown): number | undefined {
  return typeof value === 'number' && Number.isFinite(value) ? value : undefined
}

function pickString(source: Record<string, unknown>, keys: string[], fallback = ''): string {
  for (const key of keys) {
    const text = asString(source[key]).trim()
    if (text) {
      return text
    }
  }
  return fallback
}

function firstDefined(values: unknown[]): unknown {
  for (const value of values) {
    if (value !== undefined && value !== null) {
      return value
    }
  }
  return undefined
}

function isLikelyAgentObject(source: Record<string, unknown>): boolean {
  return (
    'id' in source
    || 'agent_id' in source
    || 'agentId' in source
    || 'name' in source
    || 'emoji' in source
    || 'state' in source
    || 'status' in source
    || 'model' in source
  )
}

function isLikelyAgentMap(source: Record<string, unknown>): boolean {
  const entries = Object.entries(source)
  if (entries.length === 0) {
    return false
  }

  let hints = 0
  for (const [key, value] of entries) {
    if (['updated_at', 'updatedAt', 'logs', 'providers'].includes(key)) {
      continue
    }

    if (/^(main|task\d+|agent[-_]?\d+)$/i.test(key)) {
      hints += 1
      continue
    }

    const child = asRecord(value)
    if (isLikelyAgentObject(child)) {
      hints += 1
    }
  }

  return hints > 0
}

function resolveAgentId(payload: unknown, fallback = ''): string {
  const source = asRecord(payload)
  const resolved = pickString(source, ['id', 'agent_id', 'agentId', 'agent'])
  if (resolved) {
    return resolved
  }

  if (fallback) {
    return fallback
  }

  const byName = pickString(source, ['name', 'agent_name', 'display_name'])
  if (byName) {
    return byName
  }

  return ''
}

export function normalizeHealth(payload: unknown): HealthResponse {
  const source = asRecord(payload)
  return {
    status: pickString(source, ['status', 'state', 'health'], HEALTH_EMPTY.status),
    timestamp: pickString(source, ['timestamp', 'updated_at', 'updatedAt', 'time'], HEALTH_EMPTY.timestamp),
  }
}

function normalizeAgent(payload: unknown, fallbackId = ''): LiveAgent {
  const source = asRecord(payload)
  const fallbackName = fallbackId || 'unknown'

  return {
    name: pickString(source, ['name', 'agent_name', 'display_name', 'title'], fallbackName),
    emoji: pickString(source, ['emoji', 'icon'], ''),
    state: pickString(source, ['state', 'status', 'agent_state'], 'idle'),
    detail: pickString(source, ['detail', 'description', 'desc', 'message', 'summary'], ''),
    color: pickString(source, ['color', 'highlightColor', 'highlight_color'], '#78909C'),
    model: pickString(source, ['model', 'model_name', 'modelId'], ''),
    updated_at: pickString(source, ['updated_at', 'updatedAt', 'timestamp'], ''),
    death_reason: pickString(source, ['death_reason', 'deathReason', 'reason', 'error'], ''),
    last_log_ts: pickString(source, ['last_log_ts', 'lastLogTs', 'last_ts'], ''),
  }
}

function readLogTextFromContent(content: unknown): string {
  if (typeof content === 'string' || typeof content === 'number' || typeof content === 'boolean') {
    return asString(content)
  }

  if (Array.isArray(content)) {
    for (const item of content) {
      const source = asRecord(item)
      const text = pickString(source, ['text', 'message', 'content', 'output_text', 'output'])
      if (text) {
        return text
      }
    }
    return ''
  }

  const source = asRecord(content)
  const direct = pickString(source, ['text', 'message', 'content', 'output'])
  if (direct) {
    return direct
  }

  if (Object.keys(source).length > 0) {
    try {
      return JSON.stringify(source)
    } catch {
      return ''
    }
  }

  return ''
}

function normalizeLog(payload: unknown): LiveLogEntry {
  if (typeof payload === 'string' || typeof payload === 'number' || typeof payload === 'boolean') {
    return {
      ts: '',
      type: '',
      role: 'system',
      model: '',
      stop: '',
      text: asString(payload),
      tool: '',
      inferred_state: '',
      death_reason: '',
    }
  }

  const source = asRecord(payload)
  const type = pickString(source, ['type'], '')

  const role = pickString(source, ['role', 'sender', 'actor'], '')
    || (['assistant', 'user', 'system', 'tool', 'toolResult'].includes(type) ? type : 'system')

  let text = pickString(source, ['text', 'message', 'msg', 'summary', 'output', 'result', 'body'], '')
  if (!text) {
    text = readLogTextFromContent(source.content)
  }

  if (!text) {
    text = pickString(source, ['error', 'error_message', 'errorMessage'], '')
  }

  return {
    ts: pickString(source, ['ts', 'timestamp', 'time', 'created_at', 'createdAt'], ''),
    type,
    role,
    model: pickString(source, ['model', 'modelId', 'model_name'], ''),
    stop: pickString(source, ['stop', 'stop_reason', 'stopReason'], ''),
    text,
    tool: pickString(source, ['tool', 'tool_name', 'toolName', 'name'], ''),
    inferred_state: pickString(source, ['inferred_state', 'state', 'status'], ''),
    death_reason: pickString(source, ['death_reason', 'deathReason', 'reason', 'error'], ''),
  }
}

function isLikelyLogEntry(source: Record<string, unknown>): boolean {
  return (
    'ts' in source
    || 'timestamp' in source
    || 'text' in source
    || 'message' in source
    || 'content' in source
    || 'role' in source
    || 'stop' in source
    || 'error' in source
    || 'error_message' in source
  )
}

function resolveLogAgentId(payload: unknown, fallback = ''): string {
  const source = asRecord(payload)
  const direct = pickString(source, ['agent_id', 'agentId', 'agent', 'ownerAgentId', 'source_agent', 'sourceAgent'])
  if (direct) {
    return direct
  }

  if (fallback && !['logs', 'log', 'items', 'entries', 'messages'].includes(fallback)) {
    return fallback
  }

  return 'unknown'
}

function appendLog(
  target: Record<string, LiveLogEntry[]>,
  agentId: string,
  payload: unknown,
) {
  if (!target[agentId]) {
    target[agentId] = []
  }

  target[agentId].push(normalizeLog(payload))
}

function normalizeLogs(raw: unknown): Record<string, LiveLogEntry[]> {
  const result: Record<string, LiveLogEntry[]> = {}

  if (Array.isArray(raw)) {
    raw.forEach((entry) => {
      appendLog(result, resolveLogAgentId(entry), entry)
    })
    return result
  }

  const source = asRecord(raw)
  Object.entries(source).forEach(([key, value]) => {
    if (Array.isArray(value)) {
      value.forEach((entry) => {
        appendLog(result, resolveLogAgentId(entry, key), entry)
      })
      return
    }

    if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
      appendLog(result, key, value)
      return
    }

    const valueRecord = asRecord(value)
    const logs = asArray(valueRecord.logs)
    if (logs.length > 0) {
      logs.forEach((entry) => {
        appendLog(result, resolveLogAgentId(entry, key), entry)
      })
      return
    }

    if (isLikelyLogEntry(valueRecord)) {
      appendLog(result, resolveLogAgentId(valueRecord, key), valueRecord)
      return
    }

    Object.entries(valueRecord).forEach(([nestedKey, nestedValue]) => {
      if (Array.isArray(nestedValue)) {
        nestedValue.forEach((entry) => {
          appendLog(result, resolveLogAgentId(entry, nestedKey || key), entry)
        })
        return
      }

      const nestedRecord = asRecord(nestedValue)
      if (isLikelyLogEntry(nestedRecord)) {
        appendLog(result, resolveLogAgentId(nestedRecord, nestedKey || key), nestedRecord)
      }
    })
  })

  return result
}

function normalizeProvider(payload: unknown): ProviderStatus {
  const source = asRecord(payload)
  const statusText = pickString(source, ['status', 'state', 'health'], '')
  const inferredOnline = ['online', 'ok', 'healthy', 'up', 'running'].includes(statusText.toLowerCase())

  const onlineValue = firstDefined([
    source.online,
    source.is_online,
    source.available,
    source.healthy,
    source.up,
    statusText,
  ])

  return {
    online: asBoolean(onlineValue, inferredOnline),
    error: pickString(source, ['error', 'message', 'reason'], ''),
    baseUrl: pickString(source, ['baseUrl', 'base_url', 'url', 'endpoint'], ''),
    last_check: pickString(source, ['last_check', 'lastCheck', 'checked_at', 'updated_at', 'timestamp'], ''),
  }
}

function resolveProviderId(payload: unknown, fallback = ''): string {
  const source = asRecord(payload)
  return pickString(source, ['id', 'provider_id', 'provider', 'name', 'key'], fallback || 'default')
}

function normalizeProviders(raw: unknown): Record<string, ProviderStatus> {
  const result: Record<string, ProviderStatus> = {}

  if (Array.isArray(raw)) {
    raw.forEach((item, index) => {
      const id = resolveProviderId(item, `provider-${index + 1}`)
      result[id] = normalizeProvider(item)
    })
    return result
  }

  const source = asRecord(raw)
  Object.entries(source).forEach(([key, value]) => {
    if (typeof value === 'boolean' || typeof value === 'number' || typeof value === 'string') {
      result[key] = normalizeProvider({ online: value })
      return
    }

    const id = resolveProviderId(value, key)
    result[id] = normalizeProvider(value)
  })

  return result
}

function normalizeAgents(raw: unknown): Record<string, LiveAgent> {
  const result: Record<string, LiveAgent> = {}

  if (Array.isArray(raw)) {
    raw.forEach((item, index) => {
      const id = resolveAgentId(item, `agent-${index + 1}`)
      result[id] = normalizeAgent(item, id)
    })
    return result
  }

  const source = asRecord(raw)
  Object.entries(source).forEach(([key, value]) => {
    if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
      result[key] = normalizeAgent({ id: key, name: key, state: asString(value) }, key)
      return
    }

    const id = resolveAgentId(value, key) || key
    result[id] = normalizeAgent(value, id)
  })

  return result
}

export function normalizeLive(payload: unknown): LiveResponse {
  const source = asRecord(payload)
  const rawState = source.state
  const stateSource = asRecord(rawState)

  const agentsRaw = firstDefined([
    stateSource.agents,
    source.agents,
    Array.isArray(rawState) ? rawState : undefined,
    isLikelyAgentMap(stateSource) ? stateSource : undefined,
  ])

  const logsRaw = firstDefined([
    source.logs,
    source.log,
    stateSource.logs,
    source.messages,
    stateSource.messages,
  ])

  const providersRaw = firstDefined([
    source.providers,
    source.provider_status,
    source.providerStatus,
    stateSource.providers,
  ])

  const updatedAt = pickString(
    stateSource,
    ['updated_at', 'updatedAt', 'timestamp'],
    pickString(source, ['updated_at', 'updatedAt', 'timestamp'], LIVE_EMPTY.state.updated_at),
  )

  return {
    state: {
      agents: normalizeAgents(agentsRaw),
      updated_at: updatedAt,
    },
    logs: normalizeLogs(logsRaw),
    providers: normalizeProviders(providersRaw),
  }
}

function normalizeTask(payload: unknown): TaskItem {
  const source = asRecord(payload)
  return {
    id: pickString(source, ['id', 'task_id', 'record_id'], ''),
    task_id: pickString(source, ['task_id', 'id', 'record_id'], ''),
    task_name: pickString(source, ['task_name', 'name', 'title'], ''),
    name: pickString(source, ['name', 'task_name', 'title'], ''),
    status: pickString(source, ['status', 'state'], ''),
    priority: pickString(source, ['priority', 'level'], ''),
    progress: pickString(source, ['progress'], '') || asNumber(source.progress),
    agent: pickString(source, ['agent', 'owner', 'ownerAgentId'], ''),
    description: pickString(source, ['description', 'desc', 'summary'], ''),
    desc: pickString(source, ['desc', 'description', 'summary'], ''),
  }
}

export function normalizeTasks(payload: unknown): TasksResponse {
  const source = asRecord(payload)
  const directArray = Array.isArray(payload) ? payload : undefined

  const tasks =
    asArray(firstDefined([
      source.tasks,
      source.items,
      source.list,
      source.data,
      directArray,
    ])).map((task) => normalizeTask(task))

  return {
    tasks: tasks.length > 0 ? tasks : TASKS_EMPTY.tasks,
  }
}

function normalizeOllamaModel(payload: unknown): OllamaModel {
  const source = asRecord(payload)
  return {
    name: pickString(source, ['name', 'model', 'id'], ''),
    size_mb: asNumber(firstDefined([source.size_mb, source.size])),
    family: pickString(source, ['family'], ''),
    params: pickString(source, ['params', 'parameter_size'], ''),
    quant: pickString(source, ['quant', 'quantization_level'], ''),
  }
}

function normalizeOllamaActive(payload: unknown): OllamaActiveModel {
  const source = asRecord(payload)
  return {
    name: pickString(source, ['name', 'model', 'id'], ''),
    size_mb: asNumber(firstDefined([source.size_mb, source.size])),
    expires: pickString(source, ['expires', 'expires_at', 'expire_at'], ''),
  }
}

export function normalizeOllama(payload: unknown): OllamaResponse {
  const source = asRecord(payload)
  const models = asArray(firstDefined([source.models, source.loaded, source.tags]))
  const active = asArray(firstDefined([source.active, source.running_models, source.running]))

  return {
    running: asBoolean(source.running, active.length > 0),
    models: models.map((model) => normalizeOllamaModel(model)),
    active: active.map((model) => normalizeOllamaActive(model)),
  }
}
