import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'
import { ArrowLeft, Zap, ShieldAlert, CheckCircle2, Cpu } from 'lucide-react'

const PageDetail = () => {
  const { url } = useParams()
  const decodedUrl = decodeURIComponent(url)
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    const runAudit = async () => {
      try {
        const response = await axios.post('http://localhost:8000/api/audit', { url: decodedUrl })
        setData(response.data.analysis)
      } catch (err) {
        setError('Failed to run audit. Please check your API keys and backend.')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    runAudit()
  }, [decodedUrl])

  if (loading) return (
    <div style={{ textAlign: 'center', padding: '5rem' }}>
      <Cpu className="animate-pulse" size={64} color="var(--accent-primary)" />
      <h2 style={{ marginTop: '2rem' }}>AI Agent Analyzing Crawlability...</h2>
      <p className="text-muted">Fetching rendered HTML and comparing with raw data.</p>
    </div>
  )

  if (error) return (
    <div className="glass-card" style={{ textAlign: 'center', padding: '3rem' }}>
      <ShieldAlert size={48} color="#f87171" />
      <h2 style={{ marginTop: '1rem' }}>Audit Failed</h2>
      <p>{error}</p>
      <button className="btn-primary" style={{ marginTop: '2rem' }} onClick={() => navigate('/')}>Back to Dashboard</button>
    </div>
  )

  return (
    <div className="animate-fade-in">
      <button onClick={() => navigate(-1)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '2rem' }}>
        <ArrowLeft size={18} /> Back
      </button>

      <header style={{ marginBottom: '3rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1>Audit Report</h1>
            <p className="text-muted" style={{ wordBreak: 'break-all' }}>{decodedUrl}</p>
          </div>
          <div className="glass-card" style={{ padding: '1rem 2rem', textAlign: 'center' }}>
            <span className="text-muted" style={{ fontSize: '0.8rem' }}>AI Readiness Score</span>
            <span className="stat-value" style={{ color: data.ai_readiness_score > 70 ? '#4ade80' : '#facc15' }}>
              {data.ai_readiness_score}
            </span>
          </div>
        </div>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
        <section className="glass-card">
          <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <ShieldAlert size={20} color="#f87171" /> Identified Issues
          </h3>
          <ul style={{ marginTop: '1.5rem', listStyle: 'none' }}>
            {data.issues.map((issue, i) => (
              <li key={i} style={{ marginBottom: '1rem', display: 'flex', gap: '0.75rem' }}>
                <span style={{ color: '#f87171' }}>•</span> {issue}
              </li>
            ))}
          </ul>
        </section>

        <section className="glass-card">
          <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <CheckCircle2 size={20} color="#4ade80" /> Actionable Fixes
          </h3>
          <ul style={{ marginTop: '1.5rem', listStyle: 'none' }}>
            {data.fixes.map((fix, i) => (
              <li key={i} style={{ marginBottom: '1rem', display: 'flex', gap: '0.75rem' }}>
                <span style={{ color: '#4ade80' }}>→</span> {fix}
              </li>
            ))}
          </ul>
        </section>
      </div>

      <section className="glass-card" style={{ marginTop: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h3>Estimated Impact</h3>
          <p className="text-muted">Expected improvement in AI search engine visibility after applying fixes.</p>
        </div>
        <div style={{ fontSize: '1.5rem', fontWeight: '700', color: 'var(--accent-secondary)' }}>
          {data.estimated_impact}
        </div>
      </section>

      <section className="glass-card" style={{ marginTop: '2rem' }}>
        <h3>Technical Insights</h3>
        <div style={{ display: 'flex', gap: '3rem', marginTop: '1rem' }}>
          <div>
            <span className="text-muted" style={{ fontSize: '0.8rem' }}>JS Dependency</span>
            <p style={{ fontWeight: '600', color: data.js_dependency === 'high' ? '#f87171' : '#4ade80' }}>
              {data.js_dependency.toUpperCase()}
            </p>
          </div>
          <div>
            <span className="text-muted" style={{ fontSize: '0.8rem' }}>AI Parsability</span>
            <p style={{ fontWeight: '600' }}>{data.ai_readiness_score > 50 ? 'GOOD' : 'POOR'}</p>
          </div>
        </div>
      </section>
    </div>
  )
}

export default PageDetail
