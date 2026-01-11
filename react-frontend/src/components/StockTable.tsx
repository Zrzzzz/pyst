/**
 * 股票表格组件
 */
import React, { useState } from 'react'
import { Spin } from '@arco-design/web-react'
import type { StockData } from '@/utils/api'
import TPlusCard from './TPlusCard'
import EditModal from './EditModal'
import { calculateTPlusData } from '@/utils/tplusCalculation'
import { useStockStore } from '@/stores/stockStore'
import './StockTable.scss'

interface StockTableProps {
  stocks?: StockData[]
  loading?: boolean
  otherStocks?: StockData[]
  isMergedView?: boolean
}

export const StockTable: React.FC<StockTableProps> = ({
  stocks = [],
  loading = false,
  otherStocks = [],
  isMergedView = false
}) => {
  const updateStockExtraPercent = useStockStore((state) => state.updateStockExtraPercent)
  const stocks10 = useStockStore((state) => state.stocks10)
  const stocks30 = useStockStore((state) => state.stocks30)
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set())
  const [editModalVisible, setEditModalVisible] = useState(false)
  const [editData, setEditData] = useState({
    stock: null as StockData | null,
    day: 0,
    limitUpPct: 10,
    currentValue: 10
  })

  // 调试：监听 stocks 变化
  React.useEffect(() => {
    console.log('StockTable stocks 更新:', stocks.length)
  }, [stocks])

  const toggleExpand = (idx: number) => {
    const newSet = new Set(expandedRows)
    if (newSet.has(idx)) {
      newSet.delete(idx)
    } else {
      newSet.add(idx)
    }
    setExpandedRows(newSet)
  }

  const formatNumber = (num: number | undefined): string => {
    if (num === undefined || num === null) return '-'
    return num.toFixed(2)
  }

  const getDeviationClass = (deviation: number | undefined) => {
    if (!deviation) return ''
    if (deviation > 0) return 'positive'
    if (deviation < 0) return 'negative'
    return ''
  }

  const getChangeClass = (change: number | undefined) => {
    if (!change) return ''
    if (change > 0) return 'positive'
    if (change < 0) return 'negative'
    return ''
  }

  const getMarketColor = (market: string | undefined) => {
    if (!market) return 'blue'
    if (market.includes('沪')) return 'red'
    if (market.includes('深')) return 'green'
    return 'blue'
  }

  const getTPlusData = (stock: StockData, day: number) => {
    // 优先使用已经计算好的 tPlusData，如果没有则实时计算
    if (stock.tPlusData && stock.tPlusData[day]) {
      return stock.tPlusData[day]
    }
    return calculateTPlusData(stock, day)
  }

  const getStockSource = (stock: StockData): string => {
    // 判断股票来自哪个榜单
    const inStocks10 = stocks10.some(s => s.ts_code === stock.ts_code)
    const inStocks30 = stocks30.some(s => s.ts_code === stock.ts_code)

    if (inStocks10 && inStocks30) {
      return '10/30'
    } else if (inStocks10) {
      return '10'
    } else if (inStocks30) {
      return '30'
    }
    return '-'
  }

  const handleEditTPlusDay = (stock: StockData, day: number) => {
    // 获取当日涨幅作为默认值
    const tPlusData = getTPlusData(stock, day)
    const defaultValue = tPlusData.dailyChange || (stock.limit_up || 10)

    setEditData({
      stock,
      day,
      limitUpPct: stock.limit_up || 10,
      currentValue: defaultValue
    })
    setEditModalVisible(true)
  }

  const handleSaveEdit = (value: number) => {
    const stock = editData.stock
    const day = editData.day

    if (!stock) return

    // 通过 store 更新数据，会自动更新两个榜单中的对应股票
    updateStockExtraPercent(stock.ts_code, day, value)

    console.log('保存修改:', stock.ts_code, `T+${day}`, value)
    setEditModalVisible(false)
  }

  return (
    <div className="stock-table-container">
      <Spin loading={loading} className="w-full">
        {stocks && stocks.length > 0 ? (
          <div className="stock-list">
            {/* 表头 */}
            <div className="stock-header-row">
              <div className="stock-cell rank">排名</div>
              <div className="stock-cell code font-bold">股票代码</div>
              <div className="stock-cell name">股票名称</div>
              <div className="stock-cell price">现价</div>
              <div className="stock-cell low-price">最低价</div>
              <div className="stock-cell cumulative">累计涨幅</div>
              <div className="stock-cell index-change">指数涨幅</div>
              <div className="stock-cell deviation-10">10日偏离</div>
              <div className="stock-cell deviation-t">
                {isMergedView ? '可能涨幅' : 'T+1/T+2偏离'}
              </div>
              <div className="stock-cell expand-btn">详情</div>
            </div>

            {stocks.map((stock, idx) => (
              <div key={stock.ts_code} className="stock-row">
                {/* 主行 */}
                <div className="stock-main-row" onClick={() => toggleExpand(idx)}>
                  <div className="stock-cell rank">{stock.index}</div>
                  <div className="stock-cell code">
                    <span className="font-semibold text-blue-600">{stock.ts_code}</span>
                    {isMergedView && (
                      <span className="stock-source-badge">{getStockSource(stock)}</span>
                    )}
                  </div>
                  <div className="stock-cell name">
                    <span className="font-medium">{stock.name}</span>
                  </div>
                  <div className="stock-cell price">
                    <span>{formatNumber(stock.end_price)}</span>
                  </div>
                  <div className="stock-cell low-price">
                    <span>{formatNumber(stock.low_price)}</span>
                  </div>
                  <div className="stock-cell cumulative">
                    <span className={getChangeClass(stock.price_change_pct)}>
                      {formatNumber(stock.price_change_pct)}%
                    </span>
                  </div>
                  <div className="stock-cell index-change">
                    <span className={getChangeClass(stock.index_change_pct)}>
                      {formatNumber(stock.index_change_pct)}%
                    </span>
                  </div>
                  <div className="stock-cell deviation-10">
                    <span className={getDeviationClass(stock.deviation)}>
                      {formatNumber(stock.deviation)}
                    </span>
                  </div>
                  <div className="stock-cell deviation-t">
                    {isMergedView ? (
                      // 合并视图：显示可能涨幅
                      <span className={getChangeClass((stock as StockData & { mergedPossibleChange?: number }).mergedPossibleChange)}>
                        {formatNumber((stock as StockData & { mergedPossibleChange?: number }).mergedPossibleChange)}%
                      </span>
                    ) : (
                      // 原有视图：显示 T+1/T+2 偏离
                      stock.tPlusData?.[1] && stock.tPlusData?.[2] ? (
                        <div className="t-plus-two-container">
                          <div className="t-plus-two-item">
                            <span className="t-plus-two-label">T+1:</span>
                            <span className="t-plus-two-value">
                              {formatNumber(stock.tPlusData[1].deviation)}%
                            </span>
                            <span className={`t-plus-two-badge ${stock.tPlusData[1].isAbnormal ? 'abnormal' : 'normal'}`}>
                              {stock.tPlusData[1].isAbnormal ? '✓' : '✗'}
                            </span>
                          </div>
                          <div className="t-plus-two-item">
                            <span className="t-plus-two-label">T+2:</span>
                            <span className="t-plus-two-value">
                              {formatNumber(stock.tPlusData[2].deviation)}%
                            </span>
                            <span className={`t-plus-two-badge ${stock.tPlusData[2].isAbnormal ? 'abnormal' : 'normal'}`}>
                              {stock.tPlusData[2].isAbnormal ? '✓' : '✗'}
                            </span>
                          </div>
                        </div>
                      ) : (
                        <span>-</span>
                      )
                    )}
                  </div>
                  <div className="stock-cell expand-btn">
                    <span className={`expand-toggle ${expandedRows.has(idx) ? 'expanded' : ''}`}>
                      {expandedRows.has(idx) ? '▲' : '▼'}
                    </span>
                  </div>
                </div>

                {/* 详情行 */}
                {expandedRows.has(idx) && (
                  <div className="stock-detail-row">
                    <div className="detail-content">
                      <h4 className="detail-title">T+i 偏离值数据</h4>
                      <div className="t-plus-grid">
                        {[1, 2, 3, 4, 5].map((day) => (
                          <TPlusCard
                            key={day}
                            day={day}
                            data={getTPlusData(stock, day)}
                            otherStock={otherStocks.find((s) => s.ts_code === stock.ts_code)}
                            otherDay={day}
                            onEdit={() => handleEditTPlusDay(stock, day)}
                          />
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state-compact">
            <div className="empty-icon">📊</div>
            <div className="empty-text">暂无数据</div>
          </div>
        )}
      </Spin>

      {/* 编辑模态框 */}
      <EditModal
        visible={editModalVisible}
        onVisibleChange={setEditModalVisible}
        limitUpPct={editData.limitUpPct}
        currentValue={editData.currentValue}
        onSave={handleSaveEdit}
      />
    </div>
  )
}

export default StockTable

