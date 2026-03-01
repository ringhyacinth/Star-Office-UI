import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '../../lib/utils'

const badgeVariants = cva(
  'inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium leading-none tracking-wide transition-colors',
  {
    variants: {
      variant: {
        default: 'border-primary/30 bg-primary/15 text-primary-foreground',
        secondary: 'border-border/70 bg-secondary/50 text-secondary-foreground',
        success: 'border-emerald-300/30 bg-emerald-400/15 text-emerald-100',
        warning: 'border-amber-300/30 bg-amber-400/15 text-amber-100',
        danger: 'border-rose-300/30 bg-rose-400/15 text-rose-100',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  },
)

function Badge({ className, variant, ...props }: React.ComponentProps<'div'> & VariantProps<typeof badgeVariants>) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />
}

export { Badge, badgeVariants }
