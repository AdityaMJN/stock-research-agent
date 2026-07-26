import { useQuery } from '@tanstack/react-query'
import { portfolioApi } from '../api/portfolioApi'
import { Card } from '../components/Card'
import { DataTable } from '../components/DataTable'
import { ErrorState } from '../components/ErrorState'
import { LoadingSpinner } from '../components/LoadingSpinner'
import { PageHeader } from '../components/PageHeader'
import { formatCurrency } from '../utils/formatters'
import type { PortfolioSummary } from '../types/dashboard'

export function PortfolioPage() { const query = useQuery({ queryKey: ['portfolios'], queryFn: () => portfolioApi.list() }); if (query.isLoading) return <div className="page-container"><LoadingSpinner /></div>; if (query.isError || !query.data) return <div className="page-container"><ErrorState onRetry={() => query.refetch()} /></div>; return <div className="page-container"><PageHeader title="Portfolio" description="Paper portfolios, allocations, and rebalance output." breadcrumbs={['Research', 'Portfolio']} /><Card><DataTable data={query.data} columns={[{ key: 'name', header: 'Portfolio', render: (item: PortfolioSummary) => <b>{item.name}</b> }, { key: 'holdings', header: 'Holdings', render: (item: PortfolioSummary) => item.holdings }, { key: 'value', header: 'Value', render: (item: PortfolioSummary) => formatCurrency(item.value) }, { key: 'return', header: 'Return', render: (item: PortfolioSummary) => <span className={item.returnPercent >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600'}>{item.returnPercent >= 0 ? '+' : ''}{item.returnPercent.toFixed(2)}%</span> }]} /></Card></div> }
