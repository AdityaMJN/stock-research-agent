import { useQuery } from '@tanstack/react-query'
import { backtestingApi } from '../api/backtestingApi'
import { Card } from '../components/Card'
import { DataTable } from '../components/DataTable'
import { ErrorState } from '../components/ErrorState'
import { LoadingSpinner } from '../components/LoadingSpinner'
import { PageHeader } from '../components/PageHeader'
import { formatCurrency } from '../utils/formatters'

export function BacktestingPage() {
    const query = useQuery({ queryKey: ['backtesting'], queryFn: () => backtestingApi.getBacktesting() })

    if (query.isLoading) return <div className="page-container"><LoadingSpinner /></div>
    if (query.isError || !query.data) return <div className="page-container"><ErrorState onRetry={() => query.refetch()} /></div>

    const { summary, equityCurve, benchmark } = query.data

    return <div className="page-container"><PageHeader title="Backtesting" description="Historical strategy validation and performance analytics." breadcrumbs={['Research', 'Backtesting']} /><div className="grid gap-6 xl:grid-cols-2"><Card><div className="panel-header"><h2 className="font-semibold">Strategy Summary</h2></div><DataTable data={summary} columns={[{ key: 'strategy', header: 'Strategy', render: (item) => <b>{item.strategy}</b> }, { key: 'period', header: 'Period', render: (item) => item.period }, { key: 'return', header: 'Return', render: (item) => <span className="text-emerald-600 dark:text-emerald-400">{item.totalReturnPercent.toFixed(1)}%</span> }, { key: 'sharpe', header: 'Sharpe', render: (item) => item.sharpeRatio.toFixed(2) }, { key: 'drawdown', header: 'Drawdown', render: (item) => <span className="text-rose-600">{item.maxDrawdownPercent.toFixed(1)}%</span> }]} /></Card><Card><div className="panel-header"><h2 className="font-semibold">Equity Curve</h2></div><DataTable data={equityCurve} columns={[{ key: 'month', header: 'Month', render: (item) => item.month }, { key: 'equity', header: 'Equity', render: (item) => formatCurrency(item.equity) }]} /></Card></div><Card className="mt-6"><div className="panel-header"><h2 className="font-semibold">Benchmark Comparison</h2></div><DataTable data={benchmark} columns={[{ key: 'month', header: 'Month', render: (item) => item.month }, { key: 'equity', header: 'Benchmark Equity', render: (item) => formatCurrency(item.equity) }]} /></Card></div>
}
