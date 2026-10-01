import { beforeEach, describe, expect, it } from 'vitest'
import { applyStoredTheme, applyTheme, readTheme } from './theme'

describe('theme', () => {
  beforeEach(() => {
    localStorage.clear()
    document.documentElement.classList.remove('dark')
  })

  it('stays white until night is chosen', () => {
    applyStoredTheme()
    expect(readTheme()).toBe('light')
    expect(document.documentElement.classList.contains('dark')).toBe(false)
  })

  it('sets the night class and remembers the choice', () => {
    applyTheme('night')
    expect(document.documentElement.classList.contains('dark')).toBe(true)
    expect(localStorage.getItem('theme')).toBe('night')
  })

  it('removes the night class when white is chosen again', () => {
    applyTheme('night')
    applyTheme('light')
    expect(document.documentElement.classList.contains('dark')).toBe(false)
    expect(readTheme()).toBe('light')
  })

  it('restores a saved night choice', () => {
    localStorage.setItem('theme', 'night')
    applyStoredTheme()
    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })
})
