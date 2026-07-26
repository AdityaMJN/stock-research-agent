import { useEffect, useState } from 'react'

type Theme = 'light' | 'dark'

const storageKey = 'stock-research-theme'

export function useTheme() {
  const [theme, setTheme] = useState<Theme>(() => (localStorage.getItem(storageKey) as Theme) ?? 'dark')

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark')
    localStorage.setItem(storageKey, theme)
  }, [theme])

  return { theme, toggleTheme: () => setTheme((value) => value === 'dark' ? 'light' : 'dark') }
}
