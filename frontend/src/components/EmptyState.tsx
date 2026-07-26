import { InboxIcon } from '@heroicons/react/24/outline'

export function EmptyState({ title = 'No data available', description = 'There is nothing to display yet.' }: { title?: string; description?: string }) {
  return <div className="flex min-h-48 flex-col items-center justify-center p-8 text-center"><InboxIcon className="h-9 w-9 text-slate-400" /><h3 className="mt-3 font-medium">{title}</h3><p className="mt-1 max-w-sm text-sm text-slate-500 dark:text-slate-400">{description}</p></div>
}
