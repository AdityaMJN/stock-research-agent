import { useQuery } from '@tanstack/react-query'
import { screenerApi } from '../api/screenerApi'
import { Card } from '../components/Card'
import { ErrorState } from '../components/ErrorState'
import { LoadingSpinner } from '../components/LoadingSpinner'
import { PageHeader } from '../components/PageHeader'
import { StatusBadge } from '../components/StatusBadge'

export function ScreenersPage() { const query = useQuery({ queryKey: ['screeners'], queryFn: () => screenerApi.list() }); if (query.isLoading) return <div className="page-container"><LoadingSpinner /></div>; if (query.isError || !query.data) return <div className="page-container"><ErrorState onRetry={() => query.refetch()} /></div>; return <div className="page-container"><PageHeader title="Screeners" description="Current candidate counts from technical screening models." breadcrumbs={['Research', 'Screeners']} /><div className="grid gap-4 md:grid-cols-2">{query.data.map((screener) => <Card className="p-5" key={screener.name}><div className="flex items-start justify-between"><div><h2 className="font-semibold">{screener.name}</h2><p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{screener.description}</p></div><StatusBadge status={screener.status} /></div><p className="mt-6 text-3xl font-semibold">{screener.candidateCount}</p><p className="text-xs text-slate-500">candidates</p></Card>)}</div></div> }
