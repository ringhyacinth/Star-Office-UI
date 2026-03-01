import { ApiError } from './http'

export interface PollerSnapshot<T> {
  data: T
  error: ApiError | null
  isLoading: boolean
  updatedAt: number | null
}

export interface PollerOptions<T> {
  intervalMs: number
  initialData: T
  immediate?: boolean
}

export interface Poller<T> {
  start: () => void
  stop: () => void
  refresh: () => Promise<void>
  getSnapshot: () => PollerSnapshot<T>
  subscribe: (listener: (snapshot: PollerSnapshot<T>) => void) => () => void
}

export function createPoller<T>(
  fetcher: (signal: AbortSignal) => Promise<T>,
  options: PollerOptions<T>,
): Poller<T> {
  let timer: number | null = null
  let running = false
  let inFlight = false
  let controller: AbortController | null = null

  let snapshot: PollerSnapshot<T> = {
    data: options.initialData,
    error: null,
    isLoading: false,
    updatedAt: null,
  }

  const listeners = new Set<(nextSnapshot: PollerSnapshot<T>) => void>()

  function notify() {
    for (const listener of listeners) {
      listener(snapshot)
    }
  }

  function patch(update: Partial<PollerSnapshot<T>>) {
    snapshot = { ...snapshot, ...update }
    notify()
  }

  function clearTimer() {
    if (timer !== null) {
      window.clearTimeout(timer)
      timer = null
    }
  }

  function scheduleNext() {
    clearTimer()
    if (!running) {
      return
    }

    timer = window.setTimeout(() => {
      void tick()
    }, options.intervalMs)
  }

  async function tick() {
    if (!running || inFlight) {
      return
    }

    inFlight = true
    controller = new AbortController()

    patch({ isLoading: true })

    try {
      const data = await fetcher(controller.signal)
      patch({
        data,
        error: null,
        updatedAt: Date.now(),
        isLoading: false,
      })
    } catch (error) {
      const apiError =
        error instanceof ApiError
          ? error
          : new ApiError('轮询请求失败', {
              cause: error,
            })

      patch({ error: apiError, isLoading: false })
    } finally {
      inFlight = false
      controller = null
      scheduleNext()
    }
  }

  return {
    start() {
      if (running) {
        return
      }

      running = true
      if (options.immediate ?? true) {
        void tick()
      } else {
        scheduleNext()
      }
    },

    stop() {
      running = false
      clearTimer()
      if (controller) {
        controller.abort()
        controller = null
      }
      patch({ isLoading: false })
    },

    async refresh() {
      if (!running) {
        running = true
      }
      await tick()
    },

    getSnapshot() {
      return snapshot
    },

    subscribe(listener) {
      listeners.add(listener)
      listener(snapshot)

      return () => {
        listeners.delete(listener)
      }
    },
  }
}
