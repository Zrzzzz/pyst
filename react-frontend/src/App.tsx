/**
 * 主应用组件
 */
import React, { useMemo } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { ConfigProvider } from '@arco-design/web-react'
import { useTheme } from '@/hooks/useTheme'
import Home from '@/pages/Home'
import Info from '@/pages/Info'
import '@/styles/main.scss'

function App() {
  const { isDark } = useTheme()

  // Arco Design 主题配置
  const themeConfig = useMemo(
    () => ({
      token: {
        colorBgBase: isDark ? '#0B0E11' : '#FFFFFF',
        colorTextBase: isDark ? '#EAECEF' : '#1F2937',
        colorPrimary: '#2962FF',
        colorSuccess: isDark ? '#2EBD85' : '#059669',
        colorWarning: isDark ? '#F6A500' : '#F59E0B',
        colorError: isDark ? '#F6465D' : '#DC2626',
        colorInfo: '#2962FF',
        colorBorder: isDark ? 'rgba(41, 98, 255, 0.15)' : 'rgba(41, 98, 255, 0.2)',
        colorBgContainer: isDark ? '#151A21' : '#F8F9FA',
        colorBgElevated: isDark ? '#1F2937' : '#FFFFFF',
        colorBgLayout: isDark ? '#0B0E11' : '#FFFFFF'
      }
    }),
    [isDark]
  )

  return (
    <ConfigProvider theme={themeConfig}>
      <Router>
        <div className="app-container">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/info" element={<Info />} />
          </Routes>
        </div>
      </Router>
    </ConfigProvider>
  )
}

export default App
