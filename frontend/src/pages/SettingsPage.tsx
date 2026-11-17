import { Card } from '../components/Card'
import { PageHeader } from '../components/PageHeader'

export function SettingsPage() { return <div className="page-container"><PageHeader title="Settings" description="Analyst workspace preferences and backend connection settings." breadcrumbs={['Research', 'Settings']} /><Card><div className="p-5"><h2 className="font-semibold">API Connection</h2><p className="mt-2 text-sm text-slate-500 dark:text-slate-400">Live data is enabled by default. Set <code className="rounded bg-slate-100 px-1 py-0.5 dark:bg-slate-800">VITE_USE_MOCKS=true</code> only when you want the frontend to use mock fallback values instead of the backend.</p></div></Card></div> }
