import { apiClient, mockDelay, useMocks } from './client'
import type { DashboardData } from '../types/dashboard'

const dashboardMock: DashboardData = {
  metrics: { stocksTracked: 2364, latestUpdate: '2026-07-26T09:32:00+05:30', indicatorsStatus: 'healthy', screenersStatus: 'healthy', portfolioCount: 3 },
  topMomentumStocks: [
    { stockId: 1, symbol: 'BEL', companyName: 'Bharat Electronics', score: 92.4, price: 412.8, changePercent: 3.2 },
    { stockId: 2, symbol: 'TRENT', companyName: 'Trent Limited', score: 88.1, price: 5480, changePercent: 1.8 },
    { stockId: 3, symbol: 'MAZDOCK', companyName: 'Mazagon Dock', score: 84.6, price: 2821, changePercent: 2.5 },
  ],
  latestBuySignals: [
    { stockId: 4, symbol: 'HAL', companyName: 'Hindustan Aeronautics', score: 86.2, price: 4690, changePercent: 0.9 },
    { stockId: 5, symbol: 'CDSL', companyName: 'Central Depository Services', score: 80.4, price: 1436, changePercent: 1.2 },
  ],
  recentJobs: [
    { id: 'job-1', name: 'Daily market update', status: 'healthy', startedAt: '2026-07-26T09:00:00+05:30', duration: '2m 18s' },
    { id: 'job-2', name: 'Portfolio rebalance', status: 'healthy', startedAt: '2026-07-25T18:00:00+05:30', duration: '14s' },
  ],
  portfolios: [
    { name: 'TOP20', value: 1_024_500, returnPercent: 2.45, holdings: 20 },
    { name: 'TOP10', value: 1_011_200, returnPercent: 1.12, holdings: 10 },
  ],
}

class DashboardApi {
  async getDashboard(): Promise<DashboardData> {
    if (useMocks) return mockDelay(dashboardMock)
    return (await apiClient.get<DashboardData>('/dashboard')).data
  }
}

export const dashboardApi = new DashboardApi()
