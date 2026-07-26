import { ArrowPathIcon, Bars3Icon, MoonIcon, SunIcon, UserCircleIcon } from '@heroicons/react/24/outline'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { dashboardApi } from '../api/dashboardApi'
import { stocksApi } from '../api/stocksApi'
import { SearchBar } from '../components/SearchBar'
import { useTheme } from '../hooks/useTheme'
import { formatDateTime } from '../utils/formatters'

export function TopNavigation({ onMenu }: { onMenu: () => void }) {
  const [query, setQuery] = useState('')
  const { theme, toggleTheme } = useTheme()
  const queryClient = useQueryClient()
  const dashboard = useQuery({ queryKey: ['dashboard'], queryFn: () => dashboardApi.getDashboard() })
  const search = useQuery({ queryKey: ['stock-search', query], queryFn: () => stocksApi.search(query), enabled: query.trim().length >= 2 })
  return <header className="flex h-16 items-center gap-3 border-b border-slate-200 bg-white px-4 dark:border-slate-800 dark:bg-slate-900 sm:px-6"><button onClick={onMenu} className="rounded-lg p-2 hover:bg-slate-100 dark:hover:bg-slate-800 lg:hidden"><Bars3Icon className="h-5 w-5" /></button><div className="relative w-full max-w-md"><SearchBar value={query} onChange={setQuery} />{query.trim().length >= 2 && <div className="absolute top-11 z-20 w-full overflow-hidden rounded-lg border border-slate-200 bg-white shadow-lg dark:border-slate-700 dark:bg-slate-900">{search.isLoading && <p className="px-3 py-2 text-sm text-slate-500">Searching…</p>}{search.data?.map((stock) => <button className="flex w-full items-center justify-between px-3 py-2 text-left text-sm hover:bg-slate-50 dark:hover:bg-slate-800" key={stock.stockId} onClick={() => setQuery(stock.symbol)}><span><b>{stock.symbol}</b><span className="ml-2 text-slate-500">{stock.companyName}</span></span><span className="text-slate-500">₹{stock.closePrice}</span></button>)}{search.data?.length === 0 && <p className="px-3 py-2 text-sm text-slate-500">No matching stocks.</p>}</div>}</div><div className="ml-auto hidden text-right text-xs text-slate-500 dark:text-slate-400 sm:block"><p>Last database update</p><p className="font-medium text-slate-700 dark:text-slate-300">{dashboard.data ? formatDateTime(dashboard.data.metrics.latestUpdate) : 'Loading…'}</p></div><button onClick={() => queryClient.invalidateQueries()} className="rounded-lg p-2 hover:bg-slate-100 dark:hover:bg-slate-800" aria-label="Refresh data"><ArrowPathIcon className="h-5 w-5" /></button><button onClick={toggleTheme} className="rounded-lg p-2 hover:bg-slate-100 dark:hover:bg-slate-800" aria-label="Toggle theme">{theme === 'dark' ? <SunIcon className="h-5 w-5" /> : <MoonIcon className="h-5 w-5" />}</button><button className="rounded-lg p-1 hover:bg-slate-100 dark:hover:bg-slate-800" aria-label="User menu"><UserCircleIcon className="h-7 w-7 text-slate-500" /></button></header>
}
