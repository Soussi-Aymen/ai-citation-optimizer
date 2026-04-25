import React from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import PageDetail from './pages/PageDetail'
import { Sparkles } from 'lucide-react'

const NavLink = ({ to, children }) => {
  const location = useLocation()
  const isActive = location.pathname === to
  return (
    <Link to={to} className={isActive ? 'active' : ''}>
      {children}
    </Link>
  )
}

function App() {
  return (
    <Router>
      <div className="app-container">
        <nav>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginRight: 'auto' }}>
            <Sparkles color="#3b82f6" size={28} />
            <h2 style={{ margin: 0, fontSize: '1.5rem' }}>Citation Optimizer</h2>
          </div>
          <NavLink to="/">Dashboard</NavLink>
        </nav>

        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/audit/:url" element={<PageDetail />} />
        </Routes>

        <footer style={{ marginTop: '4rem', textAlign: 'center', padding: '2rem', color: 'var(--text-muted)', borderTop: '1px solid var(--border-glass)' }}>
          <p>&copy; 2026 AI Citation Optimizer. Powered by Peec AI & Gemini.</p>
        </footer>
      </div>
    </Router>
  )
}

export default App
