import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'
import { ArrowLeft, Zap, ShieldAlert, CheckCircle2, Cpu, Activity, Terminal, ExternalLink } from 'lucide-react'

const PageDetail = () => {
  const { url } = useParams()
  const decodedUrl = decodeURIComponent(url)
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [currentStep, setCurrentStep] = useState(0)
  
  const simulationSteps = [
    "Initializing Browser Audit...",
    "Navigating & Rendering...",
    "Waiting for Network Idle...",
    "Analyzing Technical Signals...",
    "Consulting Gemini 1.5 Flash..."
  ]

  useEffect(() => {
    // Check cache first
    const cacheKey = `audit_cache_${decodedUrl}`
    const cachedResult = localStorage.getItem(cacheKey)
    
    if (cachedResult) {
      setData(JSON.parse(cachedResult))
      setLoading(false)
      return
    }

    let stepInterval = setInterval(() => {
      setCurrentStep(prev => (prev < simulationSteps.length - 1 ? prev + 1 : prev))
    }, 2000)

    const runAudit = async () => {
      try {
        const response = await axios.post('http://localhost:8000/api/audit', { url: decodedUrl })
        const analysis = response.data.analysis
        setData(analysis)
        // Cache result for 24h (simple implementation)
        localStorage.setItem(cacheKey, JSON.stringify(analysis))
      } catch (err) {
        setError('Failed to run audit. Please check your API keys and backend.')
        console.error(err)
      } finally {
        setLoading(false)
        clearInterval(stepInterval)
      }
    }
    runAudit()
    
    return () => clearInterval(stepInterval)
  }, [decodedUrl])

  if (loading) return (
    <div style={{ textAlign: 'center', padding: '10rem 2rem' }}>
      <div className="animate-spin" style={{ margin: '0 auto', width: '48px', height: '48px', border: '3px solid #3b82f6', borderTopColor: 'transparent', borderRadius: '50%' }}></div>
      <h2 style={{ marginTop: '2rem', color: '#1e293b' }}>{simulationSteps[currentStep]}</h2>
      <p className="text-muted">Analyzing {decodedUrl}...</p>
    </div>
  )

  if (error) return (
    <div className="glass-card" style={{ textAlign: 'center', padding: '3rem' }}>
      <ShieldAlert size={48} color="#ef4444" style={{ margin: '0 auto' }} />
      <h2 style={{ marginTop: '1.5rem' }}>Audit Failed</h2>
      <p className="text-muted">{error}</p>
      <button className="btn-primary" style={{ marginTop: '2rem' }} onClick={() => navigate('/')}>Back to Dashboard</button>
    </div>
  )

  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <button onClick={() => navigate('/')} style={{ background: 'none', border: 'none', color: '#64748b', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600 }}>
          <ArrowLeft size={18} /> Return to Dashboard
        </button>
        <a href={decodedUrl} target="_blank" rel="noreferrer" style={{ fontSize: '0.85rem', color: '#3b82f6', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
          View Live Page <ExternalLink size={14} />
        </a>
      </div>

      <header style={{ marginBottom: '2.5rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
          <div style={{ flex: 1, marginRight: '2rem' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 800, color: '#3b82f6', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Audit Analysis</span>
            <h1 style={{ marginTop: '0.5rem', fontSize: '1.75rem', marginBottom: '0.5rem' }}>Citation Readiness Report</h1>
            <p className="text-muted" style={{ wordBreak: 'break-all', fontSize: '0.9rem' }}>{decodedUrl}</p>
          </div>
          <div className="glass-card" style={{ padding: '1rem 2.5rem', textAlign: 'center', border: '2px solid #3b82f6', background: '#eff6ff' }}>
            <span className="text-muted" style={{ fontSize: '0.75rem', fontWeight: 700, color: '#3b82f6' }}>READINESS SCORE</span>
            <div className="stat-value" style={{ color: '#1e293b', fontSize: '2.5rem' }}>{data.ai_readiness_score}<span style={{ fontSize: '1rem', color: '#94a3b8' }}>/100</span></div>
          </div>
        </div>
      </header>

      {/* Execution Console */}
      <section style={{ marginBottom: '2.5rem' }}>
        <div style={{ background: '#0f172a', borderRadius: '0.75rem', padding: '1.25rem', color: '#94a3b8', fontFamily: 'monospace', fontSize: '0.8rem', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' }}>
          <div style={{ color: '#4ade80', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem', borderBottom: '1px solid #1e293b', paddingBottom: '0.5rem' }}>
            <Terminal size={14} /> AUDIT_LOGS_STREAM
          </div>
          <div style={{ maxHeight: '120px', overflowY: 'auto' }}>
            {data.logs && data.logs.map((log, i) => (
              <div key={i} style={{ marginBottom: '4px' }}>
                <span style={{ color: '#475569' }}>&gt;</span> {log}
              </div>
            ))}
            <div style={{ color: '#3b82f6', marginTop: '0.5rem' }}>Audit trace completed successfully.</div>
          </div>
        </div>
      </section>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
        <section className="glass-card" style={{ borderTop: '4px solid #ef4444' }}>
          <h3 style={{ fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <ShieldAlert size={20} color="#ef4444" /> AI Visibility Blockers
          </h3>
          <ul style={{ marginTop: '1.5rem', listStyle: 'none' }}>
            {data.issues.map((issue, i) => (
              <li key={i} style={{ marginBottom: '1.25rem', display: 'flex', gap: '0.75rem', fontSize: '0.95rem' }}>
                <span style={{ color: '#ef4444', fontWeight: 'bold' }}>•</span> {issue}
              </li>
            ))}
          </ul>
        </section>

        <section className="glass-card" style={{ borderTop: '4px solid #22c55e' }}>
          <h3 style={{ fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <CheckCircle2 size={20} color="#22c55e" /> Actionable Fixes
          </h3>
          <ul style={{ marginTop: '1.5rem', listStyle: 'none' }}>
            {data.fixes.map((fix, i) => (
              <li key={i} style={{ marginBottom: '1.25rem', display: 'flex', gap: '0.75rem', fontSize: '0.95rem' }}>
                <span style={{ color: '#22c55e', fontWeight: 'bold' }}>→</span> {fix}
              </li>
            ))}
          </ul>
        </section>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '2rem', marginTop: '2rem' }}>
        <section className="glass-card" style={{ background: '#f8fafc' }}>
          <span className="text-muted" style={{ fontSize: '0.75rem', fontWeight: 700 }}>EXPECTED IMPACT</span>
          <div style={{ fontSize: '2rem', fontWeight: '800', color: '#3b82f6', marginTop: '0.5rem' }}>
            {data.estimated_impact}
          </div>
          <p className="text-muted" style={{ fontSize: '0.8rem', marginTop: '0.5rem' }}>Projected visibility increase in LLM citations.</p>
        </section>

        <section className="glass-card">
          <h3 style={{ fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
            <Activity size={20} color="#3b82f6" /> Technical Signals
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem' }}>
            <div>
              <span className="text-muted" style={{ fontSize: '0.7rem', fontWeight: 800 }}>LOAD TIME</span>
              <p style={{ fontWeight: '700', fontSize: '1.1rem' }}>{data.signals.load_time_ms}ms</p>
            </div>
            <div>
              <span className="text-muted" style={{ fontSize: '0.7rem', fontWeight: 800 }}>JS HYDRATION</span>
              <p style={{ fontWeight: '700', fontSize: '1.1rem' }}>{data.js_dependency.toUpperCase()}</p>
            </div>
            <div>
              <span className="text-muted" style={{ fontSize: '0.7rem', fontWeight: 800 }}>JSON-LD</span>
              <p style={{ fontWeight: '700', fontSize: '1.1rem', color: data.signals.has_json_ld ? '#22c55e' : '#64748b' }}>
                {data.signals.has_json_ld ? 'DETECTED' : 'MISSING'}
              </p>
            </div>
          </div>
        </section>
      </div>
    </div>
  )
}

export default PageDetail
