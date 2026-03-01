import type { HealthResponse, LiveResponse, OllamaResponse, TasksResponse } from './types'

export const HEALTH_EMPTY: HealthResponse = {
  status: 'unknown',
  timestamp: '',
}

export const LIVE_EMPTY: LiveResponse = {
  state: {
    agents: {},
    updated_at: '',
  },
  logs: {},
  providers: {},
}

export const TASKS_EMPTY: TasksResponse = {
  tasks: [],
}

export const OLLAMA_EMPTY: OllamaResponse = {
  running: false,
  models: [],
  active: [],
}
