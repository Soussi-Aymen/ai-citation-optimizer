import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'
import {
  ArrowLeft,
  Zap,
  ShieldAlert,
  CheckCircle2,
  Cpu,
  Activity,
  Clock,
  Globe,
  FileJson,
  Target,
  BarChart2,
  Code2,
  Layers,
  CheckSquare,
  XSquare,
} from 'lucide-react'

const PageDetail = () => {
  const { url } = useParams()
  const decodedUrl = decodeURIComponent(url)
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [currentStep, setCurrentStep] = useState(0)
  const [expandedGuidance, setExpandedGuidance] = useState({})

  const toggleGuidance = (id) => {
    setExpandedGuidance((prev) => ({ ...prev, [id]: !prev[id] }))
  }

  const simulationSteps = [
    'Spinning up Chromium Cluster...',
    'Awaiting Network Idle (JS Hydration)...',
    'Extracting DevTools Meta-Signals...',
    'Fetching Peec Competitor Intelligence...',
    'Building Multi-Track Report with Gemini...',
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
      setCurrentStep((prev) => (prev < simulationSteps.length - 1 ? prev + 1 : prev))
    }, 3000)

    const runAudit = async () => {
      try {
        const response = await axios.post(
          'http://localhost:8000/api/audit',
          { url: decodedUrl },
          {
            timeout: 120000,
          },
        )

        if (response.data.analysis.error) {
          setData(response.data.analysis)
          setError('Audit Engine Error: ' + (response.data.analysis.message || 'Unknown Error'))
        } else {
          setData(response.data.analysis)
          localStorage.setItem(cacheKey, JSON.stringify(response.data.analysis))
        }
      } catch (err) {
        console.error(err)
        setError(
          'Connection Timeout: The audit is taking longer than 2 minutes or the backend is unresponsive.',
        )
      } finally {
        setLoading(false)
        clearInterval(stepInterval)
      }
    }
    runAudit()
    return () => clearInterval(stepInterval)
  }, [decodedUrl])

  if (loading)
    return (
      <div className="flex flex-col items-center justify-center py-32 text-center">
        <div className="mb-8 h-12 w-12 animate-spin rounded-full border-4 border-blue-500 border-t-transparent"></div>
        <h2 className="mb-2 text-2xl font-bold text-slate-900">{simulationSteps[currentStep]}</h2>
        <p className="text-slate-500">Performing deep technical crawlability audit...</p>
      </div>
    )

  if (error)
    return (
      <div className="glass-card flex flex-col items-center py-16 text-center">
        <ShieldAlert size={64} className="mb-6 text-red-500" />
        <h2 className="mb-2 text-2xl font-bold text-slate-900">Audit Engine Error</h2>
        <p className="mx-auto mb-8 max-w-lg text-slate-500">{error}</p>

        {data?.logs && (
          <div className="mb-8 w-full max-w-2xl rounded-lg bg-slate-900 p-6 text-left">
            <div className="mb-4 font-mono text-xs font-bold text-red-400">FAILURE_TRACE:</div>
            <div className="max-h-48 space-y-1 overflow-auto font-mono text-[10px] text-slate-400">
              {data.logs.map((log, i) => (
                <div key={i}>
                  <span className="mr-2 text-slate-600">&gt;</span>
                  {log}
                </div>
              ))}
            </div>
          </div>
        )}

        <button className="btn-primary" onClick={() => navigate('/')}>
          Back to Dashboard
        </button>
      </div>
    )

  return (
    <div className="animate-fade-in">
      <div className="mb-8 flex items-center justify-between">
        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-2 font-bold text-slate-500 transition-colors hover:text-slate-900"
        >
          <ArrowLeft size={18} /> Dashboard
        </button>
        <span className="text-xs font-medium text-slate-400">Powered by Gemini & Peec AI</span>
      </div>

      <header className="mb-10">
        <h1 className="mb-2 text-3xl font-extrabold tracking-tight text-slate-900">
          Technical Audit Report
        </h1>
        <p className="font-mono text-sm break-all text-slate-500">{decodedUrl}</p>
      </header>

      {data.signals && (
        <section className="glass-card mb-8">
          <div className="mb-6 flex items-center gap-2">
            <Cpu size={20} className="text-slate-400" />
            <div>
              <h3 className="text-lg font-bold text-slate-900">Technical Meta-Signals</h3>
              <p className="text-xs text-slate-500">
                Live browser render metrics captured during audit
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {/* Load Time */}
            <div className="rounded-xl border border-slate-100 bg-slate-50 p-4 ring-1 ring-slate-100">
              <div className="mb-2 flex items-center gap-2 text-[10px] font-bold tracking-widest text-slate-400 uppercase">
                <Clock size={12} /> Load Time
              </div>
              <div
                className={`text-2xl font-black ${
                  data.signals.load_time_ms < 2000
                    ? 'text-emerald-600'
                    : data.signals.load_time_ms < 4000
                      ? 'text-amber-600'
                      : 'text-red-600'
                }`}
              >
                {data.signals.load_time_ms}ms
              </div>
            </div>

            {/* JS Impact */}
            <div className="rounded-xl border border-slate-100 bg-slate-50 p-4 ring-1 ring-slate-100">
              <div className="mb-2 flex items-center gap-2 text-[10px] font-bold tracking-widest text-slate-400 uppercase">
                <Code2 size={12} /> JS Hydration
              </div>
              <div
                className={`text-2xl font-black ${
                  data.signals.js_impact === 'CRITICAL' ? 'text-red-600' : 'text-amber-600'
                }`}
              >
                {data.signals.js_impact}
              </div>
            </div>

            {/* DOM Depth */}
            <div className="rounded-xl border border-slate-100 bg-slate-50 p-4 ring-1 ring-slate-100">
              <div className="mb-2 flex items-center gap-2 text-[10px] font-bold tracking-widest text-slate-400 uppercase">
                <Layers size={12} /> DOM Depth
              </div>
              <div className="text-2xl font-black text-slate-900">{data.signals.dom_depth}</div>
            </div>

            {/* Structured Data */}
            <div className="rounded-xl border border-slate-100 bg-slate-50 p-4 ring-1 ring-slate-100">
              <div className="mb-2 flex items-center gap-2 text-[10px] font-bold tracking-widest text-slate-400 uppercase">
                <FileJson size={12} /> JSON-LD
              </div>
              <div className="flex items-center gap-2">
                {data.signals.has_json_ld ? (
                  <>
                    <CheckSquare size={20} className="text-emerald-500" />
                    <span className="text-lg font-black text-emerald-600">Present</span>
                  </>
                ) : (
                  <>
                    <XSquare size={20} className="text-red-500" />
                    <span className="text-lg font-black text-red-600">Missing</span>
                  </>
                )}
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Technical Optimization Guidance — Only shows Medium/Bad scores */}
      {data.guidance && data.guidance.length > 0 && (
        <section className="glass-card mb-8 border-amber-200 bg-amber-50/50">
          <h3 className="mb-6 flex items-center gap-2 text-lg font-bold text-amber-900">
            <Activity size={20} className="text-amber-600" /> Recommended Performance Optimizations
          </h3>
          <div className="grid grid-cols-1 gap-4">
            {data.guidance.map((item, i) => (
              <div
                key={i}
                className={`rounded-xl border-l-4 bg-white/80 p-5 shadow-sm ${
                  item.score === 'Bad' ? 'border-red-500' : 'border-amber-500'
                }`}
              >
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="mb-2 flex items-center gap-3">
                      <span className="text-[10px] font-black uppercase tracking-widest text-amber-800">
                        {item.metric.toUpperCase()}
                      </span>
                      <span
                        className={`rounded-full px-2 py-0.5 text-[10px] font-black uppercase ${
                          item.score === 'Bad'
                            ? 'bg-red-100 text-red-600'
                            : 'bg-amber-100 text-amber-600'
                        }`}
                      >
                        {item.score}
                      </span>
                    </div>
                    <div className="text-sm font-bold text-amber-900">{item.advice}</div>
                  </div>
                  <button
                    onClick={() => toggleGuidance(item.id)}
                    className={`rounded-lg px-4 py-2 text-xs font-bold text-white transition-all hover:scale-105 ${
                      item.score === 'Bad' ? 'bg-red-600' : 'bg-amber-600'
                    }`}
                  >
                    {expandedGuidance[item.id] ? 'Close Guidance' : 'View Fix Steps'}
                  </button>
                </div>

                {expandedGuidance[item.id] && (
                  <div className="mt-6 animate-fade-in rounded-lg border border-amber-100 bg-white p-5 shadow-inner">
                    <h4 className="mb-4 flex items-center gap-2 text-xs font-black uppercase tracking-widest text-amber-800">
                      <Target size={14} className="text-amber-600" /> Framework-Agnostic Implementation
                    </h4>
                    <ul className="space-y-3">
                      {item.steps.map((step, si) => (
                        <li
                          key={si}
                          className="flex items-start gap-3 text-sm leading-relaxed text-amber-900/80"
                        >
                          <span className="flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-amber-100 text-[10px] font-black text-amber-700">
                            {si + 1}
                          </span>
                          {step}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
        {/* Performance Report */}
        <section className="glass-card">
          <div className="mb-6 flex items-center justify-between">
            <h3 className="flex items-center gap-2 text-lg font-bold text-slate-900">
              <Zap size={20} className="text-amber-500" /> Performance Audit
            </h3>
            <span className="rounded-full bg-amber-50 px-3 py-1 text-sm font-bold text-amber-600">
              Score: {data.performance_report.score}/100
            </span>
          </div>

          <div className="space-y-6">
            <div>
              <h4 className="mb-3 text-xs font-bold tracking-widest text-red-500 uppercase">
                Critical Issues
              </h4>
              <ul className="space-y-2">
                {data.performance_report?.issues?.map((issue, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-slate-600">
                    <span className="mt-1.5 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-red-400" />
                    {issue}
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h4 className="mb-3 text-xs font-bold tracking-widest text-emerald-500 uppercase">
                Recommended Fixes
              </h4>
              <ul className="space-y-2">
                {data.performance_report?.fixes?.map((fix, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-slate-600">
                    <span className="mt-1.5 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-emerald-400" />
                    {fix}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </section>

        {/* Sitemap Audit */}
        <section className="glass-card">
          <div className="mb-6 flex items-center justify-between">
            <h3 className="flex items-center gap-2 text-lg font-bold text-slate-900">
              <Globe size={20} className="text-blue-500" /> Content & Sitemap
            </h3>
            <span className="rounded-full bg-blue-50 px-3 py-1 text-sm font-bold text-blue-600">
              Health: {data.sitemap_audit.score}%
            </span>
          </div>

          <div className="mb-6 rounded-lg bg-slate-50 p-4 text-sm leading-relaxed text-slate-600">
            {data.sitemap_audit.analysis}
          </div>

          <h4 className="mb-3 text-xs font-bold tracking-widest text-blue-500 uppercase">
            Roadmap for Visibility
          </h4>
          <div className="grid grid-cols-1 gap-2">
            {data.sitemap_audit?.improvements?.map((imp, i) => (
              <div
                key={i}
                className="rounded-lg border border-slate-100 bg-white p-3 text-sm text-slate-700 shadow-sm"
              >
                {imp}
              </div>
            ))}
          </div>
        </section>
      </div>

      {/* Competitive Edge */}
      <section className="glass-card mt-8 border-indigo-100 bg-indigo-50/30">
        <h3 className="mb-6 flex items-center gap-2 text-lg font-bold text-slate-900">
          <Target size={20} className="text-indigo-500" /> Competitive Landscape
        </h3>
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
          <div>
            <h4 className="mb-2 text-xs font-bold tracking-widest text-indigo-500 uppercase">
              Competitor Advantages
            </h4>
            <p className="text-sm leading-relaxed text-slate-600">
              {data.competitive_analysis.competitor_edge}
            </p>
          </div>
          <div>
            <h4 className="mb-2 text-xs font-bold tracking-widest text-indigo-500 uppercase">
              Strategic Gap to Close
            </h4>
            <div className="rounded-xl border border-indigo-200 bg-white p-5 text-lg font-bold text-indigo-600 shadow-sm">
              {data.competitive_analysis.gap_to_close}
            </div>
          </div>
        </div>
      </section>

      {/* Final Verdict */}
      <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="glass-card flex flex-col items-center justify-center py-8 text-center">
          <span className="mb-1 text-[10px] font-bold tracking-[0.2em] text-slate-400 uppercase">
            AI READINESS
          </span>
          <div className="text-4xl font-black text-slate-900">
            {data.ai_readiness.overall_score}%
          </div>
        </div>
        <div className="glass-card flex flex-col items-center justify-center border-emerald-100 bg-emerald-50 py-8 text-center">
          <span className="mb-1 text-[10px] font-bold tracking-[0.2em] text-emerald-500 uppercase">
            ESTIMATED IMPACT
          </span>
          <div className="text-4xl font-black text-emerald-600">
            {data.ai_readiness.estimated_impact}
          </div>
        </div>
        <div className="glass-card flex flex-col items-center justify-center py-8 text-center">
          <span className="mb-1 text-[10px] font-bold tracking-[0.2em] text-slate-400 uppercase">
            AUDIT SPEED
          </span>
          <div className="text-4xl font-black text-blue-500">{data.execution_time_ms}ms</div>
        </div>
      </div>

      {/* Audit Logs */}
      <div className="mt-8">
        <h3 className="mb-4 text-xs font-bold tracking-widest text-slate-400 uppercase">
          Execution Trace
        </h3>
        <div className="max-h-32 overflow-auto rounded-lg bg-slate-900 p-4 font-mono text-[10px] text-slate-500">
          {data.logs &&
            data.logs.map((log, i) => (
              <div key={i}>
                <span className="mr-2 text-slate-700">&gt;</span>
                {log}
              </div>
            ))}
        </div>
      </div>
    </div>
  )
}

export default PageDetail
