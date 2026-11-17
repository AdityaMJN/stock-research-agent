export type SystemStatus = 'healthy' | 'warning' | 'error' | 'neutral'

export interface DashboardMetrics {
  stocksTracked: number
  latestUpdate: string
  indicatorsLastUpdated?: string | null
  screenersLastUpdated?: string | null
  indicatorsStatus: SystemStatus
  screenersStatus: SystemStatus
  portfolioCount: number
}

export interface RankedStock { stockId: number; symbol: string; companyName: string; score: number; price: number; changePercent: number }
export interface JobSummary { id: string; name: string; status: SystemStatus; startedAt: string; duration: string }
export interface PortfolioSummary { name: string; value: number; returnPercent: number; holdings: number }

export interface DashboardData {
  metrics: DashboardMetrics
  topMomentumStocks: RankedStock[]
  latestBuySignals: RankedStock[]
  recentJobs: JobSummary[]
  portfolios: PortfolioSummary[]
}
