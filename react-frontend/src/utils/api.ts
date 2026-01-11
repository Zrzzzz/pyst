/**
 * API 请求工具
 */
import axios, { AxiosError } from 'axios'

// ============ 类型定义 ============

export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
  count?: Record<string, number>
  from_cache?: boolean
}

export interface PriceData {
  trade_date: string
  open: number
  high: number
  low: number
  close: number
  pre_close: number
}

export interface StockData {
  // 基础信息
  ts_code: string
  name: string
  market: string

  // 涨幅数据
  price_change_pct: number
  index_change_pct: number
  deviation: number

  // 价格数据
  start_price: number
  end_price: number
  low_price: number
  low_date: string
  start_date: string
  end_date: string

  // 涨停相关
  limit_up: number
  threshold?: number
  remaining_limit_ups?: number

  // 详细数据
  stock_prices: PriceData[]
  index_prices: PriceData[]

  // 其他字段
  price_change_low_pct?: number
  index_change_low_pct?: number
  deviation_low?: number
  deviation_date_range?: string

  // 索引（前端添加）
  index?: number

  [key: string]: any
}

export interface ChangelogItem {
  version: string
  date: string
  changes: string[]
}

export interface BothStocksResponse {
  stocks_10: StockData[]
  stocks_30: StockData[]
  changelog?: ChangelogItem[]
}

// ============ API 实例 ============

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

// 响应拦截器
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    console.error('API 请求错误:', error.message)
    return Promise.reject(error)
  }
)

/**
 * 获取双榜数据（10日和30日偏离值榜）
 */
export const getBothStocks = async (): Promise<ApiResponse<BothStocksResponse>> => {
  try {
    const { data } = await api.get<ApiResponse<BothStocksResponse>>('/stocks/both')
    return data
  } catch (error) {
    console.error('获取双榜数据失败:', error)
    throw error
  }
}

export default api
export type { ApiResponse, PriceData, StockData, ChangelogItem, BothStocksResponse }
