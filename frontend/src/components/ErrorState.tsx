import { ExclamationTriangleIcon } from '@heroicons/react/24/outline'

export function ErrorState({ onRetry }: { onRetry?: () => void }) {
  return <div className="flex min-h-48 flex-col items-center justify-center p-8 text-center"><ExclamationTriangleIcon className="h-9 w-9 text-rose-500" /><h3 className="mt-3 font-medium">Unable to load this data</h3><p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Check the API connection and try again.</p>{onRetry && <button onClick={onRetry} className="mt-4 rounded-lg bg-emerald-600 px-3 py-2 text-sm font-medium text-white hover:bg-emerald-700">Try again</button>}</div>
}
