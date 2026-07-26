import { apiClient, mockDelay, useMocks } from './client'
import type { Screener } from '../types/stocks'

class ScreenerApi {
  async list(): Promise<Screener[]> {
    const mock: Screener[] = [
      { name: 'Momentum', description: '3- and 6-month price strength', candidateCount: 100, status: 'healthy' },
      { name: 'Strong Uptrend', description: 'Aligned moving averages and RSI', candidateCount: 183, status: 'healthy' },
      { name: '52 Week High', description: 'Trading within 5% of annual high', candidateCount: 165, status: 'healthy' },
      { name: 'Golden Cross', description: 'Fresh SMA50 and SMA200 crossovers', candidateCount: 8, status: 'healthy' },
    ]
    return useMocks ? mockDelay(mock) : (await apiClient.get<Screener[]>('/screeners')).data
  }
}

export const screenerApi = new ScreenerApi()
