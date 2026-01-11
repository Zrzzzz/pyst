/**
 * 股票数据状态管理 - Zustand Store
 */
import { create } from 'zustand'
import { getBothStocks, getChangelog } from '@/utils/api'
import type { StockData, ChangelogItem } from '@/utils/api'
import { calculateAllTPlusData } from '@/utils/tplusCalculation'

interface StockStore {
  // 状态
  stocks10: StockData[]
  stocks30: StockData[]
  loading: boolean
  error: string | null
  lastUpdateTime: string | null
  fromCache: boolean
  changelog: ChangelogItem[]

  // 方法
  fetchBothStocks: () => Promise<void>
  fetchChangelog: () => Promise<void>
  searchStocks: (keyword: string, period: '10' | '30') => StockData[]
  getTopDeviationStocks: (period: '10' | '30', limit: number) => StockData[]
  updateStockExtraPercent: (tsCode: string, day: number, value: number) => void

  // 计算属性（作为方法）
  getCount10: () => number
  getCount30: () => number
  getTotalCount: () => number
  getSortedStocks10: () => StockData[]
  getSortedStocks30: () => StockData[]
  getMergedStocks: () => StockData[]
}

export const useStockStore = create<StockStore>((set, get) => ({
  // 初始状态
  stocks10: [],
  stocks30: [],
  loading: false,
  error: null,
  lastUpdateTime: null,
  fromCache: false,
  changelog: [
    {
      version: '1.0.0',
      date: '2024-01-11',
      changes: [
        '✨ 完成 React 前端重构',
        '✨ 实现 T+n 偏离值计算',
        '🎨 优化空状态样式',
        '🐛 修复 Changelog 组件'
      ]
    }
  ],

  // 计算属性（作为方法）
  getCount10: () => get().stocks10.length,
  getCount30: () => get().stocks30.length,
  getTotalCount: () => get().getCount10() + get().getCount30(),
  getSortedStocks10: () => {
    return [...get().stocks10]
      .sort((a, b) => (b.deviation || 0) - (a.deviation || 0))
      .map((stock, index) => ({ ...stock, index: index + 1 }))
  },
  getSortedStocks30: () => {
    return [...get().stocks30]
      .sort((a, b) => (b.deviation || 0) - (a.deviation || 0))
      .map((stock, index) => ({ ...stock, index: index + 1 }))
  },

  // 获取合并榜单（明天买什么）
  getMergedStocks: () => {
    const { stocks10, stocks30 } = get()

    // 创建 Map 用于去重和合并
    const stockMap = new Map<string, StockData>()

    // 先添加 10日榜的股票
    stocks10.forEach(stock => {
      stockMap.set(stock.ts_code, stock)
    })

    // 再添加 30日榜的股票，如果已存在则合并
    stocks30.forEach(stock => {
      if (stockMap.has(stock.ts_code)) {
        // 股票同时存在于两个榜单，取可能涨幅的较小值
        const existingStock = stockMap.get(stock.ts_code)!
        const stock10PossibleChange = existingStock.tPlusData?.[1]?.possibleChange ?? 0
        const stock30PossibleChange = stock.tPlusData?.[1]?.possibleChange ?? 0

        // 使用较小的可能涨幅，但保留原有的其他数据
        const mergedStock = {
          ...existingStock,
          mergedPossibleChange: Math.min(stock10PossibleChange, stock30PossibleChange)
        }
        stockMap.set(stock.ts_code, mergedStock)
      } else {
        // 股票只存在于 30日榜
        const possibleChange = stock.tPlusData?.[1]?.possibleChange ?? 0
        const mergedStock = {
          ...stock,
          mergedPossibleChange: possibleChange
        }
        stockMap.set(stock.ts_code, mergedStock)
      }
    })

    // 对于只在 10日榜的股票，添加 mergedPossibleChange
    stocks10.forEach(stock => {
      if (!stocks30.some(s => s.ts_code === stock.ts_code)) {
        const possibleChange = stock.tPlusData?.[1]?.possibleChange ?? 0
        const mergedStock = {
          ...stock,
          mergedPossibleChange: possibleChange
        }
        stockMap.set(stock.ts_code, mergedStock)
      }
    })

    // 转换为数组，按可能涨幅排序，取前30只
    return Array.from(stockMap.values())
      .sort((a, b) => {
        const aChange = (a as StockData & { mergedPossibleChange?: number }).mergedPossibleChange ?? 0
        const bChange = (b as StockData & { mergedPossibleChange?: number }).mergedPossibleChange ?? 0
        return bChange - aChange
      })
      .slice(0, 30)
      .map((stock, index) => ({ ...stock, index: index + 1 }))
  },

  // 获取双榜数据
  fetchBothStocks: async () => {
    set({ loading: true, error: null })
    try {
      const result = await getBothStocks()
      if (result.code === 0) {
        // 为每个股票添加 baseDays、extraPercent 和 tPlusData
        const stocks10 = (result.data.stocks_10 || []).map(stock => ({
          ...stock,
          baseDays: 10,
          extraPercent: stock.extraPercent || Array(5).fill(stock.limit_up || 10),
          tPlusData: calculateAllTPlusData({ ...stock, baseDays: 10, extraPercent: stock.extraPercent || Array(5).fill(stock.limit_up || 10) })
        }))
        const stocks30 = (result.data.stocks_30 || []).map(stock => ({
          ...stock,
          baseDays: 30,
          extraPercent: stock.extraPercent || Array(5).fill(stock.limit_up || 10),
          tPlusData: calculateAllTPlusData({ ...stock, baseDays: 30, extraPercent: stock.extraPercent || Array(5).fill(stock.limit_up || 10) })
        }))

        set({
          stocks10,
          stocks30,
          fromCache: result.from_cache || false,
          lastUpdateTime: new Date().toLocaleString('zh-CN')
        })
      } else {
        set({ error: result.message || '获取数据失败' })
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '请求失败'
      set({ error: errorMessage })
      console.error('获取股票数据失败:', err)
    } finally {
      set({ loading: false })
    }
  },

  // 获取更新日志
  fetchChangelog: async () => {
    try {
      const result = await getChangelog()
      if (result.code === 0) {
        set({ changelog: result.data || [] })
      }
    } catch (err) {
      console.error('获取更新日志失败:', err)
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
    const stocks = period === '10' ? get().getSortedStocks10() : get().getSortedStocks30()
    return stocks.slice(0, limit)
  },

  // 更新股票的 extraPercent 并重新计算 T+n 数据
  updateStockExtraPercent: (tsCode: string, day: number, value: number) => {
    const { stocks10, stocks30 } = get()

    console.log('更新股票 extraPercent:', { tsCode, day, value })

    // 更新 10日榜中的股票
    const newStocks10 = stocks10.map(stock => {
      if (stock.ts_code === tsCode) {
        const extraPercent = stock.extraPercent || Array(5).fill(stock.limit_up || 10)
        const newExtraPercent = [...extraPercent]
        newExtraPercent[day - 1] = value

        const updatedStock = { ...stock, extraPercent: newExtraPercent }
        const newTPlusData = calculateAllTPlusData(updatedStock)

        console.log('10日榜更新后的 tPlusData:', newTPlusData)

        return { ...updatedStock, tPlusData: newTPlusData }
      }
      return stock
    })

    // 更新 30日榜中的股票
    const newStocks30 = stocks30.map(stock => {
      if (stock.ts_code === tsCode) {
        const extraPercent = stock.extraPercent || Array(5).fill(stock.limit_up || 10)
        const newExtraPercent = [...extraPercent]
        newExtraPercent[day - 1] = value

        const updatedStock = { ...stock, extraPercent: newExtraPercent }
        const newTPlusData = calculateAllTPlusData(updatedStock)

        console.log('30日榜更新后的 tPlusData:', newTPlusData)

        return { ...updatedStock, tPlusData: newTPlusData }
      }
      return stock
    })

    set({ stocks10: newStocks10, stocks30: newStocks30 })
    console.log('Store 更新完成')
  }
}))

