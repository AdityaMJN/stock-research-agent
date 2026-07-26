import { apiClient, mockDelay, useMocks } from './client'
import type { PortfolioSummary } from '../types/dashboard'

class PortfolioApi {
  async list(): Promise<PortfolioSummary[]> {
    if (useMocks) return mockDelay([{ name: 'TOP20', value: 1_024_500, returnPercent: 2.45, holdings: 20 }, { name: 'TOP10', value: 1_011_200, returnPercent: 1.12, holdings: 10 }])
    return (await apiClient.get<PortfolioSummary[]>('/portfolios')).data
  }
}

export const portfolioApi = new PortfolioApi()
