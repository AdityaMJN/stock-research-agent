import { useQuery } from '@tanstack/react-query'
import { jobsApi } from '../api/jobsApi'
import { Card } from '../components/Card'
import { DataTable } from '../components/DataTable'
import { ErrorState } from '../components/ErrorState'
import { LoadingSpinner } from '../components/LoadingSpinner'
import { PageHeader } from '../components/PageHeader'
import { StatusBadge } from '../components/StatusBadge'
import { formatDateTime } from '../utils/formatters'

export function JobsPage() {
    const query = useQuery({ queryKey: ['jobs'], queryFn: () => jobsApi.list() })

    if (query.isLoading) return <div className="page-container"><LoadingSpinner /></div>
    if (query.isError || !query.data) return <div className="page-container"><ErrorState onRetry={() => query.refetch()} /></div>

    return <div className="page-container"><PageHeader title="Jobs" description="Pipeline activity, scheduled runs, and operational health." breadcrumbs={['Research', 'Jobs']} /><Card><div className="panel-header"><h2 className="font-semibold">Scheduled Pipeline</h2><StatusBadge status="healthy" /></div><DataTable data={query.data} columns={[{ key: 'name', header: 'Job', render: (job) => <b>{job.name}</b> }, { key: 'startedAt', header: 'Started', render: (job) => formatDateTime(job.startedAt) }, { key: 'duration', header: 'Duration', render: (job) => job.duration }, { key: 'status', header: 'Status', render: (job) => <StatusBadge status={job.status} /> }]} /></Card></div>
}
