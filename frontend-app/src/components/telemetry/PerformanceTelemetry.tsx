import { useEffect, useMemo, useState } from 'react'
import './performanceTelemetry.css'

type RefreshStatus = 'refreshing' | 'stalled' | 'background'

interface TelemetrySnapshot {
  fps: number
  frameAgeMs: number
  status: RefreshStatus
}

const STORAGE_KEY = 'office-v2:telemetry-visible'
const SAMPLE_INTERVAL_MS = 500
const STALLED_THRESHOLD_MS = 800

function parseBooleanFlag(value: unknown): boolean | undefined {
  if (typeof value !== 'string') {
    return undefined
  }

  const normalized = value.trim().toLowerCase()

  if (['1', 'true', 'on', 'yes'].includes(normalized)) {
    return true
  }

  if (['0', 'false', 'off', 'no'].includes(normalized)) {
    return false
  }

  return undefined
}

function readQueryOverride(): boolean | undefined {
  if (typeof window === 'undefined') {
    return undefined
  }

  const raw = new URLSearchParams(window.location.search).get('telemetry')
  return parseBooleanFlag(raw)
}

function readStoragePreference(): boolean | undefined {
  if (typeof window === 'undefined') {
    return undefined
  }

  const raw = window.localStorage.getItem(STORAGE_KEY)
  return parseBooleanFlag(raw)
}

function resolveAvailability(): boolean {
  if (import.meta.env.DEV) {
    return true
  }

  const envSwitch = parseBooleanFlag(import.meta.env.VITE_TELEMETRY_ENABLED)
  if (envSwitch !== undefined) {
    return envSwitch
  }

  return readQueryOverride() ?? false
}

function resolveDefaultVisible(): boolean {
  const queryOverride = readQueryOverride()
  if (queryOverride !== undefined) {
    return queryOverride
  }

  const storedPreference = readStoragePreference()
  if (storedPreference !== undefined) {
    return storedPreference
  }

  if (import.meta.env.DEV) {
    return false
  }

  return parseBooleanFlag(import.meta.env.VITE_TELEMETRY_DEFAULT_VISIBLE) ?? false
}

function getStatusLabel(status: RefreshStatus): string {
  switch (status) {
    case 'refreshing':
      return '刷新中'
    case 'stalled':
      return '低频/停滞'
    case 'background':
      return '后台暂停'
    default:
      return '未知'
  }
}

export function PerformanceTelemetry() {
  const telemetryAvailable = useMemo(() => resolveAvailability(), [])
  const [visible, setVisible] = useState<boolean>(() => resolveDefaultVisible())
  const [snapshot, setSnapshot] = useState<TelemetrySnapshot>({
    fps: 0,
    frameAgeMs: 0,
    status: document.hidden ? 'background' : 'refreshing',
  })

  useEffect(() => {
    if (!telemetryAvailable || typeof window === 'undefined') {
      return
    }

    window.localStorage.setItem(STORAGE_KEY, visible ? '1' : '0')
  }, [telemetryAvailable, visible])

  useEffect(() => {
    if (!telemetryAvailable || !visible) {
      return
    }

    let rafId = 0
    let frameCount = 0
    let sampleStart = performance.now()
    let lastFrameAt = sampleStart

    const onFrame = (timestamp: number) => {
      frameCount += 1
      lastFrameAt = timestamp
      rafId = window.requestAnimationFrame(onFrame)
    }

    rafId = window.requestAnimationFrame(onFrame)

    const intervalId = window.setInterval(() => {
      const now = performance.now()
      const elapsedMs = now - sampleStart
      const rawFps = elapsedMs > 0 ? (frameCount * 1000) / elapsedMs : 0

      sampleStart = now
      frameCount = 0

      const frameAgeMs = Math.max(0, Math.round(now - lastFrameAt))
      const fps = Math.max(0, Math.round(rawFps))
      const status: RefreshStatus = document.hidden
        ? 'background'
        : frameAgeMs > STALLED_THRESHOLD_MS
          ? 'stalled'
          : 'refreshing'

      setSnapshot((prev) => {
        if (
          prev.fps === fps
          && prev.status === status
          && Math.abs(prev.frameAgeMs - frameAgeMs) < 16
        ) {
          return prev
        }

        return { fps, frameAgeMs, status }
      })
    }, SAMPLE_INTERVAL_MS)

    const onVisibilityChange = () => {
      if (!document.hidden) {
        return
      }

      setSnapshot((prev) => {
        if (prev.status === 'background') {
          return prev
        }

        return { ...prev, status: 'background' }
      })
    }

    document.addEventListener('visibilitychange', onVisibilityChange)

    return () => {
      document.removeEventListener('visibilitychange', onVisibilityChange)
      window.clearInterval(intervalId)
      window.cancelAnimationFrame(rafId)
    }
  }, [telemetryAvailable, visible])

  if (!telemetryAvailable) {
    return null
  }

  return (
    <div className="telemetry-root">
      <button
        className="telemetry-toggle"
        type="button"
        aria-pressed={visible}
        onClick={() => setVisible((prev) => !prev)}
      >
        遥测 {visible ? 'ON' : 'OFF'}
      </button>

      {visible && (
        <aside className="telemetry-panel" aria-live="polite">
          <h2>渲染遥测</h2>
          <div className="telemetry-row">
            <span>FPS</span>
            <strong>{snapshot.fps}</strong>
          </div>
          <div className="telemetry-row">
            <span>刷新状态</span>
            <strong className={`status status-${snapshot.status}`}>
              {getStatusLabel(snapshot.status)}
            </strong>
          </div>
          <div className="telemetry-row">
            <span>最近帧间隔</span>
            <strong>{snapshot.frameAgeMs} ms</strong>
          </div>
        </aside>
      )}
    </div>
  )
}
