import React, { useState } from 'react'
import axios from 'axios'
import { TrendingUp, BarChart3, Target } from 'lucide-react'

const Benchmark = () => {
  const [domain, setDomain] = useState('')
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState(null)
  const [error, setError] = useState('')

  const fetchBenchmark = async (e) => {
    e.preventDefault()
    if (!domain) return
    
    setLoading(true)
    setError('')
    try {
      const response = await axios.get(`http://localhost:8000/api/benchmark?domain=${domain}`)
      setData(response.data)
    } catch (err) {
      setError('Failed to fetch benchmark data.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="animate-fade-in">
      <header style={{ marginBottom: '3rem' }}>
        <h1>Visibility Benchmark</h1>
        <p className="text-muted">Compare your current AI citation metrics with potential growth after optimization.</p>
      </header>

      <section className="glass-card" style={{ marginBottom: '3rem' }}>
        <form onSubmit={fetchBenchmark} style={{ display: 'flex', gap: '1rem' }}>
          <div style={{ flex: 1 }}>
            <input 
              type="text" 
              placeholder="Enter domain (e.g. example.com)" 
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              required
            />
          </div>
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Calculating...' : 'Run Benchmark'}
          </button>
        </form>
      </section>

      {data && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
          <section className="glass-card">
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <BarChart3 size={20} color="var(--text-muted)" /> Current Baseline
            </h3>
            <div style={{ marginTop: '2rem' }}>
              <div style={{ marginBottom: '2rem' }}>
                <span className="text-muted">Visibility Score</span>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <div style={{ flex: 1, height: '12px', background: 'rgba(255,255,255,0.1)', borderRadius: '6px' }}>
                    <div style={{ height: '100%', width: `${data.current.visibility_score}%`, background: 'var(--text-muted)', borderRadius: '6px' }}></div>
                  </div>
                  <span style={{ fontWeight: '700' }}>{data.current.visibility_score}%</span>
                </div>
              </div>
              <div>
                <span className="text-muted">Citation Count</span>
                <p style={{ fontSize: '2rem', fontWeight: '800' }}>{data.current.citation_count}</p>
              </div>
            </div>
          </section>

          <section className="glass-card" style={{ border: '1px solid var(--accent-primary)' }}>
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <TrendingUp size={20} color="var(--accent-primary)" /> Projected Optimization
            </h3>
            <div style={{ marginTop: '2rem' }}>
              <div style={{ marginBottom: '2rem' }}>
                <span className="text-muted">Visibility Score</span>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <div style={{ flex: 1, height: '12px', background: 'rgba(255,255,255,0.1)', borderRadius: '6px' }}>
                    <div style={{ height: '100%', width: `${data.estimated.visibility_score}%`, background: 'linear-gradient(to right, var(--accent-primary), var(--accent-secondary))', borderRadius: '6px' }}></div>
                  </div>
                  <span style={{ fontWeight: '700', color: 'var(--accent-primary)' }}>{data.estimated.visibility_score}%</span>
                </div>
              </div>
              <div>
                <span className="text-muted">Citation Count</span>
                <p style={{ fontSize: '2rem', fontWeight: '800', color: 'var(--accent-primary)' }}>{data.estimated.citation_count}</p>
                <p style={{ color: '#4ade80', fontSize: '0.9rem', marginTop: '0.5rem' }}>
                  +{Math.round(((data.estimated.citation_count - data.current.citation_count) / data.current.citation_count) * 100)}% increase
                </p>
              </div>
            </div>
          </section>

          <section className="glass-card" style={{ gridColumn: 'span 2', textAlign: 'center', padding: '3rem' }}>
            <Target size={48} color="var(--accent-secondary)" style={{ margin: '0 auto 1.5rem' }} />
            <h2>Unlock Your AI Potential</h2>
            <p className="text-muted" style={{ maxWidth: '600px', margin: '0 auto' }}>
              By fixing the identified crawlability issues and enhancing content clarity, your brand can become a primary source for AI-generated answers.
            </p>
          </section>
        </div>
      )}
    </div>
  )
}

export default Benchmark
