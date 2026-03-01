export interface HealthResponse {
  status: string
  timestamp: string
}

export interface LiveAgent {
  name: string
  emoji: string
  state: string
  detail: string
  color: string
  model: string
  updated_at?: string
  death_reason?: string
  last_log_ts?: string
  [key: string]: unknown
}

export interface LiveState {
  agents: Record<string, LiveAgent>
  updated_at?: string
}

export interface LiveLogEntry {
  ts: string
  type?: string
  role: string
  model?: string
  stop?: string
  text: string
  tool?: string
  inferred_state?: string
  death_reason?: string
  [key: string]: unknown
}

export interface ProviderStatus {
  online: boolean
  error?: string
  baseUrl?: string
  last_check?: string
  [key: string]: unknown
}

export interface LiveResponse {
  state: LiveState
  logs: Record<string, LiveLogEntry[]>
  providers: Record<string, ProviderStatus>
}

export interface TaskItem {
  id?: string
  task_id?: string
  task_name?: string
  name?: string
  status?: string
  priority?: string
  progress?: string | number
  agent?: string
  description?: string
  desc?: string
  [key: string]: unknown
}

export interface TasksResponse {
  tasks: TaskItem[]
}

export interface OllamaModel {
  name: string
  size_mb?: number
  family?: string
  params?: string
  quant?: string
  [key: string]: unknown
}

export interface OllamaActiveModel {
  name: string
  size_mb?: number
  expires?: string
  [key: string]: unknown
}

export interface OllamaResponse {
  running: boolean
  models: OllamaModel[]
  active: OllamaActiveModel[]
}

export interface ApiErrorInfo {
  message: string
  status?: number
  endpoint?: string
  cause?: unknown
}
