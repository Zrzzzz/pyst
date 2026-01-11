/**
 * 编辑模态框组件
 */
import React, { useState, useEffect } from 'react'
import { Modal, Form, InputNumber } from '@arco-design/web-react'
import './EditModal.scss'

interface EditModalProps {
  visible: boolean
  onVisibleChange: (visible: boolean) => void
  limitUpPct?: number
  currentValue?: number
  onSave: (value: number) => void
}

export const EditModal: React.FC<EditModalProps> = ({
  visible,
  onVisibleChange,
  limitUpPct = 10,
  currentValue = 10,
  onSave
}) => {
  const [form] = Form.useForm()
  const [value, setValue] = useState(currentValue)

  useEffect(() => {
    setValue(currentValue)
    form.setFieldValue('value', currentValue)
  }, [currentValue, form])

  const handleSave = () => {
    if (value === undefined || value === null) {
      return
    }
    if (value < -limitUpPct || value > limitUpPct) {
      return
    }
    onSave(value)
    onVisibleChange(false)
  }

  const handleCancel = () => {
    onVisibleChange(false)
  }

  const formatNumber = (num: number): string => {
    return parseFloat(num.toFixed(2)).toString()
  }

  return (
    <Modal
      title="修改涨幅"
      visible={visible}
      onOk={handleSave}
      onCancel={handleCancel}
      width={400}
    >
      <Form form={form} layout="vertical">
        <Form.Item label="修改涨幅 (%)" required>
          <InputNumber
            value={value}
            onChange={(val) => setValue(val || 0)}
            step={0.01}
            min={-limitUpPct}
            max={limitUpPct}
            placeholder="输入涨幅百分比"
          />
        </Form.Item>
        <Form.Item>
          <div className="form-hint">
            范围: {formatNumber(-limitUpPct)}% ~ {formatNumber(limitUpPct)}%
          </div>
        </Form.Item>
      </Form>
    </Modal>
  )
}

export default EditModal

