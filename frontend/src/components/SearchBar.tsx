import { MagnifyingGlassIcon } from '@heroicons/react/20/solid'

export function SearchBar({ value, onChange, placeholder = 'Search stocks…' }: { value: string; onChange: (value: string) => void; placeholder?: string }) {
  return <label className="relative block"><MagnifyingGlassIcon className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" /><input value={value} onChange={(event) => onChange(event.target.value)} placeholder={placeholder} className="h-9 w-full rounded-lg border border-slate-200 bg-slate-50 pl-9 pr-3 text-sm outline-none transition focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/15 dark:border-slate-700 dark:bg-slate-800" /></label>
}
