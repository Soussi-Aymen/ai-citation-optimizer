import type { GeoCheck, GeoCheckStatus, GeoCheckTier } from '../types/api'

const STATUS: Record<GeoCheckStatus, { mark: string; color: string; label: string }> = {
  pass: { mark: '✅', color: 'text-emerald-600', label: 'Pass' },
  warn: { mark: '🟡', color: 'text-amber-600', label: 'Warn' },
  fail: { mark: '🔴', color: 'text-red-600', label: 'Fail' },
  skipped: { mark: '⚪', color: 'text-slate-500', label: 'Skipped' },
  error: { mark: '⚪', color: 'text-slate-500', label: 'Error' },
}

function CheckGroup({
  title,
  checks,
  loading = false,
}: {
  title: string
  checks: GeoCheck[]
  loading?: boolean
}) {
  return (
    <details className="disclosure" open>
      <summary className="motion-safe-scale text-xs font-bold tracking-wide text-slate-500 uppercase">
        {title}
      </summary>
      {loading && checks.length === 0 && (
        <p className="mt-3 text-sm text-slate-500">Deep checks are still running.</p>
      )}
      <ul className="mt-3 space-y-3">
        {checks.map((check) => {
          const status = STATUS[check.status]
          return (
            <li key={check.id} className="border-b border-slate-50 pb-3 last:border-0 last:pb-0">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                <div className="w-full text-xs font-semibold text-slate-400 sm:w-48">
                  {check.name}
                </div>
                <div className={`text-sm font-bold ${status.color}`}>
                  {status.mark} {status.label}
                </div>
              </div>
              {check.status === 'skipped' && typeof check.evidence?.reason === 'string' && (
                <p className="mt-1 text-xs text-slate-600">{check.evidence.reason}</p>
              )}
              {check.fix_hint && check.status !== 'pass' && (
                <p className="mt-1 text-xs text-slate-600">{check.fix_hint}</p>
              )}
            </li>
          )
        })}
      </ul>
    </details>
  )
}

export function GeoCheckMatrix({
  checks,
  deepLoading,
}: {
  checks: GeoCheck[]
  deepLoading: boolean
}) {
  const grouped = (tier: GeoCheckTier) => checks.filter((check) => check.tier === tier)
  return (
    <div className="mt-6 space-y-4 border-t border-slate-100 pt-6">
      <h5 className="text-sm font-bold text-slate-800">Technical Health Matrix</h5>
      <CheckGroup title="Fast checks" checks={grouped('fast')} />
      <section aria-busy={deepLoading}>
        <CheckGroup title="Deep checks" checks={grouped('deep')} loading={deepLoading} />
      </section>
    </div>
  )
}
