import type { GeoCheck } from '../types/api'

type Effort = 'small' | 'medium' | 'larger'

type FixWeight = {
  impact: number
  complexity: number
  effort: Effort
  reason: string
}

const FIX_WEIGHTS: Record<string, FixWeight> = {
  ai_bot_access: {
    impact: 3,
    complexity: 1,
    effort: 'small',
    reason: 'Bots cannot read this page until they are allowed in.',
  },
  bot_view_diff: {
    impact: 3,
    complexity: 3,
    effort: 'larger',
    reason: 'The visible copy is missing from the HTML bots fetch.',
  },
  answer_readiness: {
    impact: 2,
    complexity: 2,
    effort: 'medium',
    reason: 'A direct answer makes the page easier to quote.',
  },
  schema_validation: {
    impact: 2,
    complexity: 2,
    effort: 'medium',
    reason: 'Structured data tells models what the page is.',
  },
  canonical_and_redirects: {
    impact: 1,
    complexity: 1,
    effort: 'small',
    reason: 'The canonical or redirect chain sends bots to the wrong URL.',
  },
  freshness_consistency: {
    impact: 1,
    complexity: 1,
    effort: 'small',
    reason: 'Stale or conflicting dates make the page look outdated.',
  },
  orphan_page_check: {
    impact: 1,
    complexity: 2,
    effort: 'medium',
    reason: 'Nothing on the site links to this page.',
  },
  llm_citability_review: {
    impact: 0,
    complexity: 2,
    effort: 'medium',
    reason: 'The review found questions the page still does not answer.',
  },
}

const DEFAULT_WEIGHT: FixWeight = {
  impact: 0,
  complexity: 2,
  effort: 'medium',
  reason: 'This check still needs a fix before the page is easy to cite.',
}

export type FixPriority = {
  id: string
  rank: number
  name: string
  effort: Effort
  summary: string
}

export function prioritizeFixes(checks: GeoCheck[]): FixPriority[] {
  const actionable = checks.filter((check) => check.status === 'fail' || check.status === 'warn')
  const ranked = [...actionable].sort((left, right) => {
    const a = FIX_WEIGHTS[left.id] ?? DEFAULT_WEIGHT
    const b = FIX_WEIGHTS[right.id] ?? DEFAULT_WEIGHT
    if (b.impact !== a.impact) return b.impact - a.impact
    if (a.complexity !== b.complexity) return a.complexity - b.complexity
    if (left.status !== right.status) return left.status === 'fail' ? -1 : 1
    return left.name.localeCompare(right.name)
  })
  return ranked.slice(0, 5).map((check, index) => {
    const weight = FIX_WEIGHTS[check.id] ?? DEFAULT_WEIGHT
    const lead = index === 0 ? 'Start here.' : 'Then this.'
    return {
      id: check.id,
      rank: index + 1,
      name: check.name,
      effort: weight.effort,
      summary: `${lead} ${weight.reason} This is a ${weight.effort} change.`,
    }
  })
}

export function mergeDeepChecks(current: GeoCheck[], incoming: GeoCheck[]): GeoCheck[] {
  const incomingIds = new Set(incoming.map((check) => check.id))
  return [...current.filter((check) => !incomingIds.has(check.id)), ...incoming]
}

export function appendFixHints(checklist: string[], checks: GeoCheck[]): string[] {
  const next = [...checklist]
  for (const check of checks) {
    if (
      (check.status === 'fail' || check.status === 'warn') &&
      check.fix_hint &&
      !next.includes(check.fix_hint)
    ) {
      next.push(check.fix_hint)
    }
  }
  return next
}
