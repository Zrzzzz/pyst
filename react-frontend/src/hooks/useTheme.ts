/**
 * 主题管理 Hook
 */
import { useState, useEffect } from 'react'

export function useTheme() {
  const [isDark, setIsDark] = useState(false)

  // 初始化主题
  const initTheme = () => {
    // 从 localStorage 读取用户偏好
    const savedTheme = localStorage.getItem('theme')
    if (savedTheme) {
      setIsDark(savedTheme === 'dark')
      applyTheme(savedTheme === 'dark')
    } else {
      // 检测系统主题偏好
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      setIsDark(prefersDark)
      applyTheme(prefersDark)
    }
  }

  // 应用主题
  const applyTheme = (dark: boolean) => {
    if (dark) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  // 切换主题
  const toggleTheme = () => {
    const newDark = !isDark
    setIsDark(newDark)
    localStorage.setItem('theme', newDark ? 'dark' : 'light')
    applyTheme(newDark)
  }

  // 初始化和监听系统主题变化
  useEffect(() => {
    initTheme()

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    const handleChange = (e: MediaQueryListEvent) => {
      if (!localStorage.getItem('theme')) {
        setIsDark(e.matches)
        applyTheme(e.matches)
      }
    }

    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [])

  return {
    isDark,
    toggleTheme,
    initTheme
  }
}

