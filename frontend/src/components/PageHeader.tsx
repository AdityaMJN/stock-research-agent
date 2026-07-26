import type { ReactNode } from 'react'
import { ChevronRightIcon } from '@heroicons/react/20/solid'

export function PageHeader({ title, description, actions, breadcrumbs = [] }: { title: string; description?: string; actions?: ReactNode; breadcrumbs?: string[] }) {
  return <header className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end"><div>{breadcrumbs.length > 0 && <nav aria-label="Breadcrumb" className="mb-2 flex items-center gap-1 text-xs text-slate-500 dark:text-slate-400">{breadcrumbs.map((crumb, index) => <span className="flex items-center gap-1" key={crumb}>{index > 0 && <ChevronRightIcon className="h-3 w-3" />}{crumb}</span>)}</nav>}<h1 className="text-2xl font-semibold tracking-tight">{title}</h1>{description && <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{description}</p>}</div>{actions && <div className="flex items-center gap-2">{actions}</div>}</header>
}
