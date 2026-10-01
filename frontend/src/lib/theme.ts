export type ThemeName = 'light' | 'night'

const STORAGE_KEY = 'theme'

export function readTheme(): ThemeName {
  try {
    return localStorage.getItem(STORAGE_KEY) === 'night' ? 'night' : 'light'
  } catch {
    return 'light'
  }
}

export function applyTheme(theme: ThemeName): void {
  document.documentElement.classList.toggle('dark', theme === 'night')
  try {
    localStorage.setItem(STORAGE_KEY, theme)
  } catch {
    // Private mode can block storage. The class still applies for this visit.
  }
}

export function applyStoredTheme(): void {
  document.documentElement.classList.toggle('dark', readTheme() === 'night')
}
