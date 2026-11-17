import axios from 'axios'

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1',
  timeout: 10_000,
})

export const useMocks = import.meta.env.VITE_USE_MOCKS === 'true'

export const mockDelay = <T>(data: T, delay = 250): Promise<T> => new Promise((resolve) => {
  window.setTimeout(() => resolve(data), delay)
})
