import { cn } from '../utils/cn'
import type { SystemStatus } from '../types/dashboard'

const styles: Record<SystemStatus, string> = {
  healthy: 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-400',
  warning: 'bg-amber-500/10 text-amber-700 dark:text-amber-400',
  error: 'bg-rose-500/10 text-rose-700 dark:text-rose-400',
  neutral: 'bg-slate-500/10 text-slate-700 dark:text-slate-300',
}

export function StatusBadge({ status }: { status: SystemStatus }) {
  return <span className={cn('inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold capitalize', styles[status])}><span className="h-1.5 w-1.5 rounded-full bg-current" />{status}</span>
}
