import React, { useState } from 'react'
import axios from 'axios'
import { Search, AlertCircle, CheckCircle, ExternalLink, ArrowRight } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

const Dashboard = () => {
  const [domain, setDomain] = useState('')
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const fetchGaps = async (e) => {
    e.preventDefault()
    if (!domain) return
    
    setLoading(true)
    setError('')
    try {
      const response = await axios.get(`http://localhost:8000/api/gaps?domain=${domain}`)
      setData(response.data)
    } catch (err) {
      setError('Failed to fetch data. Ensure backend is running.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="animate-fade-in">
      <header style={{ marginBottom: '3rem' }}>
        <h1>AI Citation Gaps</h1>
        <p className="text-muted">Identify pages that exist but are ignored by AI search engines like ChatGPT and Gemini.</p>
      </header>

      <section className="glass-card" style={{ marginBottom: '2rem' }}>
        <form onSubmit={fetchGaps} style={{ display: 'flex', gap: '1rem' }}>
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
            {loading ? 'Analyzing...' : 'Analyze Gaps'}
          </button>
        </form>
        {error && <p style={{ color: '#f87171', marginTop: '1rem' }}>{error}</p>}
      </section>

      {data && (
        <>
          <div className="stats-grid">
            <div className="glass-card stat-box">
              <span className="text-muted">Total Sitemap Pages</span>
              <span className="stat-value">{data.total_sitemap_pages}</span>
            </div>
            <div className="glass-card stat-box">
              <span className="text-muted">Pages Cited by AI</span>
              <span className="stat-value" style={{ color: 'var(--accent-primary)' }}>{data.total_cited_pages}</span>
            </div>
            <div className="glass-card stat-box">
              <span className="text-muted">Citation Gap</span>
              <span className="stat-value" style={{ color: 'var(--accent-secondary)' }}>
                {data.total_sitemap_pages - data.total_cited_pages}
              </span>
            </div>
          </div>

          <section className="glass-card">
            <h3>Non-Cited Pages (Priority Fixes)</h3>
            <div style={{ marginTop: '1rem' }}>
              {data.gaps.length > 0 ? (
                data.gaps.map((url, index) => (
                  <div key={index} className="list-item">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                      <AlertCircle size={20} color="#f87171" />
                      <span style={{ fontSize: '0.9rem', maxWidth: '500px', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {url}
                      </span>
                    </div>
                    <button 
                      className="btn-primary" 
                      style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem' }}
                      onClick={() => navigate(`/audit/${encodeURIComponent(url)}`)}
                    >
                      Run Audit <ArrowRight size={14} style={{ marginLeft: '4px' }} />
                    </button>
                  </div>
                ))
              ) : (
                <p>No gaps found! Your pages are well-cited.</p>
              )}
            </div>
          </section>
        </>
      )}
    </div>
  )
}

export default Dashboard
