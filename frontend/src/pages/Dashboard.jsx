import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { Search, AlertCircle, TrendingUp, ArrowRight, ChevronLeft, ChevronRight, BarChart2, Zap, ListChecks, Globe, CheckCircle2, Trophy, ShieldCheck, ShieldX, Copy, Check } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

const renderMarkdownLinks = (text) => {
  if (!text) return null;
  const parts = text.split(/(\[[^\]]+\]\([^)]+\))/g);
  return parts.map((part, i) => {
    const match = part.match(/\[([^\]]+)\]\(([^)]+)\)/);
    if (match) {
      return <a key={i} href={match[2]} target="_blank" rel="noreferrer" style={{color: '#3b82f6', textDecoration: 'underline'}}>{match[1]}</a>;
    }
    return <span key={i}>{part}</span>;
  });
};

const Dashboard = () => {
  const [domain, setDomain] = useState('')
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [benchmarkData, setBenchmarkData] = useState(null)
  
  // New States
  const [generatedFixes, setGeneratedFixes] = useState({})
  const [generatingFix, setGeneratingFix] = useState({})
  const [copiedFix, setCopiedFix] = useState({})
  
  const [generatedContent, setGeneratedContent] = useState({})
  const [generatingContent, setGeneratingContent] = useState({})
  const [copiedContent, setCopiedContent] = useState({})
  const [activeTab, setActiveTab] = useState('YouTube')
  
  const itemsPerPage = 5
  
  const navigate = useNavigate()

  useEffect(() => {
    const cachedDomain = localStorage.getItem('last_analyzed_domain')
    if (cachedDomain) {
      setDomain(cachedDomain)
    }
  }, [])

  const fetchGaps = async (e) => {
    if (e) e.preventDefault()
    if (!domain) return
    
    setLoading(true)
    setError('')
    setData(null)
    setBenchmarkData(null)
    try {
      const response = await axios.get(`http://localhost:8000/api/gaps?domain=${domain}`)
      setData(response.data)
      localStorage.setItem('last_analyzed_domain', domain)
      setCurrentPage(1)
      
      const benchResponse = await axios.get(`http://localhost:8000/api/benchmark?domain=${domain}`)
      setBenchmarkData(benchResponse.data)
    } catch (err) {
      setError('Failed to fetch data. Ensure backend is running and URL is valid.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateFix = async (url) => {
    setGeneratingFix(prev => ({...prev, [url]: true}))
    try {
      const res = await axios.post('http://localhost:8000/api/generate-fix', { url })
      setGeneratedFixes(prev => ({...prev, [url]: res.data}))
    } catch(err) {
      console.error(err)
    } finally {
      setGeneratingFix(prev => ({...prev, [url]: false}))
    }
  }

  const copyToClipboard = (text, key, type = 'fix') => {
    navigator.clipboard.writeText(text)
    if (type === 'fix') {
      setCopiedFix(prev => ({...prev, [key]: true}))
      setTimeout(() => setCopiedFix(prev => ({...prev, [key]: false})), 2000)
    } else {
      setCopiedContent(prev => ({...prev, [key]: true}))
      setTimeout(() => setCopiedContent(prev => ({...prev, [key]: false})), 2000)
    }
  }

  const handleGenerateContent = async (actionType, actionText, key) => {
    setGeneratingContent(prev => ({...prev, [key]: true}))
    try {
      const res = await axios.post('http://localhost:8000/api/generate-content', { action_type: actionType, action_text: actionText })
      setGeneratedContent(prev => ({...prev, [key]: res.data.content}))
    } catch(e) {
      console.error(e)
    } finally {
      setGeneratingContent(prev => ({...prev, [key]: false}))
    }
  }

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
          <div className="stats-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
            <div className="glass-card stat-box" style={{ borderColor: '#3b82f6', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#64748b', fontSize: '0.9rem', fontWeight: 600 }}>
                <Globe size={16} /> Sitemap Pages
              </div>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#1e293b' }}>{data.total_sitemap_pages}</div>
            </div>

            <div className="glass-card stat-box" style={{ borderColor: '#22c55e', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#16a34a', fontSize: '0.9rem', fontWeight: 600 }}>
                <CheckCircle2 size={16} /> Cited by AI
              </div>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#16a34a' }}>{data.total_cited_pages}</div>
            </div>

            <div className="glass-card stat-box" style={{ borderColor: '#ef4444', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#ef4444', fontSize: '0.9rem', fontWeight: 600 }}>
                <AlertCircle size={16} /> Citation Gaps
              </div>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#ef4444' }}>
                {(data.total_sitemap_pages || 0) - (data.total_cited_pages || 0)}
              </div>
            </div>

            <div className="glass-card stat-box" style={{ borderColor: '#eab308', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#ca8a04', fontSize: '0.9rem', fontWeight: 600 }}>
                <Zap size={16} fill="#eab308" /> Perf. Ranking
              </div>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#ca8a04' }}>{data.performance_score}/100</div>
              <div style={{ fontSize: '0.72rem', color: '#94a3b8' }}>Based on citation coverage</div>
            </div>

            {data.citation_coverage_pct !== undefined && (
              <div className="glass-card stat-box" style={{ borderColor: '#a855f7', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#9333ea', fontSize: '0.9rem', fontWeight: 600 }}>
                  <BarChart2 size={16} /> AI Coverage
                </div>
                <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#9333ea' }}>{data.citation_coverage_pct}%</div>
                <div style={{ fontSize: '0.72rem', color: '#94a3b8' }}>of sitemap cited by AI</div>
              </div>
            )}
          </div>

          {benchmarkData && (
            <div className="animate-fade-in" style={{ marginBottom: '2rem' }}>
              <section className="glass-card" style={{ border: '1px solid #e2e8f0' }}>
                <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <ListChecks size={20} color="#3b82f6" /> Your Action Plan to Beat Competitors in AI Search
                </h3>
                <div style={{ marginTop: '1.5rem' }}>
                  {benchmarkData.roadmap.map((item, index) => {
                    const badgeColor = item.priority === 'HIGH' ? '#ef4444' : item.priority === 'MEDIUM' ? '#eab308' : '#cbd5e1';
                    return (
                    <div key={index} style={{ marginBottom: '1.5rem', padding: '1.5rem', background: '#f8fafc', borderRadius: '0.5rem', border: '1px solid #e2e8f0' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                        <span style={{ fontSize: '0.85rem', fontWeight: 700 }}>{item.priority_emoji} {item.priority} PRIORITY</span>
                        <span style={{ color: '#64748b', margin: '0 0.5rem' }}>|</span>
                        <span style={{ fontSize: '1rem', fontWeight: 600, color: '#1e293b' }}>{item.title}</span>
                      </div>
                      
                      <div style={{ fontSize: '0.95rem', color: '#334155', marginBottom: '1rem' }}>
                        {item.gap_percentage}% of {item.channel.toLowerCase()} results cite competitors but NOT {benchmarkData.own_brand_name}.
                      </div>
                      
                      <div style={{ fontWeight: 600, fontSize: '0.9rem', marginBottom: '0.5rem' }}>What to do:</div>
                      <ul style={{ paddingLeft: '1.5rem', fontSize: '0.9rem', color: '#334155', marginBottom: '1.5rem' }}>
                        {item.actions.map((act, i) => (
                           <li key={i} style={{ marginBottom: '0.25rem' }}>{renderMarkdownLinks(act.text)}</li>
                        ))}
                      </ul>
                      
                      <div style={{ display: 'flex', gap: '1rem' }}>
                        {item.actions.map((act, i) => (
                          <div key={`act_${i}`}>
                            <button 
                              className="btn-primary" 
                              style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem', background: '#fff', color: '#3b82f6', border: '1px solid #3b82f6' }}
                              onClick={() => handleGenerateContent(item.type, act.text, `roadmap_${index}_${i}`)}
                              disabled={generatingContent[`roadmap_${index}_${i}`]}
                            >
                              {generatingContent[`roadmap_${index}_${i}`] ? 'Generating...' : `Draft Content ${i+1} →`}
                            </button>
                            {generatedContent[`roadmap_${index}_${i}`] && (
                              <div style={{ marginTop: '1rem', padding: '1rem', background: '#fff', border: '1px solid #e2e8f0', borderRadius: '0.5rem', width: '100%', maxWidth: '600px' }}>
                                <p style={{ whiteSpace: 'pre-wrap', fontSize: '0.85rem', marginBottom: '0.75rem', color: '#334155' }}>
                                  {generatedContent[`roadmap_${index}_${i}`]}
                                </p>
                                <button 
                                  onClick={() => copyToClipboard(generatedContent[`roadmap_${index}_${i}`], `roadmap_${index}_${i}`, 'content')}
                                  style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', fontSize: '0.8rem', color: '#64748b', background: 'none', border: 'none', cursor: 'pointer' }}
                                >
                                  {copiedContent[`roadmap_${index}_${i}`] ? <Check size={14} color="#10b981" /> : <Copy size={14} />} 
                                  {copiedContent[`roadmap_${index}_${i}`] ? 'Copied!' : 'Copy'}
                                </button>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )})}
                </div>
              </section>
            </div>
          )}

          <section className="glass-card" style={{ marginBottom: '2rem' }}>
            <h3>Your Pages Missing from AI Answers</h3>
            <p className="text-muted" style={{ marginBottom: '1.5rem' }}>These pages exist on your sitemap but AI engines like ChatGPT and Perplexity are not citing them. Click 'How to Fix' on any page for a specific action plan.</p>
            
            <div style={{ border: '1px solid var(--border-subtle)', borderRadius: '0.5rem', overflow: 'hidden' }}>
              {currentItems.length > 0 ? (
                currentItems.map((url, index) => (
                  <div key={index} style={{ borderBottom: index === currentItems.length - 1 ? 'none' : '1px solid var(--border-subtle)', background: index % 2 === 0 ? '#fff' : '#f8fafc' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', minWidth: 0 }}>
                        <AlertCircle size={18} color="#ef4444" style={{ flexShrink: 0 }} />
                        <span style={{ fontSize: '0.9rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', color: '#334155' }}>
                          {url}
                        </span>
                      </div>
                      <button 
                        className="btn-primary" 
                        style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem', flexShrink: 0 }}
                        onClick={() => handleGenerateFix(url)}
                        disabled={generatingFix[url]}
                      >
                        {generatingFix[url] ? 'Generating...' : 'How to Fix →'}
                      </button>
                    </div>
                    
                    {/* Expandable Fix Panel */}
                    {generatedFixes[url] && (
                      <div style={{ padding: '1.5rem', background: '#fff', borderTop: '1px solid var(--border-subtle)', borderLeft: '4px solid #3b82f6' }}>
                        <p style={{ fontWeight: 'bold', fontSize: '0.9rem', marginBottom: '0.5rem', color: '#1e293b' }}>The Problem</p>
                        <p style={{ fontSize: '0.85rem', color: '#475569', marginBottom: '1.5rem' }}>{generatedFixes[url].problem}</p>
                        
                        <p style={{ fontWeight: 'bold', fontSize: '0.9rem', marginBottom: '0.5rem', color: '#1e293b' }}>What you need to do</p>
                        <ol style={{ fontSize: '0.85rem', color: '#475569', marginBottom: '1.5rem', paddingLeft: '1.5rem' }}>
                          {generatedFixes[url].checklist.map((item, i) => <li key={i} style={{ marginBottom: '0.25rem' }}>{item}</li>)}
                        </ol>
                        
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                          <p style={{ fontWeight: 'bold', fontSize: '0.9rem', color: '#1e293b', margin: 0 }}>Code Snippet ({generatedFixes[url].schema_type})</p>
                          <button 
                              onClick={() => copyToClipboard(generatedFixes[url].json_ld, url, 'fix')}
                              style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', fontSize: '0.8rem', color: '#3b82f6', background: 'none', border: 'none', cursor: 'pointer', fontWeight: 600 }}
                            >
                              {copiedFix[url] ? <Check size={14} color="#10b981" /> : <Copy size={14} />} 
                              {copiedFix[url] ? 'Copied!' : 'Copy'}
                            </button>
                        </div>
                        <pre style={{ background: '#1e293b', color: '#f8fafc', padding: '1rem', borderRadius: '0.5rem', overflowX: 'auto', fontSize: '0.8rem', margin: 0 }}>
                          <code>{generatedFixes[url].json_ld}</code>
                        </pre>
                      </div>
                    )}
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

          {/* Competitor Advantage Breakdown */}
          {benchmarkData && benchmarkData.channel_gaps && (
            <div className="animate-fade-in" style={{ marginBottom: '2rem' }}>
              <section className="glass-card" style={{ border: '1px solid #3b82f6', background: '#eff6ff', marginBottom: '1rem' }}>
                <h3 style={{ marginBottom: '1.5rem' }}>Growth Opportunity</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1.5rem' }}>
                  <div>
                    <span className="text-muted" style={{ fontSize: '0.75rem' }}>CURRENT VISIBILITY</span>
                    <div style={{ fontSize: '1.4rem', fontWeight: '800' }}>{benchmarkData.current.visibility_score}%</div>
                  </div>
                  <div>
                    <span className="text-muted" style={{ fontSize: '0.75rem', display: 'block', marginBottom: '0.25rem' }}>TARGET VISIBILITY</span>
                    <div style={{ fontSize: '1.4rem', fontWeight: '800', color: '#2563eb' }}>
                      {benchmarkData.estimated.visibility_score}% <TrendingUp size={18} style={{ verticalAlign: 'middle' }} />
                    </div>
                    <div style={{ fontSize: '0.7rem', color: '#64748b', marginTop: '0.25rem' }}>(if top 3 actions completed)</div>
                  </div>
                  <div>
                    <span className="text-muted" style={{ fontSize: '0.75rem' }}>CURRENT CITATIONS</span>
                    <div style={{ fontSize: '1.4rem', fontWeight: '800' }}>{benchmarkData.current.citation_count}</div>
                  </div>
                  <div>
                    <span className="text-muted" style={{ fontSize: '0.75rem' }}>TARGET CITATIONS</span>
                    <div style={{ fontSize: '1.4rem', fontWeight: '800', color: '#2563eb' }}>{benchmarkData.estimated.citation_count} <TrendingUp size={18} style={{ verticalAlign: 'middle' }} /></div>
                  </div>
                </div>
              </section>

              <section className="glass-card" style={{ marginBottom: '2rem' }}>
                <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem', textTransform: 'uppercase', fontSize: '0.9rem', letterSpacing: '0.05em' }}>
                  Where Competitors Have The Advantage Over You (last 30 days)
                </h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                  {benchmarkData.channel_gaps.map((cg, i) => (
                    <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                      <div style={{ width: '120px', fontSize: '0.9rem', fontWeight: 600, color: '#334155' }}>
                        {cg.channel}
                      </div>
                      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                        {cg.competitors.map((comp, idx) => (
                          <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <div style={{ width: '80px', fontSize: '0.8rem', color: '#64748b' }}>{comp.name}</div>
                            <div style={{ flex: 1, background: '#e2e8f0', height: '16px', borderRadius: '2px', overflow: 'hidden' }}>
                               <div style={{ width: `${Math.max(2, comp.visibility)}%`, background: '#94a3b8', height: '100%' }}></div>
                            </div>
                            <div style={{ width: '40px', fontSize: '0.8rem', fontWeight: 600, color: '#64748b', textAlign: 'right' }}>
                              {comp.visibility}%
                            </div>
                          </div>
                        ))}
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <div style={{ width: '80px', fontSize: '0.8rem', color: '#ef4444', fontWeight: 700 }}>{cg.own.name}</div>
                          <div style={{ flex: 1, background: '#fecaca', height: '16px', borderRadius: '2px', overflow: 'hidden' }}>
                             <div style={{ width: `${Math.max(2, cg.own.visibility)}%`, background: '#ef4444', height: '100%' }}></div>
                          </div>
                          <div style={{ width: '140px', fontSize: '0.8rem', fontWeight: 700, color: '#ef4444', display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '0.5rem' }}>
                            {cg.own.visibility}% <span style={{ fontSize: '0.7rem', background: '#fef2f2', padding: '0.1rem 0.3rem', borderRadius: '4px', color: '#ef4444' }}>← You are here</span>
                          </div>
                        </div>
                      </div>
                      <div style={{ width: '100px', fontSize: '0.8rem', fontWeight: 700, textAlign: 'right', color: cg.gap_label === 'CRITICAL' ? '#b91c1c' : cg.gap_label === 'HIGH' ? '#ea580c' : '#ca8a04' }}>
                        Gap: {cg.gap_label}
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            </div>
          )}

          {/* Gap Sources Tab Panel */}
          {benchmarkData && benchmarkData.tab_actions && (
            <section className="glass-card" style={{ marginBottom: '2rem' }}>
              <h3 style={{ marginBottom: '1.5rem' }}>Gap Sources</h3>
              <div style={{ display: 'flex', borderBottom: '1px solid #e2e8f0', marginBottom: '1.5rem' }}>
                {['YouTube', 'Reddit', 'Editorial'].map(tab => (
                  <button 
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    style={{
                      padding: '0.75rem 1.5rem',
                      background: 'none',
                      border: 'none',
                      borderBottom: activeTab === tab ? '2px solid #3b82f6' : '2px solid transparent',
                      color: activeTab === tab ? '#3b82f6' : '#64748b',
                      fontWeight: activeTab === tab ? 600 : 400,
                      cursor: 'pointer'
                    }}
                  >
                    {tab}
                  </button>
                ))}
              </div>
              
              <div>
                {benchmarkData.tab_actions[activeTab] && benchmarkData.tab_actions[activeTab].has_data ? (
                  <div style={{ marginBottom: '1.5rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
                      <span style={{ 
                        padding: '0.2rem 0.6rem', 
                        borderRadius: '1rem', 
                        fontSize: '0.75rem', 
                        fontWeight: 700, 
                        background: benchmarkData.tab_actions[activeTab].opportunity_score > 70 ? '#fecaca' : benchmarkData.tab_actions[activeTab].opportunity_score > 40 ? '#fed7aa' : '#dbeafe',
                        color: benchmarkData.tab_actions[activeTab].opportunity_score > 70 ? '#b91c1c' : benchmarkData.tab_actions[activeTab].opportunity_score > 40 ? '#9a3412' : '#1e40af'
                      }}>
                        {benchmarkData.tab_actions[activeTab].opportunity_score > 70 ? 'High' : benchmarkData.tab_actions[activeTab].opportunity_score > 40 ? 'Medium' : 'Low'} Opportunity
                      </span>
                      <span style={{ color: '#64748b', fontSize: '0.9rem' }}>— {benchmarkData.tab_actions[activeTab].gap_percentage}% of {activeTab.toLowerCase()} cite competitors, not your brand</span>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                      {benchmarkData.tab_actions[activeTab].items.map((gapItem, idx) => (
                        <div key={idx} style={{ padding: '1rem', background: '#f8fafc', borderRadius: '0.5rem', borderLeft: '3px solid #cbd5e1' }}>
                           <div style={{ fontSize: '0.9rem', marginBottom: '0.75rem', color: '#1e293b', fontWeight: 500 }}>
                             {renderMarkdownLinks(gapItem.text)}
                           </div>
                           <button 
                             className="btn-primary" 
                             style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem' }}
                             onClick={() => handleGenerateContent(activeTab, gapItem.text, gapItem.id)}
                             disabled={generatingContent[gapItem.id]}
                           >
                             {generatingContent[gapItem.id] ? 'Generating...' : 'Generate Content →'}
                           </button>
                           
                           {generatedContent[gapItem.id] && (
                             <div style={{ marginTop: '1rem', padding: '1rem', background: '#fff', border: '1px solid #e2e8f0', borderRadius: '0.5rem' }}>
                               <p style={{ whiteSpace: 'pre-wrap', fontSize: '0.85rem', marginBottom: '0.75rem', color: '#334155' }}>
                                 {generatedContent[gapItem.id]}
                               </p>
                               <button 
                                 onClick={() => copyToClipboard(generatedContent[gapItem.id], gapItem.id, 'content')}
                                 style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', fontSize: '0.8rem', color: '#64748b', background: 'none', border: 'none', cursor: 'pointer' }}
                               >
                                 {copiedContent[gapItem.id] ? <Check size={14} color="#10b981" /> : <Copy size={14} />} 
                                 {copiedContent[gapItem.id] ? 'Copied!' : 'Copy'}
                               </button>
                             </div>
                           )}
                        </div>
                      ))}
                    </div>
                  </div>
                ) : <p className="text-muted" style={{ padding: '2rem', textAlign: 'center' }}>Not enough data yet — Peec needs 3–5 more days of prompt tracking to surface gaps here.</p>}
              </div>
            </section>
          )}

        </>
      )}
    </div>
  )
}

export default Dashboard
