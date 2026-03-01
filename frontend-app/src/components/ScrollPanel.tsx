import { motion } from 'framer-motion'
import { ClipboardCheck, ScrollText, ShieldAlert, Swords } from 'lucide-react'
import type { TaskItem } from '../types'
import { Badge } from './ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'

interface ScrollPanelProps {
  tasks: TaskItem[]
}

function priorityClass(priority: TaskItem['priority']) {
  if (priority === 'P0') return 'bg-rose-500/80 text-white'
  if (priority === 'P1') return 'bg-amber-500/80 text-amber-50'
  if (priority === 'P2') return 'bg-sky-500/80 text-sky-50'
  return 'bg-slate-500/75 text-slate-100'
}

export function ScrollPanel({ tasks }: ScrollPanelProps) {
  const doingTasks = tasks.filter((task) => task.status === '进行中')
  const todoTasks = tasks.filter((task) => task.status === '待办')
  const doneTasks = tasks.filter((task) => task.status === '已完成')

  return (
    <div id="scroll-wrapper">
      <Card className="border-slate-500/25 bg-slate-950/70">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between gap-2">
            <CardTitle className="flex items-center gap-2 text-slate-100">
              <ScrollText className="h-4 w-4 text-cyan-200" /> 战令卷轴
            </CardTitle>
            <div id="scroll-handle" aria-hidden="true" className="grid h-9 w-9 place-items-center rounded-full border border-cyan-300/35 bg-cyan-500/10 text-sm">
              📜
            </div>
          </div>
        </CardHeader>

        <CardContent id="scroll-body" data-mount="scroll-panel" className="space-y-3">
          <section className="space-y-2 rounded-lg border border-emerald-300/20 bg-emerald-950/15 p-3">
            <h3 className="scroll-section-title flex items-center gap-2 text-sm font-semibold text-emerald-100">
              <Swords className="h-3.5 w-3.5" /> 激战中的战令
            </h3>
            {doingTasks.length === 0 ? <p className="scroll-empty text-xs text-slate-400">暂无进行中任务</p> : null}
            {doingTasks.map((task) => (
              <motion.article key={task.id} whileHover={{ x: 2 }} className="rounded-md border border-emerald-300/20 bg-slate-900/55 p-2.5">
                <div className="text-xs font-semibold text-slate-100">{task.title}</div>
                <div className="mt-1 text-[11px] text-slate-400">{task.summary}</div>
              </motion.article>
            ))}
          </section>

          <section className="space-y-2 rounded-lg border border-amber-300/20 bg-amber-950/15 p-3">
            <h3 className="scroll-section-title flex items-center gap-2 text-sm font-semibold text-amber-100">
              <ShieldAlert className="h-3.5 w-3.5" /> 待接的悬赏令
            </h3>
            {todoTasks.length === 0 ? <p className="scroll-empty text-xs text-slate-400">暂无待办任务</p> : null}
            {todoTasks.map((task) => (
              <article key={task.id} className="rounded-md border border-amber-300/20 bg-slate-900/55 p-2.5">
                <Badge className={`mb-1 ${priorityClass(task.priority)}`}>{task.priority}</Badge>
                <div className="text-xs font-semibold text-slate-100">{task.title}</div>
                <div className="mt-1 text-[11px] text-slate-400">{task.summary}</div>
              </article>
            ))}
          </section>

          <section className="space-y-2 rounded-lg border border-sky-300/20 bg-sky-950/15 p-3">
            <h3 className="scroll-section-title flex items-center gap-2 text-sm font-semibold text-sky-100">
              <ClipboardCheck className="h-3.5 w-3.5" /> 已完成的战报
            </h3>
            <div className="done-count text-[11px] text-slate-400">共 {doneTasks.length} 条</div>
            {doneTasks.length === 0 ? <p className="scroll-empty text-xs text-slate-400">暂无已完成任务</p> : null}
            {doneTasks.map((task) => (
              <article key={task.id} className="flex items-center gap-2 rounded-md border border-sky-300/20 bg-slate-900/55 p-2.5">
                <span className="text-xs text-emerald-200">✔</span>
                <div className="text-xs font-semibold text-slate-100">{task.title}</div>
              </article>
            ))}
          </section>
        </CardContent>
      </Card>
    </div>
  )
}
