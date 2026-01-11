/**
 * 首页 - 股票异动监控
 */
import React, { useState, useEffect } from 'react'
import { Button } from '@arco-design/web-react'
import { useStockStore } from '@/stores/stockStore'
import StockTable from '@/components/StockTable'
import InfoBox from '@/components/InfoBox'
import ThemeToggle from '@/components/ThemeToggle'
import Changelog from '@/components/Changelog'
import './Home.scss'

export const Home: React.FC = () => {
  const [showChangelog, setShowChangelog] = useState(false)
  const stockStore = useStockStore()

  useEffect(() => {
    stockStore.fetchBothStocks()
  }, [])

  return (
    <div className="home-page">
      {/* 页头 */}
      <div className="page-header">
        <div className="header-content">
          <div className="header-text">
            <h1 className="page-title">股票异动监控</h1>
            <p className="page-subtitle">实时监控股票涨幅和偏离值</p>
          </div>
          <div className="header-actions">
            <Button type="text" onClick={() => setShowChangelog(true)} className="changelog-btn">
              📝 更新日志
            </Button>
          </div>
        </div>
      </div>

      {/* 偏离值说明 */}
      <InfoBox
        title="偏离值"
        content="偏离值 = 股票涨幅(%) - 指数涨幅(%) | 正值表示股票强于指数，负值表示股票弱于指数"
      />

      {/* 10日榜 */}
      <div className="section">
        <div className="section-header">
          <h2 className="section-title">📊 10日偏离值榜 Top 30</h2>
          <span className="count-badge">{stockStore.count10}</span>
        </div>

        <StockTable
          stocks={stockStore.sortedStocks10}
          loading={stockStore.loading}
          otherStocks={stockStore.sortedStocks30}
        />
      </div>

      {/* 分割线 */}
      <hr className="divider" />

      {/* 30日榜 */}
      <div className="section">
        <div className="section-header">
          <h2 className="section-title">📈 30日偏离值榜 Top 30</h2>
          <span className="count-badge">{stockStore.count30}</span>
        </div>

        <StockTable
          stocks={stockStore.sortedStocks30}
          loading={stockStore.loading}
          otherStocks={stockStore.sortedStocks10}
        />
      </div>

      {/* 页脚 */}
      <div className="page-footer">
        <p className="text-gray-600">股票异动监控系统 | © 2024</p>
      </div>

      {/* 主题切换悬浮按钮 */}
      <ThemeToggle />

      {/* 更新日志抽屉 */}
      <Changelog
        visible={showChangelog}
        onVisibleChange={setShowChangelog}
        changelog={stockStore.changelog}
      />
    </div>
  )
}

export default Home

