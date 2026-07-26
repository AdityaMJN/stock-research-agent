import { useQuery } from '@tanstack/react-query'
import { rulesApi } from '../api/rulesApi'
import { Card } from '../components/Card'
import { DataTable } from '../components/DataTable'
import { ErrorState } from '../components/ErrorState'
import { LoadingSpinner } from '../components/LoadingSpinner'
import { PageHeader } from '../components/PageHeader'
import { StatusBadge } from '../components/StatusBadge'
import type { Rule } from '../types/stocks'

export function RulesPage() { const query = useQuery({ queryKey: ['rules'], queryFn: () => rulesApi.list() }); if (query.isLoading) return <div className="page-container"><LoadingSpinner /></div>; if (query.isError || !query.data) return <div className="page-container"><ErrorState onRetry={() => query.refetch()} /></div>; return <div className="page-container"><PageHeader title="Portfolio Rules" description="Enabled rules and their contribution to portfolio scores." breadcrumbs={['Research', 'Rules']} /><Card><DataTable data={query.data} columns={[{ key: 'name', header: 'Rule', render: (rule: Rule) => <b>{rule.ruleName}</b> }, { key: 'type', header: 'Type', render: (rule: Rule) => rule.ruleType }, { key: 'weight', header: 'Weight', render: (rule: Rule) => `${(rule.weight * 100).toFixed(0)}%` }, { key: 'status', header: 'Status', render: (rule: Rule) => <StatusBadge status={rule.enabled ? 'healthy' : 'neutral'} /> }]} /></Card></div> }
