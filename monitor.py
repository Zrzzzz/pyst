"""
股票异动监控模块
计算股票异动指标和监控规则
"""
from datetime import datetime, timedelta
import logger_config  # 必须在导入 logger 之前
from loguru import logger
from database import get_session, close_session, StockDailyData, IndexDailyData, TradeCal, StockBasic

# 全局常量定义
INDEX_CODES = [
    '000001.SH',  # 上证指数
    '399107.SZ',  # 深证A指
    '399102.SZ',  # 创业板综
    '000688.SH',  # 科创板指
    '899050.BJ'   # 北交所指数
]


class StockMonitor:
    """股票监控类"""
    
    def __init__(self):
        self.session = get_session()
    
    def __del__(self):
        close_session(self.session)


    def get_trading_days(self, start_date, end_date, exchange='SSE'):
        """获取指定日期范围内的交易日"""
        try:
            trading_days = self.session.query(TradeCal).filter(
                TradeCal.exchange == exchange,
                TradeCal.cal_date >= start_date,
                TradeCal.cal_date <= end_date,
                TradeCal.is_open == '1'
            ).order_by(TradeCal.cal_date).all()
            return trading_days
        except Exception as e:
            logger.error(f"获取交易日失败: {e}")
            raise

    def get_last_trading_day(self, exchange='SSE'):
        """获取最后一个交易日"""
        try:
            last_trading_day = self.session.query(TradeCal).filter(
                TradeCal.exchange == exchange,
                TradeCal.is_open == '1'
            ).order_by(TradeCal.cal_date.desc()).first()
            return last_trading_day
        except Exception as e:
            logger.error(f"获取最后交易日失败: {e}")
            raise

    def get_last_n_trading_days(self, n, include_today=False, end_date=None, exchange='SSE'):
        """
        获取过去n个交易日的日期范围

        参数:
            n: 交易日数量
            include_today: 是否包含今天（如果今天是交易日）
            end_date: 结束日期 (YYYYMMDD)，默认为今天
            exchange: 交易所 (SSE/SZSE)

        返回:
            {'start_date': 'YYYYMMDD', 'end_date': 'YYYYMMDD'}
        """
        try:
            today = datetime.now().strftime('%Y%m%d')

            # 如果未指定结束日期，使用今天
            if end_date is None:
                end_date = today

            # 获取最后一个交易日
            last_trading_day = self.get_last_trading_day(exchange)
            if not last_trading_day:
                logger.warning("未找到交易日数据")
                return None

            # 确定结束日期
            if include_today:
                # 检查指定的结束日期是否为交易日
                end_date_trading = self.session.query(TradeCal).filter(
                    TradeCal.exchange == exchange,
                    TradeCal.cal_date == end_date,
                    TradeCal.is_open == '1'
                ).first()

                if end_date_trading:
                    logger.info(f"结束日期 {end_date} 是交易日，包含在内")
                else:
                    # 如果指定的结束日期不是交易日，使用最后交易日
                    end_date = last_trading_day.cal_date
                    logger.info(f"结束日期 {end_date} 不是交易日，使用最后交易日 {end_date}")
            else:
                # 获取指定结束日期之前的最后一个交易日
                prev_trading_day = self.session.query(TradeCal).filter(
                    TradeCal.exchange == exchange,
                    TradeCal.cal_date <= end_date,
                    TradeCal.is_open == '1'
                ).order_by(TradeCal.cal_date.desc()).first()

                if prev_trading_day:
                    end_date = prev_trading_day.cal_date
                    logger.info(f"使用 {end_date} 之前的最后交易日: {end_date}")
                else:
                    logger.warning(f"未找到 {end_date} 之前的交易日")
                    return None

            # 获取过去n个交易日
            trading_days = self.session.query(TradeCal).filter(
                TradeCal.exchange == exchange,
                TradeCal.cal_date <= end_date,
                TradeCal.is_open == '1'
            ).order_by(TradeCal.cal_date.desc()).limit(n).all()

            if len(trading_days) < n:
                logger.warning(f"交易日数据不足，只找到 {len(trading_days)} 个交易日")

            # 排序后获取开始和结束日期
            trading_days = sorted(trading_days, key=lambda x: x.cal_date)
            start_date = trading_days[0].cal_date
            final_end_date = trading_days[-1].cal_date

            logger.info(f"获取过去 {n} 个交易日: {start_date} - {final_end_date}")

            return {
                'start_date': start_date,
                'end_date': final_end_date
            }
        except Exception as e:
            logger.error(f"获取过去 {n} 个交易日失败: {e}")
            raise

    def get_price_change_ranking(self, n, market_filter=None):
        """
        获取过去n个交易日的涨幅排序

        涨幅计算公式: 结束日期收盘价 / 开始日期前一天收盘价 × 100% - 100%

        参数:
            n: 过去n个交易日
            market_filter: 市场过滤条件，可选值为列表，如 ['主板', '创业板', '科创板', '北交所']
                          如果为 None，则不过滤

        返回:
            按涨幅从高到低排序的列表，每项包含:
            {
                'ts_code': 股票代码,
                'start_price': 开始日期的前一天收盘价,
                'end_price': 结束日期收盘价,
                'price_change': 价格变化,
                'price_change_pct': 涨幅百分比,
                'low_price': n日内最低的pre_price价格,
                'low_date': n日内最低的pre_price价格对应的日期,
                'price_change_low_pct': low_price到end_price的涨幅百分比,
                'daily_data': 每个交易日的数据列表，包含 {trade_date, close, pre_close},
                't_plus_data': t+1到t+6的数据，每项包含 {low_price, low_date, end_zhangting_price, price_change_low_pct}
                              其中end_zhangting_price是end_price乘以i个涨停幅度的价格
                              price_change_low_pct是从low_price到end_zhangting_price的涨幅
            }
        """
        try:
            logger.info(f"获取过去 {n} 个交易日的涨幅排序，市场过滤: {market_filter}")

            # 获取数据库中最新的 n 个交易日的日期
            trading_dates = self.session.query(StockDailyData.trade_date).group_by(
                StockDailyData.trade_date
            ).order_by(
                StockDailyData.trade_date.desc()
            ).limit(n).all()

            if not trading_dates or len(trading_dates) < 2:
                logger.warning("数据库中交易日数据不足")
                return []

            # 获取开始和结束日期
            trading_dates = sorted([d[0] for d in trading_dates])
            start_date = trading_dates[0]
            end_date = trading_dates[-1]
            trading_dates_list = trading_dates  # 保存交易日期列表供后续使用

            logger.info(f"数据库中过去 {n} 个交易日: {start_date} - {end_date}")

            # 构建市场过滤条件
            market_condition = None
            if market_filter is not None:
                market_condition = StockBasic.market.in_(market_filter)

            # 获取开始日期的 pre_close（带市场过滤）
            start_query = self.session.query(
                StockDailyData.ts_code,
                StockDailyData.pre_close
            ).join(
                StockBasic,
                StockDailyData.ts_code == StockBasic.ts_code
            ).filter(StockDailyData.trade_date == start_date)

            if market_condition is not None:
                start_query = start_query.filter(market_condition)

            start_data = start_query.all()
            start_data_dict = {row[0]: row[1] for row in start_data}

            # 获取结束日期的收盘价（带市场过滤）
            end_query = self.session.query(
                StockDailyData.ts_code,
                StockDailyData.close
            ).join(
                StockBasic,
                StockDailyData.ts_code == StockBasic.ts_code
            ).filter(StockDailyData.trade_date == end_date)

            if market_condition is not None:
                end_query = end_query.filter(market_condition)

            end_data = end_query.all()
            end_data_dict = {row[0]: row[1] for row in end_data}

            # 获取 n 个交易日内所有股票的 pre_close 数据（用于找最低价）
            all_prices_query = self.session.query(
                StockDailyData.ts_code,
                StockDailyData.trade_date,
                StockDailyData.pre_close
            ).join(
                StockBasic,
                StockDailyData.ts_code == StockBasic.ts_code
            ).filter(
                StockDailyData.trade_date >= start_date,
                StockDailyData.trade_date <= end_date
            )

            if market_condition is not None:
                all_prices_query = all_prices_query.filter(market_condition)

            all_prices_data = all_prices_query.all()

            # 获取每个交易日的所有股票数据（用于 t+i 计算）
            daily_data_query = self.session.query(
                StockDailyData.ts_code,
                StockDailyData.trade_date,
                StockDailyData.close,
                StockDailyData.pre_close
            ).join(
                StockBasic,
                StockDailyData.ts_code == StockBasic.ts_code
            ).filter(
                StockDailyData.trade_date >= start_date,
                StockDailyData.trade_date <= end_date
            )

            if market_condition is not None:
                daily_data_query = daily_data_query.filter(market_condition)

            daily_data = daily_data_query.all()

            # 构建字典：{ts_code: [(trade_date, pre_close), ...]}
            prices_by_stock = {}
            # 构建字典：{ts_code: {trade_date: {close, pre_close}, ...}}
            daily_data_by_stock = {}
            for ts_code, trade_date, pre_close in all_prices_data:
                if ts_code not in prices_by_stock:
                    prices_by_stock[ts_code] = []
                prices_by_stock[ts_code].append((trade_date, pre_close))

            for ts_code, trade_date, close, pre_close in daily_data:
                if ts_code not in daily_data_by_stock:
                    daily_data_by_stock[ts_code] = {}
                daily_data_by_stock[ts_code][trade_date] = {
                    'close': close,
                    'pre_close': pre_close
                }

            # 计算涨幅
            result_list = []
            for ts_code in start_data_dict:
                if ts_code not in end_data_dict:
                    continue

                start_price = start_data_dict[ts_code]
                end_price = end_data_dict[ts_code]

                price_change = end_price - start_price
                price_change_pct = (price_change / start_price * 100)

                # 获取股票基本信息（用于获取市场类型）
                stock_basic = self.session.query(StockBasic).filter(
                    StockBasic.ts_code == ts_code
                ).first()

                # 获取涨停幅度
                limit_up_pct = 0
                if stock_basic:
                    limit_up_pct = self._get_limit_up_percentage(stock_basic.market)

                # 计算 n 日内最低的 pre_price 和对应日期
                low_price = None
                low_date = None
                if ts_code in prices_by_stock:
                    prices_list = prices_by_stock[ts_code]
                    if prices_list:
                        # 找最低的 pre_close
                        min_item = min(prices_list, key=lambda x: float(x[1]))
                        low_date = min_item[0]
                        low_price = float(min_item[1])

                # 计算 n 日内最低的 pre_price 与 end_price 的涨幅百分比
                price_change_low_pct = None
                if low_price is not None and low_price > 0:
                    price_change_low_pct = round((float(end_price) / low_price - 1) * 100, 2)

                # 构建每个交易日的数据列表
                daily_list = []
                if ts_code in daily_data_by_stock:
                    for trade_date in trading_dates:
                        if trade_date in daily_data_by_stock[ts_code]:
                            data = daily_data_by_stock[ts_code][trade_date]
                            daily_list.append({
                                'trade_date': trade_date,
                                'close': round(float(data['close']), 2),
                                'pre_close': round(float(data['pre_close']), 2)
                            })

                # 计算 t+1 到 t+6 的 low_price 和 low_date
                # t+i 表示从第 i+1 个交易日开始到结束日期的数据
                # 例如：过去 n 个交易日是 [d1, d2, ..., dn]
                # t+1 是从 d2 开始到 dn 的数据（抛弃第一个交易日）
                # t+2 是从 d3 开始到 dn 的数据（抛弃前两个交易日）
                t_plus_data = {}
                for i in range(1, 7):
                    # t+i 从第 i 个位置开始（0-indexed，所以是 i）
                    start_idx = i

                    if start_idx < len(daily_list):
                        # 获取从该日期开始到结束日期的所有数据
                        prices_in_range = []

                        for j in range(start_idx, len(daily_list)):
                            prices_in_range.append((daily_list[j]['trade_date'], daily_list[j]['pre_close']))

                        if prices_in_range:
                            # 找最低的 pre_close
                            min_item = min(prices_in_range, key=lambda x: float(x[1]))
                            ti_low_date = min_item[0]
                            ti_low_price = float(min_item[1])

                            # 计算 t+i 的涨停价格（end_price 乘以 i 个涨停幅度）
                            ti_zhangting_price = float(end_price)
                            for _ in range(i):
                                ti_zhangting_price = ti_zhangting_price * (1 + limit_up_pct / 100)
                            ti_zhangting_price = round(ti_zhangting_price, 2)

                            # 计算从该最低价到 t+i 涨停价格的涨幅
                            ti_price_change_low_pct = None
                            if ti_low_price > 0:
                                ti_price_change_low_pct = round((ti_zhangting_price / ti_low_price - 1) * 100, 2)

                            t_plus_data[f't+{i}'] = {
                                'low_price': round(ti_low_price, 2),
                                'low_date': ti_low_date,
                                'end_zhangting_price': ti_zhangting_price,
                                'price_change_low_pct': ti_price_change_low_pct
                            }
                        else:
                            t_plus_data[f't+{i}'] = {
                                'low_price': None,
                                'low_date': None,
                                'end_zhangting_price': None,
                                'price_change_low_pct': None
                            }
                    else:
                        t_plus_data[f't+{i}'] = {
                            'low_price': None,
                            'low_date': None,
                            'end_zhangting_price': None,
                            'price_change_low_pct': None
                        }

                result_list.append({
                    'ts_code': ts_code,
                    'start_price': round(float(start_price), 2),
                    'end_price': round(float(end_price), 2),
                    'price_change': round(float(price_change), 2),
                    'price_change_pct': round(float(price_change_pct), 2),
                    'low_price': round(low_price, 2) if low_price is not None else None,
                    'low_date': low_date,
                    'price_change_low_pct': price_change_low_pct,
                    'daily_data': daily_list,
                    't_plus_data': t_plus_data
                })

            # 按最低起涨幅从高到低排序
            result_list.sort(key=lambda x: x['price_change_low_pct'], reverse=True)

            logger.info(f"共获取 {len(result_list)} 只股票的涨幅数据")
            return result_list
        except Exception as e:
            logger.error(f"获取涨幅排序失败: {e}")
            raise

    def _get_market_type(self, ts_code):
        """根据股票代码获取市场类型"""
        try:
            stock = self.session.query(StockBasic).filter(
                StockBasic.ts_code == ts_code
            ).first()

            if not stock:
                return None

            return stock.market
        except Exception as e:
            logger.error(f"获取 {ts_code} 市场类型失败: {e}")
            return None

    def _get_index_code_by_market(self, market, ts_code=None):
        """
        根据市场类型和股票代码获取对应的指数代码

        参数:
            market: 市场类型
            ts_code: 股票代码，用于区分沪深主板
        """
        # 对于主板，需要根据股票代码区分沪深
        if market == '主板':
            if ts_code and ts_code.endswith('.SZ'):
                # 深市主板使用深证A指
                return '399107.SZ'
            else:
                # 沪市主板使用上证指数
                return '000001.SH'

        # 其他市场的指数映射
        index_map = {
            '创业板': '399102.SZ',    # 创业板综
            '科创板': '000688.SH',    # 科创板指
            '北交所': '899050.BJ'     # 北交所指数
        }
        return index_map.get(market, '000001.SH')  # 默认上证指数

    def _get_limit_up_percentage(self, market):
        """根据市场类型获取涨停幅度"""
        limit_up_map = {
            '主板': 10,
            '创业板': 20,
            '科创板': 20,
            '北交所': 30
        }
        return limit_up_map.get(market, 10)  # 默认10%

    def _calculate_remaining_limit_ups(self, current_price, limit_up_pct):
        """计算还能有多少个涨停"""
        if current_price <= 0:
            return 0

        limit_up_price = current_price * (1 + limit_up_pct / 100)
        count = 0
        price = current_price

        # 计算从当前价格到涨停价格需要多少个涨停
        while price < limit_up_price:
            price = price * (1 + limit_up_pct / 100)
            count += 1

        return count

    def _can_limit_up_next_day(self, current_price, limit_up_pct):
        """判断次日是否能涨停"""
        if current_price <= 0:
            return False

        # 次日涨停价格
        limit_up_price = current_price * (1 + limit_up_pct / 100)
        # 如果当前价格小于涨停价格，说明次日可能涨停
        return True  # 理论上任何价格都可能涨停

    def _can_continuous_limit_up(self, current_price, limit_up_pct):
        """判断后日是否能连续涨停（两个涨停）"""
        if current_price <= 0:
            return False

        # 第一个涨停后的价格
        price_after_first = current_price * (1 + limit_up_pct / 100)
        # 第二个涨停后的价格
        price_after_second = price_after_first * (1 + limit_up_pct / 100)

        # 理论上任何价格都可能连续涨停
        return True

    def query_stocks(self, n, top_n=None, threshold=None, is_sg=False,
                     include_cyb=True, include_kcb=False, include_bj=False):
        """
        查询符合条件的股票信息

        参数:
            n: 过去n个交易日
            top_n: 返回前多少只股票，按涨幅从高到低排序。如果为 None，则返回全部
            threshold: 涨幅阈值（%），用于计算还能涨多少。如果为 None，则不计算
            is_sg: 是否包含新股，默认 False, False 表示过滤掉新股（is_sg=1 的股票）
            include_cyb: 是否包含创业板，默认 True
            include_kcb: 是否包含科创板，默认 False
            include_bj: 是否包含北交所，默认 False

        说明:
            根据股票市场类型自动选择对应指数计算偏离值：
            - 主板: 000001.SH (上证指数) 或 399107.SZ (深证A指)
            - 创业板: 399102.SZ (创业板综)
            - 科创板: 000688.SH (科创板指)
            - 北交所: 899050.BJ (北交所指数)

        返回:
            按涨幅从高到低排序的列表，每项包含:
            {
                'ts_code': 股票代码,
                'name': 股票名称,
                'market': 市场类型,
                'start_price': 开始日期的前一天收盘价,
                'end_price': 结束日期收盘价,
                'price_change_pct': 累计涨幅(%),
                'index_change_pct': 指数涨幅(%),
                'deviation': 基于low_price的偏离值(%),
                'remaining_limit_ups': 还能有x个涨停,
                'start_date': 开始日期,
                'end_date': 结束日期,
                'low_price': n日内最低的pre_price价格,
                'low_date': n日内最低的pre_price价格对应的日期,
                'price_change_low_pct': low_price到end_price的涨幅百分比,
                'index_change_low_pct': 指数从low_date到end_date的涨幅百分比,
                'deviation_low': 基于low_price的偏离值(%),
                'deviation_date_range': low_date到end_date的交易日周期,
                't_plus_data': {
                    't+1': {
                        'low_price': t+1的最低价,
                        'low_date': t+1的最低价日期,
                        'end_zhangting_price': end_price乘以1个涨停幅度的价格,
                        'price_change_low_pct': t+1的涨幅(%)，从low_price到end_zhangting_price
                    },
                    't+2': {
                        'low_price': t+2的最低价,
                        'low_date': t+2的最低价日期,
                        'end_zhangting_price': end_price乘以2个涨停幅度的价格,
                        'price_change_low_pct': t+2的涨幅(%)，从low_price到end_zhangting_price
                    },
                    ...
                    't+6': {...}，end_price乘以6个涨停幅度
                },
                't+1': {
                    'low_price': t+1的最低价,
                    'low_date': t+1的最低价日期,
                    'end_zhangting_price': end_price乘以1个涨停幅度的价格,
                    'price_change_pct': t+1的涨幅(%),
                    'deviation': t+1的偏离值(%),
                    'is_abnormal': 是否超过异动阈值
                },
                't+2': {...},
                't+3': {...},
                't+4': {...},
                't+5': {...},
                't+6': {...}
            }

            说明:
            - t+i 表示从第 i+1 个交易日开始到结束日期的数据
            - 例如：过去 n 个交易日是 [d1, d2, ..., dn]
            - t+1 是从 d2 开始到 dn 的数据（抛弃第一个交易日）
            - t+2 是从 d3 开始到 dn 的数据（抛弃前两个交易日）
            - t+i 的涨幅计算：从该周期的最低价到 end_price 乘以 i 个涨停幅度的价格
        """
        try:
            # 构建市场过滤列表
            market_filter = ['主板']
            if include_cyb:
                market_filter.append('创业板')
            if include_kcb:
                market_filter.append('科创板')
            if include_bj:
                market_filter.append('北交所')

            logger.info(f"查询过去 {n} 个交易日，涨幅阈值 {threshold}%，市场过滤: {market_filter} 的股票")

            # 获取涨幅排序
            price_changes = self.get_price_change_ranking(n, market_filter=market_filter)

            if not price_changes:
                logger.warning("未获取到涨幅数据")
                return []

            # 获取数据库中最新的交易日期作为结束日期
            latest_date = self.session.query(StockDailyData.trade_date).order_by(
                StockDailyData.trade_date.desc()
            ).first()
            if not latest_date:
                logger.warning("未获取到最新交易日期")
                return []

            end_date = latest_date[0]

            # 获取开始和结束日期
            trading_dates = self.session.query(StockDailyData.trade_date).group_by(
                StockDailyData.trade_date
            ).order_by(
                StockDailyData.trade_date.desc()
            ).limit(n).all()

            if trading_dates:
                trading_dates = sorted([d[0] for d in trading_dates])
                start_date = trading_dates[0]
                end_date = trading_dates[-1]
            else:
                logger.warning("无法获取交易日期")
                return []

            # 处理每只股票的数据
            results = []

            # 缓存指数涨幅：key 为 index_code，value 为涨幅
            index_change_cache = {}

            # 预先获取所有需要的指数数据，用于 t+i 计算
            # 使用全局定义的指数代码
            unique_indices = set(INDEX_CODES)

            # 缓存指数数据：key 为 (index_code, trade_date)，value 为 {pre_close, close}
            index_data_cache = {}
            if unique_indices:
                # 获取所有需要的日期范围内的指数数据
                all_dates = set()
                for price_change in price_changes:
                    t_plus_data = price_change.get('t_plus_data', {})
                    for i in range(1, 7):
                        ti_key = f't+{i}'
                        if ti_key in t_plus_data:
                            ti_low_date = t_plus_data[ti_key]['low_date']
                            if ti_low_date:
                                all_dates.add(ti_low_date)
                    all_dates.add(end_date)

                # 批量查询指数数据
                for index_code in unique_indices:
                    index_data = self.session.query(
                        IndexDailyData.trade_date,
                        IndexDailyData.pre_close,
                        IndexDailyData.close
                    ).filter(
                        IndexDailyData.ts_code == index_code,
                        IndexDailyData.trade_date.in_(list(all_dates))
                    ).all()

                    for trade_date, pre_close, close in index_data:
                        index_data_cache[(index_code, trade_date)] = {
                            'pre_close': pre_close,
                            'close': close
                        }

            for price_change in price_changes:
                ts_code = price_change['ts_code']
                price_change_pct = price_change['price_change_pct']
                low_price = price_change['low_price']
                low_date = price_change['low_date']
                price_change_low_pct = price_change['price_change_low_pct']

                # 获取股票基本信息
                stock_basic = self.session.query(StockBasic).filter(
                    StockBasic.ts_code == ts_code
                ).first()

                if not stock_basic:
                    logger.warning(f"未找到 {ts_code} 的基本信息")
                    continue

                # 过滤新股：如果 is_sg=False，过滤掉上市日期到现在少于60个交易日的股票
                if not is_sg:
                    # 计算从上市日期到现在的交易日数
                    trading_days_since_listing = self.session.query(TradeCal).filter(
                        TradeCal.cal_date >= stock_basic.list_date,
                        TradeCal.cal_date <= end_date,
                        TradeCal.is_open == '1'
                    ).count()

                    if trading_days_since_listing < 60:
                        logger.debug(f"过滤掉新股 {ts_code}，上市交易日数: {trading_days_since_listing}")
                        continue

                # 根据股票市场类型获取对应的指数代码
                market = stock_basic.market
                stock_index_code = self._get_index_code_by_market(market, ts_code)

                # 从缓存中获取该股票对应的指数涨幅，如果缓存中没有则计算
                if stock_index_code not in index_change_cache:
                    try:
                        # 获取 start_date 的指数 pre_close
                        index_start = self.session.query(IndexDailyData.pre_close).filter(
                            IndexDailyData.ts_code == stock_index_code,
                            IndexDailyData.trade_date == start_date
                        ).first()

                        # 获取 end_date 的指数收盘价
                        index_end = self.session.query(IndexDailyData.close).filter(
                            IndexDailyData.ts_code == stock_index_code,
                            IndexDailyData.trade_date == end_date
                        ).first()

                        if index_start and index_end and index_start[0] and index_end[0]:
                            start_close = float(index_start[0])
                            end_close = float(index_end[0])
                            change_pct = round((end_close / start_close - 1) * 100, 2)
                            index_change_cache[stock_index_code] = change_pct
                            logger.debug(f"指数 {stock_index_code} 从 {start_date} 到 {end_date} 的涨幅: {change_pct}%")
                        else:
                            logger.warning(f"指数 {stock_index_code} 在 {start_date} 或 {end_date} 的数据不足")
                            index_change_cache[stock_index_code] = 0
                    except Exception as e:
                        logger.warning(f"计算指数涨幅失败 ({stock_index_code}): {e}")
                        index_change_cache[stock_index_code] = 0

                # 从缓存中获取该股票对应的指数涨幅
                index_change_pct = index_change_cache.get(stock_index_code, 0)

                # 计算指数从 low_date 到 end_date 的涨幅
                index_change_low_pct = 0
                try:
                    if low_date:
                        # 获取 low_date 的指数 pre_close
                        index_low = self.session.query(IndexDailyData.pre_close).filter(
                            IndexDailyData.ts_code == stock_index_code,
                            IndexDailyData.trade_date == low_date
                        ).first()

                        # 获取 end_date 的指数收盘价
                        index_end_for_low = self.session.query(IndexDailyData.close).filter(
                            IndexDailyData.ts_code == stock_index_code,
                            IndexDailyData.trade_date == end_date
                        ).first()

                        if index_low and index_end_for_low and index_low[0] and index_end_for_low[0]:
                            low_close = float(index_low[0])
                            end_close_for_low = float(index_end_for_low[0])
                            index_change_low_pct = round((end_close_for_low / low_close - 1) * 100, 2)
                            logger.debug(f"指数 {stock_index_code} 从 {low_date} 到 {end_date} 的涨幅: {index_change_low_pct}%")
                        else:
                            logger.debug(f"指数 {stock_index_code} 在 {low_date} 或 {end_date} 的数据不足")
                            index_change_low_pct = 0
                except Exception as e:
                    logger.warning(f"计算指数从 {low_date} 到 {end_date} 的涨幅失败 ({stock_index_code}): {e}")
                    index_change_low_pct = 0

                # 计算基于 low_price 的偏离值（直接使用 deviation_low）
                deviation_low = price_change_low_pct - index_change_low_pct if price_change_low_pct is not None else None

                # 计算 low_date 到 end_date 的交易日周期
                deviation_date_range = 0
                try:
                    if low_date and end_date:
                        deviation_date_range = self.session.query(TradeCal.cal_date).filter(
                            TradeCal.cal_date >= low_date,
                            TradeCal.cal_date <= end_date,
                            TradeCal.is_open == '1'
                        ).distinct().count()
                        logger.debug(f"股票 {ts_code} 从 {low_date} 到 {end_date} 的交易日数: {deviation_date_range}")
                except Exception as e:
                    logger.warning(f"计算交易日周期失败 ({ts_code}): {e}")
                    deviation_date_range = 0

                # 获取涨停幅度
                limit_up_pct = self._get_limit_up_percentage(market)

                # 计算还能有多少个涨停
                remaining_limit_ups = self._calculate_remaining_limit_ups(
                    price_change['end_price'],
                    limit_up_pct
                )

                # 计算 t+1 到 t+6 的数据
                # 使用 t_plus_data 中的 low_price 和 low_date，计算涨幅和偏离值
                future_data = {}
                t_plus_data = price_change.get('t_plus_data', {})

                for i in range(1, 7):
                    ti_key = f't+{i}'

                    if ti_key in t_plus_data:
                        ti_info = t_plus_data[ti_key]
                        ti_low_date = ti_info['low_date']
                        ti_low_price = ti_info['low_price']
                        ti_end_zhangting_price = ti_info['end_zhangting_price']
                        price_change_ti = ti_info['price_change_low_pct']

                        # 计算指数从 ti_low_date 到 end_date 的涨幅
                        index_change_ti = 0
                        try:
                            if ti_low_date and end_date:
                                # 从缓存中获取指数数据
                                index_low_data = index_data_cache.get((stock_index_code, ti_low_date))
                                index_end_data = index_data_cache.get((stock_index_code, end_date))

                                if index_low_data and index_end_data:
                                    low_close = float(index_low_data['pre_close'])
                                    end_close = float(index_end_data['close'])
                                    if low_close > 0:
                                        index_change_ti = round((end_close / low_close - 1) * 100, 2)
                        except Exception as e:
                            logger.debug(f"计算指数 t+{i} 涨幅失败: {e}")
                            index_change_ti = 0

                        # 计算偏离值
                        deviation_ti = price_change_ti - index_change_ti if price_change_ti is not None else None

                        # 判断是否超过异动阈值
                        is_abnormal = False
                        if threshold is not None and deviation_ti is not None and deviation_ti > threshold:
                            is_abnormal = True

                        future_data[ti_key] = {
                            'low_price': ti_low_price,
                            'low_date': ti_low_date,
                            'end_zhangting_price': ti_end_zhangting_price,
                            'price_change_pct': price_change_ti,
                            'deviation': round(deviation_ti, 2) if deviation_ti is not None else None,
                            'is_abnormal': is_abnormal
                        }
                    else:
                        future_data[ti_key] = {
                            'low_price': None,
                            'low_date': None,
                            'end_zhangting_price': None,
                            'price_change_pct': None,
                            'deviation': None,
                            'is_abnormal': False
                        }

                result_item = {
                    'ts_code': ts_code,
                    'name': stock_basic.name,
                    'market': market,
                    'start_price': price_change['start_price'],
                    'end_price': price_change['end_price'],
                    'price_change_pct': price_change_pct,
                    'index_change_pct': round(index_change_pct, 2),
                    'deviation': round(deviation_low, 2) if deviation_low is not None else None,
                    'remaining_limit_ups': remaining_limit_ups,
                    'start_date': start_date,
                    'end_date': end_date,
                    'low_price': low_price,
                    'low_date': low_date,
                    'price_change_low_pct': price_change_low_pct,
                    'index_change_low_pct': round(index_change_low_pct, 2),
                    'deviation_low': round(deviation_low, 2) if deviation_low is not None else None,
                    'deviation_date_range': deviation_date_range,
                }

                # 添加 t+1 到 t+6 的数据
                for i in range(1, 7):
                    result_item[f't+{i}'] = future_data[f't+{i}']

                results.append(result_item)

            logger.info(f"共找到 {len(results)} 只符合条件的股票")

            # 如果指定了 top_n，只返回前 N 个
            if top_n is not None:
                results = results[:top_n]
                logger.info(f"返回前 {top_n} 只股票")
            else:
                # 如果没有指定 top_n，为了避免超时，默认只返回前 100 只
                if len(results) > 100:
                    logger.warning(f"结果数量过多 ({len(results)} 只)，为避免超时，只返回前 100 只")
                    results = results[:100]

            # 为每只股票添加完整的价格数据
            for result in results:
                ts_code = result['ts_code']
                stock_index_code = self._get_index_code_by_market(result['market'], ts_code)

                # 获取股票在 n 个交易日内的完整价格数据
                stock_prices = self.session.query(
                    StockDailyData.trade_date,
                    StockDailyData.open,
                    StockDailyData.high,
                    StockDailyData.low,
                    StockDailyData.close,
                    StockDailyData.pre_close
                ).filter(
                    StockDailyData.ts_code == ts_code,
                    StockDailyData.trade_date >= start_date,
                    StockDailyData.trade_date <= end_date
                ).order_by(StockDailyData.trade_date.asc()).all()

                # 获取指数在 n 个交易日内的完整价格数据
                index_prices = self.session.query(
                    IndexDailyData.trade_date,
                    IndexDailyData.open,
                    IndexDailyData.high,
                    IndexDailyData.low,
                    IndexDailyData.close,
                    IndexDailyData.pre_close
                ).filter(
                    IndexDailyData.ts_code == stock_index_code,
                    IndexDailyData.trade_date >= start_date,
                    IndexDailyData.trade_date <= end_date
                ).order_by(IndexDailyData.trade_date.asc()).all()

                # 如果查询失败，使用空列表
                if stock_prices is None:
                    stock_prices = []
                if index_prices is None:
                    index_prices = []

                # 转换为字典列表
                result['stock_prices'] = [
                    {
                        'trade_date': row[0],
                        'open': round(float(row[1]), 2),
                        'high': round(float(row[2]), 2),
                        'low': round(float(row[3]), 2),
                        'close': round(float(row[4]), 2),
                        'pre_close': round(float(row[5]), 2)
                    }
                    for row in stock_prices
                ]

                result['index_prices'] = [
                    {
                        'trade_date': row[0],
                        'open': round(float(row[1]), 2),
                        'high': round(float(row[2]), 2),
                        'low': round(float(row[3]), 2),
                        'close': round(float(row[4]), 2),
                        'pre_close': round(float(row[5]), 2)
                    }
                    for row in index_prices
                ]

            return results
        except Exception as e:
            logger.error(f"查询股票失败: {e}")
            raise


if __name__ == "__main__":
    monitor = StockMonitor()
    results = monitor.query_stocks(
        n=10,
        top_n=20,
        threshold=100,
        include_cyb=True,
        include_kcb=False,
        include_bj=False,
        is_sg=False
    )
    for stock in results:
        logger.info(stock)
