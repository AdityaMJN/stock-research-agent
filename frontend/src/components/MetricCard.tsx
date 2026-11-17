import type { ReactNode } from 'react'
import { Card } from './Card'

export function MetricCard({ label, value, icon, detail, action }: { label: string; value: ReactNode; icon: ReactNode; detail?: ReactNode; action?: ReactNode }) {
  return <Card className="p-5"><div className="flex items-start justify-between"><div className="min-w-0 flex-1"><p className="text-sm font-medium text-slate-500 dark:text-slate-400">{label}</p><p className="mt-2 text-2xl font-semibold tracking-tight">{value}</p>{detail && <div className="mt-2 text-xs text-slate-500 dark:text-slate-400">{detail}</div>}</div><div className="flex items-center gap-2"><div className="rounded-lg bg-emerald-500/10 p-2.5 text-emerald-600 dark:text-emerald-400">{icon}</div>{action && <div className="shrink-0">{action}</div>}</div></div></Card>
}
