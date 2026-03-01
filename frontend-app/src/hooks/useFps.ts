import { useEffect, useState } from 'react'

const BUFFER_SIZE = 30

export function useFps(): number {
  const [fps, setFps] = useState(60)

  useEffect(() => {
    let rafId = 0
    let last = performance.now()
    let sampleStart = last
    const frameDeltas: number[] = []

    const loop = (now: number) => {
      const delta = Math.max(1, now - last)
      last = now
      frameDeltas.push(delta)
      if (frameDeltas.length > BUFFER_SIZE) {
        frameDeltas.shift()
      }

      if (now - sampleStart >= 500) {
        const avgDelta = frameDeltas.reduce((sum, value) => sum + value, 0) / frameDeltas.length
        const value = Math.max(1, Math.min(240, Math.round(1000 / avgDelta)))
        setFps(value)
        sampleStart = now
      }

      rafId = requestAnimationFrame(loop)
    }

    rafId = requestAnimationFrame(loop)

    return () => {
      cancelAnimationFrame(rafId)
    }
  }, [])

  return fps
}
