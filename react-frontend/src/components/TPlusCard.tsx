/**
 * T+n 数据卡片组件
 */
import React from 'react'
import './TPlusCard.scss'

interface TPlusDataFormat {
  lowestPrice: number
  lowestDate: string
  currentClose: number
  changePercent: number
  dailyChange: number
  indexChangePercent: number
  deviation: number
  isAbnormal: boolean
  possibleHighestPrice: number
  possibleChange: number
  error?: string
}

interface TPlusCardProps {
  day: number
  data: TPlusDataFormat
  otherStock?: any
  otherDay?: number
  onEdit: () => void
}

export const TPlusCard: React.FC<TPlusCardProps> = ({
  day,
  data,
  otherStock,
  otherDay,
  onEdit
}) => {
  const formatNumber = (num: number | undefined): string => {
    if (num === undefined || num === null) return '-'
    return num.toFixed(2)
  }

  const getChangeClass = (change: number | undefined) => {
    if (!change) return ''
    if (change > 0) return 'positive'
    if (change < 0) return 'negative'
    return ''
  }

  const otherStockData = otherStock && otherDay ? otherStock.tPlusData?.[otherDay] : null

  return (
    <div className="t-plus-card">
      <div className="t-plus-title">
        <span>T+{day}</span>
        <button className="edit-btn" onClick={onEdit}>
          ✏️ 修改
        </button>
      </div>

      {data.error ? (
        <div className="error-message">{data.error}</div>
      ) : (
        <>
          {/* 基础数据组 */}
          <div className="data-section">
            <div className="section-label">基础数据</div>
            <div className="t-plus-item">
              <span className="t-plus-label">最低价:</span>
              <span className="t-plus-value">{formatNumber(data.lowestPrice)}</span>
            </div>
            <div className="t-plus-item">
              <span className="t-plus-label">日期:</span>
              <span className="t-plus-value">{data.lowestDate}</span>
            </div>
            <div className="t-plus-item">
              <span className="t-plus-label">当日价:</span>
              <span className="t-plus-value">{formatNumber(data.currentClose)}</span>
            </div>
          </div>

          {/* 涨幅数据组 */}
          <div className="data-section">
            <div className="section-label">涨幅数据</div>
            <div className="t-plus-item">
              <span className="t-plus-label">涨幅:</span>
              <span className={`t-plus-value ${getChangeClass(data.changePercent)}`}>
                {formatNumber(data.changePercent)}%
              </span>
            </div>
            <div className="t-plus-item">
              <span className="t-plus-label">当日涨幅:</span>
              <span className={`t-plus-value ${getChangeClass(data.dailyChange)}`}>
                {formatNumber(data.dailyChange)}%
              </span>
            </div>
            <div className="t-plus-item">
              <span className="t-plus-label">指数涨幅:</span>
              <span className="t-plus-value">{formatNumber(data.indexChangePercent)}%</span>
            </div>
          </div>

          {/* 偏离值和异动 */}
          <div className="data-section">
            <div className="section-label">偏离值</div>
            <div className="t-plus-item">
              <span className="t-plus-label">偏离值:</span>
              <span className={`t-plus-value ${getChangeClass(data.deviation)}`}>
                {formatNumber(data.deviation)}%
              </span>
            </div>
            <div className="t-plus-item">
              <span className="t-plus-label">异动:</span>
              <span className={`abnormal-badge ${data.isAbnormal ? 'yes' : 'no'}`}>
                {data.isAbnormal ? '是' : '否'}
              </span>
            </div>
          </div>

          {/* 预测数据组 */}
          <div className="data-section">
            <div className="section-label">预测数据</div>
            <div className="t-plus-item">
              <span className="t-plus-label">可能最高价:</span>
              <span className="t-plus-value">{formatNumber(data.possibleHighestPrice)}</span>
            </div>
            <div className="t-plus-item">
              <span className="t-plus-label">可能涨幅:</span>
              <span className={`t-plus-value ${getChangeClass(data.possibleChange)}`}>
                {formatNumber(data.possibleChange)}%
              </span>
            </div>
          </div>
        </>
      )}

      {/* 另一榜单异动信息 */}
      <div className="other-list-section">
        <div className="section-label">另一榜单</div>
        {otherStockData ? (
          <>
            <div className="t-plus-item">
              <span className="t-plus-label">异动:</span>
              <span className={`abnormal-badge ${otherStockData.isAbnormal ? 'yes' : 'no'}`}>
                {otherStockData.isAbnormal ? '是' : '否'}
              </span>
            </div>
            {otherStockData.isAbnormal && (
              <>
                <div className="t-plus-item">
                  <span className="t-plus-label">最高价:</span>
                  <span className="t-plus-value">
                    {formatNumber(otherStockData.possibleHighestPrice)}
                  </span>
                </div>
                <div className="t-plus-item">
                  <span className="t-plus-label">可能涨幅:</span>
                  <span className={`t-plus-value ${getChangeClass(otherStockData.possibleChange)}`}>
                    {formatNumber(otherStockData.possibleChange)}%
                  </span>
                </div>
              </>
            )}
          </>
        ) : (
          <div className="no-data-message">另一榜单无数据</div>
        )}
      </div>
    </div>
  )
}

export default TPlusCard

