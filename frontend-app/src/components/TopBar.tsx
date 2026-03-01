import { useEffect, useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import { Activity, Clock3, GaugeCircle, Wifi } from 'lucide-react'
import { Badge } from './ui/badge'
import { Button } from './ui/button'
import type { Agent } from '../types'

interface TopBarProps {
  fps: number
  onlineCount: number
  activeCount: number
  totalCount: number
  selectedAgent: Agent | null
  onClearSelection: () => void
}

function useClockText() {
  const [clockText, setClockText] = useState(() =>
    new Date().toLocaleTimeString('zh-CN', { hour12: false }),
  )

  useEffect(() => {
    const timer = window.setInterval(() => {
      setClockText(new Date().toLocaleTimeString('zh-CN', { hour12: false }))
    }, 1000)

    return () => {
      window.clearInterval(timer)
    }
  }, [])

  return clockText
}

export function TopBar({
  fps,
  onlineCount,
  activeCount,
  totalCount,
  selectedAgent,
  onClearSelection,
}: TopBarProps) {
  const clockText = useClockText()

  const healthTone = useMemo(() => {
    if (fps >= 55) return 'success'
    if (fps >= 30) return 'warning'
    return 'danger'
  }, [fps])

  return (
    <motion.header
      id="top-bar"
      className="pixel-panel rounded-2xl border border-sky-300/25 bg-slate-950/70 px-4 py-3 backdrop-blur"
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant="success" className="font-mono">
            <Wifi className="h-3.5 w-3.5" />
            在线 {onlineCount}/{totalCount}
          </Badge>

          <Badge variant="secondary" className="font-mono text-slate-100">
            <Activity className="h-3.5 w-3.5 text-emerald-300" />
            活跃 {activeCount}
          </Badge>

          <Badge
            id="fps-indicator"
            data-mount="fps-indicator"
            variant={healthTone}
            className="font-mono"
          >
            <GaugeCircle className="h-3.5 w-3.5" />
            FPS {fps}
          </Badge>

          <Badge variant="secondary" className="font-mono text-slate-100">
            <Clock3 className="h-3.5 w-3.5 text-violet-200" />
            {clockText}
          </Badge>
        </div>

        {selectedAgent && (
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.2 }}
          >
            <Button
              variant="outline"
              size="sm"
              className="border-emerald-300/50 bg-emerald-500/10 text-emerald-100 hover:bg-emerald-500/20"
              onClick={onClearSelection}
              title="清除点名高亮"
            >
              点名：{selectedAgent.emoji} {selectedAgent.name} ×
            </Button>
          </motion.div>
        )}
      </div>
    </motion.header>
  )
}
