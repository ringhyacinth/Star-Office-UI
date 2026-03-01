export class ApiError extends Error {
  readonly status?: number
  readonly endpoint?: string
  readonly cause?: unknown

  constructor(message: string, opts?: { status?: number; endpoint?: string; cause?: unknown }) {
    super(message)
    this.name = 'ApiError'
    this.status = opts?.status
    this.endpoint = opts?.endpoint
    this.cause = opts?.cause
  }
}

export interface RequestJsonOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'
  body?: unknown
  headers?: Record<string, string>
  signal?: AbortSignal
  timeoutMs?: number
}

const DEFAULT_TIMEOUT_MS = 8_000

async function parseBodyAsJson(response: Response): Promise<unknown> {
  const raw = await response.text()
  if (!raw) {
    return {}
  }

  try {
    return JSON.parse(raw) as unknown
  } catch {
    return { raw }
  }
}

export async function requestJson<T>(endpoint: string, options: RequestJsonOptions = {}): Promise<T> {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), options.timeoutMs ?? DEFAULT_TIMEOUT_MS)

  const signals: AbortSignal[] = [controller.signal]
  if (options.signal) {
    signals.push(options.signal)
  }

  const signal = mergeSignals(signals)

  try {
    const response = await fetch(endpoint, {
      method: options.method ?? 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      body: options.body ? JSON.stringify(options.body) : undefined,
      signal,
    })

    const data = await parseBodyAsJson(response)

    if (!response.ok) {
      const message = getHttpErrorMessage(response.status, data)
      throw new ApiError(message, {
        status: response.status,
        endpoint,
        cause: data,
      })
    }

    return data as T
  } catch (error) {
    if (error instanceof ApiError) {
      throw error
    }

    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new ApiError('请求超时或已取消', {
        endpoint,
        cause: error,
      })
    }

    throw new ApiError('网络请求失败', {
      endpoint,
      cause: error,
    })
  } finally {
    clearTimeout(timeout)
  }
}

function getHttpErrorMessage(status: number, payload: unknown): string {
  if (payload && typeof payload === 'object' && 'error' in payload) {
    const maybeError = (payload as { error?: unknown }).error
    if (typeof maybeError === 'string' && maybeError.trim()) {
      return `HTTP ${status}: ${maybeError}`
    }
  }
  return `HTTP ${status}`
}

function mergeSignals(signals: AbortSignal[]): AbortSignal {
  if (signals.length === 1) {
    return signals[0]
  }

  const controller = new AbortController()

  const onAbort = () => {
    controller.abort()
  }

  for (const signal of signals) {
    if (signal.aborted) {
      controller.abort()
      break
    }
    signal.addEventListener('abort', onAbort, { once: true })
  }

  return controller.signal
}
