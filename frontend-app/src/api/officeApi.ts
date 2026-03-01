import { HEALTH_EMPTY, LIVE_EMPTY, OLLAMA_EMPTY, TASKS_EMPTY } from './defaults'
import { ApiError, requestJson } from './http'
import { normalizeHealth, normalizeLive, normalizeOllama, normalizeTasks } from './normalizers'
import type { HealthResponse, LiveResponse, OllamaResponse, TasksResponse } from './types'

export interface SafeApiResult<T> {
  data: T
  error: ApiError | null
}

export class OfficeApi {
  private readonly baseUrl: string

  constructor(baseUrl = import.meta.env.VITE_API_BASE_URL ?? '') {
    this.baseUrl = baseUrl.replace(/\/$/, '')
  }

  async getHealth(signal?: AbortSignal): Promise<HealthResponse> {
    const endpoint = this.buildEndpoint('/health')
    const payload = await requestJson<unknown>(endpoint, { signal, timeoutMs: 5_000 })
    return normalizeHealth(payload)
  }

  async getLive(signal?: AbortSignal): Promise<LiveResponse> {
    const endpoint = this.buildEndpoint('/live')
    const payload = await requestJson<unknown>(endpoint, { signal, timeoutMs: 10_000 })
    return normalizeLive(payload)
  }

  async getTasks(signal?: AbortSignal): Promise<TasksResponse> {
    const endpoint = this.buildEndpoint('/tasks')
    const payload = await requestJson<unknown>(endpoint, { signal, timeoutMs: 10_000 })
    return normalizeTasks(payload)
  }

  async getOllama(signal?: AbortSignal): Promise<OllamaResponse> {
    const endpoint = this.buildEndpoint('/ollama')
    const payload = await requestJson<unknown>(endpoint, { signal, timeoutMs: 8_000 })
    return normalizeOllama(payload)
  }

  async getHealthSafe(signal?: AbortSignal): Promise<SafeApiResult<HealthResponse>> {
    return safeRequest(() => this.getHealth(signal), HEALTH_EMPTY)
  }

  async getLiveSafe(signal?: AbortSignal): Promise<SafeApiResult<LiveResponse>> {
    return safeRequest(() => this.getLive(signal), LIVE_EMPTY)
  }

  async getTasksSafe(signal?: AbortSignal): Promise<SafeApiResult<TasksResponse>> {
    return safeRequest(() => this.getTasks(signal), TASKS_EMPTY)
  }

  async getOllamaSafe(signal?: AbortSignal): Promise<SafeApiResult<OllamaResponse>> {
    return safeRequest(() => this.getOllama(signal), OLLAMA_EMPTY)
  }

  private buildEndpoint(path: string): string {
    if (!this.baseUrl) {
      return path
    }
    return `${this.baseUrl}${path}`
  }
}

async function safeRequest<T>(
  fetcher: () => Promise<T>,
  fallback: T,
): Promise<SafeApiResult<T>> {
  try {
    const data = await fetcher()
    return { data, error: null }
  } catch (error) {
    const apiError =
      error instanceof ApiError
        ? error
        : new ApiError('未知请求错误', {
            cause: error,
          })

    return {
      data: fallback,
      error: apiError,
    }
  }
}

export const officeApi = new OfficeApi()
