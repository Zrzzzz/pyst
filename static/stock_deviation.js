/**
 * 股票偏离值计算模块
 * 用于计算股票相对于指数的偏离值和预计偏离值
 */

/**
 * 计算偏离值
 * 偏离值 = 股价涨幅 - 指数涨幅
 * 其中涨幅 = (现在close - low_date的pre_close) / low_date的pre_close * 100
 * 
 * @param {number} stockClose - 股票现在的收盘价
 * @param {number} stockLowPreClose - 股票最低点那天的前收盘价
 * @param {number} indexClose - 指数现在的收盘价
 * @param {number} indexLowPreClose - 指数最低点那天的前收盘价
 * @returns {number} 偏离值百分比
 */
function calculateDeviation(stockClose, stockLowPreClose, indexClose, indexLowPreClose) {
  if (stockLowPreClose <= 0 || indexLowPreClose <= 0) {
    return null;
  }
  
  const stockChangePercent = ((stockClose - stockLowPreClose) / stockLowPreClose) * 100;
  const indexChangePercent = ((indexClose - indexLowPreClose) / indexLowPreClose) * 100;
  
  return parseFloat((stockChangePercent - indexChangePercent).toFixed(2));
}

/**
 * 找到指定日期范围内的最低pre_close价格和对应日期
 * 
 * @param {Array} prices - 价格数据数组，每项包含 {trade_date, pre_close, close, ...}
 * @param {number} startIndex - 开始索引（包含）
 * @param {number} endIndex - 结束索引（包含）
 * @returns {Object} {lowPrice, lowDate, lowIndex} 或 null
 */
function findLowestPrice(prices, startIndex, endIndex) {
  if (startIndex < 0 || endIndex >= prices.length || startIndex > endIndex) {
    return null;
  }
  
  let lowestPrice = prices[startIndex].pre_close;
  let lowestDate = prices[startIndex].trade_date;
  let lowestIndex = startIndex;
  
  for (let i = startIndex + 1; i <= endIndex; i++) {
    if (prices[i].pre_close < lowestPrice) {
      lowestPrice = prices[i].pre_close;
      lowestDate = prices[i].trade_date;
      lowestIndex = i;
    }
  }
  
  return {
    lowPrice: lowestPrice,
    lowDate: lowestDate,
    lowIndex: lowestIndex
  };
}

/**
 * 计算后n日的偏离值
 *
 * @param {Array} stockPrices - 股票价格数据数组（原始的n日数据）
 * @param {Array} indexPrices - 指数价格数据数组（原始的n日数据）
 * @param {number} n - 后n日（n >= 1）
 * @param {Array} extraStockPrices - 额外的股票价格数据，模拟涨停后的价格（可选）
 *                                   例如：[lastPrice*(1+limitUp), lastPrice*(1+limitUp)^2, ...]
 * @returns {Object} 包含偏离值计算结果
 */
function calculateTrailingDeviation(stockPrices, indexPrices, n, extraStockPrices = null) {
  // 合并价格数据
  let mergedStockPrices = [...stockPrices];
  let mergedIndexPrices = [...indexPrices];

  // 如果有额外价格，添加到末尾
  if (extraStockPrices && extraStockPrices.length > 0) {
    // 为额外的股票价格创建完整的价格对象
    const extraStockPriceObjects = extraStockPrices.map((price, idx) => ({
      trade_date: `T+${idx + 1}`,
      open: price,
      high: price,
      low: price,
      close: price,
      pre_close: price
    }));
    mergedStockPrices = [...mergedStockPrices, ...extraStockPriceObjects];

    // 为指数添加等同天数的价格（使用最后一天的价格）
    const lastIndexPrice = indexPrices[indexPrices.length - 1];
    const extraIndexPrices = extraStockPrices.map((_, idx) => ({
      trade_date: `T+${idx + 1}`,
      open: lastIndexPrice.close,
      high: lastIndexPrice.close,
      low: lastIndexPrice.close,
      close: lastIndexPrice.close,
      pre_close: lastIndexPrice.close
    }));
    mergedIndexPrices = [...mergedIndexPrices, ...extraIndexPrices];
  }

  const totalDays = mergedStockPrices.length;

  // 验证输入
  if (n < 1 || n > totalDays) {
    return {
      error: `n 必须在 1 到 ${totalDays} 之间`,
      n: n,
      totalDays: totalDays
    };
  }

  if (mergedStockPrices.length !== mergedIndexPrices.length) {
    return {
      error: '股票价格和指数价格的天数不匹配',
      stockDays: mergedStockPrices.length,
      indexDays: mergedIndexPrices.length
    };
  }

  // 计算后n日的偏离值
  const startIndex = totalDays - n;
  const endIndex = totalDays - 1;

  // 找到后n日内股票的最低价格
  const lowestInfo = findLowestPrice(mergedStockPrices, startIndex, endIndex);

  if (!lowestInfo) {
    return {
      error: '无法找到最低价格'
    };
  }

  // 获取现在的价格（最后一天）
  const currentStockClose = mergedStockPrices[endIndex].close;
  const currentIndexClose = mergedIndexPrices[endIndex].close;

  // 获取股票最低价对应日期的指数pre_close
  const indexLowPreClose = mergedIndexPrices[lowestInfo.lowIndex].pre_close;

  // 计算偏离值
  const deviation = calculateDeviation(
    currentStockClose,
    lowestInfo.lowPrice,
    currentIndexClose,
    indexLowPreClose
  );

  return {
    success: true,
    n: n,
    totalDays: totalDays,
    hasExtraPrices: extraStockPrices && extraStockPrices.length > 0,
    extraPricesDays: extraStockPrices ? extraStockPrices.length : 0,

    // 股票信息
    stock: {
      currentClose: parseFloat(currentStockClose.toFixed(2)),
      lowestPreClose: parseFloat(lowestInfo.lowPrice.toFixed(2)),
      lowestDate: lowestInfo.lowDate,
      lowestIndex: lowestInfo.lowIndex,
      changePercent: parseFloat(
        (((currentStockClose - lowestInfo.lowPrice) / lowestInfo.lowPrice) * 100).toFixed(2)
      )
    },

    // 指数信息
    index: {
      currentClose: parseFloat(currentIndexClose.toFixed(2)),
      lowestPreClose: parseFloat(indexLowPreClose.toFixed(2)),
      lowestDate: lowestInfo.lowDate,
      lowestIndex: lowestInfo.lowIndex,
      changePercent: parseFloat(
        (((currentIndexClose - indexLowPreClose) / indexLowPreClose) * 100).toFixed(2)
      )
    },

    // 偏离值
    deviation: deviation,

    // 后n日的价格数据
    trailingPrices: {
      stock: mergedStockPrices.slice(startIndex, endIndex + 1),
      index: mergedIndexPrices.slice(startIndex, endIndex + 1)
    }
  };
}

/**
 * 生成模拟涨停价格数组
 *
 * @param {number} lastPrice - 最后一天的收盘价
 * @param {number} limitUpPct - 涨停幅度百分比（例如 10 表示 10%）
 * @param {number} days - 要生成的天数
 * @returns {Array} 模拟涨停后的价格数组
 */
function generateLimitUpPrices(lastPrice, limitUpPct, days) {
  const prices = [];
  let currentPrice = lastPrice;

  for (let i = 0; i < days; i++) {
    currentPrice = currentPrice * (1 + limitUpPct / 100);
    prices.push(parseFloat(currentPrice.toFixed(2)));
  }

  return prices;
}

// 导出函数
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    calculateDeviation,
    findLowestPrice,
    calculateTrailingDeviation,
    generateLimitUpPrices
  };
}

