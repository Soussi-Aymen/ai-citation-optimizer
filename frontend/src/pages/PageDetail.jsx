import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'
import { ArrowLeft, Zap, ShieldAlert, CheckCircle2, Cpu, Activity, Clock, Globe, FileJson, Target, BarChart2, Code2, Layers, CheckSquare, XSquare } from 'lucide-react'

const PageDetail = () => {
  const { url } = useParams()
  const decodedUrl = decodeURIComponent(url)
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [currentStep, setCurrentStep] = useState(0)
  
  const simulationSteps = [
    "Spinning up Chromium Cluster...",
    "Awaiting Network Idle (JS Hydration)...",
    "Extracting DevTools Meta-Signals...",
    "Fetching Peec Competitor Intelligence...",
    "Building Multi-Track Report with Gemini 3 Flash..."
  ]

  useEffect(() => {
    const cacheKey = `audit_cache_${decodedUrl}`
    const cachedResult = localStorage.getItem(cacheKey)
    if (cachedResult) {
      setData(JSON.parse(cachedResult))
      setLoading(false)
      return
    }

    let stepInterval = setInterval(() => {
      setCurrentStep(prev => (prev < simulationSteps.length - 1 ? prev + 1 : prev))
    }, 3000)

    const runAudit = async () => {
      try {
        const response = await axios.post('http://localhost:8000/api/audit', { url: decodedUrl }, {
          timeout: 120000 // 2 minute timeout for deep audits
        })
        
        if (response.data.analysis.error) {
           setData(response.data.analysis) // Set data even on error to show logs
           setError("Audit Engine Error: " + (response.data.analysis.message || "Unknown Error"))
        } else {
          setData(response.data.analysis)
          localStorage.setItem(cacheKey, JSON.stringify(response.data.analysis))
        }
      } catch (err) {
        console.error(err)
        setError('Connection Timeout: The audit is taking longer than 2 minutes or the backend is unresponsive.')
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
      <p className="text-muted">Performing deep technical crawlability audit...</p>
    </div>
  )

  if (error) return (
    <div className="glass-card" style={{ textAlign: 'center', padding: '3rem' }}>
      <ShieldAlert size={48} color="#ef4444" style={{ margin: '0 auto' }} />
      <h2 style={{ marginTop: '1.5rem' }}>Audit Engine Error</h2>
      <p className="text-muted" style={{ maxWidth: '600px', margin: '0.5rem auto 2rem' }}>{error}</p>
      
      {/* Show logs even on error for debugging */}
      <div className="log-window" style={{ textAlign: 'left', marginBottom: '2rem', maxHeight: '200px', overflowY: 'auto' }}>
        <div style={{ color: '#ef4444', marginBottom: '0.5rem', fontWeight: 700 }}>FAILURE_TRACE:</div>
        {data?.logs?.map((log, i) => (
          <div key={i} style={{ fontSize: '0.75rem', marginBottom: '2px' }}><span style={{ color: '#475569' }}>&gt;</span> {log}</div>
        ))}
      </div>

      <button className="btn-primary" onClick={() => navigate('/')}>Back to Dashboard</button>
    </div>
  )

  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <button onClick={() => navigate('/')} style={{ background: 'none', border: 'none', color: '#64748b', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600 }}>
          <ArrowLeft size={18} /> Dashboard
        </button>
        <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>Powered by Gemini 3 Flash</span>
      </div>

      <header style={{ marginBottom: '2.5rem' }}>
        <h1>Technical Audit Report</h1>
        <p className="text-muted" style={{ wordBreak: 'break-all' }}>{decodedUrl}</p>
      </header>

      {/* 0. Raw DevTools Signals — The Foundation of this Report */}
      {data.signals && (
        <section className="glass-card" style={{ marginBottom: '2rem', border: '1px solid #e2e8f0' }}>
          <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
            <Cpu size={20} color="#64748b" /> How This Score Was Calculated
          </h3>
          <p className="text-muted" style={{ fontSize: '0.85rem', marginBottom: '1.5rem' }}>Raw DevTools signals captured during live browser render — these are the exact inputs Gemini 3 used to generate the report below.</p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))', gap: '1rem' }}>

            {/* Load Time */}
            {data.signals.load_time_ms !== undefined && (() => {
              const ms = data.signals.load_time_ms
              const color = ms < 2000 ? '#16a34a' : ms < 4000 ? '#f59e0b' : '#ef4444'
              const label = ms < 2000 ? 'Fast' : ms < 4000 ? 'Moderate' : 'Slow'
              return (
                <div style={{ padding: '1rem', borderRadius: '0.75rem', background: '#f8fafc', border: `1px solid ${color}30` }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#64748b', fontSize: '0.78rem', fontWeight: 700, marginBottom: '0.5rem' }}>
                    <Clock size={14} /> LOAD TIME
                  </div>
                  <div style={{ fontSize: '1.3rem', fontWeight: 800, color }}>{ms}ms</div>
                  <div style={{ fontSize: '0.72rem', color, fontWeight: 600, marginTop: '0.2rem' }}>{label}</div>
                </div>
              )
            })()}

            {/* JS Hydration Impact */}
            {data.signals.js_impact && (() => {
              const color = data.signals.js_impact === 'LOW' ? '#16a34a' : data.signals.js_impact === 'MODERATE' ? '#f59e0b' : '#ef4444'
              return (
                <div style={{ padding: '1rem', borderRadius: '0.75rem', background: '#f8fafc', border: `1px solid ${color}30` }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#64748b', fontSize: '0.78rem', fontWeight: 700, marginBottom: '0.5rem' }}>
                    <Code2 size={14} /> JS HYDRATION
                  </div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 800, color }}>{data.signals.js_impact}</div>
                  <div style={{ fontSize: '0.72rem', color: '#94a3b8', marginTop: '0.2rem' }}>Δ {data.signals.text_delta ?? '—'} chars</div>
                </div>
              )
            })()}

            {/* DOM Depth */}
            {data.signals.dom_depth !== undefined && (() => {
              const d = data.signals.dom_depth
              const color = d < 12 ? '#16a34a' : d < 20 ? '#f59e0b' : '#ef4444'
              const label = d < 12 ? 'Shallow (Good)' : d < 20 ? 'Moderate' : 'Deep (Bad)'
              return (
                <div style={{ padding: '1rem', borderRadius: '0.75rem', background: '#f8fafc', border: `1px solid ${color}30` }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#64748b', fontSize: '0.78rem', fontWeight: 700, marginBottom: '0.5rem' }}>
                    <Layers size={14} /> DOM DEPTH
                  </div>
                  <div style={{ fontSize: '1.3rem', fontWeight: 800, color }}>{d}</div>
                  <div style={{ fontSize: '0.72rem', color, fontWeight: 600, marginTop: '0.2rem' }}>{label}</div>
                </div>
              )
            })()}

            {/* JSON-LD / Structured Data */}
            {data.signals.has_json_ld !== undefined && (
              <div style={{ padding: '1rem', borderRadius: '0.75rem', background: '#f8fafc', border: `1px solid ${data.signals.has_json_ld ? '#16a34a30' : '#ef444430'}` }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#64748b', fontSize: '0.78rem', fontWeight: 700, marginBottom: '0.5rem' }}>
                  <FileJson size={14} /> STRUCTURED DATA
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  {data.signals.has_json_ld
                    ? <><CheckSquare size={20} color="#16a34a" /><span style={{ fontWeight: 800, color: '#16a34a' }}>JSON-LD Found</span></>
                    : <><XSquare size={20} color="#ef4444" /><span style={{ fontWeight: 800, color: '#ef4444' }}>Missing</span></>}
                </div>
                <div style={{ fontSize: '0.72rem', color: '#94a3b8', marginTop: '0.4rem' }}>
                  {data.signals.has_json_ld ? 'AI crawlers can parse semantic context' : 'Add Schema.org JSON-LD markup'}
                </div>
              </div>
            )}

            {/* Raw Content Volume */}
            {data.signals.raw_text_length !== undefined && (
              <div style={{ padding: '1rem', borderRadius: '0.75rem', background: '#f8fafc', border: '1px solid #e2e8f0' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#64748b', fontSize: '0.78rem', fontWeight: 700, marginBottom: '0.5rem' }}>
                  <BarChart2 size={14} /> RAW CONTENT
                </div>
                <div style={{ fontSize: '1.3rem', fontWeight: 800, color: '#1e293b' }}>{data.signals.raw_text_length.toLocaleString()}</div>
                <div style={{ fontSize: '0.72rem', color: '#94a3b8', marginTop: '0.2rem' }}>chars (pre-JS)</div>
              </div>
            )}
          </div>
        </section>
      )}

      {/* 1. Performance Report Section */}
      <section className="glass-card" style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Zap size={20} color="#eab308" /> 1. Performance Optimization Report
          </h3>
          <div style={{ padding: '0.5rem 1rem', background: '#fefce8', color: '#854d0e', borderRadius: '2rem', fontWeight: 700, fontSize: '0.9rem' }}>
            Score: {data.performance_report.score}/100
          </div>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
          <div>
            <h4 style={{ fontSize: '0.85rem', color: '#ef4444', marginBottom: '1rem' }}>SPEED BLOCKERS</h4>
            <ul style={{ listStyle: 'none' }}>
              {data.performance_report.issues.map((issue, i) => (
                <li key={i} style={{ marginBottom: '0.5rem', fontSize: '0.9rem', color: '#475569' }}>• {issue}</li>
              ))}
            </ul>
          </div>
          <div>
            <h4 style={{ fontSize: '0.85rem', color: '#22c55e', marginBottom: '1rem' }}>TECHNICAL FIXES</h4>
            <ul style={{ listStyle: 'none' }}>
              {data.performance_report.fixes.map((fix, i) => (
                <li key={i} style={{ marginBottom: '0.5rem', fontSize: '0.9rem', color: '#475569' }}>→ {fix}</li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      {/* 2. Sitemap Audit Section */}
      <section className="glass-card" style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <FileJson size={20} color="#3b82f6" /> 2. Sitemap & Structure Analysis
          </h3>
          <div style={{ padding: '0.5rem 1rem', background: '#eff6ff', color: '#1e40af', borderRadius: '2rem', fontWeight: 700, fontSize: '0.9rem' }}>
             Health: {data.sitemap_audit.score}%
          </div>
        </div>
        <p style={{ fontSize: '0.95rem', color: '#475569', marginBottom: '1.5rem', background: '#f8fafc', padding: '1rem', borderRadius: '0.5rem', borderLeft: '4px solid #3b82f6' }}>
          {data.sitemap_audit.analysis}
        </p>
        <h4 style={{ fontSize: '0.85rem', color: '#3b82f6', marginBottom: '1rem' }}>RECOMMENDED IMPROVEMENTS</h4>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem' }}>
          {data.sitemap_audit.improvements.map((imp, i) => (
            <div key={i} style={{ padding: '0.75rem', border: '1px solid #e2e8f0', borderRadius: '0.5rem', fontSize: '0.85rem' }}>
              {imp}
            </div>
          ))}
        </div>
      </section>

      {/* 3. Competitive Analysis Section */}
      <section className="glass-card" style={{ marginBottom: '2rem', background: '#faf5ff', borderColor: '#d8b4fe' }}>
        <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#7e22ce', marginBottom: '1.5rem' }}>
          <Target size={20} color="#7e22ce" /> 3. Competitive Citation Edge
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
          <div>
            <h4 style={{ fontSize: '0.8rem', color: '#7e22ce', marginBottom: '0.75rem' }}>WHAT COMPETITORS DO BETTER</h4>
            <p style={{ fontSize: '0.9rem', color: '#581c87' }}>{data.competitive_analysis.competitor_edge}</p>
          </div>
          <div>
            <h4 style={{ fontSize: '0.8rem', color: '#7e22ce', marginBottom: '0.75rem' }}>KEY GAP TO CLOSE</h4>
            <div style={{ padding: '1rem', background: '#ffffff', borderRadius: '0.5rem', border: '1px solid #d8b4fe', fontWeight: 600, color: '#7e22ce' }}>
              {data.competitive_analysis.gap_to_close}
            </div>
          </div>
        </div>
      </section>

      {/* Overall Stat Summary */}
      <section style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1.5rem', marginTop: '2rem' }}>
        <div className="glass-card" style={{ textAlign: 'center' }}>
          <span className="text-muted" style={{ fontSize: '0.7rem', fontWeight: 800 }}>AI READINESS SCORE</span>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#1e293b' }}>{data.ai_readiness.overall_score}%</div>
        </div>
        <div className="glass-card" style={{ textAlign: 'center', background: '#f0fdf4', borderColor: '#bbf7d0' }}>
          <span className="text-muted" style={{ fontSize: '0.7rem', fontWeight: 800 }}>ESTIMATED IMPACT</span>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#16a34a' }}>{data.ai_readiness.estimated_impact}</div>
        </div>
        <div className="glass-card" style={{ textAlign: 'center' }}>
          <span className="text-muted" style={{ fontSize: '0.7rem', fontWeight: 800 }}>AUDIT TIME</span>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#3b82f6' }}>{data.execution_time_ms}ms</div>
        </div>
      </section>

      {/* Execution Trace */}
      <section style={{ marginTop: '2rem' }}>
        <div className="log-window" style={{ maxHeight: '120px', overflowY: 'auto' }}>
          {data.logs && data.logs.map((log, i) => (
            <div key={i} style={{ marginBottom: '2px' }}><span style={{ color: '#475569' }}>&gt;</span> {log}</div>
          ))}
        </div>
      </section>
    </div>
  )
}

export default PageDetail
