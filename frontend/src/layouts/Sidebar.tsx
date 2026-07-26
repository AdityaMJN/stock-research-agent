import { ChartBarIcon, ChartPieIcon, ClockIcon, Cog6ToothIcon, HomeIcon, PresentationChartLineIcon, QueueListIcon, ScaleIcon, WrenchScrewdriverIcon } from '@heroicons/react/24/outline'
import { NavLink } from 'react-router-dom'
import { cn } from '../utils/cn'

const navigation = [
  { label: 'Dashboard', to: '/', icon: HomeIcon }, { label: 'Stocks', to: '/stocks', icon: ChartBarIcon },
  { label: 'Screeners', to: '/screeners', icon: QueueListIcon }, { label: 'Portfolio', to: '/portfolio', icon: ChartPieIcon },
  { label: 'Backtesting', to: '/backtesting', icon: PresentationChartLineIcon }, { label: 'Rules', to: '/rules', icon: ScaleIcon },
  { label: 'Jobs', to: '/jobs', icon: ClockIcon }, { label: 'Settings', to: '/settings', icon: Cog6ToothIcon },
]

export function Sidebar({ onNavigate }: { onNavigate?: () => void }) {
  return <aside className="flex h-full w-64 flex-col border-r border-slate-800 bg-terminal px-3 py-5 text-slate-300"><div className="flex items-center gap-2 px-3"><WrenchScrewdriverIcon className="h-6 w-6 text-emerald-400" /><div><p className="font-semibold text-white">Stock Research</p><p className="text-xs text-slate-500">Analyst Workspace</p></div></div><nav className="mt-8 space-y-1">{navigation.map(({ label, to, icon: Icon }) => <NavLink end={to === '/'} key={to} onClick={onNavigate} to={to} className={({ isActive }) => cn('flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition', isActive ? 'bg-emerald-500/15 text-emerald-300' : 'hover:bg-slate-800 hover:text-white')}><Icon className="h-5 w-5" />{label}</NavLink>)}</nav><div className="mt-auto rounded-lg border border-slate-800 bg-slate-900/50 p-3 text-xs text-slate-500">Internal analyst dashboard<br /><span className="text-emerald-400">Backend connection ready</span></div></aside>
}
