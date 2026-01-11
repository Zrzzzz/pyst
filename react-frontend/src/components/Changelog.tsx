/**
 * 更新日志组件
 */
import React from 'react'
import { Drawer, Space, Tag } from '@arco-design/web-react'
import type { ChangelogItem } from '@/utils/api'
import './Changelog.scss'

interface ChangelogProps {
  visible: boolean
  onVisibleChange: (visible: boolean) => void
  changelog: ChangelogItem[]
}

export const Changelog: React.FC<ChangelogProps> = ({
  visible,
  onVisibleChange,
  changelog
}) => {
  return (
    <Drawer
      title="📝 更新日志"
      placement="right"
      onCancel={() => onVisibleChange(false)}
      visible={visible}
      width={400}
      closable={true}
    >
      <div className="changelog-content">
        {changelog.map((log) => (
          <div key={log.version} className="changelog-item">
            <div className="changelog-header">
              <Space size="small">
                <Tag color="blue">v{log.version}</Tag>
                <span className="date-badge">{log.date}</span>
              </Space>
            </div>
            <ul className="changelog-list">
              {log.changes.map((change, idx) => (
                <li key={idx} className="changelog-change">
                  {change}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </Drawer>
  )
}

export default Changelog

