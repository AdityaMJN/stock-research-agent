import { ArrowPathIcon, ChartBarIcon, ClockIcon, DocumentChartBarIcon, RectangleStackIcon, WalletIcon, XMarkIcon } from '@heroicons/react/24/outline'
import { useQuery } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { dashboardApi } from '../api/dashboardApi'
import { jobsApi, type JobExecution } from '../api/jobsApi'
import { Card } from '../components/Card'
import { DataTable } from '../components/DataTable'
import { ErrorState } from '../components/ErrorState'
import { LoadingSpinner } from '../components/LoadingSpinner'
import { MetricCard } from '../components/MetricCard'
import { PageHeader } from '../components/PageHeader'
import { StatusBadge } from '../components/StatusBadge'
import { formatCurrency, formatDateOnly, formatDateTime, formatNumber } from '../utils/formatters'
import type { JobSummary, PortfolioSummary, RankedStock } from '../types/dashboard'

const stockColumns = [
  { key: 'symbol', header: 'Symbol', render: (stock: RankedStock) => <span className="font-semibold">{stock.symbol}</span> },
  { key: 'company', header: 'Company', render: (stock: RankedStock) => <span className="text-slate-500 dark:text-slate-400">{stock.companyName}</span> },
  { key: 'score', header: 'Score', render: (stock: RankedStock) => stock.score.toFixed(1) },
  { key: 'change', header: 'Change', render: (stock: RankedStock) => <span className={stock.changePercent >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600'}>{stock.changePercent >= 0 ? '+' : ''}{stock.changePercent.toFixed(2)}%</span> },
]

export function DashboardPage() {
  const query = useQuery({ queryKey: ['dashboard'], queryFn: () => dashboardApi.getDashboard() })
  const [activeJob, setActiveJob] = useState<JobExecution | null>(null)
  const [jobOutput, setJobOutput] = useState<string[]>([])
  const [jobRunning, setJobRunning] = useState(false)
  const [jobStatusMessage, setJobStatusMessage] = useState('Idle')
  const [showOutputDialog, setShowOutputDialog] = useState(false)

  useEffect(() => {
    if (!activeJob || activeJob.status !== 'running') return

    const timer = window.setInterval(async () => {
      try {
        const latest = await jobsApi.getJob(activeJob.id)
        setActiveJob(latest)
        setJobOutput(latest.output ?? [])
        if (latest.status !== 'running') {
          window.clearInterval(timer)
          setJobRunning(false)
        }
      } catch {
        window.clearInterval(timer)
        setJobRunning(false)
      }
    }, 1000)

    return () => window.clearInterval(timer)
  }, [activeJob?.id, activeJob?.status])

  const startJob = async (command: 'full-portfolio-run' | 'validate-pipeline' | 'run-all-checks' | 'update-indicators' | 'run-screeners') => {
    setJobOutput([])
    setJobRunning(true)
    setShowOutputDialog(true)

    const labelMap = {
      'full-portfolio-run': 'Starting Full Portfolio Run...',
      'validate-pipeline': 'Starting Validate Pipeline...',
      'run-all-checks': 'Running all checks...',
      'update-indicators': 'Refreshing indicators...',
      'run-screeners': 'Refreshing screeners...',
    }

    setJobStatusMessage(labelMap[command])
    try {
      const job = await jobsApi.runJob(command)
      setActiveJob(job)
      setJobOutput(job.output ?? [])
      setJobStatusMessage(job.status === 'running' ? 'Job started successfully' : 'Job finished')
      if (job.status !== 'running') {
        window.setTimeout(() => void query.refetch(), 1000)
      }
    } catch (error) {
      setJobOutput([`Failed to start job: ${error instanceof Error ? error.message : String(error)}`])
      setJobRunning(false)
      setJobStatusMessage('Failed to start job')
    }
  }

  const andRefresh = async (command: 'full-portfolio-run' | 'validate-pipeline' | 'run-all-checks' | 'update-indicators' | 'run-screeners') => {
    await startJob(command)
    window.setTimeout(() => void query.refetch(), 1200)
  }

  const outputText = jobOutput.length ? jobOutput.join('\n') : (jobRunning ? 'Starting job, please wait...' : 'Press a button to start a job and watch the console-style output here.')

  if (query.isLoading) return <div className="page-container"><LoadingSpinner /></div>
  if (query.isError || !query.data) return <div className="page-container"><ErrorState onRetry={() => query.refetch()} /></div>
  const { metrics, topMomentumStocks, latestBuySignals, recentJobs, portfolios } = query.data
  const latestUpdateDate = metrics.latestUpdate ? new Intl.DateTimeFormat('en-US', { day: 'numeric', month: 'short' }).format(new Date(metrics.latestUpdate)) : 'Not available'
  const latestUpdateYearAndTime = metrics.latestUpdate ? new Intl.DateTimeFormat('en-US', { year: 'numeric', hour: 'numeric', minute: '2-digit' }).format(new Date(metrics.latestUpdate)) : 'Not available'
  const indicatorsUpdatedText = formatDateTime(metrics.indicatorsLastUpdated)
  const screenersUpdatedText = formatDateTime(metrics.screenersLastUpdated)

  return <div className="page-container"><PageHeader title="Market Overview" description="Operational view of the NSE research pipeline and model outputs." breadcrumbs={['Research', 'Dashboard']} /><div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5"><MetricCard label="Stocks Tracked" value={formatNumber(metrics.stocksTracked)} icon={<ChartBarIcon className="h-5 w-5" />} /><MetricCard label="Latest Update" value={<div className="space-y-1"><div className="text-[2rem] font-semibold leading-none tracking-tight text-slate-900 dark:text-white">{latestUpdateDate}</div><div className="text-lg font-medium leading-none text-slate-700 dark:text-slate-200">{latestUpdateYearAndTime}</div></div>} action={<button onClick={() => void andRefresh('full-portfolio-run')} className="rounded border border-emerald-500/40 bg-emerald-500/10 p-2 text-emerald-300 transition hover:bg-emerald-500/20" aria-label="Refresh latest update"><ArrowPathIcon className="h-4 w-4" /></button>} icon={<ClockIcon className="h-5 w-5" />} /><MetricCard label="Indicators" value={<StatusBadge status={metrics.indicatorsStatus} />} detail={<span>Last updated: {indicatorsUpdatedText}</span>} action={<button onClick={() => void andRefresh('update-indicators')} className="rounded border border-slate-700 p-2 text-slate-300 transition hover:bg-slate-800" aria-label="Refresh indicators"><ArrowPathIcon className="h-4 w-4" /></button>} icon={<DocumentChartBarIcon className="h-5 w-5" />} /><MetricCard label="Screeners" value={<StatusBadge status={metrics.screenersStatus} />} detail={<span>Last updated: {screenersUpdatedText}</span>} action={<button onClick={() => void andRefresh('run-screeners')} className="rounded border border-slate-700 p-2 text-slate-300 transition hover:bg-slate-800" aria-label="Refresh screeners"><ArrowPathIcon className="h-4 w-4" /></button>} icon={<RectangleStackIcon className="h-5 w-5" />} /><MetricCard label="Portfolios" value={metrics.portfolioCount} icon={<WalletIcon className="h-5 w-5" />} /></div><div className="grid gap-6 xl:grid-cols-2"><Card className="xl:col-span-2"><div className="panel-header"><h2 className="font-semibold">Run Pipeline Jobs</h2><div className="flex flex-wrap gap-2"><button onClick={() => void startJob('validate-pipeline')} className="rounded bg-emerald-600 px-3 py-2 text-sm font-medium text-white hover:bg-emerald-700">Validate Pipeline</button><button onClick={() => void startJob('run-all-checks')} className="rounded bg-violet-600 px-3 py-2 text-sm font-medium text-white hover:bg-violet-700">Run All Checks</button><button onClick={() => void startJob('full-portfolio-run')} className="rounded bg-slate-800 px-3 py-2 text-sm font-medium text-white hover:bg-slate-700">Full Portfolio Run</button></div></div><div className="mt-4 rounded-lg border border-slate-200 bg-slate-950/95 p-4 text-sm text-slate-100 dark:border-slate-800"><div className="mb-2 flex items-center justify-between"><div><p className="font-medium">Live output</p><p className="mt-1 text-xs text-slate-400">{jobStatusMessage}</p></div><div className="flex items-center gap-2"><button onClick={() => setShowOutputDialog(true)} className="rounded border border-slate-700 px-2.5 py-1 text-xs font-medium text-slate-200 hover:bg-slate-800">Open output</button><StatusBadge status={activeJob?.status === 'failed' ? 'error' : activeJob?.status === 'completed' ? 'healthy' : jobRunning ? 'neutral' : 'neutral'} /></div></div><p className="text-xs text-slate-400">The job stream will appear in a separate dialog while it runs.</p></div>{showOutputDialog && <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 p-4"><div className="flex max-h-[80vh] w-full max-w-3xl flex-col rounded-xl border border-slate-200 bg-white p-4 text-slate-800 shadow-2xl dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"><div className="mb-3 flex items-center justify-between"><div><p className="font-semibold">Job output</p><p className="text-xs text-slate-500 dark:text-slate-400">{jobStatusMessage}</p></div><button onClick={() => setShowOutputDialog(false)} className="rounded p-1 text-slate-500 hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-800 dark:hover:text-slate-200"><XMarkIcon className="h-5 w-5" /></button></div><pre className="overflow-auto whitespace-pre-wrap font-mono text-xs leading-5">{outputText}</pre></div></div>} </Card><DashboardTable title="Top Momentum Stocks" data={topMomentumStocks} /><DashboardTable title="Latest Buy Signals" data={latestBuySignals} /><RecentJobs jobs={recentJobs} /><PortfolioSummary portfolios={portfolios} /></div></div>
}

function DashboardTable({ title, data }: { title: string; data: RankedStock[] }) { return <Card><div className="panel-header"><h2 className="font-semibold">{title}</h2><button className="text-sm font-medium text-emerald-600 hover:text-emerald-700 dark:text-emerald-400">View all</button></div><DataTable columns={stockColumns} data={data} /></Card> }
function RecentJobs({ jobs }: { jobs: JobSummary[] }) { return <Card><div className="panel-header"><h2 className="font-semibold">Recent Jobs</h2></div><div className="divide-y divide-slate-100 dark:divide-slate-800">{jobs.map((job) => <div className="flex items-center justify-between px-5 py-4" key={job.id}><div><p className="font-medium">{job.name}</p><p className="mt-1 text-xs text-slate-500">{formatDateTime(job.startedAt)} · {job.duration}</p></div><StatusBadge status={job.status} /></div>)}</div></Card> }
function PortfolioSummary({ portfolios }: { portfolios: PortfolioSummary[] }) { return <Card><div className="panel-header"><h2 className="font-semibold">Portfolio Summary</h2></div><div className="divide-y divide-slate-100 dark:divide-slate-800">{portfolios.map((portfolio) => <div className="flex items-center justify-between px-5 py-4" key={portfolio.name}><div><p className="font-medium">{portfolio.name}</p><p className="mt-1 text-xs text-slate-500">{portfolio.holdings} holdings</p></div><div className="text-right"><p className="font-semibold">{formatCurrency(portfolio.value)}</p><p className={portfolio.returnPercent >= 0 ? 'text-xs text-emerald-600 dark:text-emerald-400' : 'text-xs text-rose-600'}>{portfolio.returnPercent >= 0 ? '+' : ''}{portfolio.returnPercent.toFixed(2)}%</p></div></div>)}</div></Card> }
