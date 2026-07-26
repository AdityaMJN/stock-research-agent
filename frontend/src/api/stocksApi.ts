import { apiClient, mockDelay, useMocks } from './client'
import type { Stock } from '../types/stocks'

const stocksMock: Stock[] = [
  { stockId: 1, symbol: 'BEL', companyName: 'Bharat Electronics', sector: 'Defence', closePrice: 412.8, momentumScore: 92.4, rsi14: 68.2 },
  { stockId: 2, symbol: 'TRENT', companyName: 'Trent Limited', sector: 'Retail', closePrice: 5480, momentumScore: 88.1, rsi14: 63.9 },
]

class StocksApi {
  async list(): Promise<Stock[]> { return useMocks ? mockDelay(stocksMock) : (await apiClient.get<Stock[]>('/stocks')).data }
  async search(query: string): Promise<Stock[]> {
    if (useMocks) return mockDelay(stocksMock.filter((stock) => stock.symbol.includes(query.toUpperCase()) || stock.companyName.toLowerCase().includes(query.toLowerCase())))
    return (await apiClient.get<Stock[]>('/stocks', { params: { query } })).data
  }
}

export const stocksApi = new StocksApi()
