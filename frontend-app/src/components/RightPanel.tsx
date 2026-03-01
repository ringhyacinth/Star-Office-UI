import { motion } from 'framer-motion'
import { Bot, ChartNoAxesCombined, Cpu, Gauge, ListTodo, Timer } from 'lucide-react'
import type { Agent, TaskItem } from '../types'
import { Badge } from './ui/badge'
import { Button } from './ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Progress } from './ui/progress'

export interface RuntimeModelInfo {
  name: string
  sizeMb?: number
  active?: boolean
  expires?: string
}

interface RightPanelProps {
  agents: Agent[]
  tasks: TaskItem[]
  selectedAgentId: string | null
  onSelectAgent: (agentId: string) => void
  models?: RuntimeModelInfo[]
}

function countByStatus(tasks: TaskItem[]) {
  return {
    total: tasks.length,
    done: tasks.filter((task) => task.status === '已完成').length,
    doing: tasks.filter((task) => task.status === '进行中').length,
    todo: tasks.filter((task) => task.status === '待办').length,
  }
}

function estimateLoad(loadTasks: number, status: Agent['status']) {
  const statusBonus = status === 'working' ? 45 : status === 'error' ? 28 : status === 'idle' ? 18 : 5
  return Math.min(100, loadTasks * 22 + statusBonus)
}

export function RightPanel({ agents, tasks, selectedAgentId, onSelectAgent, models = [] }: RightPanelProps) {
  const stats = countByStatus(tasks)

  return (
    <aside id="office-right" className="space-y-3">
      <motion.div initial={{ opacity: 0, x: 16 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.25 }}>
        <Card className="border-cyan-300/25 bg-slate-900/80">
          <CardHeader>
            <div className="flex items-center justify-between gap-3">
              <div>
                <CardTitle className="flex items-center gap-2 text-cyan-100">
                  <ChartNoAxesCombined className="h-4 w-4" /> 任务态势
                </CardTitle>
                <CardDescription>实时分布（任务 / 执行节奏）</CardDescription>
              </div>
              <Badge variant="success">API 实时版</Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-2">
              <div className="kpi-box">
                <span>总任务</span>
                <strong>{stats.total}</strong>
              </div>
              <div className="kpi-box">
                <span>进行中</span>
                <strong className="text-emerald-200">{stats.doing}</strong>
              </div>
              <div className="kpi-box">
                <span>已完成</span>
                <strong className="text-sky-200">{stats.done}</strong>
              </div>
              <div className="kpi-box">
                <span>待办</span>
                <strong className="text-amber-200">{stats.todo}</strong>
              </div>
            </div>
            {tasks.length === 0 ? <p className="mt-3 text-xs text-slate-400">/tasks 返回空数组，面板已降级显示</p> : null}
          </CardContent>
        </Card>
      </motion.div>

      <motion.div initial={{ opacity: 0, x: 16 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.3, delay: 0.05 }}>
        <Card className="border-violet-300/20 bg-slate-900/80">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-violet-100">
              <Cpu className="h-4 w-4" /> 模型工位
            </CardTitle>
            <CardDescription>来源：/ollama</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {models.length === 0 ? (
              <p className="rounded-md border border-dashed border-slate-500/30 p-3 text-xs text-slate-400">
                /ollama 暂无模型数据
              </p>
            ) : (
              models.map((model) => (
                <div key={model.name} className="rounded-lg border border-slate-500/25 bg-slate-900/70 p-3">
                  <div className="mb-2 flex items-center justify-between text-xs text-slate-200">
                    <span className="flex items-center gap-1.5 font-medium text-slate-100">
                      <Bot className="h-3.5 w-3.5 text-violet-200" />
                      {model.name}
                    </span>
                    <Badge variant={model.active ? 'success' : 'secondary'}>{model.active ? 'active' : 'loaded'}</Badge>
                  </div>
                  <div className="grid gap-1 text-[11px] text-slate-400">
                    <span>大小：{typeof model.sizeMb === 'number' ? `${model.sizeMb} MB` : '--'}</span>
                    <span className="inline-flex items-center gap-1">
                      <Timer className="h-3 w-3" /> 过期：{model.expires?.trim() ? model.expires : '--'}
                    </span>
                  </div>
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </motion.div>

      <motion.div initial={{ opacity: 0, x: 16 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.32, delay: 0.1 }}>
        <Card className="border-emerald-300/20 bg-slate-900/80">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-emerald-100">
              <ListTodo className="h-4 w-4" /> Agent 负载
            </CardTitle>
            <CardDescription>点击卡片触发点名高亮</CardDescription>
          </CardHeader>

          <CardContent>
            <div className="grid gap-2" data-mount="agent-highlight">
              {agents.length === 0 ? (
                <p className="rounded-md border border-dashed border-slate-500/30 p-3 text-xs text-slate-400">
                  /live 无 agent，已返回空态
                </p>
              ) : (
                agents.map((agent) => {
                  const isSelected = agent.id === selectedAgentId
                  const ownedTasks = tasks.filter((task) => task.ownerAgentId === agent.id)
                  const load = estimateLoad(ownedTasks.length, agent.status)

                  return (
                    <motion.div key={agent.id} whileHover={{ y: -1.5 }} whileTap={{ scale: 0.99 }}>
                      <Button
                        variant="outline"
                        className={`group h-auto w-full justify-start rounded-lg border px-3 py-2 text-left transition-colors ${
                          isSelected
                            ? 'border-emerald-300/60 bg-emerald-400/10 text-emerald-50'
                            : 'border-slate-500/35 bg-slate-900/75 text-slate-100 hover:bg-slate-800/80'
                        }`}
                        onClick={() => onSelectAgent(agent.id)}
                        style={{ borderColor: isSelected ? agent.highlightColor : undefined }}
                      >
                        <div className="w-full">
                          <div className="flex items-center justify-between gap-2">
                            <span className="text-sm font-semibold">
                              {agent.emoji} {agent.name}
                            </span>
                            <span className="inline-flex items-center gap-1 text-[11px] text-slate-300">
                              <span
                                className={`dot status-${agent.status} ${agent.status === 'working' ? 'status-breathing' : ''}`}
                              />
                              {agent.team}
                            </span>
                          </div>
                          <div className="mt-2 flex items-center justify-between text-[11px] text-slate-400">
                            <span>{ownedTasks.length} 任务</span>
                            <span className="inline-flex items-center gap-1">
                              <Gauge className="h-3 w-3" /> {load}%
                            </span>
                          </div>
                          <Progress value={load} className="mt-1.5" />
                        </div>
                      </Button>
                    </motion.div>
                  )
                })
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </aside>
  )
}
