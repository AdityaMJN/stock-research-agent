import { apiClient, mockDelay, useMocks } from './client'

export interface BacktestingSummary {
    strategy: string
    period: string
    totalReturnPercent: number
    sharpeRatio: number
    maxDrawdownPercent: number
    winRatePercent: number
}

export interface BacktestingPoint {
    month: string
    equity: number
}

export interface BacktestingData {
    summary: BacktestingSummary[]
    equityCurve: BacktestingPoint[]
    benchmark: BacktestingPoint[]
}

class BacktestingApi {
    async getBacktesting(): Promise<BacktestingData> {
        const mock: BacktestingData = {
            summary: [
                { strategy: 'Momentum', period: '12M', totalReturnPercent: 26.8, sharpeRatio: 1.41, maxDrawdownPercent: -8.1, winRatePercent: 63.4 },
                { strategy: 'Golden Cross', period: '24M', totalReturnPercent: 18.5, sharpeRatio: 1.18, maxDrawdownPercent: -10.2, winRatePercent: 58.7 },
            ],
            equityCurve: [
                { month: 'Jan', equity: 100000 },
                { month: 'Feb', equity: 104500 },
                { month: 'Mar', equity: 109100 },
                { month: 'Apr', equity: 112800 },
                { month: 'May', equity: 118600 },
                { month: 'Jun', equity: 126800 },
            ],
            benchmark: [
                { month: 'Jan', equity: 100000 },
                { month: 'Feb', equity: 102300 },
                { month: 'Mar', equity: 103100 },
                { month: 'Apr', equity: 104700 },
                { month: 'May', equity: 106400 },
                { month: 'Jun', equity: 108900 },
            ],
        }

        return useMocks ? mockDelay(mock) : (await apiClient.get<BacktestingData>('/backtesting')).data
    }
}

export const backtestingApi = new BacktestingApi()
