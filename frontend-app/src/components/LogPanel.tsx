import { AnimatePresence, motion } from 'framer-motion'
import { AlertTriangle, Bot, Cog, Filter, TerminalSquare, UserRound } from 'lucide-react'
import type { Agent, LogEntry, LogQuickFilter } from '../types'
import { Badge } from './ui/badge'
import { Button } from './ui/button'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'

interface LogPanelProps {
  agents: Agent[]
  logs: LogEntry[]
  totalLiveLogs: number
  liveUpdatedAt: number | null
  liveError: string | null
  liveHint: string | null
  isLiveLoading: boolean
  quickFilter: LogQuickFilter
  onQuickFilterChange: (filter: LogQuickFilter) => void
  selectedAgentId: string | null
  onClearAgentFilter: () => void
}

const quickFilterOptions: Array<{ id: LogQuickFilter; label: string }> = [
  { id: 'all', label: '全部日志' },
  { id: 'error', label: '仅异常' },
  { id: 'done', label: '仅完成' },
]

function RoleIcon({ role }: { role: LogEntry['role'] }) {
  if (role === 'user') return <UserRound className="h-3.5 w-3.5 text-sky-200" />
  if (role === 'assistant') return <Bot className="h-3.5 w-3.5 text-violet-200" />
  if (role === 'tool') return <Cog className="h-3.5 w-3.5 text-cyan-200" />
  return <TerminalSquare className="h-3.5 w-3.5 text-slate-300" />
}

function formatUpdatedAt(updatedAt: number | null): string {
  if (!updatedAt) {
    return '--'
  }

  return new Date(updatedAt).toLocaleString('zh-CN', {
    hour12: false,
  })
}

export function LogPanel({
  agents,
  logs,
  totalLiveLogs,
  liveUpdatedAt,
  liveError,
  liveHint,
  isLiveLoading,
  quickFilter,
  onQuickFilterChange,
  selectedAgentId,
  onClearAgentFilter,
}: LogPanelProps) {
  const nameMap = new Map(agents.map((agent) => [agent.id, `${agent.emoji} ${agent.name}`]))

  const emptyMessage =
    totalLiveLogs === 0
      ? '/live 暂无日志流'
      : `当前筛选条件下暂无日志（/live 原始日志 ${totalLiveLogs} 条）`

  return (
    <section data-testid="office-log-panel" className="log-shell overflow-hidden rounded-2xl">
      <Card className="border-slate-500/25 bg-slate-950/70">
        <CardHeader className="pb-3">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <CardTitle className="flex items-center gap-2 text-base text-slate-100">
              <TerminalSquare className="h-4 w-4 text-cyan-200" />
              <h2 className="log-title text-base">日志区</h2>
            </CardTitle>
            <Badge variant="secondary" className="text-[11px] text-slate-200">
              来源 /live · {totalLiveLogs} 条
            </Badge>
          </div>

          <div id="log-enhance-v1">
            <div
              className="log-v1-row mt-2 flex flex-wrap items-center gap-2"
              id="log-filter-chips"
              data-mount="zh-filter-chips"
            >
              <span className="inline-flex items-center gap-1 text-[11px] text-slate-400">
                <Filter className="h-3 w-3" /> 中文筛选
              </span>
              {quickFilterOptions.map((item) => (
                <Button
                  key={item.id}
                  variant={quickFilter === item.id ? 'default' : 'outline'}
                  size="sm"
                  className={
                    quickFilter === item.id
                      ? 'border-emerald-300/40 bg-emerald-400/20 text-emerald-50 hover:bg-emerald-400/25'
                      : 'border-slate-500/35 bg-slate-900/80 text-slate-200 hover:bg-slate-800/75'
                  }
                  onClick={() => onQuickFilterChange(item.id)}
                >
                  {item.label}
                </Button>
              ))}

              {selectedAgentId && (
                <Button
                  variant="outline"
                  size="sm"
                  className="border-cyan-300/40 bg-cyan-500/10 text-cyan-100 hover:bg-cyan-500/20"
                  onClick={onClearAgentFilter}
                >
                  清除点名筛选 ×
                </Button>
              )}
            </div>
          </div>
        </CardHeader>

        <CardContent>
          <div id="log-panel" className="max-h-[320px] space-y-2 overflow-auto pr-1">
            {liveError ? (
              <div className="rounded-lg border border-rose-300/40 bg-rose-950/20 p-4 text-xs text-rose-100">
                <p className="inline-flex items-center gap-1 font-semibold">
                  <AlertTriangle className="h-3.5 w-3.5" /> /live 日志流拉取失败
                </p>
                <p className="mt-1 break-words text-rose-200/90">{liveError}</p>
              </div>
            ) : liveHint ? (
              <div className="rounded-lg border border-amber-300/35 bg-amber-950/20 p-4 text-xs text-amber-100">
                {liveHint}
              </div>
            ) : isLiveLoading && totalLiveLogs === 0 ? (
              <div className="rounded-lg border border-dashed border-slate-500/30 bg-slate-900/50 p-4 text-center text-xs text-slate-400">
                正在拉取 /live 日志流…
              </div>
            ) : logs.length === 0 ? (
              <div className="rounded-lg border border-dashed border-slate-500/30 bg-slate-900/50 p-4 text-center text-xs text-slate-400">
                {emptyMessage}
              </div>
            ) : (
              <AnimatePresence initial={false}>
                {logs.map((log) => (
                  <motion.article
                    key={log.id}
                    layout
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -8 }}
                    className={`rounded-lg border p-3 ${
                      log.isError
                        ? 'border-rose-300/40 bg-rose-950/20'
                        : log.isDone
                          ? 'border-emerald-300/30 bg-emerald-950/15'
                          : 'border-slate-600/30 bg-slate-900/65'
                    }`}
                  >
                    <header className="mb-1.5 flex items-center justify-between gap-3">
                      <span className="truncate text-xs font-semibold text-slate-100">
                        {nameMap.get(log.agentId) ?? log.agentId}
                      </span>
                      <span className="shrink-0 font-mono text-[11px] text-slate-400">{log.ts}</span>
                    </header>

                    <div className="grid grid-cols-[auto_1fr] items-start gap-2">
                      <span className="mt-0.5">{log.isError ? <AlertTriangle className="h-3.5 w-3.5 text-rose-300" /> : <RoleIcon role={log.role} />}</span>
                      <span className={`text-xs leading-relaxed ${log.isError ? 'text-rose-100' : 'text-slate-200'}`}>
                        {log.text}
                      </span>
                    </div>
                  </motion.article>
                ))}
              </AnimatePresence>
            )}
          </div>

          <p className="mt-2 text-[11px] text-slate-400">
            /live 更新时间：{formatUpdatedAt(liveUpdatedAt)}
          </p>
        </CardContent>
      </Card>
    </section>
  )
}
