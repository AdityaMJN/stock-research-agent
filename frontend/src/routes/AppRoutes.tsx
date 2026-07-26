import { Navigate, Route, Routes } from 'react-router-dom'
import { AppLayout } from '../layouts/AppLayout'
import { BacktestingPage } from '../pages/BacktestingPage'
import { DashboardPage } from '../pages/DashboardPage'
import { JobsPage } from '../pages/JobsPage'
import { PortfolioPage } from '../pages/PortfolioPage'
import { RulesPage } from '../pages/RulesPage'
import { ScreenersPage } from '../pages/ScreenersPage'
import { SettingsPage } from '../pages/SettingsPage'
import { StocksPage } from '../pages/StocksPage'

export function AppRoutes() { return <AppLayout><Routes><Route path="/" element={<DashboardPage />} /><Route path="/stocks" element={<StocksPage />} /><Route path="/screeners" element={<ScreenersPage />} /><Route path="/portfolio" element={<PortfolioPage />} /><Route path="/backtesting" element={<BacktestingPage />} /><Route path="/rules" element={<RulesPage />} /><Route path="/jobs" element={<JobsPage />} /><Route path="/settings" element={<SettingsPage />} /><Route path="*" element={<Navigate to="/" replace />} /></Routes></AppLayout> }
