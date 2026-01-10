import { ref, onMounted } from 'vue'

const isDark = ref(true)

export function useTheme() {
  // 检查是否在浏览器环境
  const isBrowser = typeof window !== 'undefined'

  // 初始化主题
  const initTheme = () => {
    if (!isBrowser) return

    // 从 localStorage 读取用户偏好
    const savedTheme = localStorage.getItem('theme')
    if (savedTheme) {
      isDark.value = savedTheme === 'dark'
    } else {
      // 检测系统主题偏好
      isDark.value = window.matchMedia('(prefers-color-scheme: dark)').matches
    }
    applyTheme()
  }

  // 应用主题
  const applyTheme = () => {
    if (!isBrowser) return

    if (isDark.value) {
      // 自定义深色主题
      document.documentElement.classList.add('dark')
      // Arco Design 暗黑模式
      document.body.setAttribute('arco-theme', 'dark')
    } else {
      // 亮色主题
      document.documentElement.classList.remove('dark')
      // Arco Design 亮色模式
      document.body.removeAttribute('arco-theme')
    }
  }

  // 切换主题
  const toggleTheme = () => {
    if (!isBrowser) return

    isDark.value = !isDark.value
    localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
    applyTheme()
  }

  // 监听系统主题变化
  onMounted(() => {
    if (!isBrowser) return

    initTheme()

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    const handleChange = (e: MediaQueryListEvent) => {
      if (!localStorage.getItem('theme')) {
        isDark.value = e.matches
        applyTheme()
      }
    }

    mediaQuery.addEventListener('change', handleChange)
  })

  return {
    isDark,
    toggleTheme,
    initTheme
  }
}

