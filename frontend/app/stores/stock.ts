/**
 * 股票数据状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useApi, type StockData, type ChangelogItem } from '@/composables/useApi'
import { calculateAllTPlusData } from '@/utils/tplusCalculation'

export const useStockStore = defineStore('stock', () => {
  const { getBothStocks } = useApi()

  // 状态
  const stocks10 = ref<StockData[]>([])
  const stocks30 = ref<StockData[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const lastUpdateTime = ref<string | null>(null)
  const fromCache = ref(false)
  const changelog = ref<ChangelogItem[]>([])

  // 计算属性
  const count10 = computed(() => stocks10.value.length)
  const count30 = computed(() => stocks30.value.length)
  const totalCount = computed(() => count10.value + count30.value)

  // 获取排序后的数据
  const sortedStocks10 = computed(() => {
    return [...stocks10.value]
      .sort((a, b) => (b.deviation || 0) - (a.deviation || 0))
      .map((stock, index) => ({ ...stock, index: index + 1 }))
  })

  const sortedStocks30 = computed(() => {
    return [...stocks30.value]
      .sort((a, b) => (b.deviation || 0) - (a.deviation || 0))
      .map((stock, index) => ({ ...stock, index: index + 1 }))
  })

  // 初始化 extraPercent 并计算 T+n 数据（为每个股票添加 T+1~T+5 的涨幅数组和计算结果）
  const initializeExtraPercent = (stocks: any[], baseDays: number) => {
    return stocks.map((stock) => {
      const stockWithExtra = {
        ...stock,
        baseDays,
        extraPercent: Array(5).fill(stock.limit_up || 10) // 默认为 5 个 limitup
      }

      // 使用 util 函数计算 T+1 到 T+5 的数据
      const tPlusData = calculateAllTPlusData(stockWithExtra)

      return {
        ...stockWithExtra,
        tPlusData
      }
    })
  }

  // 方法
  const fetchBothStocks = async () => {
    loading.value = true
    error.value = null
    try {
      const result = await getBothStocks()
      if (result.code === 0) {
        // 初始化 extraPercent
        stocks10.value = initializeExtraPercent(result.data.stocks_10 || [], 10)
        stocks30.value = initializeExtraPercent(result.data.stocks_30 || [], 30)
        fromCache.value = result.from_cache || false
        changelog.value = result.changelog || []
        lastUpdateTime.value = new Date().toLocaleString('zh-CN')
      } else {
        error.value = result.message || '获取数据失败'
      }
    } catch (err: any) {
      error.value = err.message || '请求失败'
      console.error('获取股票数据失败:', err)
    } finally {
      loading.value = false
    }
  }

  // 搜索股票
  const searchStocks = (keyword: string, period: '10' | '30' = '10') => {
    const stocks = period === '10' ? stocks10.value : stocks30.value
    if (!keyword) return stocks

    const lowerKeyword = keyword.toLowerCase()
    return stocks.filter(
      (stock) =>
        stock.ts_code.toLowerCase().includes(lowerKeyword) ||
        stock.name.toLowerCase().includes(lowerKeyword)
    )
  }

  // 获取偏离值最高的股票
  const getTopDeviationStocks = (period: '10' | '30' = '10', limit: number = 10) => {
    const stocks = period === '10' ? sortedStocks10.value : sortedStocks30.value
    return stocks.slice(0, limit)
  }

  // 获取偏离值最低的股票
  const getBottomDeviationStocks = (period: '10' | '30' = '10', limit: number = 10) => {
    const stocks = period === '10' ? sortedStocks10.value : sortedStocks30.value
    return stocks.slice(-limit).reverse()
  }

  return {
    // 状态
    stocks10,
    stocks30,
    loading,
    error,
    lastUpdateTime,
    fromCache,
    changelog,
    // 计算属性
    count10,
    count30,
    totalCount,
    sortedStocks10,
    sortedStocks30,
    // 方法
    fetchBothStocks,
    searchStocks,
    getTopDeviationStocks,
    getBottomDeviationStocks
  }
})

