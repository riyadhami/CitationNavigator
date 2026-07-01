import { useState, useEffect } from 'react'

export function useTheme() {
  const [isDark, setIsDark] = useState(
    () => localStorage.getItem('cn-theme') === 'dark'
  )

  useEffect(() => {
    document.documentElement.classList.toggle('dark', isDark)
    localStorage.setItem('cn-theme', isDark ? 'dark' : 'light')
  }, [isDark])

  return { isDark, toggleTheme: () => setIsDark(d => !d) }
}
