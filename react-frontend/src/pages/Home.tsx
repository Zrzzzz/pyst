/**
 * 首页 - 股票异动监控
 */
import React, { useState, useEffect } from 'react'
import { Layout, Button, Card, Space, Alert, Tag, Divider } from '@arco-design/web-react'
import { useStockStore } from '@/stores/stockStore'
import StockTable from '@/components/StockTable'
import ThemeToggle from '@/components/ThemeToggle'
import Changelog from '@/components/Changelog'
import Watermark from '@/components/Watermark'
import './Home.scss'

const { Header, Content, Footer } = Layout

export const Home: React.FC = () => {
  const [showChangelog, setShowChangelog] = useState(false)
  const [showMergedStocks, setShowMergedStocks] = useState(false)
  const loading = useStockStore((state) => state.loading)
  const changelog = useStockStore((state) => state.changelog)
  const stocks10 = useStockStore((state) => state.stocks10)
  const stocks30 = useStockStore((state) => state.stocks30)
  const getMergedStocks = useStockStore((state) => state.getMergedStocks)

  // 计算排序后的数据
  const sortedStocks10 = React.useMemo(() => {
    return [...stocks10]
      .sort((a, b) => (b.deviation || 0) - (a.deviation || 0))
      .map((stock, index) => ({ ...stock, index: index + 1 }))
  }, [stocks10])

  const sortedStocks30 = React.useMemo(() => {
    return [...stocks30]
      .sort((a, b) => (b.deviation || 0) - (a.deviation || 0))
      .map((stock, index) => ({ ...stock, index: index + 1 }))
  }, [stocks30])

  const mergedStocks = React.useMemo(() => {
    return getMergedStocks()
  }, [stocks10, stocks30, getMergedStocks])

  useEffect(() => {
    const fetchData = async () => {
      console.log('开始获取数据...')
      try {
        await useStockStore.getState().fetchBothStocks()
        console.log('股票数据获取成功:', {
          stocks10: useStockStore.getState().stocks10.length,
          stocks30: useStockStore.getState().stocks30.length
        })
      } catch (err) {
        console.error('股票数据获取失败:', err)
      }

      try {
        await useStockStore.getState().fetchChangelog()
        console.log('更新日志获取成功:', useStockStore.getState().changelog.length)
      } catch (err) {
        console.error('更新日志获取失败:', err)
      }
    }

    fetchData()
  }, [])

  return (
    <Layout className="home-layout">
      {/* 页头 */}
      <Header className="home-header">
        <div className="header-container">
          <div className="header-left">
            <h1 className="header-title">股票异动监控</h1>
            <p className="header-subtitle">实时监控股票涨幅和偏离值</p>
          </div>
          <Space>
            <Button
              type={showMergedStocks ? 'secondary' : 'primary'}
              onClick={() => setShowMergedStocks(!showMergedStocks)}
            >
              {showMergedStocks ? '今天看什么' : '明天买什么'}
            </Button>
            <Button type="primary" onClick={() => setShowChangelog(true)}>
              📝 更新日志
            </Button>
          </Space>
        </div>
      </Header>

      {/* 主内容 */}
      <Content className="home-content">
        {showMergedStocks ? (
          <>
            {/* 合并榜单 - 明天买什么 */}
            <Alert
              type="info"
              title="明天买什么"
              content="综合10日和30日榜单，按可能涨幅排序，取两个榜单中可能涨幅的较小值"
              closable={false}
              style={{ marginBottom: '2rem' }}
            />

            <Card
              title={
                <Space>
                  <span>🚀 明天买什么 Top 30</span>
                  <Tag color="blue">{mergedStocks.length}</Tag>
                </Space>
              }
            >
              <StockTable
                stocks={mergedStocks}
                loading={loading}
                isMergedView={true}
              />
            </Card>
          </>
        ) : (
          <>
            {/* 原有的两个分离榜单 */}
            <Alert
              type="info"
              title="偏离值说明"
              content="偏离值 = 股票涨幅(%) - 指数涨幅(%) | 正值表示股票强于指数，负值表示股票弱于指数"
              closable={false}
              style={{ marginBottom: '2rem' }}
            />

            {/* 10日榜 */}
            <Card
              title={
                <Space>
                  <span>📊 10日偏离值榜 Top 50</span>
                  <Tag color="blue">{stocks10.length}</Tag>
                </Space>
              }
              style={{ marginBottom: '2rem' }}
            >
              <StockTable
                stocks={sortedStocks10}
                loading={loading}
                otherStocks={sortedStocks30}
              />
            </Card>

            <Divider />

            {/* 30日榜 */}
            <Card
              title={
                <Space>
                  <span>📈 30日偏离值榜 Top 50</span>
                  <Tag color="blue">{stocks30.length}</Tag>
                </Space>
              }
            >
              <StockTable
                stocks={sortedStocks30}
                loading={loading}
                otherStocks={sortedStocks10}
              />
            </Card>
          </>
        )}
      </Content>

      {/* 页脚 */}
      <Footer className="home-footer">
        <p>股票异动监控系统 | © 2024</p>
      </Footer>

      {/* 主题切换悬浮按钮 */}
      <ThemeToggle />

      {/* 水印 */}
      <Watermark text="小X爱股" />

      {/* 更新日志模态框 */}
      <Changelog
        visible={showChangelog}
        onVisibleChange={setShowChangelog}
        changelog={changelog}
      />
    </Layout>
  )
}

export default Home

