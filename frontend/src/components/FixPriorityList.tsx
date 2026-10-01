import type { GeoCheck } from '../types/api'
import { prioritizeFixes } from '../lib/geoChecks'

export function FixPriorityList({ checks }: { checks: GeoCheck[] }) {
  const items = prioritizeFixes(checks)
  if (items.length === 0) return null
  return (
    <section
      className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
      aria-label="Fix priority"
    >
      <h4 className="mb-1 text-sm font-bold text-slate-800">What to fix first</h4>
      <p className="mb-4 text-sm text-slate-500">
        A hand-set order from assumed citation impact and how large the change is. It is not a
        measured result.
      </p>
      <ol className="space-y-4">
        {items.map((item) => (
          <li key={item.id} className="flex items-start gap-3">
            <span className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-slate-900 text-xs font-black text-white">
              {item.rank}
            </span>
            <div>
              <p className="text-sm font-bold text-slate-900">{item.name}</p>
              <p className="mt-1 text-sm leading-relaxed text-slate-600">{item.summary}</p>
            </div>
          </li>
        ))}
      </ol>
    </section>
  )
}
