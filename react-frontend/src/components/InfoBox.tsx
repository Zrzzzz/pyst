/**
 * 信息提示框组件
 */
import React from 'react'
import './InfoBox.scss'

interface InfoBoxProps {
  title?: string
  content?: string
}

export const InfoBox: React.FC<InfoBoxProps> = ({
  title = '偏离值',
  content = '偏离值 = 股票涨幅(%) - 指数涨幅(%) | 正值表示股票强于指数，负值表示股票弱于指数'
}) => {
  return (
    <div className="info-box">
      <div className="info-box-content">
        <span className="info-icon">💡</span>
        <div className="info-text">
          <strong>{title}</strong>
          <p>{content}</p>
        </div>
      </div>
    </div>
  )
}

export default InfoBox

