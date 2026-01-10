/**
 * T+n 数据计算工具函数
 */

export interface TPlusDataFormat {
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

/**
 * 计算单个 T+n 的数据
 */
export const calculateTPlusData = (stock: any, day: number): TPlusDataFormat => {
  if (!stock.stock_prices || !stock.index_prices || stock.stock_prices.length === 0 ||
      stock.stock_prices.length !== stock.baseDays
  ) {
    return {
      lowestPrice: 0,
      lowestDate: '-',
      currentClose: 0,
      changePercent: 0,
      dailyChange: 0,
      indexChangePercent: 0,
      deviation: 0,
      isAbnormal: false,
      possibleHighestPrice: 0,
      possibleChange: 0,
      error: '价格数据不完整'
    }
  }

  const lastPrice = stock.stock_prices[stock.stock_prices.length - 1].close
  const threshold = stock.threshold || 100
  const baseDays = stock.baseDays || 10
  const extraPercent = stock.extraPercent || Array(5).fill(stock.limit_up || 10)

  // 生成 T+day 的价格序列（使用 extraPercent）
  const extraPrices: number[] = []
  let currentPrice = lastPrice
  for (let i = 0; i < day; i++) {
    const dailyPercent = extraPercent[i] ?? (stock.limit_up || 10)
    currentPrice = currentPrice * (1 + dailyPercent / 100)
    extraPrices.push(parseFloat(currentPrice.toFixed(2)))
  }

  // 合并基础数据和 T+n 数据
  const allPrices = [...stock.stock_prices, ...extraPrices.map((price, idx) => ({
    trade_date: `T+${idx + 1}`,
    close: price,
    pre_close: idx === 0 ? lastPrice : extraPrices[idx - 1]
  }))]

  // 滑动窗口：取第 i 天到 T+i 天的数据（窗口大小为 baseDays）
  const windowStart = day
  const windowEnd = day + baseDays

  // 在窗口内找最低价
  let lowestPrice = allPrices[windowStart].pre_close
  let lowestDate = allPrices[windowStart].trade_date || '-'

  for (let i = windowStart; i < windowEnd; i++) {
    if (allPrices[i].pre_close < lowestPrice) {
      lowestPrice = allPrices[i].pre_close
      lowestDate = allPrices[i].trade_date || '-'
    }
  }

  // 计算股票累计涨幅
  const tPlusCurrentPrice = extraPrices[day - 1] ?? 0
  const stockChangePercent = ((tPlusCurrentPrice - lowestPrice) / lowestPrice) * 100

  // 计算指数累计涨幅
  let indexChangePercent = 0
  if (stock.index_prices && stock.index_prices.length > 0) {
    let indexLowestPrice = stock.index_prices[0].pre_close

    // 找到 lowestDate 对应的指数 pre_close
    for (let i = 0; i < stock.index_prices.length; i++) {
      if (stock.index_prices[i].trade_date === lowestDate) {
        indexLowestPrice = stock.index_prices[i].pre_close
        break
      }
    }

    // 指数当前价格是最后一天的 close
    const indexCurrentPrice = stock.index_prices[stock.index_prices.length - 1].close
    indexChangePercent = ((indexCurrentPrice - indexLowestPrice) / indexLowestPrice) * 100
  }

  // 计算偏离值
  const deviation = stockChangePercent - indexChangePercent

  // 判断是否异动
  const isAbnormal = deviation > threshold

  // 计算当日涨幅
  let dailyChange = 0
  if (day === 1) {
    dailyChange = ((extraPrices[0]! - lastPrice) / lastPrice) * 100
  } else {
    const prevPrice = extraPrices[day - 2]
    const currentPrice = extraPrices[day - 1]
    if (prevPrice !== undefined && currentPrice !== undefined) {
      dailyChange = ((currentPrice - prevPrice) / prevPrice) * 100
    }
  }

  // 计算可能的最高价格和可能的涨幅
  // 可能最高价 = lowestPrice * (1 + threshold/100 + indexChangePercent/100)
  const possibleHighestPrice = lowestPrice * (1 + threshold / 100 + indexChangePercent / 100)
  const possibleChange = ((possibleHighestPrice - lastPrice) / lastPrice) * 100

  return {
    lowestPrice: parseFloat(lowestPrice.toFixed(2)),
    lowestDate,
    currentClose: tPlusCurrentPrice,
    changePercent: parseFloat(stockChangePercent.toFixed(2)),
    dailyChange: parseFloat(dailyChange.toFixed(2)),
    indexChangePercent: parseFloat(indexChangePercent.toFixed(2)),
    deviation: parseFloat(deviation.toFixed(2)),
    isAbnormal,
    possibleHighestPrice: parseFloat(possibleHighestPrice.toFixed(2)),
    possibleChange: parseFloat(possibleChange.toFixed(2))
  }
}

/**
 * 计算股票的所有 T+1~T+5 数据
 */
export const calculateAllTPlusData = (stock: any) => {
  const tPlusData: Record<number, TPlusDataFormat> = {}
  for (let day = 1; day <= 5; day++) {
    tPlusData[day] = calculateTPlusData(stock, day)
  }
  return tPlusData
}

