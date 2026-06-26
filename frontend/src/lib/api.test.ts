import { describe, it, expect, vi, beforeEach } from 'vitest'

describe('apiUrl', () => {
  beforeEach(() => {
    vi.resetModules()
  })

  it('defaults to localhost when VITE_API_URL is unset', async () => {
    vi.stubEnv('VITE_API_URL', '')
    const { API_BASE, apiUrl } = await import('../lib/api')
    expect(API_BASE).toBe('http://localhost:8000')
    expect(apiUrl('/api/health')).toBe('http://localhost:8000/api/health')
  })

  it('uses VITE_API_URL and strips trailing slash', async () => {
    vi.stubEnv('VITE_API_URL', 'http://api.test/')
    const { API_BASE, apiUrl } = await import('../lib/api')
    expect(API_BASE).toBe('http://api.test')
    expect(apiUrl('api/gaps')).toBe('http://api.test/api/gaps')
  })
})
