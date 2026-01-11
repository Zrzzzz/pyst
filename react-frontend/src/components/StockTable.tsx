/**
 * 股票表格组件
 */
import React, { useState, useMemo } from 'react'
import { Spin, Pagination, Empty, Tag } from '@arco-design/web-react'
import type { StockData } from '@/utils/api'
import TPlusCard from './TPlusCard'
import EditModal from './EditModal'
import './StockTable.scss'

interface StockTableProps {
  stocks?: StockData[]
  loading?: boolean
  otherStocks?: StockData[]
}

export const StockTable: React.FC<StockTableProps> = ({
  stocks = [],
  loading = false,
  otherStocks = []
}) => {
  const [currentPage, setCurrentPage] = useState(1)
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set())
  const [editModalVisible, setEditModalVisible] = useState(false)
  const [editData, setEditData] = useState({
    stock: null as StockData | null,
    day: 0,
    limitUpPct: 10,
    currentValue: 10
  })

  const pageSize = 30

  const paginatedStocks = useMemo(() => {
    const start = (currentPage - 1) * pageSize
    const end = start + pageSize
    return stocks.slice(start, end)
  }, [stocks, currentPage])

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
    // 这里返回模拟数据，实际应该从API获取
    return {
      lowestPrice: stock.low_price || 0,
      lowestDate: stock.low_date || '-',
      currentClose: stock.end_price || 0,
      changePercent: stock.price_change_pct || 0,
      dailyChange: 0,
      indexChangePercent: stock.index_change_pct || 0,
      deviation: stock.deviation || 0,
      isAbnormal: (stock.deviation || 0) > 5,
      possibleHighestPrice: (stock.end_price || 0) * 1.1,
      possibleChange: 10
    }
  }

  const handleEditTPlusDay = (stock: StockData, day: number) => {
    setEditData({
      stock,
      day,
      limitUpPct: stock.limit_up || 10,
      currentValue: stock.price_change_pct || 0
    })
    setEditModalVisible(true)
  }

  const handleSaveEdit = (value: number) => {
    console.log('保存编辑:', editData.stock?.ts_code, editData.day, value)
    setEditModalVisible(false)
  }

  return (
    <div className="stock-table-container">
      <Spin loading={loading} className="w-full">
        {stocks && stocks.length > 0 ? (
          <div className="stock-list">
            {paginatedStocks.map((stock, idx) => (
              <div key={stock.ts_code} className="stock-row">
                {/* 主行 */}
                <div className="stock-main-row" onClick={() => toggleExpand(idx)}>
                  <div className="stock-cell rank">{stock.index}</div>
                  <div className="stock-cell code">
                    <span className="font-semibold text-blue-600">{stock.ts_code}</span>
                  </div>
                  <div className="stock-cell name">
                    <span className="font-medium">{stock.name}</span>
                  </div>
                  <div className="stock-cell deviation">
                    <span className={getDeviationClass(stock.deviation)}>
                      {formatNumber(stock.deviation)}
                    </span>
                  </div>
                  <div className="stock-cell change">
                    <span className={getChangeClass(stock.price_change_pct)}>
                      {formatNumber(stock.price_change_pct)}%
                    </span>
                  </div>
                  <div className="stock-cell market">
                    <Tag color={getMarketColor(stock.market)}>
                      {stock.market || '-'}
                    </Tag>
                  </div>
                  <div className="stock-cell expand-btn">
                    <span className={`expand-toggle ${expandedRows.has(idx) ? 'expanded' : ''}`}>
                      {expandedRows.has(idx) ? '▲ 收起' : '▼ 展开'}
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

            {/* 分页 */}
            <div className="pagination-container">
              <Pagination
                current={currentPage}
                pageSize={pageSize}
                total={stocks.length}
                onChange={setCurrentPage}
                showTotal
              />
            </div>
          </div>
        ) : (
          <Empty description="暂无数据" />
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

