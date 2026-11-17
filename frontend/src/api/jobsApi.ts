import { apiClient, mockDelay, useMocks } from './client'
import type { JobSummary } from '../types/dashboard'

export interface JobExecution {
    id: string
    name: string
    status: 'running' | 'completed' | 'failed'
    startedAt: string
    duration?: string | null
    output: string[]
    exitCode?: number | null
    command?: string[]
}

type JobCommand = 'full-portfolio-run' | 'validate-pipeline' | 'run-all-checks' | 'update-indicators' | 'run-screeners'

class JobsApi {
    async list(): Promise<JobSummary[]> {
        const mock: JobSummary[] = [
            { id: 'job-1', name: 'Daily market update', status: 'healthy', startedAt: '2026-07-26T09:00:00+05:30', duration: '2m 18s' },
            { id: 'job-2', name: 'Portfolio rebalance', status: 'healthy', startedAt: '2026-07-25T18:00:00+05:30', duration: '14s' },
            { id: 'job-3', name: 'Screener refresh', status: 'warning', startedAt: '2026-07-25T16:30:00+05:30', duration: '1m 05s' },
        ]

        return useMocks ? mockDelay(mock) : (await apiClient.get<JobSummary[]>('/jobs')).data
    }

    async runJob(command: JobCommand): Promise<JobExecution> {
        return (await apiClient.post<JobExecution>(`/jobs/run/${command}`)).data
    }

    async getJob(jobId: string): Promise<JobExecution> {
        return (await apiClient.get<JobExecution>(`/jobs/${jobId}`)).data
    }
}

export const jobsApi = new JobsApi()
export type { JobCommand }
