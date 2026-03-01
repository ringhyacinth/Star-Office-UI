import { cn } from '../../lib/utils'

interface ProgressProps {
  value: number
  className?: string
}

export function Progress({ value, className }: ProgressProps) {
  const clamped = Math.max(0, Math.min(100, value))

  return (
    <div
      className={cn(
        'relative h-2 w-full overflow-hidden rounded-full bg-slate-800/80 ring-1 ring-inset ring-slate-600/30',
        className,
      )}
      role="progressbar"
      aria-valuenow={Math.round(clamped)}
      aria-valuemin={0}
      aria-valuemax={100}
    >
      <div
        className="h-full rounded-full bg-gradient-to-r from-cyan-300 via-sky-400 to-emerald-300 transition-all duration-500"
        style={{ width: `${clamped}%` }}
      />
    </div>
  )
}
