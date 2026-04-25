import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { Search, AlertCircle, TrendingUp, ArrowRight, ChevronLeft, ChevronRight, BarChart2 } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

const Dashboard = () => {
  const [domain, setDomain] = useState('')
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [showBenchmark, setShowBenchmark] = useState(false)
  const [benchmarkData, setBenchmarkData] = useState(null)
  const itemsPerPage = 5
  
  const navigate = useNavigate()

  // Load cached data from localStorage on mount
  useEffect(() => {
    const cachedData = localStorage.getItem('gap_analysis_data')
    const cachedDomain = localStorage.getItem('last_analyzed_domain')
    if (cachedData) {
      setData(JSON.parse(cachedData))
    }
    if (cachedDomain) {
      setDomain(cachedDomain)
    }
  }, [])

  const fetchGaps = async (e) => {
    if (e) e.preventDefault()
    if (!domain) return
    
    setLoading(true)
    setError('')
    setShowBenchmark(false)
    try {
      const response = await axios.get(`http://localhost:8000/api/gaps?domain=${domain}`)
      setData(response.data)
      // Cache the result
      localStorage.setItem('gap_analysis_data', JSON.stringify(response.data))
      localStorage.setItem('last_analyzed_domain', domain)
      setCurrentPage(1)
    } catch (err) {
      setError('Failed to fetch data. Ensure backend is running.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const fetchBenchmark = async () => {
    if (showBenchmark) {
      setShowBenchmark(false)
      return
    }
    setLoading(true)
    try {
      const response = await axios.get(`http://localhost:8000/api/benchmark?domain=${domain}`)
      setBenchmarkData(response.data)
      setShowBenchmark(true)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  // Pagination Logic
  const indexOfLastItem = currentPage * itemsPerPage
  const indexOfFirstItem = indexOfLastItem - itemsPerPage
  const currentItems = data?.gaps.slice(indexOfFirstItem, indexOfLastItem) || []
  const totalPages = Math.ceil((data?.gaps.length || 0) / itemsPerPage)

  return (
    <div className="animate-fade-in">
      <header style={{ marginBottom: '2.5rem' }}>
        <h1>AI Search Dashboard</h1>
        <p className="text-muted">Analyze your website's visibility and detect citation gaps in AI models.</p>
      </header>

      <section className="glass-card" style={{ marginBottom: '2rem' }}>
        <form onSubmit={fetchGaps} style={{ display: 'flex', gap: '1rem' }}>
          <div style={{ flex: 1, position: 'relative' }}>
            <Search style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#94a3b8' }} size={18} />
            <input 
              type="text" 
              placeholder="Enter your domain (e.g. peec.ai)" 
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              style={{ paddingLeft: '2.5rem', width: '100%', height: '48px', borderRadius: '0.5rem', border: '1px solid var(--border-subtle)', background: '#fff' }}
              required
            />
          </div>
          <button type="submit" className="btn-primary" disabled={loading} style={{ height: '48px' }}>
            {loading ? 'Analyzing...' : 'Run Analysis'}
          </button>
        </form>
        {error && <p style={{ color: '#ef4444', marginTop: '1rem', fontSize: '0.9rem' }}>{error}</p>}
      </section>

      {data && (
        <>
          <div className="stats-grid">
            <div className="glass-card stat-box">
              <span className="text-muted">Sitemap URLs</span>
              <span className="stat-value">{data.total_sitemap_pages}</span>
            </div>
            <div className="glass-card stat-box" style={{ borderColor: '#22c55e' }}>
              <span className="text-muted">Cited by AI</span>
              <span className="stat-value" style={{ color: '#22c55e' }}>{data.total_cited_pages}</span>
            </div>
            <div className="glass-card stat-box" style={{ borderColor: '#ef4444' }}>
              <span className="text-muted">Citation Gaps</span>
              <span className="stat-value" style={{ color: '#ef4444' }}>{data.total_sitemap_pages - data.total_cited_pages}</span>
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '1.5rem' }}>
            <button className="btn-secondary" onClick={fetchBenchmark} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <BarChart2 size={18} /> {showBenchmark ? 'Hide Benchmark' : 'View Opportunity Benchmark'}
            </button>
          </div>

          {showBenchmark && benchmarkData && (
            <section className="glass-card animate-fade-in" style={{ marginBottom: '2rem', border: '1px solid #3b82f6', background: '#eff6ff' }}>
              <h3>Growth Opportunity</h3>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginTop: '1.5rem' }}>
                <div>
                  <span className="text-muted">Current Visibility Score</span>
                  <div style={{ fontSize: '1.5rem', fontWeight: '800' }}>{benchmarkData.current.visibility_score}%</div>
                </div>
                <div>
                  <span className="text-muted">Target (After Fixes)</span>
                  <div style={{ fontSize: '1.5rem', fontWeight: '800', color: '#2563eb' }}>{benchmarkData.estimated.visibility_score}% <TrendingUp size={20} style={{ verticalAlign: 'middle' }} /></div>
                </div>
              </div>
            </section>
          )}

          <section className="glass-card">
            <h3>Non-Cited Pages (Priority Fixes)</h3>
            <p className="text-muted" style={{ marginBottom: '1.5rem' }}>These pages are indexed but missing from AI citations. Run an audit to fix.</p>
            
            <div style={{ border: '1px solid var(--border-subtle)', borderRadius: '0.5rem', overflow: 'hidden' }}>
              {currentItems.length > 0 ? (
                currentItems.map((url, index) => (
                  <div key={index} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem', borderBottom: index === currentItems.length - 1 ? 'none' : '1px solid var(--border-subtle)', background: index % 2 === 0 ? '#fff' : '#f8fafc' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', minWidth: 0 }}>
                      <AlertCircle size={18} color="#ef4444" style={{ flexShrink: 0 }} />
                      <span style={{ fontSize: '0.9rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', color: '#334155' }}>
                        {url}
                      </span>
                    </div>
                    <button 
                      className="btn-primary" 
                      style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem', flexShrink: 0 }}
                      onClick={() => navigate(`/audit/${encodeURIComponent(url)}`)}
                    >
                      Audit Page <ArrowRight size={14} />
                    </button>
                  </div>
                ))
              ) : (
                <div style={{ padding: '2rem', textAlign: 'center' }}>No gaps found!</div>
              )}
            </div>

            {totalPages > 1 && (
              <div className="pagination">
                <button className="page-btn" onClick={() => setCurrentPage(p => Math.max(1, p - 1))} disabled={currentPage === 1}>
                  <ChevronLeft size={16} />
                </button>
                <span className="text-muted" style={{ fontSize: '0.85rem' }}>Page {currentPage} of {totalPages}</span>
                <button className="page-btn" onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))} disabled={currentPage === totalPages}>
                  <ChevronRight size={16} />
                </button>
              </div>
            )}
          </section>
        </>
      )}
    </div>
  )
}

export default Dashboard
