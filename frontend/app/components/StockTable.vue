<template>
  <div class="stock-table-container">
    <a-spin :loading="loading" class="w-full spin-wrapper">
      <template #icon>
        <div class="custom-spinner">
          <div class="spinner-ring"></div>
          <div class="spinner-text">加载中...</div>
        </div>
      </template>
      <div v-if="!loading && stocks && stocks.length > 0" class="stock-list">
        <!-- 表头 -->
        <div class="stock-header-row">
          <div class="stock-cell rank">排名</div>
          <div class="stock-cell code">股票代码</div>
          <div class="stock-cell name">股票名称</div>
          <div class="stock-cell price">现价</div>
          <div class="stock-cell low-price">最低价</div>
          <div class="stock-cell cumulative">累计涨幅</div>
          <div class="stock-cell index-change">指数涨幅</div>
          <div class="stock-cell deviation-10">10日偏离</div>
          <div class="stock-cell deviation-t">T+1/T+2偏离</div>
          <div class="stock-cell date-range">交易日周期</div>
          <div class="stock-cell expand-btn">详情</div>
        </div>

        <div v-for="(stock, idx) in paginatedStocks" :key="stock.ts_code" class="stock-row">
          <!-- 主行 -->
          <div class="stock-main-row" @click="toggleExpand(idx)">
            <div class="stock-cell rank">{{ stock.index }}</div>
            <div class="stock-cell code">
              <span class="font-semibold">{{ stock.ts_code }}</span>
            </div>
            <div class="stock-cell name">
              <span class="font-medium">{{ stock.name }}</span>
            </div>
            <div class="stock-cell price">
              <span>{{ formatNumber(stock.end_price) }}</span>
            </div>
            <div class="stock-cell low-price">
              <span>{{ formatNumber(stock.low_price) }}</span>
            </div>
            <div class="stock-cell cumulative">
              <span :class="getChangeClass(stock.price_change_pct)">
                {{ formatNumber(stock.price_change_pct) }}%
              </span>
            </div>
            <div class="stock-cell index-change">
              <span :class="getChangeClass(stock.index_change_pct)">
                {{ formatNumber(stock.index_change_pct) }}%
              </span>
            </div>
            <div class="stock-cell deviation-10">
              <span :class="getDeviationClass(stock.deviation)">
                {{ formatNumber(stock.deviation) }}
              </span>
            </div>
            <div class="stock-cell deviation-t">
              <template v-if="stock.tPlusData?.[1] && stock.tPlusData?.[2]">
                <div class="t-plus-two-container">
                  <div class="t-plus-two-item">
                    <span class="t-plus-two-label">T+1:</span>
                    <span class="t-plus-two-value">{{ formatNumber(stock.tPlusData[1].deviation) }}%</span>
                    <span :class="['t-plus-two-badge', stock.tPlusData[1].isAbnormal ? 'abnormal' : 'normal']">
                      {{ stock.tPlusData[1].isAbnormal ? '✓' : '✗' }}
                    </span>
                  </div>
                  <div class="t-plus-two-item">
                    <span class="t-plus-two-label">T+2:</span>
                    <span class="t-plus-two-value">{{ formatNumber(stock.tPlusData[2].deviation) }}%</span>
                    <span :class="['t-plus-two-badge', stock.tPlusData[2].isAbnormal ? 'abnormal' : 'normal']">
                      {{ stock.tPlusData[2].isAbnormal ? '✓' : '✗' }}
                    </span>
                  </div>
                </div>
              </template>
              <span v-else>-</span>
            </div>
            <div class="stock-cell date-range">
              <span class="text-xs">{{ formatDateRange(stock.low_date, stock.end_date) }}</span>
            </div>
            <div class="stock-cell expand-btn">
              <span class="expand-toggle" :class="{ expanded: expandedRows.has(idx) }">
                {{ expandedRows.has(idx) ? '▲' : '▼' }}
              </span>
            </div>
          </div>

          <!-- 详情行 -->
          <div v-if="expandedRows.has(idx)" class="stock-detail-row">
            <div class="detail-content">
              <h4 class="detail-title">T+i 偏离值数据</h4>
              <div class="t-plus-grid">
                <TPlusCard
                  v-for="day in 5"
                  :key="day"
                  :day="day"
                  :data="stock.tPlusData?.[day] || {}"
                  :other-stock="findOtherStock(stock.ts_code)"
                  :other-day="day"
                  @edit="handleEditTPlusDay(stock, day)"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- 分页 -->
        <div class="pagination-container">
          <a-pagination
            v-model:current="currentPage"
            :total="stocks.length"
            :page-size="pageSize"
            show-total
          />
        </div>
      </div>

      <a-empty v-else-if="!loading" description="暂无数据" />
    </a-spin>

    <!-- 编辑模态框 -->
    <EditModal
      v-model:visible="editModalVisible"
      :limit-up-pct="editData.limitUpPct"
      :current-value="editData.currentValue"
      @save="handleSaveEdit"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import TPlusCard from './TPlusCard.vue'
import EditModal from './EditModal.vue'
import { calculateAllTPlusData } from '@/utils/tplusCalculation'

interface StockData {
  ts_code: string
  name: string
  market?: string
  deviation?: number
  price_change_pct?: number
  index?: number
  limit_up?: number
  threshold?: number
  stock_prices?: any[]
  index_prices?: any[]
  low_price?: number
  low_date?: string
  end_price?: number
  index_change_pct?: number
  extraPercent?: number[] // T+1 到 T+5 的涨幅百分比
  baseDays?: number // 基础天数（10 或 30）
  [key: string]: any
}

interface Props {
  stocks?: StockData[]
  loading?: boolean
  otherStocks?: StockData[] // 另一榜单的数据（用于显示跨榜单异动）
}

const props = withDefaults(defineProps<Props>(), {
  stocks: () => [],
  loading: false,
  otherStocks: () => []
})

const stocks = computed(() => props.stocks || [])
const loading = computed(() => props.loading)

// 分页
const currentPage = ref(1)
const pageSize = 30

const paginatedStocks = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  const end = start + pageSize
  return stocks.value.slice(start, end)
})

// 展开状态
const expandedRows = ref<Set<number>>(new Set())

const toggleExpand = (idx: number) => {
  if (expandedRows.value.has(idx)) {
    expandedRows.value.delete(idx)
  } else {
    expandedRows.value.add(idx)
  }
}

// 在另一榜单中查找同一股票
const findOtherStock = (tsCode: string) => {
  return props.otherStocks?.find(stock => stock.ts_code === tsCode)
}

// 编辑模态框
const editModalVisible = ref(false)
const editData = ref({
  stock: null as StockData | null,
  day: 0,
  limitUpPct: 10,
  currentValue: 10
})

const handleEditTPlusDay = (stock: StockData, day: number) => {
  editData.value = {
    stock,
    day,
    limitUpPct: stock.limit_up || 10,
    currentValue: stock.limit_up || 10
  }
  editModalVisible.value = true
}

const handleSaveEdit = (value: number) => {
  const stock = editData.value.stock
  const day = editData.value.day

  if (!stock) return

  // 1. 修改 extraPercent
  if (!stock.extraPercent) {
    stock.extraPercent = Array(5).fill(stock.limit_up || 10)
  }
  stock.extraPercent[day - 1] = value

  // 2. 重新计算该股票的所有 T+n 数据
  const newTPlusData = calculateAllTPlusData(stock)
  // 使用 Object.assign 确保响应式更新
  Object.assign(stock.tPlusData, newTPlusData)

  // 3. 检查另一榜单中是否有对应股票
  const otherStock = findOtherStock(stock.ts_code)
  if (otherStock) {
    // 修改另一榜单的 extraPercent
    if (!otherStock.extraPercent) {
      otherStock.extraPercent = Array(5).fill(otherStock.limit_up || 10)
    }
    otherStock.extraPercent[day - 1] = value

    // 重新计算另一榜单的 T+n 数据
    const otherNewTPlusData = calculateAllTPlusData(otherStock)
    // 使用 Object.assign 确保响应式更新
    Object.assign(otherStock.tPlusData, otherNewTPlusData)
  }

  console.log('保存修改:', stock.ts_code, `T+${day}`, value)
}



const formatNumber = (num: number | undefined): string => {
  if (num === undefined || num === null) return '-'
  return num.toFixed(2)
}

const formatDateRange = (startDate: string | undefined, endDate: string | undefined): string => {
  if (!startDate && !endDate) return '-'
  if (!startDate) return endDate || '-'
  if (!endDate) return startDate || '-'
  return `${startDate} ~ ${endDate}`
}

const getDeviationClass = (deviation: number | undefined) => {
  if (!deviation) return 'text-gray-500'
  // 10日偏离始终使用红色加粗
  return 'deviation-highlight'
}

const getChangeClass = (change: number | undefined) => {
  if (!change) return 'text-gray-500'
  // 累计涨幅和指数涨幅始终使用红色
  return 'change-highlight'
}
</script>

<style scoped>
.stock-table-container {
  width: 100%;
  background: rgba(248, 249, 250, 0.8);
  backdrop-filter: blur(12px);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08), 0 0 20px rgba(41, 98, 255, 0.08);
  border: 1px solid rgba(41, 98, 255, 0.15);
  transition: all 0.3s ease;
  overflow-x: auto;
}

/* 亮色模式 */
:global(html:not(.dark)) .stock-table-container {
  background: rgba(248, 249, 250, 0.9);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08), 0 0 20px rgba(41, 98, 255, 0.08);
  border: 1px solid rgba(41, 98, 255, 0.15);
}

/* 深色模式 */
:global(html.dark) .stock-table-container {
  background: rgba(21, 26, 33, 0.7);
  border: 1px solid rgba(41, 98, 255, 0.15);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4), 0 0 20px rgba(41, 98, 255, 0.1);
}

:global(.stock-table-container .w-full) {
  width: 100% !important;
  display: flex;
  flex-direction: column;
}

.spin-wrapper {
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.custom-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.spinner-ring {
  width: 50px;
  height: 50px;
  border: 3px solid rgba(41, 98, 255, 0.2);
  border-top-color: #2962FF;
  border-right-color: #2962FF;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.spinner-text {
  color: #2962FF;
  font-size: 0.875rem;
  font-weight: 500;
  letter-spacing: 0.05em;
  animation: pulse-text 1.5s ease-in-out infinite;
}

@keyframes pulse-text {
  0%, 100% {
    opacity: 0.6;
  }
  50% {
    opacity: 1;
  }
}

.stock-list {
  width: 100%;
  overflow-x: auto;
  display: flex;
  flex-direction: column;
}

/* 表头样式 */
.stock-header-row {
  display: grid;
  grid-template-columns: 60px 100px 120px 80px 80px 90px 90px 90px minmax(140px, 1fr) 160px 50px;
  gap: 0.75rem;
  padding: 1rem;
  align-items: center;
  background: linear-gradient(90deg, rgba(41, 98, 255, 0.1) 0%, rgba(61, 90, 254, 0.05) 100%);
  border-bottom: 2px solid rgba(41, 98, 255, 0.2);
  border-radius: 8px 8px 0 0;
  font-weight: 700;
  font-size: 0.85rem;
  color: #2962FF;
  text-shadow: 0 0 8px rgba(41, 98, 255, 0.2);
  position: sticky;
  top: 0;
  z-index: 10;
  width: 100%;
  min-width: fit-content;
  box-sizing: border-box;
}

:global(.dark) .stock-header-row {
  background: linear-gradient(90deg, rgba(41, 98, 255, 0.1) 0%, rgba(61, 90, 254, 0.05) 100%);
  border-bottom: 2px solid rgba(41, 98, 255, 0.2);
  color: #2962FF;
  text-shadow: 0 0 8px rgba(41, 98, 255, 0.2);
}

.stock-row {
  border-bottom: 1px solid rgba(41, 98, 255, 0.1);
  transition: all 0.2s ease;
}

:global(.dark) .stock-row {
  border-bottom: 1px solid rgba(41, 98, 255, 0.1);
}

.stock-row:last-child {
  border-bottom: none;
}

.stock-main-row {
  display: grid;
  grid-template-columns: 60px 100px 120px 80px 80px 90px 90px 90px minmax(140px, 1fr) 160px 50px;
  gap: 0.75rem;
  padding: 1rem;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-size: 0.9rem;
  border-radius: 8px;
  width: 100%;
  min-width: fit-content;
  box-sizing: border-box;
}

.stock-main-row:hover {
  background: linear-gradient(90deg, rgba(41, 98, 255, 0.08) 0%, rgba(61, 90, 254, 0.08) 100%);
  transform: translateX(4px);
}

:global(.dark) .stock-main-row:hover {
  background: linear-gradient(90deg, rgba(41, 98, 255, 0.08) 0%, rgba(61, 90, 254, 0.08) 100%);
}

.stock-cell {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  color: var(--text-primary);
  transition: color 0.2s ease;
  font-family: 'JetBrains Mono', 'Roboto Mono', monospace;
}

.stock-cell.rank {
  justify-content: center;
  font-weight: 700;
  font-size: 1rem;
  background: linear-gradient(135deg, #2962FF 0%, #3D5AFE 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

:global(.dark) .stock-cell.rank {
  background: linear-gradient(135deg, #2962FF 0%, #3D5AFE 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stock-cell.code {
  font-weight: 600;
  color: #2962FF;
  font-family: 'JetBrains Mono', 'Roboto Mono', monospace;
  text-shadow: 0 0 8px rgba(41, 98, 255, 0.3);
}

:global(.dark) .stock-cell.code {
  color: #2962FF;
  text-shadow: 0 0 8px rgba(41, 98, 255, 0.3);
}

.stock-cell.name {
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.stock-cell.price,
.stock-cell.low-price,
.stock-cell.cumulative,
.stock-cell.index-change,
.stock-cell.deviation-10,
.stock-cell.deviation-t {
  justify-content: flex-end;
  font-weight: 600;
}

.stock-cell.date-range {
  justify-content: flex-start;
  font-size: 0.8rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.stock-cell.expand-btn {
  justify-content: center;
}

.expand-toggle {
  color: #2962FF;
  font-weight: 600;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  user-select: none;
  background: rgba(41, 98, 255, 0.15);
  border: 1px solid rgba(41, 98, 255, 0.2);
}

:global(.dark) .expand-toggle {
  color: #2962FF;
  background: rgba(41, 98, 255, 0.15);
  border: 1px solid rgba(41, 98, 255, 0.2);
}

.expand-toggle:hover {
  background: rgba(41, 98, 255, 0.25);
  transform: scale(1.05);
  box-shadow: 0 0 8px rgba(41, 98, 255, 0.3);
}

:global(.dark) .expand-toggle:hover {
  background: rgba(41, 98, 255, 0.25);
  box-shadow: 0 0 8px rgba(41, 98, 255, 0.3);
}

.expand-toggle.expanded {
  color: #3D5AFE;
  background: rgba(61, 90, 254, 0.2);
  border: 1px solid rgba(61, 90, 254, 0.3);
}

:global(.dark) .expand-toggle.expanded {
  color: #3D5AFE;
  background: rgba(61, 90, 254, 0.2);
  border: 1px solid rgba(61, 90, 254, 0.3);
}

/* 表格数据高亮样式 */
.change-highlight {
  color: #DC2626;
  font-weight: 600;
  text-shadow: 0 0 8px rgba(220, 38, 38, 0.15);
}

/* 亮色模式 */
:global(html:not(.dark)) .change-highlight {
  color: #DC2626;
  text-shadow: 0 0 8px rgba(220, 38, 38, 0.15);
}

/* 深色模式 */
:global(html.dark) .change-highlight {
  color: #f87171;
  text-shadow: 0 0 8px rgba(248, 113, 113, 0.2);
}

.deviation-highlight {
  color: #DC2626;
  font-weight: 700;
  text-shadow: 0 0 8px rgba(220, 38, 38, 0.15);
}

/* 亮色模式 */
:global(html:not(.dark)) .deviation-highlight {
  color: #DC2626;
  text-shadow: 0 0 8px rgba(220, 38, 38, 0.15);
}

/* 深色模式 */
:global(html.dark) .deviation-highlight {
  color: #f87171;
  text-shadow: 0 0 8px rgba(248, 113, 113, 0.2);
}

/* T+1/T+2 偏离值样式 */
.t-plus-two-container {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  width: 100%;
}

.t-plus-two-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  justify-content: flex-end;
}

.t-plus-two-label {
  color: #6B7280;
  font-weight: 600;
  font-size: 0.75rem;
  min-width: 30px;
  text-align: right;
}

/* 亮色模式 */
:global(html:not(.dark)) .t-plus-two-label {
  color: #6B7280;
}

/* 深色模式 */
:global(html.dark) .t-plus-two-label {
  color: #94a3b8;
}

.t-plus-two-value {
  color: #DC2626;
  font-weight: 700;
  font-family: 'Monaco', 'Courier New', monospace;
  font-size: 0.875rem;
}

/* 亮色模式 */
:global(html:not(.dark)) .t-plus-two-value {
  color: #DC2626;
}

/* 深色模式 */
:global(html.dark) .t-plus-two-value {
  color: #f87171;
}

.t-plus-two-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 6px;
  font-weight: 700;
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.t-plus-two-badge.abnormal {
  background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
  color: white;
  box-shadow: 0 0 8px rgba(220, 38, 38, 0.3);
}

:global(.dark) .t-plus-two-badge.abnormal {
  background: linear-gradient(135deg, #f87171 0%, #dc2626 100%);
  box-shadow: 0 0 8px rgba(248, 113, 113, 0.3);
}

.t-plus-two-badge.normal {
  background: linear-gradient(135deg, #16a34a 0%, #15803d 100%);
  color: white;
  box-shadow: 0 0 8px rgba(22, 163, 74, 0.3);
}

:global(.dark) .t-plus-two-badge.normal {
  background: linear-gradient(135deg, #4ade80 0%, #16a34a 100%);
  box-shadow: 0 0 8px rgba(74, 222, 128, 0.3);
}

.t-plus-two-badge:hover {
  transform: scale(1.1);
}

.stock-detail-row {
  background: linear-gradient(135deg, rgba(243, 244, 246, 0.6) 0%, rgba(248, 249, 250, 0.6) 100%);
  border-top: 1px solid rgba(41, 98, 255, 0.1);
  padding: 2rem;
  border-radius: 0 0 12px 12px;
  animation: slideDown 0.3s ease-out;
}

/* 亮色模式 */
:global(html:not(.dark)) .stock-detail-row {
  background: linear-gradient(135deg, rgba(243, 244, 246, 0.8) 0%, rgba(248, 249, 250, 0.8) 100%);
  border-top: 1px solid rgba(41, 98, 255, 0.1);
}

/* 深色模式 */
:global(html.dark) .stock-detail-row {
  background: linear-gradient(135deg, rgba(11, 14, 17, 0.5) 0%, rgba(21, 26, 33, 0.5) 100%);
  border-top: 1px solid rgba(41, 98, 255, 0.1);
}

@keyframes slideDown {
  from {
    opacity: 0;
    max-height: 0;
    padding-top: 0;
    padding-bottom: 0;
  }
  to {
    opacity: 1;
    max-height: 500px;
    padding-top: 2rem;
    padding-bottom: 2rem;
  }
}

.detail-content {
  width: 100%;
}

.detail-title {
  margin: 0 0 1.5rem 0;
  color: #2962FF;
  font-size: 1.125rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-shadow: 0 0 8px rgba(41, 98, 255, 0.2);
}

:global(.dark) .detail-title {
  color: #2962FF;
  text-shadow: 0 0 8px rgba(41, 98, 255, 0.2);
}

.detail-title::before {
  content: '';
  width: 4px;
  height: 1.5rem;
  background: linear-gradient(135deg, #2962FF 0%, #3D5AFE 100%);
  border-radius: 2px;
  box-shadow: 0 0 8px rgba(41, 98, 255, 0.3);
}

:global(.dark) .detail-title::before {
  background: linear-gradient(135deg, #2962FF 0%, #3D5AFE 100%);
  box-shadow: 0 0 8px rgba(41, 98, 255, 0.3);
}

.t-plus-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
  width: 100%;
}

.pagination-container {
  display: flex;
  justify-content: center;
  padding: 1.5rem;
  border-top: 1px solid rgba(41, 98, 255, 0.1);
  margin-top: 1rem;
}

:global(.dark) .pagination-container {
  border-top: 1px solid rgba(41, 98, 255, 0.1);
}

.pagination-container :deep(.arco-pagination) {
  gap: 0.5rem;
}

.pagination-container :deep(.arco-pagination-item) {
  border-radius: 8px;
  transition: all 0.2s ease;
}

.pagination-container :deep(.arco-pagination-item:hover) {
  transform: translateY(-2px);
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .stock-header-row,
  .stock-main-row {
    grid-template-columns: 55px 95px 110px 75px 75px 85px 85px 85px minmax(130px, 1fr) 150px 45px;
    gap: 0.6rem;
    font-size: 0.85rem;
  }

  .stock-header-row {
    padding: 0.75rem;
  }

  .stock-main-row {
    padding: 0.75rem;
  }
}

@media (max-width: 1024px) {
  .stock-header-row,
  .stock-main-row {
    grid-template-columns: 50px 85px 100px 70px 70px 80px 80px 80px minmax(130px, 1fr) 140px 45px;
    gap: 0.5rem;
    font-size: 0.8rem;
  }

  .stock-header-row {
    padding: 0.5rem;
  }

  .stock-main-row {
    padding: 0.5rem;
  }

  .t-plus-grid {
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  }
}

@media (max-width: 768px) {
  .stock-table-container {
    padding: 1rem;
    border-radius: 12px;
    overflow-x: auto;
  }

  .stock-list {
    min-width: 100%;
  }

  .stock-header-row,
  .stock-main-row {
    grid-template-columns: 45px 75px 90px 65px 65px 75px 75px 75px minmax(120px, 1fr) 130px 40px;
    gap: 0.4rem;
    padding: 0.5rem;
    font-size: 0.75rem;
  }

  .t-plus-grid {
    grid-template-columns: 1fr;
  }

  .stock-detail-row {
    padding: 1.5rem;
  }
}
</style>

