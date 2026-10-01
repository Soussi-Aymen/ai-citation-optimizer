import type { GeoCheck } from '../types/api'

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
