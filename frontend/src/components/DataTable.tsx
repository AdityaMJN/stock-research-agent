import type { ReactNode } from 'react'
import { EmptyState } from './EmptyState'

export interface Column<T> { key: string; header: string; render: (row: T) => ReactNode; className?: string }

export function DataTable<T>({ columns, data, emptyMessage }: { columns: Column<T>[]; data: T[]; emptyMessage?: string }) {
  if (!data.length) return <EmptyState description={emptyMessage} />
  return <div className="overflow-x-auto"><table className="w-full text-left text-sm"><thead className="border-b border-slate-100 text-xs uppercase tracking-wide text-slate-500 dark:border-slate-800 dark:text-slate-400"><tr>{columns.map((column) => <th key={column.key} className="px-5 py-3 font-medium">{column.header}</th>)}</tr></thead><tbody className="divide-y divide-slate-100 dark:divide-slate-800">{data.map((row, index) => <tr className="transition hover:bg-slate-50/80 dark:hover:bg-slate-800/50" key={index}>{columns.map((column) => <td className="px-5 py-3.5" key={column.key}>{column.render(row)}</td>)}</tr>)}</tbody></table></div>
}
