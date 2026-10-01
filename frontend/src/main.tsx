import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { applyStoredTheme } from './lib/theme'
import './index.css'
import App from './App'

applyStoredTheme()

const root = document.getElementById('root')
if (!root) {
  throw new Error('Root element #root not found')
}

createRoot(root).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
