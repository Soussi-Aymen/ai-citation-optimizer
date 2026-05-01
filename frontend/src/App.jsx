import React from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import PageDetail from './pages/PageDetail'
import { Sparkles } from 'lucide-react'

const NavLink = ({ to, children }) => {
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

function App() {
  return (
    <Router>
      <div className="mx-auto min-h-screen max-w-6xl px-4 py-8">
        <nav className="mb-12 flex items-center justify-between border-b border-slate-200 pb-6">
          <div className="flex items-center gap-3">
            <Sparkles className="text-blue-500" size={32} />
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">Citation Optimizer</h1>
          </div>
          <div className="flex gap-2">
            <NavLink to="/">Dashboard</NavLink>
          </div>
        </nav>

        <main className="min-h-[calc(100vh-250px)]">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/audit/:url" element={<PageDetail />} />
          </Routes>
        </main>

        <footer className="mt-16 border-t border-slate-200 py-8 text-center text-slate-500">
          <p className="text-sm">&copy; 2026 AI Citation Optimizer. Powered by Peec AI & Gemini.</p>
        </footer>
      </div>
    </Router>
  )
}

export default App
