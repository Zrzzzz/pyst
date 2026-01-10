<template>
  <div class="t-plus-card">
    <div class="t-plus-title">
      <span>T+{{ day }}</span>
      <button class="edit-btn" @click="handleEdit">✏️ 修改</button>
    </div>

    <!-- 错误提示 -->
    <div v-if="data.error" class="error-message">
      {{ data.error }}
    </div>

    <!-- 正常数据显示 -->
    <template v-else>
      <!-- 基础数据组 -->
      <div class="data-section">
        <div class="section-label">基础数据</div>
        <div class="t-plus-item">
          <span class="t-plus-label">最低价:</span>
          <span class="t-plus-value">{{ formatNumber(data.lowestPrice) }}</span>
        </div>
        <div class="t-plus-item">
          <span class="t-plus-label">日期:</span>
          <span class="t-plus-value">{{ data.lowestDate }}</span>
        </div>
        <div class="t-plus-item">
          <span class="t-plus-label">当日价:</span>
          <span class="t-plus-value">{{ formatNumber(data.currentClose) }}</span>
        </div>
      </div>

      <!-- 涨幅数据组 -->
      <div class="data-section">
        <div class="section-label">涨幅数据</div>
        <div class="t-plus-item">
          <span class="t-plus-label">涨幅:</span>
          <span :class="['t-plus-value', getChangeClass(data.changePercent)]">
            {{ formatNumber(data.changePercent) }}%
          </span>
        </div>
        <div class="t-plus-item">
          <span class="t-plus-label">当日涨幅:</span>
          <span :class="['t-plus-value', getChangeClass(data.dailyChange)]">
            {{ formatNumber(data.dailyChange) }}%
          </span>
        </div>
        <div class="t-plus-item">
          <span class="t-plus-label">指数涨幅:</span>
          <span class="t-plus-value">{{ formatNumber(data.indexChangePercent) }}%</span>
        </div>
      </div>

      <!-- 偏离值和异动 -->
      <div class="data-section">
        <div class="section-label">偏离值</div>
        <div class="t-plus-item">
          <span class="t-plus-label">偏离值:</span>
          <span :class="['t-plus-value', getChangeClass(data.deviation)]">
            {{ formatNumber(data.deviation) }}%
          </span>
        </div>
        <div class="t-plus-item">
          <span class="t-plus-label">异动:</span>
          <span :class="['abnormal-badge', data.isAbnormal ? 'yes' : 'no']">
            {{ data.isAbnormal ? '是' : '否' }}
          </span>
        </div>
      </div>

      <!-- 预测数据组 -->
      <div class="data-section">
        <div class="section-label">预测数据</div>
        <div class="t-plus-item">
          <span class="t-plus-label">可能最高价:</span>
          <span class="t-plus-value">{{ formatNumber(data.possibleHighestPrice) }}</span>
        </div>
        <div class="t-plus-item">
          <span class="t-plus-label">可能涨幅:</span>
          <span :class="['t-plus-value', getChangeClass(data.possibleChange)]">
            {{ formatNumber(data.possibleChange) }}%
          </span>
        </div>
      </div>
    </template>

    <!-- 另一榜单异动信息 -->
    <div class="other-list-section">
      <div class="section-label">另一榜单</div>
      <template v-if="otherStockData">
        <div class="t-plus-item">
          <span class="t-plus-label">异动:</span>
          <span :class="['abnormal-badge', otherStockData.isAbnormal ? 'yes' : 'no']">
            {{ otherStockData.isAbnormal ? '是' : '否' }}
          </span>
        </div>
        <template v-if="otherStockData.isAbnormal">
          <div class="t-plus-item">
            <span class="t-plus-label">最高价:</span>
            <span class="t-plus-value">{{ formatNumber(otherStockData.possibleHighestPrice) }}</span>
          </div>
          <div class="t-plus-item">
            <span class="t-plus-label">可能涨幅:</span>
            <span :class="['t-plus-value', getChangeClass(otherStockData.possibleChange)]">
              {{ formatNumber(otherStockData.possibleChange) }}%
            </span>
          </div>
        </template>
      </template>
      <div v-else class="no-data-message">另一榜单无数据</div>
    </div>
  </div>
</template>

<script setup lang="ts">
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

interface Props {
  day: number
  data: TPlusDataFormat
  otherStock?: any // 另一榜单的股票数据
  otherDay?: number // 另一榜单的 T+n 天数
}

const props = defineProps<Props>()

const emit = defineEmits<{
  edit: []
}>()

// 获取另一榜单的 T+n 数据
import { computed } from 'vue'
const otherStockData = computed(() => {
  if (!props.otherStock || !props.otherDay) return null
  return props.otherStock.tPlusData?.[props.otherDay]
})

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

const handleEdit = () => {
  emit('edit')
}
</script>

<style scoped>
.t-plus-card {
  background: linear-gradient(135deg, rgba(248, 249, 250, 0.8) 0%, rgba(243, 244, 246, 0.8) 100%);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(41, 98, 255, 0.15);
  border-radius: 12px;
  padding: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-size: 0.875rem;
  position: relative;
  overflow: hidden;
}

/* 亮色模式 */
:global(html:not(.dark)) .t-plus-card {
  background: linear-gradient(135deg, rgba(248, 249, 250, 0.9) 0%, rgba(243, 244, 246, 0.9) 100%);
  border: 1px solid rgba(41, 98, 255, 0.15);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

/* 深色模式 */
:global(html.dark) .t-plus-card {
  background: linear-gradient(135deg, rgba(21, 26, 33, 0.7) 0%, rgba(15, 23, 42, 0.7) 100%);
  border: 1px solid rgba(41, 98, 255, 0.15);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.t-plus-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

:global(.dark) .t-plus-card::before {
  background: linear-gradient(90deg, #818cf8 0%, #c084fc 100%);
}

.t-plus-card:hover {
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
  transform: translateY(-4px) scale(1.02);
  border-color: rgba(102, 126, 234, 0.3);
}

:global(.dark) .t-plus-card:hover {
  box-shadow: 0 8px 24px rgba(129, 140, 248, 0.2);
  border-color: rgba(129, 140, 248, 0.3);
}

.t-plus-card:hover::before {
  opacity: 1;
}

.t-plus-title {
  font-weight: 700;
  color: #2962FF;
  margin-bottom: 0.75rem;
  font-size: 1.125rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  letter-spacing: -0.01em;
}

:global(.dark) .t-plus-title {
  color: #2962FF;
}

/* 数据分组 */
.data-section {
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(102, 126, 234, 0.1);
}

.data-section:last-of-type {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

:global(.dark) .data-section {
  border-bottom-color: rgba(129, 140, 248, 0.1);
}

.section-label {
  font-size: 0.7rem;
  font-weight: 700;
  color: #667eea;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 0.5rem;
  padding-left: 0.25rem;
}

:global(.dark) .section-label {
  color: #818cf8;
}

.t-plus-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 0.375rem 0;
  font-size: 0.875rem;
  padding: 0.25rem 0;
  transition: all 0.2s ease;
}

.t-plus-item:hover {
  padding-left: 0.25rem;
}

.t-plus-label {
  color: #6B7280;
  font-weight: 500;
  min-width: 85px;
  flex-shrink: 0;
}

/* 亮色模式 */
:global(html:not(.dark)) .t-plus-label {
  color: #6B7280;
}

/* 深色模式 */
:global(html.dark) .t-plus-label {
  color: #94a3b8;
}

.t-plus-value {
  font-weight: 700;
  text-align: right;
  font-family: 'Monaco', 'Courier New', monospace;
  color: #1F2937;
}

/* 亮色模式 */
:global(html:not(.dark)) .t-plus-value {
  color: #1F2937;
}

/* 深色模式 */
:global(html.dark) .t-plus-value {
  color: #f1f5f9;
}

.t-plus-value.positive {
  color: #dc2626;
  text-shadow: 0 0 10px rgba(220, 38, 38, 0.2);
}

:global(.dark) .t-plus-value.positive {
  color: #f87171;
  text-shadow: 0 0 10px rgba(248, 113, 113, 0.3);
}

.t-plus-value.negative {
  color: #16a34a;
  text-shadow: 0 0 10px rgba(22, 163, 74, 0.2);
}

:global(.dark) .t-plus-value.negative {
  color: #4ade80;
  text-shadow: 0 0 10px rgba(74, 222, 128, 0.3);
}

.abnormal-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  transition: all 0.2s ease;
}

/* 亮色模式 */
:global(html:not(.dark)) .abnormal-badge.yes {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  color: #dc2626;
  box-shadow: 0 2px 4px rgba(220, 38, 38, 0.2);
}

/* 深色模式 */
:global(html.dark) .abnormal-badge.yes {
  background: linear-gradient(135deg, rgba(220, 38, 38, 0.2) 0%, rgba(220, 38, 38, 0.3) 100%);
  color: #f87171;
}

/* 亮色模式 */
:global(html:not(.dark)) .abnormal-badge.no {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #059669;
  box-shadow: 0 2px 4px rgba(5, 150, 105, 0.2);
}

/* 深色模式 */
:global(html.dark) .abnormal-badge.no {
  background: linear-gradient(135deg, rgba(5, 150, 105, 0.2) 0%, rgba(5, 150, 105, 0.3) 100%);
  color: #4ade80;
}

.edit-btn {
  background: rgba(41, 98, 255, 0.2);
  border: 1px solid rgba(41, 98, 255, 0.3);
  color: #2962FF;
  cursor: pointer;
  font-size: 0.75rem;
  padding: 0.375rem 0.625rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 6px;
  white-space: nowrap;
  font-weight: 600;
  box-shadow: 0 2px 4px rgba(41, 98, 255, 0.1);
}

:global(.dark) .edit-btn {
  background: rgba(41, 98, 255, 0.2);
  border: 1px solid rgba(41, 98, 255, 0.3);
  color: #2962FF;
}

.edit-btn:hover {
  background: rgba(41, 98, 255, 0.3);
  border-color: rgba(41, 98, 255, 0.5);
  box-shadow: 0 4px 8px rgba(41, 98, 255, 0.2);
}

:global(.dark) .edit-btn:hover {
  background: rgba(41, 98, 255, 0.3);
  border-color: rgba(41, 98, 255, 0.5);
  box-shadow: 0 4px 8px rgba(41, 98, 255, 0.2);
}

.edit-btn:active {
  transform: scale(0.95);
}

.metrics-divider {
  margin: 0.75rem 0;
  padding: 0.75rem 0;
  border-top: 1px solid rgba(229, 231, 235, 0.5);
  position: relative;
}

:global(.dark) .metrics-divider {
  border-top: 1px solid rgba(51, 65, 85, 0.5);
}

.metrics-divider::before {
  content: '';
  position: absolute;
  top: -1px;
  left: 0;
  width: 30%;
  height: 1px;
  background: linear-gradient(90deg, #667eea 0%, transparent 100%);
}

:global(.dark) .metrics-divider::before {
  background: linear-gradient(90deg, #818cf8 0%, transparent 100%);
}

.error-message {
  padding: 0.75rem;
  background: linear-gradient(135deg, rgba(220, 38, 38, 0.1) 0%, rgba(220, 38, 38, 0.05) 100%);
  border: 1px solid rgba(220, 38, 38, 0.3);
  border-radius: 8px;
  color: #dc2626;
  font-size: 0.875rem;
  font-weight: 500;
  text-align: center;
  margin-bottom: 0.5rem;
}

:global(.dark) .error-message {
  background: linear-gradient(135deg, rgba(220, 38, 38, 0.15) 0%, rgba(220, 38, 38, 0.08) 100%);
  border-color: rgba(220, 38, 38, 0.4);
  color: #f87171;
}

.other-list-section {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 2px solid rgba(102, 126, 234, 0.15);
}

:global(.dark) .other-list-section {
  border-top-color: rgba(129, 140, 248, 0.15);
}

.no-data-message {
  padding: 0.75rem;
  text-align: center;
  color: #cbd5e1;
  font-size: 0.8125rem;
  background: linear-gradient(135deg, rgba(148, 163, 184, 0.05) 0%, rgba(148, 163, 184, 0.02) 100%);
  border-radius: 6px;
  border: 1px solid rgba(148, 163, 184, 0.15);
  font-weight: 500;
  letter-spacing: 0.02em;
}

:global(.dark) .no-data-message {
  color: #94a3b8;
  background: linear-gradient(135deg, rgba(148, 163, 184, 0.08) 0%, rgba(148, 163, 184, 0.03) 100%);
  border-color: rgba(148, 163, 184, 0.2);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .t-plus-card {
    padding: 0.875rem;
  }

  .t-plus-title {
    font-size: 1rem;
  }

  .t-plus-item {
    font-size: 0.8125rem;
    margin: 0.3rem 0;
  }

  .t-plus-label {
    min-width: 75px;
  }

  .section-label {
    font-size: 0.65rem;
    margin-bottom: 0.375rem;
  }

  .data-section {
    margin-bottom: 0.75rem;
    padding-bottom: 0.75rem;
  }
}
</style>

