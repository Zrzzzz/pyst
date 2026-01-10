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

    const htmlElement = document.documentElement
    const bodyElement = document.body

    if (isDark.value) {
      // 深色主题
      htmlElement.classList.add('dark')
      bodyElement.setAttribute('arco-theme', 'dark')
      // 移除亮色主题类
      htmlElement.classList.remove('light')
    } else {
      // 亮色主题
      htmlElement.classList.remove('dark')
      htmlElement.classList.add('light')
      // 移除 Arco Design 暗黑模式
      bodyElement.removeAttribute('arco-theme')
    }

    // 触发自定义事件，通知其他组件主题已改变
    window.dispatchEvent(new CustomEvent('theme-change', { detail: { isDark: isDark.value } }))
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

