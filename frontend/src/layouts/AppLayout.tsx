import { useState, type PropsWithChildren } from 'react'
import { Sidebar } from './Sidebar'
import { TopNavigation } from './TopNavigation'

export function AppLayout({ children }: PropsWithChildren) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  return <div className="min-h-screen bg-canvas dark:bg-slate-950"><div className="hidden lg:fixed lg:inset-y-0 lg:flex"><Sidebar /></div>{sidebarOpen && <div className="fixed inset-0 z-40 lg:hidden"><button aria-label="Close menu" className="absolute inset-0 bg-slate-950/60" onClick={() => setSidebarOpen(false)} /><div className="relative h-full"><Sidebar onNavigate={() => setSidebarOpen(false)} /></div></div>}<div className="lg:pl-64"><TopNavigation onMenu={() => setSidebarOpen(true)} /><main>{children}</main></div></div>
}
