import { useCallback, useEffect, useMemo, useState } from 'react'
import { Activity, AlertTriangle, Bot, GaugeCircle, ListTodo, Wifi } from 'lucide-react'
import { HEALTH_EMPTY, LIVE_EMPTY, OLLAMA_EMPTY, TASKS_EMPTY, OfficeApi, officeApi } from './api'
import { CanvasShell } from './components/CanvasShell'
import { LogPanel } from './components/LogPanel'
import { PerformanceTelemetry } from './components/telemetry/PerformanceTelemetry'
import { Badge } from './components/ui/badge'
import { Button } from './components/ui/button'
import { mapLiveAgents, mapLiveLogs, mapTasks } from './data/realtimeAdapters'
import { useApiPoller } from './hooks/useApiPoller'
import { useFps } from './hooks/useFps'
import type { HealthResponse, LiveResponse, OllamaResponse, TasksResponse } from './api/types'
import type { LogEntry, LogQuickFilter } from './types'
import './App.css'

function applyLogFilter(logs: LogEntry[], quickFilter: LogQuickFilter, selectedAgentId: string | null) {
  return logs.filter((log) => {
    if (selectedAgentId && log.agentId !== selectedAgentId) {
      return false
    }

    if (quickFilter === 'error') {
      return Boolean(log.isError)
    }

    if (quickFilter === 'done') {
      return Boolean(log.isDone)
    }

    return true
  })
}

function toStatusVariant(hasError: boolean, isLoading: boolean): 'success' | 'warning' | 'danger' {
  if (hasError) {
    return 'danger'
  }

  if (isLoading) {
    return 'warning'
  }

  return 'success'
}

function resolveDevApiBaseUrl(): string {
  if (typeof window === 'undefined') {
    return ''
  }

  const configuredBase = (import.meta.env.VITE_API_BASE_URL ?? '').trim()
  if (configuredBase) {
    return ''
  }

  const { protocol, hostname, port } = window.location
  const isLikelyViteDevPort = /^4\d{3}$/.test(port) || /^5\d{3}$/.test(port)
  if (!isLikelyViteDevPort) {
    return ''
  }

  const fallbackPort = `${import.meta.env.VITE_API_DEV_PORT ?? '19800'}`.trim() || '19800'
  return `${protocol}//${hostname}:${fallbackPort}`
}

function hasLivePayload(data: LiveResponse): boolean {
  return (
    Object.keys(data.state.agents).length > 0
    || Object.keys(data.logs).length > 0
    || Object.keys(data.providers).length > 0
  )
}

function isHealthLikelyEmpty(data: HealthResponse): boolean {
  return data.status === 'unknown' && !data.timestamp
}

function isTasksLikelyEmpty(data: TasksResponse): boolean {
  return data.tasks.length === 0
}

function isOllamaLikelyEmpty(data: OllamaResponse): boolean {
  return !data.running && data.models.length === 0 && data.active.length === 0
}

function App() {
  const fps = useFps()
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null)
  const [quickFilter, setQuickFilter] = useState<LogQuickFilter>('all')

  const devApiBaseUrl = useMemo(() => resolveDevApiBaseUrl(), [])
  const devApiClient = useMemo(
    () => (devApiBaseUrl ? new OfficeApi(devApiBaseUrl) : null),
    [devApiBaseUrl],
  )

  const healthFetcher = useCallback(async (signal: AbortSignal) => {
    const primary = await officeApi.getHealth(signal)
    if (!devApiClient || !isHealthLikelyEmpty(primary)) {
      return primary
    }

    try {
      return await devApiClient.getHealth(signal)
    } catch {
      return primary
    }
  }, [devApiClient])

  const liveFetcher = useCallback(async (signal: AbortSignal) => {
    const primary = await officeApi.getLive(signal)
    if (!devApiClient || hasLivePayload(primary)) {
      return primary
    }

    try {
      const fallback = await devApiClient.getLive(signal)
      return hasLivePayload(fallback) ? fallback : primary
    } catch {
      return primary
    }
  }, [devApiClient])

  const tasksFetcher = useCallback(async (signal: AbortSignal) => {
    const primary = await officeApi.getTasks(signal)
    if (!devApiClient || !isTasksLikelyEmpty(primary)) {
      return primary
    }

    try {
      return await devApiClient.getTasks(signal)
    } catch {
      return primary
    }
  }, [devApiClient])

  const ollamaFetcher = useCallback(async (signal: AbortSignal) => {
    const primary = await officeApi.getOllama(signal)
    if (!devApiClient || !isOllamaLikelyEmpty(primary)) {
      return primary
    }

    try {
      return await devApiClient.getOllama(signal)
    } catch {
      return primary
    }
  }, [devApiClient])

  const healthSnapshot = useApiPoller(healthFetcher, {
    intervalMs: 10_000,
    initialData: HEALTH_EMPTY,
  })

  const liveSnapshot = useApiPoller(liveFetcher, {
    intervalMs: 3_000,
    initialData: LIVE_EMPTY,
  })

  const tasksSnapshot = useApiPoller(tasksFetcher, {
    intervalMs: 8_000,
    initialData: TASKS_EMPTY,
  })

  const ollamaSnapshot = useApiPoller(ollamaFetcher, {
    intervalMs: 15_000,
    initialData: OLLAMA_EMPTY,
  })

  const agents = useMemo(() => mapLiveAgents(liveSnapshot.data), [liveSnapshot.data])
  const logs = useMemo(() => mapLiveLogs(liveSnapshot.data.logs), [liveSnapshot.data.logs])
  const tasks = useMemo(() => mapTasks(tasksSnapshot.data), [tasksSnapshot.data])

  useEffect(() => {
    if (!selectedAgentId) {
      return
    }

    const stillExists = agents.some((agent) => agent.id === selectedAgentId)
    if (!stillExists) {
      setSelectedAgentId(null)
    }
  }, [agents, selectedAgentId])

  const selectedAgent = useMemo(
    () => agents.find((agent) => agent.id === selectedAgentId) ?? null,
    [agents, selectedAgentId],
  )

  const filteredLogs = useMemo(
    () => applyLogFilter(logs, quickFilter, selectedAgentId),
    [logs, quickFilter, selectedAgentId],
  )

  const totalLiveLogs = useMemo(
    () => Object.values(liveSnapshot.data.logs).reduce((count, items) => count + items.length, 0),
    [liveSnapshot.data.logs],
  )

  const liveHint = useMemo(() => {
    if (liveSnapshot.error || liveSnapshot.isLoading) {
      return null
    }

    if (!devApiClient || agents.length > 0 || totalLiveLogs > 0) {
      return null
    }

    return '检测到 /live 仍为空；若在 Vite dev 下，请确认已配置代理或后端允许跨域。'
  }, [liveSnapshot.error, liveSnapshot.isLoading, devApiClient, agents.length, totalLiveLogs])

  const fpsTone = useMemo(() => {
    if (fps >= 55) return 'success'
    if (fps >= 30) return 'warning'
    return 'danger'
  }, [fps])

  const providerSummary = useMemo(() => {
    const providers = Object.values(liveSnapshot.data.providers)
    const online = providers.filter((provider) => provider.online).length
    return {
      online,
      total: providers.length,
    }
  }, [liveSnapshot.data.providers])

  const taskSummary = useMemo(() => {
    return {
      total: tasks.length,
      doing: tasks.filter((task) => task.status === '进行中').length,
      done: tasks.filter((task) => task.status === '已完成').length,
    }
  }, [tasks])

  const endpointErrors = useMemo(
    () =>
      [
        healthSnapshot.error ? `/health：${healthSnapshot.error.message}` : null,
        liveSnapshot.error ? `/live：${liveSnapshot.error.message}` : null,
        tasksSnapshot.error ? `/tasks：${tasksSnapshot.error.message}` : null,
        ollamaSnapshot.error ? `/ollama：${ollamaSnapshot.error.message}` : null,
      ].filter((message): message is string => Boolean(message)),
    [healthSnapshot.error, liveSnapshot.error, tasksSnapshot.error, ollamaSnapshot.error],
  )

  const handleSelectAgent = (agentId: string) => {
    setSelectedAgentId((current) => (current === agentId ? null : agentId))
  }

  const clearSelection = () => {
    setSelectedAgentId(null)
  }

  return (
    <>
      <main className="office-v2-app" data-testid="office-v2-page">
        <section id="view-office" className="office-stage-layout">
          <div className="stage-hud" aria-label="舞台角标信息">
            <Badge id="fps-indicator" data-mount="fps-indicator" variant={fpsTone} className="font-mono shadow-lg shadow-slate-950/40">
              <GaugeCircle className="h-3.5 w-3.5" /> FPS {fps}
            </Badge>

            {selectedAgent && (
              <Button
                variant="outline"
                size="sm"
                className="stage-mention-chip border-emerald-300/55 bg-emerald-500/12 text-emerald-100 hover:bg-emerald-500/24"
                onClick={clearSelection}
                title="清除点名高亮"
              >
                点名：{selectedAgent.emoji} {selectedAgent.name} ×
              </Button>
            )}
          </div>

          <section className="api-strip" aria-label="OpenClaw 实时数据状态">
            <Badge
              variant={toStatusVariant(Boolean(healthSnapshot.error), healthSnapshot.isLoading)}
              className="font-mono"
            >
              <Activity className="h-3.5 w-3.5" /> /health {healthSnapshot.data.status || 'unknown'}
            </Badge>

            <Badge
              variant={toStatusVariant(Boolean(liveSnapshot.error), liveSnapshot.isLoading)}
              className="font-mono"
            >
              <Wifi className="h-3.5 w-3.5" /> /live {agents.length} agents · logs {totalLiveLogs} · provider {providerSummary.online}/{providerSummary.total}
            </Badge>

            <Badge
              variant={toStatusVariant(Boolean(tasksSnapshot.error), tasksSnapshot.isLoading)}
              className="font-mono"
            >
              <ListTodo className="h-3.5 w-3.5" /> /tasks {taskSummary.total}（进行中 {taskSummary.doing} / 已完成 {taskSummary.done}）
            </Badge>

            <Badge
              variant={toStatusVariant(Boolean(ollamaSnapshot.error), ollamaSnapshot.isLoading)}
              className="font-mono"
            >
              <Bot className="h-3.5 w-3.5" /> /ollama {ollamaSnapshot.data.running ? 'running' : 'offline'} · models {ollamaSnapshot.data.models.length} · active {ollamaSnapshot.data.active.length}
            </Badge>
          </section>

          {endpointErrors.length > 0 && (
            <section className="api-error-banner" role="alert" aria-live="polite">
              <h2 className="api-error-title">
                <AlertTriangle className="h-4 w-4" /> 实时接口异常（已展示错误态/空态，未回退假数据）
              </h2>
              <ul>
                {endpointErrors.map((message) => (
                  <li key={message}>{message}</li>
                ))}
              </ul>
            </section>
          )}

          {!liveSnapshot.isLoading && !liveSnapshot.error && agents.length === 0 && (
            <section className="api-empty-banner" role="status">
              <strong>/live 暂无 agent 数据</strong>
              <span>页面保持空态展示，不注入任何 mock 数据。</span>
            </section>
          )}

          <CanvasShell
            agents={agents}
            selectedAgentId={selectedAgentId}
            onSelectAgent={handleSelectAgent}
          />

          <LogPanel
            agents={agents}
            logs={filteredLogs}
            totalLiveLogs={totalLiveLogs}
            liveUpdatedAt={liveSnapshot.updatedAt}
            liveError={liveSnapshot.error?.message ?? null}
            liveHint={liveHint}
            isLiveLoading={liveSnapshot.isLoading}
            quickFilter={quickFilter}
            onQuickFilterChange={setQuickFilter}
            selectedAgentId={selectedAgentId}
            onClearAgentFilter={clearSelection}
          />
        </section>
      </main>

      <PerformanceTelemetry />
    </>
  )
}

export default App
