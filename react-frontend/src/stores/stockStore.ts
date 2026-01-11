/**
 * 股票数据状态管理 - Zustand Store
 */
import { create } from 'zustand'
import { getBothStocks } from '@/utils/api'
import type { StockData, ChangelogItem } from '@/utils/api'

interface StockStore {
  // 状态
  stocks10: StockData[]
  stocks30: StockData[]
  loading: boolean
  error: string | null
  lastUpdateTime: string | null
  fromCache: boolean
  changelog: ChangelogItem[]

  // 计算属性
  count10: number
  count30: number
  totalCount: number
  sortedStocks10: StockData[]
  sortedStocks30: StockData[]

  // 方法
  fetchBothStocks: () => Promise<void>
  searchStocks: (keyword: string, period: '10' | '30') => StockData[]
  getTopDeviationStocks: (period: '10' | '30', limit: number) => StockData[]
}

export const useStockStore = create<StockStore>((set, get) => ({
  // 初始状态
  stocks10: [],
  stocks30: [],
  loading: false,
  error: null,
  lastUpdateTime: null,
  fromCache: false,
  changelog: [],

  // 计算属性
  get count10() {
    return get().stocks10.length
  },
  get count30() {
    return get().stocks30.length
  },
  get totalCount() {
    return get().count10 + get().count30
  },
  get sortedStocks10() {
    return [...get().stocks10]
      .sort((a, b) => (b.deviation || 0) - (a.deviation || 0))
      .map((stock, index) => ({ ...stock, index: index + 1 }))
  },
  get sortedStocks30() {
    return [...get().stocks30]
      .sort((a, b) => (b.deviation || 0) - (a.deviation || 0))
      .map((stock, index) => ({ ...stock, index: index + 1 }))
  },

  // 获取双榜数据
  fetchBothStocks: async () => {
    set({ loading: true, error: null })
    try {
      const result = await getBothStocks()
      if (result.code === 0) {
        set({
          stocks10: result.data.stocks_10 || [],
          stocks30: result.data.stocks_30 || [],
          fromCache: result.from_cache || false,
          lastUpdateTime: new Date().toLocaleString('zh-CN'),
          changelog: result.data.changelog || []
        })
      } else {
        set({ error: result.message || '获取数据失败' })
      }
    } catch (err: any) {
      set({ error: err.message || '请求失败' })
      console.error('获取股票数据失败:', err)
    } finally {
      set({ loading: false })
    }
  },

  // 搜索股票
  searchStocks: (keyword: string, period: '10' | '30' = '10') => {
    const stocks = period === '10' ? get().stocks10 : get().stocks30
    if (!keyword) return stocks

    const lowerKeyword = keyword.toLowerCase()
    return stocks.filter(
      (stock) =>
        stock.ts_code.toLowerCase().includes(lowerKeyword) ||
        stock.name.toLowerCase().includes(lowerKeyword)
    )
  },

  // 获取偏离值最高的股票
  getTopDeviationStocks: (period: '10' | '30' = '10', limit: number = 10) => {
    const stocks = period === '10' ? get().sortedStocks10 : get().sortedStocks30
    return stocks.slice(0, limit)
  }
}))

