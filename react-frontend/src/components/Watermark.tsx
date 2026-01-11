/**
 * 水印组件
 */
import React from 'react'
import './Watermark.scss'

interface WatermarkProps {
  text?: string
}

export const Watermark: React.FC<WatermarkProps> = ({ text = '小X爱股' }) => {
  return (
    <div className="watermark-container">
      <div className="watermark-text">{text}</div>
    </div>
  )
}

export default Watermark

