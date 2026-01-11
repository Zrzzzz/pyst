/**
 * 信息提示框组件
 */
import React from 'react'
import { Alert } from '@arco-design/web-react'

interface InfoBoxProps {
  title?: string
  content?: string
}

export const InfoBox: React.FC<InfoBoxProps> = ({
  title = '偏离值',
  content = '偏离值 = 股票涨幅(%) - 指数涨幅(%) | 正值表示股票强于指数，负值表示股票弱于指数'
}) => {
  return (
    <Alert
      type="info"
      title={title}
      content={content}
      closable={false}
    />
  )
}

export default InfoBox

