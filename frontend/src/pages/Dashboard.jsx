import React, { useState, useEffect } from 'react'
import axios from 'axios'
import {
  Search,
  AlertCircle,
  TrendingUp,
  ArrowRight,
  ChevronLeft,
  ChevronRight,
  BarChart2,
  Zap,
  ListChecks,
  Globe,
  CheckCircle2,
  Trophy,
  Copy,
  Check,
  FileCode,
  Cpu,
  ExternalLink,
  Mail,
  MessageSquare,
  PlayCircle,
  FileText,
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'

const renderMarkdownLinks = (text) => {
  if (!text) return null
  const parts = text.split(/(\[[^\]]+\]\([^)]+\))/g)
  return parts.map((part, i) => {
    const match = part.match(/\[([^\]]+)\]\(([^)]+)\)/)
    if (match) {
      return (
        <a
          key={i}
          href={match[2]}
          target="_blank"
          rel="noreferrer"
          className="text-blue-600 underline hover:text-blue-800"
        >
          {match[1]}
        </a>
      )
    }
    return <span key={i}>{part}</span>
  })
}

const Dashboard = () => {
  const [domain, setDomain] = useState('')
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [benchmarkData, setBenchmarkData] = useState(null)

  const [generatedFixes, setGeneratedFixes] = useState({})
  const [generatingFix, setGeneratingFix] = useState({})
  const [expandedFix, setExpandedFix] = useState({})
  const [expandedGuidance, setExpandedGuidance] = useState({})

  const toggleGuidance = (url, metricId) => {
    const key = `${url}-${metricId}`
    setExpandedGuidance((prev) => ({ ...prev, [key]: !prev[key] }))
  }

  const [generatedContent, setGeneratedContent] = useState({})
  const [generatingContent, setGeneratingContent] = useState({})
  const [copiedContent, setCopiedContent] = useState({})
  const [copiedFix, setCopiedFix] = useState({})
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

  const handleHowToFix = async (url) => {
    if (generatedFixes[url]) {
      setGeneratedFixes((prev) => {
        const next = { ...prev }
        delete next[url]
        return next
      })
      return
    }
    setGeneratingFix((prev) => ({ ...prev, [url]: true }))
    try {
      const res = await axios.post('http://localhost:8000/api/generate-fix', { url })
      setGeneratedFixes((prev) => ({ ...prev, [url]: res.data }))
    } catch (err) {
      console.error(err)
    } finally {
      setGeneratingFix((prev) => ({ ...prev, [url]: false }))
    }
  }

  const copyToClipboard = (text, key, type = 'fix') => {
    navigator.clipboard.writeText(text)
    if (type === 'fix') {
      setCopiedFix((prev) => ({ ...prev, [key]: true }))
      setTimeout(() => setCopiedFix((prev) => ({ ...prev, [key]: false })), 2000)
    } else {
      setCopiedContent((prev) => ({ ...prev, [key]: true }))
      setTimeout(() => setCopiedContent((prev) => ({ ...prev, [key]: false })), 2000)
    }
  }

  const handleGenerateContent = async (actionType, actionText, key) => {
    setGeneratingContent((prev) => ({ ...prev, [key]: true }))
    try {
      const res = await axios.post('http://localhost:8000/api/generate-content', {
        action_type: actionType,
        action_text: actionText,
      })
      setGeneratedContent((prev) => ({ ...prev, [key]: res.data.content }))
    } catch (e) {
      console.error(e)
    } finally {
      setGeneratingContent((prev) => ({ ...prev, [key]: false }))
    }
  }

  const indexOfLastItem = currentPage * itemsPerPage
  const indexOfFirstItem = indexOfLastItem - itemsPerPage
  const currentItems = data?.gaps.slice(indexOfFirstItem, indexOfLastItem) || []
  const totalPages = Math.ceil((data?.gaps.length || 0) / itemsPerPage)

  return (
    <div className="animate-fade-in">
      <header className="mb-10">
        <h1 className="mb-2 text-4xl font-extrabold tracking-tight text-slate-900">
          AI Search Dashboard
        </h1>
        <p className="text-lg text-slate-500">
          Analyze your website's visibility and detect citation gaps in AI models.
        </p>
      </header>

      <section className="glass-card mb-8">
        <form onSubmit={fetchGaps} className="flex gap-4">
          <div className="relative flex-1">
            <Search className="absolute top-1/2 left-4 -translate-y-1/2 text-slate-400" size={20} />
            <input
              type="text"
              placeholder="Enter your domain (e.g. nothing.tech)"
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              className="h-12 w-full rounded-lg border border-slate-200 bg-white pr-4 pl-12 transition-all focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 focus:outline-none"
              required
            />
          </div>
          <button type="submit" className="btn-primary h-12" disabled={loading}>
            {loading ? 'Analyzing...' : 'Run Analysis'}
          </button>
        </form>
        {error && <p className="mt-4 text-sm font-medium text-red-500">{error}</p>}
      </section>

      {data && (
        <>
          <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
            <div className="glass-card stat-box border-blue-500 p-4">
              <div className="mb-1 flex items-center gap-2 text-sm font-semibold text-slate-500">
                <Globe size={16} /> Sitemap Pages
              </div>
              <div className="text-2xl font-bold text-slate-900">{data.total_sitemap_pages}</div>
            </div>

            <div className="glass-card stat-box border-emerald-500 p-4">
              <div className="mb-1 flex items-center gap-2 text-sm font-semibold text-emerald-600">
                <CheckCircle2 size={16} /> Cited by AI
              </div>
              <div className="text-2xl font-bold text-emerald-600">{data.total_cited_pages}</div>
            </div>

            <div className="glass-card stat-box border-red-500 p-4">
              <div className="mb-1 flex items-center gap-2 text-sm font-semibold text-red-500">
                <AlertCircle size={16} /> Citation Gaps
              </div>
              <div className="text-2xl font-bold text-red-500">
                {(data.total_sitemap_pages || 0) - (data.total_cited_pages || 0)}
              </div>
            </div>

            <div className="glass-card stat-box border-amber-500 p-4">
              <div className="mb-1 flex items-center gap-2 text-sm font-semibold text-amber-600">
                <Zap size={16} className="fill-amber-500" /> Perf. Ranking
              </div>
              <div className="text-2xl font-bold text-amber-600">{data.performance_score}/100</div>
              <div className="text-[10px] text-slate-400">Based on citation coverage</div>
            </div>

            <div className="glass-card stat-box border-purple-500 p-4">
              <div className="mb-1 flex items-center gap-2 text-sm font-semibold text-purple-600">
                <BarChart2 size={16} /> AI Coverage
              </div>
              <div className="text-2xl font-bold text-purple-600">
                {data.citation_coverage_pct}%
              </div>
              <div className="text-[10px] text-slate-400">of sitemap cited by AI</div>
            </div>
          </div>

          {benchmarkData && (
            <div className="mb-8 space-y-6">
              <section className="rounded-xl border border-blue-100 bg-blue-50 p-6 shadow-sm">
                <h3 className="mb-6 text-xl font-bold text-slate-900">Growth Opportunity</h3>
                <div className="grid grid-cols-2 gap-8 sm:grid-cols-4">
                  <div>
                    <span className="text-[10px] font-bold tracking-wider text-slate-400 uppercase">
                      CURRENT VISIBILITY
                    </span>
                    <div className="text-2xl font-black text-slate-900">
                      {benchmarkData.current.visibility_score}%
                    </div>
                  </div>
                  <div>
                    <span className="text-[10px] font-bold tracking-wider text-blue-400 uppercase">
                      TARGET VISIBILITY
                    </span>
                    <div className="flex items-center gap-2 text-2xl font-black text-blue-600">
                      {benchmarkData.estimated.visibility_score}% <TrendingUp size={20} />
                    </div>
                    <p className="mt-1 text-[10px] text-slate-500">if top 3 actions completed</p>
                  </div>
                  <div>
                    <span className="text-[10px] font-bold tracking-wider text-slate-400 uppercase">
                      CURRENT CITATIONS
                    </span>
                    <div className="text-2xl font-black text-slate-900">
                      {benchmarkData.current.citation_count}
                    </div>
                  </div>
                  <div>
                    <span className="text-[10px] font-bold tracking-wider text-blue-400 uppercase">
                      TARGET CITATIONS
                    </span>
                    <div className="flex items-center gap-2 text-2xl font-black text-blue-600">
                      {benchmarkData.estimated.citation_count} <TrendingUp size={20} />
                    </div>
                  </div>
                </div>

                <div className="mt-8 border-t border-blue-100 pt-8">
                  <h4 className="mb-6 text-[10px] font-bold tracking-[0.2em] text-blue-500 uppercase">
                    WHERE COMPETITORS HAVE THE ADVANTAGE OVER YOU (last 30 days)
                  </h4>
                  <div className="space-y-4">
                    {benchmarkData.channel_gaps.map((cg, i) => (
                      <div
                        key={i}
                        className="flex flex-col gap-4 border-b border-blue-100 pb-4 last:border-0 lg:flex-row lg:items-center lg:justify-between lg:pb-0"
                      >
                        <div className="w-32 font-bold text-slate-700">{cg.channel}</div>
                        <div className="flex flex-1 flex-wrap items-center gap-6">
                          {cg.competitors.map((comp, idx) => (
                            <div key={idx} className="flex items-center gap-2">
                              <span className="text-sm font-medium text-slate-500">
                                {comp.name}
                              </span>
                              <div className="flex items-center gap-1 font-mono text-xs">
                                <span className="text-slate-300">████████</span>
                                <span className="font-bold text-slate-700">{comp.visibility}%</span>
                              </div>
                            </div>
                          ))}
                          <div className="flex items-center gap-2 rounded-lg bg-orange-50 px-3 py-1 ring-1 ring-orange-200">
                            <span className="text-sm font-bold text-orange-600">{cg.own.name}</span>
                            <div className="flex items-center gap-1 font-mono text-xs">
                              <span className="text-orange-200">░░</span>
                              <span className="font-black text-orange-600">
                                {cg.own.visibility}%
                              </span>
                            </div>
                            <span className="text-[10px] font-bold text-orange-400">
                              ← You are here
                            </span>
                          </div>
                        </div>
                        <div
                          className={`text-right text-[10px] font-black tracking-widest ${
                            cg.gap_label === 'CRITICAL'
                              ? 'text-red-600'
                              : cg.gap_label === 'HIGH'
                                ? 'text-orange-600'
                                : 'text-amber-600'
                          }`}
                        >
                          Gap: {cg.gap_label}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </section>
            </div>
          )}

          {benchmarkData && (
            <section className="mb-8 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
              <div className="border-b border-slate-200 bg-slate-50 px-6 py-4">
                <h3 className="flex items-center gap-2 text-lg font-bold text-slate-900">
                  <ListChecks className="text-blue-500" size={24} />
                  Your Action Plan to Beat Competitors in AI Search
                </h3>
              </div>
              <div className="divide-y divide-slate-100 p-6">
                {benchmarkData.roadmap.map((item, index) => (
                  <div key={index} className="py-6 first:pt-0 last:pb-0">
                    <div className="mb-4 flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <span
                          className={`rounded-full px-3 py-1 text-[10px] font-black tracking-wider uppercase ${
                            item.priority === 'HIGH'
                              ? 'bg-red-100 text-red-600'
                              : item.priority === 'MEDIUM'
                                ? 'bg-amber-100 text-amber-600'
                                : 'bg-slate-100 text-slate-500'
                          }`}
                        >
                          {item.priority_emoji} {item.priority} PRIORITY
                        </span>
                        <h4 className="text-lg font-bold text-slate-800">{item.title}</h4>
                      </div>
                      <div className="text-sm font-bold text-slate-400">
                        Gap: {item.gap_percentage}%
                      </div>
                    </div>

                    <p className="mb-6 text-slate-600">
                      <strong>{item.gap_percentage}%</strong> of {item.channel.toLowerCase()}{' '}
                      results cite competitors but NOT {benchmarkData.own_brand_name}.
                    </p>

                    <div className="mb-6 rounded-lg bg-slate-50 p-4 ring-1 ring-slate-100">
                      <h5 className="mb-3 text-xs font-bold tracking-widest text-slate-400 uppercase">
                        What to do:
                      </h5>
                      <ul className="space-y-3">
                        {item.actions.map((act, i) => (
                          <li
                            key={i}
                            className="flex items-start gap-3 text-sm leading-relaxed text-slate-700"
                          >
                            <span className="mt-1.5 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-blue-500" />
                            <div className="flex-1">
                              {renderMarkdownLinks(act.text)}
                              {act.url && (
                                <a
                                  href={act.url}
                                  target="_blank"
                                  rel="noreferrer"
                                  className="ml-2 inline-flex items-center gap-1 text-blue-500 hover:underline"
                                >
                                  [link] <ExternalLink size={12} />
                                </a>
                              )}
                            </div>
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div className="flex flex-wrap gap-3">
                      {item.actions.map((act, i) => {
                        const contentKey = `roadmap_${index}_${i}`
                        const isYouTube = item.channel.toLowerCase().includes('youtube')
                        const isReddit = item.channel.toLowerCase().includes('reddit')

                        return (
                          <div key={contentKey} className="w-full sm:w-auto">
                            <button
                              onClick={() => handleGenerateContent(item.type, act.text, contentKey)}
                              disabled={generatingContent[contentKey]}
                              className="btn-secondary w-full justify-center py-2 text-xs"
                            >
                              {generatingContent[contentKey] ? (
                                'Generating...'
                              ) : (
                                <>
                                  {isYouTube ? (
                                    <PlayCircle size={14} />
                                  ) : isReddit ? (
                                    <MessageSquare size={14} />
                                  ) : (
                                    <FileText size={14} />
                                  )}
                                  Draft{' '}
                                  {isYouTube ? 'Video Script' : isReddit ? 'Reddit Post' : 'Pitch'}{' '}
                                  {i + 1} →
                                </>
                              )}
                            </button>
                            {generatedContent[contentKey] && (
                              <div className="mt-4 rounded-lg border border-blue-100 bg-blue-50/50 p-4">
                                <div className="mb-3 flex items-center justify-between">
                                  <span className="text-[10px] font-bold tracking-widest text-blue-500 uppercase">
                                    GEMINI DRAFT
                                  </span>
                                  <button
                                    onClick={() =>
                                      copyToClipboard(
                                        generatedContent[contentKey],
                                        contentKey,
                                        'content',
                                      )
                                    }
                                    className="flex items-center gap-1.5 text-xs font-bold text-blue-600 hover:text-blue-800"
                                  >
                                    {copiedContent[contentKey] ? (
                                      <Check size={14} />
                                    ) : (
                                      <Copy size={14} />
                                    )}
                                    {copiedContent[contentKey] ? 'Copied!' : 'Copy Draft'}
                                  </button>
                                </div>
                                <div className="text-sm leading-relaxed whitespace-pre-wrap text-slate-700">
                                  {generatedContent[contentKey]}
                                </div>
                              </div>
                            )}
                          </div>
                        )
                      })}
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          <section className="glass-card mb-8">
            <h3 className="mb-2 text-xl font-bold text-slate-900">
              Your Pages Missing from AI Answers
            </h3>
            <p className="mb-6 text-sm text-slate-500">
              These pages exist on your sitemap but AI engines like ChatGPT and Perplexity are not
              citing them. Click 'How to Fix' on any page for a specific action plan.
            </p>

            <div className="overflow-hidden rounded-xl border border-slate-200">
              {currentItems.length > 0 ? (
                currentItems.map((url, index) => (
                  <div
                    key={index}
                    className={`border-b border-slate-100 last:border-0 ${
                      index % 2 === 0 ? 'bg-white' : 'bg-slate-50/50'
                    }`}
                  >
                    <div className="flex items-center justify-between p-4">
                      <div className="flex min-w-0 items-center gap-3">
                        <AlertCircle className="flex-shrink-0 text-red-500" size={18} />
                        <span className="truncate font-mono text-sm text-slate-600">{url}</span>
                      </div>
                      <button
                        onClick={() => handleHowToFix(url)}
                        disabled={generatingFix[url]}
                        className={`ml-4 flex-shrink-0 rounded-lg px-4 py-2 text-xs font-bold transition-all ${
                          generatedFixes[url]
                            ? 'bg-slate-100 text-slate-600'
                            : 'bg-blue-600 text-white hover:bg-blue-700'
                        }`}
                      >
                        {generatingFix[url]
                          ? 'Analyzing...'
                          : generatedFixes[url]
                            ? 'Close Plan'
                            : 'How to Fix →'}
                      </button>
                    </div>

                    {generatedFixes[url] && (
                      <div className="animate-fade-in border-t border-slate-100 bg-blue-50/30 p-6">
                        <div className="mx-auto max-w-4xl space-y-8">
                          {generatedFixes[url]?.metrics && (
                            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
                              <h4 className="mb-6 flex items-center gap-2 text-sm font-bold text-slate-800">
                                <Cpu size={16} className="text-blue-500" />
                                Page Audit Result
                              </h4>
                              <div className="space-y-4">
                                {[
                                  { id: 'js_hydration', label: 'JS Dependency', value: generatedFixes[url].metrics?.js_impact === 'CRITICAL' ? '🔴 CRITICAL — heavy JS dependency' : (generatedFixes[url].metrics?.js_impact === 'MODERATE' ? '🟡 Moderate JS dependency' : '✅ Low JS dependency'), color: generatedFixes[url].metrics?.js_impact === 'CRITICAL' ? 'text-red-600' : (generatedFixes[url].metrics?.js_impact === 'MODERATE' ? 'text-amber-600' : 'text-emerald-600'), score: generatedFixes[url].metrics?.js_impact === 'LOW' ? 'Good' : (generatedFixes[url].metrics?.js_impact === 'MODERATE' ? 'Medium' : 'Bad') },
                                  { id: 'unused_js', label: 'Unused JavaScript', value: (generatedFixes[url].metrics?.unused_js_pct ?? 0) > 60 ? `🔴 ${generatedFixes[url].metrics.unused_js_pct}% unused (dead code blocking crawlers)` : ((generatedFixes[url].metrics?.unused_js_pct ?? 0) >= 30 ? `🟡 ${generatedFixes[url].metrics.unused_js_pct}% unused JS is downloaded but never executed` : `✅ ${generatedFixes[url].metrics?.unused_js_pct ?? 0}% unused — highly efficient`), color: (generatedFixes[url].metrics?.unused_js_pct ?? 0) > 60 ? 'text-red-600' : ((generatedFixes[url].metrics?.unused_js_pct ?? 0) >= 30 ? 'text-amber-600' : 'text-emerald-600'), score: (generatedFixes[url].metrics?.unused_js_pct ?? 0) > 60 ? 'Bad' : ((generatedFixes[url].metrics?.unused_js_pct ?? 0) >= 30 ? 'Medium' : 'Good') },
                                  { id: 'js_payload', label: 'JS Bundle Size', value: (generatedFixes[url].metrics?.js_payload_mb ?? 0) > 3 ? `🔴 ${generatedFixes[url].metrics.js_payload_mb}MB — timeout risk for bots` : ((generatedFixes[url].metrics?.js_payload_mb ?? 0) >= 1 ? `🟡 ${generatedFixes[url].metrics.js_payload_mb}MB — may slow AI crawler indexing` : `✅ ${generatedFixes[url].metrics?.js_payload_mb ?? 0}MB JS payload — crawler friendly`), color: (generatedFixes[url].metrics?.js_payload_mb ?? 0) > 3 ? 'text-red-600' : ((generatedFixes[url].metrics?.js_payload_mb ?? 0) >= 1 ? 'text-amber-600' : 'text-emerald-600'), score: (generatedFixes[url].metrics?.js_payload_mb ?? 0) > 3 ? 'Bad' : ((generatedFixes[url].metrics?.js_payload_mb ?? 0) >= 1 ? 'Medium' : 'Good') },
                                  { id: 'lcp', label: 'Page Load (LCP)', value: (generatedFixes[url].metrics?.lcp_seconds ?? 0) > 4 ? `🔴 ${generatedFixes[url].metrics.lcp_seconds}s LCP — too slow for bot timeouts` : ((generatedFixes[url].metrics?.lcp_seconds ?? 0) >= 2.5 ? `🟡 ${generatedFixes[url].metrics.lcp_seconds}s LCP — borderline for AI crawlers` : `✅ ${generatedFixes[url].metrics?.lcp_seconds ?? 0}s LCP — fast enough for AI crawlers`), color: (generatedFixes[url].metrics?.lcp_seconds ?? 0) > 4 ? 'text-red-600' : ((generatedFixes[url].metrics?.lcp_seconds ?? 0) >= 2.5 ? 'text-amber-600' : 'text-emerald-600'), score: (generatedFixes[url].metrics?.lcp_seconds ?? 0) > 4 ? 'Bad' : ((generatedFixes[url].metrics?.lcp_seconds ?? 0) >= 2.5 ? 'Medium' : 'Good') },
                                  { id: 'console_errors', label: 'Console Errors', value: (generatedFixes[url].metrics?.console_errors ?? 0) >= 3 ? `🔴 ${generatedFixes[url].metrics.console_errors} errors — page may appear broken to bots` : ((generatedFixes[url].metrics?.console_errors ?? 0) >= 1 ? `🟡 ${generatedFixes[url].metrics.console_errors} errors — check for failed API calls` : `✅ No JS errors detected`), color: (generatedFixes[url].metrics?.console_errors ?? 0) >= 3 ? 'text-red-600' : ((generatedFixes[url].metrics?.console_errors ?? 0) >= 1 ? 'text-amber-600' : 'text-emerald-600'), score: (generatedFixes[url].metrics?.console_errors ?? 0) >= 3 ? 'Bad' : ((generatedFixes[url].metrics?.console_errors ?? 0) >= 1 ? 'Medium' : 'Good') },
                                ].map((row) => (
                                  <div key={row.id} className="border-b border-slate-50 pb-3 last:border-0 last:pb-0">
                                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                                      <div className="flex flex-col sm:flex-row sm:items-center">
                                        <div className="w-full text-xs font-semibold text-slate-400 sm:w-48">{row.label}</div>
                                        <div className={`text-sm font-bold ${row.color}`}>{row.value}</div>
                                      </div>
                                      {row.score !== 'Good' && (
                                        <button
                                          onClick={() => toggleGuidance(url, row.id)}
                                          className={`mt-2 flex items-center gap-1.5 rounded-lg px-3 py-1 text-[10px] font-black uppercase tracking-tight transition-all hover:scale-105 sm:mt-0 ${
                                            row.score === 'Bad' ? 'bg-red-50 text-red-600' : 'bg-amber-50 text-amber-600'
                                          }`}
                                        >
                                          {expandedGuidance[`${url}-${row.id}`] ? 'Hide Guidance' : 'Guidance →'}
                                        </button>
                                      )}
                                    </div>
                                    {expandedGuidance[`${url}-${row.id}`] && (
                                      <div className={`mt-3 animate-fade-in rounded-lg p-4 ring-1 ${
                                        row.score === 'Bad' ? 'bg-red-50/50 ring-red-100' : 'bg-amber-50/50 ring-amber-100'
                                      }`}>
                                        <ul className="space-y-2">
                                          {generatedFixes[url].guidance.find(g => g.id === row.id)?.steps?.map((step, si) => (
                                            <li key={si} className="flex items-start gap-2 text-xs text-slate-700">
                                              <span className={`mt-1 h-1 w-1 flex-shrink-0 rounded-full ${
                                                row.score === 'Bad' ? 'bg-red-400' : 'bg-amber-400'
                                              }`} />
                                              {step}
                                            </li>
                                          ))}
                                        </ul>
                                      </div>
                                    )}
                                  </div>
                                ))}
                                <div className="mt-6 border-t border-slate-100 pt-6">
                                  <div className="flex items-center gap-2 font-bold text-slate-900">
                                    Overall: {
                                      (() => {
                                        const m = generatedFixes[url]?.metrics;
                                        if (!m) return <span className="text-slate-400">Analysis Pending</span>;
                                        const isBad = m.js_impact === 'CRITICAL' || (m.unused_js_pct ?? 0) > 60 || (m.js_payload_mb ?? 0) > 3 || (m.lcp_seconds ?? 0) > 4 || (m.console_errors ?? 0) >= 3;
                                        const isMed = m.js_impact === 'MODERATE' || (m.unused_js_pct ?? 0) >= 30 || (m.js_payload_mb ?? 0) >= 1 || (m.lcp_seconds ?? 0) >= 2.5 || (m.console_errors ?? 0) >= 1;
                                        if (isBad) return <><span className="text-red-600">🔴 Poor AI Crawlability</span></>;
                                        if (isMed) return <><span className="text-amber-600">🟡 Moderate AI Crawlability</span></>;
                                        return <><span className="text-emerald-600">✅ Good AI Crawlability</span></>;
                                      })()
                                    }
                                  </div>
                                </div>
                              </div>
                            </div>
                          )}

                          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
                            <h4 className="mb-4 flex items-center gap-2 text-sm font-bold text-slate-800">
                              <AlertCircle size={16} className="text-blue-500" />
                              The Problem
                            </h4>
                            <p className="text-sm leading-relaxed text-slate-600">
                              {generatedFixes[url].problem}
                            </p>
                          </div>

                          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
                            <h4 className="mb-4 flex items-center gap-2 text-sm font-bold text-slate-800">
                              <CheckCircle2 size={16} className="text-blue-500" />
                              What YOU need to do
                            </h4>
                            <ul className="space-y-3">
                              {generatedFixes[url]?.checklist?.map((item, i) => (
                                <li
                                  key={i}
                                  className="flex items-start gap-3 text-sm text-slate-600"
                                >
                                  <span className="flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-blue-100 text-[10px] font-black text-blue-600">
                                    {i + 1}
                                  </span>
                                  {item}
                                </li>
                              ))}
                            </ul>
                          </div>

                          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
                            <div className="mb-4 flex items-center justify-between">
                              <h4 className="flex items-center gap-2 text-sm font-bold text-slate-800">
                                <FileCode size={16} className="text-blue-500" />
                                JSON-LD Schema Template
                              </h4>
                              <button
                                onClick={() =>
                                  copyToClipboard(generatedFixes[url].json_ld, url, 'fix')
                                }
                                className="flex items-center gap-1.5 text-xs font-bold text-blue-600 hover:text-blue-800"
                              >
                                {copiedFix[url] ? <Check size={14} /> : <Copy size={14} />}
                                {copiedFix[url] ? 'Copied!' : 'Copy Code'}
                              </button>
                            </div>
                            <div className="relative">
                              <pre className="max-h-80 overflow-auto rounded-lg bg-slate-900 p-4 font-mono text-[10px] leading-relaxed text-slate-300">
                                <code>{generatedFixes[url]?.json_ld ?? '// No schema generated'}</code>
                              </pre>
                            </div>
                            <p className="mt-4 text-[10px] italic text-slate-400">
                              Paste this into your website's &lt;head&gt; tag. Brand is set to
                              'Nothing' based on your profile.
                            </p>
                            <div className="mt-6 border-t border-slate-100 pt-6">
                              <button
                                onClick={() => navigate(`/audit/${encodeURIComponent(url)}`)}
                                className="flex w-full items-center justify-center gap-2 rounded-lg border border-slate-200 py-2.5 text-xs font-bold text-slate-600 transition-all hover:bg-slate-50"
                              >
                                View Deep Technical Audit Report <ArrowRight size={14} />
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="py-12 text-center text-slate-400">
                  No missing pages found. Your sitemap is fully cited!
                </div>
              )}
            </div>

            {totalPages > 1 && (
              <div className="mt-6 flex items-center justify-center gap-4">
                <button
                  className="rounded-lg border border-slate-200 p-2 text-slate-500 transition-all hover:bg-slate-100 disabled:opacity-30"
                  onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                >
                  <ChevronLeft size={20} />
                </button>
                <span className="text-sm font-medium text-slate-600">
                  Page {currentPage} of {totalPages}
                </span>
                <button
                  className="rounded-lg border border-slate-200 p-2 text-slate-500 transition-all hover:bg-slate-100 disabled:opacity-30"
                  onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                >
                  <ChevronRight size={20} />
                </button>
              </div>
            )}
          </section>

          {/* Fix 4: Gap Sources (Data Fetch Fix and Empty State Message) */}
          {benchmarkData && benchmarkData.tab_actions && (
            <section className="glass-card">
              <h3 className="mb-6 text-xl font-bold text-slate-900">Gap Sources</h3>
              <div className="mb-8 flex gap-2 border-b border-slate-200">
                {['YouTube', 'Reddit', 'Editorial'].map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`relative px-6 py-3 text-sm font-bold transition-all ${
                      activeTab === tab ? 'text-blue-600' : 'text-slate-500 hover:text-slate-800'
                    }`}
                  >
                    {tab}
                    {activeTab === tab && (
                      <div className="absolute bottom-0 left-0 h-0.5 w-full bg-blue-600" />
                    )}
                  </button>
                ))}
              </div>

              <div>
                {benchmarkData.tab_actions[activeTab] &&
                benchmarkData.tab_actions[activeTab].has_data ? (
                  <div className="space-y-6">
                    <div className="flex items-center gap-3">
                      <span
                        className={`rounded-full px-3 py-1 text-[10px] font-black tracking-widest uppercase ${
                          benchmarkData.tab_actions[activeTab].opportunity_score > 70
                            ? 'bg-red-100 text-red-600'
                            : benchmarkData.tab_actions[activeTab].opportunity_score > 40
                              ? 'bg-orange-100 text-orange-600'
                              : 'bg-blue-100 text-blue-600'
                        }`}
                      >
                        {benchmarkData.tab_actions[activeTab].opportunity_score > 70
                          ? 'High'
                          : benchmarkData.tab_actions[activeTab].opportunity_score > 40
                            ? 'Medium'
                            : 'Low'}{' '}
                        Opportunity
                      </span>
                      <span className="text-sm font-medium text-slate-400">
                        — {benchmarkData.tab_actions[activeTab].gap_percentage}% of{' '}
                        {activeTab.toLowerCase()} cite competitors, not your brand
                      </span>
                    </div>

                    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                      {benchmarkData.tab_actions[activeTab].items.map((gapItem, idx) => (
                        <div
                          key={idx}
                          className="flex flex-col justify-between rounded-xl border border-slate-100 bg-slate-50/50 p-5 ring-1 ring-slate-100"
                        >
                          <div className="mb-4 text-sm leading-relaxed text-slate-700">
                            {renderMarkdownLinks(gapItem.text)}
                          </div>
                          <button
                            onClick={() =>
                              handleGenerateContent(activeTab, gapItem.text, gapItem.id)
                            }
                            disabled={generatingContent[gapItem.id]}
                            className="btn-primary w-full justify-center py-2 text-xs"
                          >
                            {generatingContent[gapItem.id] ? 'Generating...' : 'Generate Content →'}
                          </button>

                          {generatedContent[gapItem.id] && (
                            <div className="mt-4 rounded-lg bg-white p-4 shadow-sm ring-1 ring-slate-200">
                              <p className="mb-3 text-xs leading-relaxed whitespace-pre-wrap text-slate-600">
                                {generatedContent[gapItem.id]}
                              </p>
                              <button
                                onClick={() =>
                                  copyToClipboard(
                                    generatedContent[gapItem.id],
                                    gapItem.id,
                                    'content',
                                  )
                                }
                                className="flex items-center gap-1 text-[10px] font-bold text-blue-600"
                              >
                                {copiedContent[gapItem.id] ? (
                                  <Check size={12} />
                                ) : (
                                  <Copy size={12} />
                                )}
                                {copiedContent[gapItem.id] ? 'Copied!' : 'Copy'}
                              </button>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="flex h-40 items-center justify-center text-center">
                    <p className="max-w-md text-sm font-medium text-slate-400">
                      Not enough data yet — Peec needs 3–5 more days of prompt tracking to surface
                      gaps here.
                    </p>
                  </div>
                )}
              </div>
            </section>
          )}
        </>
      )}
    </div>
  )
}

export default Dashboard
