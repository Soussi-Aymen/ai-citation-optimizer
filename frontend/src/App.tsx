import { useEffect, useState, type ReactNode } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useLocation, useParams } from 'react-router-dom'
import axios from 'axios'
import { apiUrl } from './lib/api'
import type { HealthResponse } from './types/api'
import Dashboard from './pages/Dashboard'
import PageDetail from './pages/PageDetail'
import { Sparkles } from 'lucide-react'

interface NavLinkProps {
  to: string
  children: ReactNode
}

const NavLink = ({ to, children }: NavLinkProps) => {
  const location = useLocation()
  const isActive = location.pathname === to
  return (
    <Link
      to={to}
      className={`rounded-lg px-4 py-2 font-medium transition-all ${
        isActive
          ? 'bg-blue-50 text-blue-600'
          : 'text-slate-500 hover:bg-slate-100 hover:text-slate-900'
      }`}
    >
      {children}
    </Link>
  )
}

function AuditPage() {
  const { url } = useParams()
  return <PageDetail key={url} />
}

function App() {
  const [peecAvailable, setPeecAvailable] = useState<boolean | null>(null)

  useEffect(() => {
    axios
      .get<HealthResponse>(apiUrl('/api/health'))
      .then((res) => setPeecAvailable(res.data.peec_available === true))
      .catch(() => setPeecAvailable(false))
  }, [])

  const poweredBy =
    peecAvailable === null
      ? 'Powered by Gemini'
      : peecAvailable
        ? 'Powered by Peec AI & Gemini'
        : 'Powered by Gemini'

  return (
    <Router>
      <div className="mx-auto min-h-screen max-w-6xl px-4 py-8">
        <nav className="mb-12 flex items-center justify-between border-b border-slate-200 pb-6">
          <div className="flex items-center gap-3">
            <Sparkles className="text-blue-500" size={32} aria-hidden />
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">Citation Optimizer</h1>
          </div>
          <div className="flex gap-2">
            <NavLink to="/">Dashboard</NavLink>
          </div>
        </nav>

        <main className="min-h-[calc(100vh-250px)]">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/audit/:url" element={<AuditPage />} />
          </Routes>
        </main>

        <footer className="mt-16 border-t border-slate-200 py-8 text-center text-slate-500">
          <p className="text-sm">&copy; 2026 AI Citation Optimizer. {poweredBy}.</p>
        </footer>
      </div>
    </Router>
  )
}

export default App
