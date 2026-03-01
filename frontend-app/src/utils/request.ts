const DEFAULT_TIMEOUT_MS = 6_000

export class RequestTimeoutError extends Error {
  constructor(message = '请求超时') {
    super(message)
    this.name = 'RequestTimeoutError'
  }
}

export class HttpRequestError extends Error {
  public readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'HttpRequestError'
    this.status = status
  }
}

type RequestOptions = RequestInit & {
  timeoutMs?: number
}

export async function fetchJsonWithTimeout<T>(
  input: RequestInfo | URL,
  options: RequestOptions = {},
): Promise<T> {
  const { timeoutMs = DEFAULT_TIMEOUT_MS, headers, ...rest } = options

  const controller = new AbortController()
  const timeoutId = window.setTimeout(() => {
    controller.abort(new RequestTimeoutError())
  }, timeoutMs)

  try {
    const response = await fetch(input, {
      ...rest,
      headers: {
        Accept: 'application/json',
        ...headers,
      },
      signal: controller.signal,
    })

    if (!response.ok) {
      throw new HttpRequestError(response.status, `请求失败（HTTP ${response.status}）`)
    }

    return (await response.json()) as T
  } catch (error) {
    if (error instanceof RequestTimeoutError) {
      throw error
    }

    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new RequestTimeoutError()
    }

    throw error
  } finally {
    window.clearTimeout(timeoutId)
  }
}

export function toReadableRequestError(error: unknown): string {
  if (error instanceof RequestTimeoutError) {
    return '请求超时，请检查后端状态或网络连接。'
  }

  if (error instanceof HttpRequestError) {
    return `接口返回异常（HTTP ${error.status}）。`
  }

  if (error instanceof Error && error.message) {
    return error.message
  }

  return '未知请求错误'
}
