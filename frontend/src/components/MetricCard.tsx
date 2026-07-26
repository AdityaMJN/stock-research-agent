import type { ReactNode } from 'react'
import { Card } from './Card'

export function MetricCard({ label, value, icon, detail }: { label: string; value: ReactNode; icon: ReactNode; detail?: ReactNode }) {
  return <Card className="p-5"><div className="flex items-start justify-between"><div><p className="text-sm font-medium text-slate-500 dark:text-slate-400">{label}</p><p className="mt-2 text-2xl font-semibold tracking-tight">{value}</p>{detail && <div className="mt-2 text-xs text-slate-500 dark:text-slate-400">{detail}</div>}</div><div className="rounded-lg bg-emerald-500/10 p-2.5 text-emerald-600 dark:text-emerald-400">{icon}</div></div></Card>
}
