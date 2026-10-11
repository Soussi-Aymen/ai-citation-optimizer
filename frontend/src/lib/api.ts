import { z } from 'zod'

/** Backend base URL — override with VITE_API_URL in .env or docker-compose */
export const API_BASE = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '')

export function apiUrl(path: string): string {
  return `${API_BASE}${path.startsWith('/') ? path : `/${path}`}`
}

export const healthResponseSchema = z.object({
  peec_available: z.boolean(),
})

export type HealthResponse = z.infer<typeof healthResponseSchema>
