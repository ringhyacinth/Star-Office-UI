import { useEffect, useMemo, useState } from 'react'

import { createPoller, type PollerSnapshot } from '../api/poller'

export interface UseApiPollerOptions<T> {
  intervalMs: number
  initialData: T
  immediate?: boolean
}

export function useApiPoller<T>(
  fetcher: (signal: AbortSignal) => Promise<T>,
  options: UseApiPollerOptions<T>,
): PollerSnapshot<T> {
  const poller = useMemo(
    () =>
      createPoller(fetcher, {
        intervalMs: options.intervalMs,
        initialData: options.initialData,
        immediate: options.immediate,
      }),
    [fetcher, options.immediate, options.initialData, options.intervalMs],
  )

  const [snapshot, setSnapshot] = useState<PollerSnapshot<T>>(poller.getSnapshot())

  useEffect(() => {
    const unsubscribe = poller.subscribe(setSnapshot)
    poller.start()

    return () => {
      unsubscribe()
      poller.stop()
    }
  }, [poller])

  return snapshot
}
