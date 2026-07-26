export interface Stock { stockId: number; symbol: string; companyName: string; sector: string; closePrice: number; momentumScore: number; rsi14: number }
export interface Screener { name: string; description: string; candidateCount: number; status: 'healthy' | 'warning' | 'error' | 'neutral' }
export interface Rule { id: number; ruleName: string; ruleType: string; weight: number; enabled: boolean }
