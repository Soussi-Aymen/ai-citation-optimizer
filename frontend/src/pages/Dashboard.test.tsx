import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import axios from 'axios'
import type { AxiosResponse } from 'axios'
import type { BenchmarkResponse, GapsResponse } from '../types/api'
import Dashboard from './Dashboard'

vi.mock('axios')
const mockedAxios = vi.mocked(axios, true)

const gapsWithoutPeec: GapsResponse = {
  domain: 'example.com',
  peec_available: false,
  total_sitemap_pages: 2,
  total_cited_pages: null,
  citation_coverage_pct: null,
  performance_score: null,
  gaps: ['https://example.com/page-a', 'https://example.com/page-b'],
  orphans: [],
  sitemap_metrics: {},
  brands: [],
  competitors: [],
}

const gapsWithPeec: GapsResponse = {
  domain: 'example.com',
  peec_available: true,
  total_sitemap_pages: 2,
  total_cited_pages: 1,
  citation_coverage_pct: 50,
  performance_score: 80,
  gaps: ['https://example.com/page-b'],
  orphans: [],
  sitemap_metrics: {},
  brands: [],
  competitors: [],
}

function renderDashboard() {
  return render(
    <MemoryRouter>
      <Dashboard />
    </MemoryRouter>,
  )
}

describe('Dashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  it('renders the domain search form', () => {
    renderDashboard()
    expect(screen.getByPlaceholderText(/enter your domain/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /run analysis/i })).toBeInTheDocument()
  })

  it('hides Peec citation stats when API reports unavailable', async () => {
    mockedAxios.get.mockResolvedValueOnce({ data: gapsWithoutPeec } as AxiosResponse)
    const user = userEvent.setup()

    renderDashboard()
    await user.type(screen.getByPlaceholderText(/enter your domain/i), 'example.com')
    await user.click(screen.getByRole('button', { name: /run analysis/i }))

    await waitFor(() => {
      expect(screen.getByText('Sitemap Pages')).toBeInTheDocument()
    })

    expect(screen.queryByText('Cited by AI')).not.toBeInTheDocument()
    expect(screen.queryByText('AI Coverage')).not.toBeInTheDocument()
    expect(screen.getByText('Your Sitemap Pages')).toBeInTheDocument()
    expect(mockedAxios.get).toHaveBeenCalledTimes(1)
  })

  it('shows Peec citation stats and fetches benchmark when available', async () => {
    const benchmark: BenchmarkResponse = {
      domain: 'example.com',
      current: { visibility_score: 10, citation_count: 1 },
      estimated: { visibility_score: 20, citation_count: 2 },
      roadmap: [],
      channel_gaps: [],
      tab_actions: {},
      own_brand_name: 'Example',
    }

    mockedAxios.get
      .mockResolvedValueOnce({ data: gapsWithPeec } as AxiosResponse)
      .mockResolvedValueOnce({ data: benchmark } as AxiosResponse)

    const user = userEvent.setup()
    renderDashboard()
    await user.type(screen.getByPlaceholderText(/enter your domain/i), 'example.com')
    await user.click(screen.getByRole('button', { name: /run analysis/i }))

    await waitFor(() => {
      expect(screen.getByText('Cited by AI')).toBeInTheDocument()
    })

    expect(screen.getByText('AI Coverage')).toBeInTheDocument()
    expect(screen.getByText('Your Pages Missing from AI Answers')).toBeInTheDocument()
    expect(mockedAxios.get).toHaveBeenCalledTimes(2)
  })
})
