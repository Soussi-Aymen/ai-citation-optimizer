/** Backend base URL — override with VITE_API_URL in .env or docker-compose */
export const API_BASE = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(
  /\/$/,
  '',
)

export const apiUrl = (path) => `${API_BASE}${path.startsWith('/') ? path : `/${path}`}`
