import { useQuery } from '@tanstack/react-query'
import { stocksApi } from '../api/stocksApi'
import { Card } from '../components/Card'
import { DataTable } from '../components/DataTable'
import { ErrorState } from '../components/ErrorState'
import { LoadingSpinner } from '../components/LoadingSpinner'
import { PageHeader } from '../components/PageHeader'
import { formatCurrency } from '../utils/formatters'
import type { Stock } from '../types/stocks'

export function StocksPage() { const query = useQuery({ queryKey: ['stocks'], queryFn: () => stocksApi.list() }); if (query.isLoading) return <div className="page-container"><LoadingSpinner /></div>; if (query.isError || !query.data) return <div className="page-container"><ErrorState onRetry={() => query.refetch()} /></div>; return <div className="page-container"><PageHeader title="Stocks" description="NSE universe with current technical snapshot." breadcrumbs={['Research', 'Stocks']} /><Card><DataTable data={query.data} columns={[{ key: 'symbol', header: 'Symbol', render: (stock: Stock) => <b>{stock.symbol}</b> }, { key: 'name', header: 'Company', render: (stock: Stock) => stock.companyName }, { key: 'sector', header: 'Sector', render: (stock: Stock) => stock.sector }, { key: 'price', header: 'Close', render: (stock: Stock) => formatCurrency(stock.closePrice) }, { key: 'momentum', header: 'Momentum', render: (stock: Stock) => stock.momentumScore.toFixed(1) }, { key: 'rsi', header: 'RSI 14', render: (stock: Stock) => stock.rsi14.toFixed(1) }]} /></Card></div> }
