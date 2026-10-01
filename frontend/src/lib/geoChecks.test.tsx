import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { FixPriorityList } from '../components/FixPriorityList'
import type { GeoCheck } from '../types/api'
import { prioritizeFixes } from './geoChecks'

function check(id: string, status: GeoCheck['status'], name = id): GeoCheck {
  return { id, name, tier: 'fast', status }
}

describe('prioritizeFixes', () => {
  it('ranks high-impact failures ahead of easier low-impact ones', () => {
    const ranked = prioritizeFixes([
      check('freshness_consistency', 'warn', 'Freshness'),
      check('schema_validation', 'fail', 'Schema'),
      check('ai_bot_access', 'fail', 'Bot access'),
    ])
    expect(ranked.map((item) => item.id)).toEqual([
      'ai_bot_access',
      'schema_validation',
      'freshness_consistency',
    ])
    expect(ranked[0]?.summary).toContain('Start here.')
    expect(ranked[0]?.summary).toContain('small change')
    expect(ranked[1]?.summary).toContain('Then this.')
  })

  it('does an easier change before a larger one in the same impact band', () => {
    const ranked = prioritizeFixes([
      check('bot_view_diff', 'fail', 'Bot view'),
      check('ai_bot_access', 'fail', 'Bot access'),
    ])
    expect(ranked.map((item) => item.id)).toEqual(['ai_bot_access', 'bot_view_diff'])
    expect(ranked[1]?.effort).toBe('larger')
  })

  it('keeps a citability failure below an answer-readiness failure', () => {
    const ranked = prioritizeFixes([
      check('llm_citability_review', 'fail', 'Citability'),
      check('answer_readiness', 'fail', 'Answers'),
    ])
    expect(ranked.map((item) => item.id)).toEqual(['answer_readiness', 'llm_citability_review'])
  })

  it('drops passed and skipped checks', () => {
    expect(
      prioritizeFixes([
        check('ai_bot_access', 'pass', 'Bot access'),
        check('schema_validation', 'skipped', 'Schema'),
        check('orphan_page_check', 'error', 'Orphan'),
      ]),
    ).toEqual([])
  })

  it('returns at most five items and puts a failure ahead of a warning at the same effort', () => {
    const ranked = prioritizeFixes([
      check('canonical_and_redirects', 'warn', 'Canonical'),
      check('freshness_consistency', 'fail', 'Freshness'),
      check('ai_bot_access', 'fail', 'Bot access'),
      check('bot_view_diff', 'warn', 'Bot view'),
      check('answer_readiness', 'fail', 'Answers'),
      check('schema_validation', 'fail', 'Schema'),
      check('orphan_page_check', 'fail', 'Orphan'),
    ])
    expect(ranked).toHaveLength(5)
    expect(ranked.map((item) => item.id)).not.toContain('orphan_page_check')
    const sameBand = prioritizeFixes([
      check('freshness_consistency', 'warn', 'Freshness'),
      check('canonical_and_redirects', 'fail', 'Canonical'),
    ])
    expect(sameBand.map((item) => item.id)).toEqual([
      'canonical_and_redirects',
      'freshness_consistency',
    ])
  })
})

describe('FixPriorityList', () => {
  it('renders the numbered reasons and hides itself when nothing failed', () => {
    const { rerender } = render(
      <FixPriorityList
        checks={[
          check('ai_bot_access', 'fail', 'AI bot access'),
          check('schema_validation', 'pass', 'Schema'),
        ]}
      />,
    )
    expect(screen.getByRole('region', { name: 'Fix priority' })).toBeInTheDocument()
    expect(screen.getByText('AI bot access')).toBeInTheDocument()
    expect(screen.getByText(/Start here\./)).toBeInTheDocument()
    expect(screen.queryByText('Schema')).not.toBeInTheDocument()

    rerender(<FixPriorityList checks={[check('schema_validation', 'pass', 'Schema')]} />)
    expect(screen.queryByRole('region', { name: 'Fix priority' })).not.toBeInTheDocument()
  })
})
