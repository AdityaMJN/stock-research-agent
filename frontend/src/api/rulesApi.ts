import { apiClient, mockDelay, useMocks } from './client'
import type { Rule } from '../types/stocks'

class RulesApi {
  async list(): Promise<Rule[]> {
    const mock: Rule[] = [
      { id: 1, ruleName: 'Momentum', ruleType: 'momentum', weight: 0.25, enabled: true },
      { id: 2, ruleName: 'Strong Uptrend', ruleType: 'strong_uptrend', weight: 0.20, enabled: true },
      { id: 3, ruleName: 'Golden Cross', ruleType: 'golden_cross', weight: 0.10, enabled: true },
    ]
    return useMocks ? mockDelay(mock) : (await apiClient.get<Rule[]>('/rules')).data
  }
}

export const rulesApi = new RulesApi()
