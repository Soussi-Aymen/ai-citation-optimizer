import type { KeyboardEvent } from 'react'

/** Roving focus for WAI-ARIA tablist pattern (Arrow/Home/End keys). */
export function handleTabListKeyDown<T extends string>(
  e: KeyboardEvent<HTMLButtonElement>,
  tabs: readonly T[],
  activeTab: T,
  setActiveTab: (tab: T) => void,
  tabIdPrefix: string,
) {
  const idx = tabs.indexOf(activeTab)
  if (idx === -1) return

  const focusTab = (tab: T) => {
    setActiveTab(tab)
    document.getElementById(`${tabIdPrefix}${tab}`)?.focus()
  }

  switch (e.key) {
    case 'ArrowRight':
    case 'ArrowDown':
      e.preventDefault()
      focusTab(tabs[(idx + 1) % tabs.length]!)
      break
    case 'ArrowLeft':
    case 'ArrowUp':
      e.preventDefault()
      focusTab(tabs[(idx - 1 + tabs.length) % tabs.length]!)
      break
    case 'Home':
      e.preventDefault()
      focusTab(tabs[0]!)
      break
    case 'End':
      e.preventDefault()
      focusTab(tabs[tabs.length - 1]!)
      break
  }
}
