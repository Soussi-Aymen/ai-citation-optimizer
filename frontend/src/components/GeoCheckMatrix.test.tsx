import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import type { GeoCheck } from '../types/api'
import { appendFixHints, mergeDeepChecks } from '../lib/geoChecks'
import { GeoCheckMatrix } from './GeoCheckMatrix'

const fast: GeoCheck = {
  id: 'ai_bot_access',
  name: 'AI bot access',
  tier: 'fast',
  status: 'fail',
  fix_hint: 'Allow GPTBot in robots.txt',
}

const deep: GeoCheck = {
  id: 'orphan_page_check',
  name: 'Orphan page',
  tier: 'deep',
  status: 'pass',
}

describe('GeoCheckMatrix', () => {
  it('groups fast and deep checks with the same status marks', () => {
    render(<GeoCheckMatrix checks={[fast, deep]} deepLoading={false} />)
    expect(screen.getByText('Technical Health Matrix')).toBeInTheDocument()
    expect(screen.getByText('Fast checks')).toBeInTheDocument()
    expect(screen.getByText('Deep checks')).toBeInTheDocument()
    expect(screen.getByText('AI bot access')).toBeInTheDocument()
    expect(screen.getByText(/Fail/)).toBeInTheDocument()
    expect(screen.getByText(/Pass/)).toBeInTheDocument()
    expect(screen.getByText('Allow GPTBot in robots.txt')).toBeInTheDocument()
  })

  it('shows a busy loading state while deep checks are still running', () => {
    const { container } = render(<GeoCheckMatrix checks={[fast]} deepLoading />)
    expect(container.querySelector('[aria-busy="true"]')).toBeTruthy()
    expect(screen.getByText('Deep checks are still running.')).toBeInTheDocument()
  })
})

describe('geo check updates', () => {
  it('merges deep results and appends only fail or warn hints', () => {
    const merged = mergeDeepChecks([fast], [deep])
    expect(merged.map((check) => check.id)).toEqual(['ai_bot_access', 'orphan_page_check'])
    expect(
      appendFixHints(
        ['Step 1'],
        [
          deep,
          { ...deep, id: 'llm', status: 'warn', fix_hint: 'Answer the question in HTML' },
          { ...fast, fix_hint: 'Step 1' },
        ],
      ),
    ).toEqual(['Step 1', 'Answer the question in HTML'])
  })
})
