"""
数据管理模块
负责从 Tushare 获取股票数据并存储到 SQLite 数据库
"""
import os
import tushare as ts
from datetime import datetime, timedelta
from tqdm import tqdm
import logger_config  # 必须在导入 logger 之前
from loguru import logger
from database import get_session, close_session, StockBasic, StockDailyData, IndexDailyData, TradeCal

# 初始化 Tushare
TUSHARE_TOKEN = os.getenv("TUSHARE_TOKEN", "")
if not TUSHARE_TOKEN:
    logger.warning("未设置 TUSHARE_TOKEN 环境变量，请在 .env 文件中配置")

ts.set_token(TUSHARE_TOKEN)
pro = ts.pro_api()


class DataManager:
    """数据管理类"""
    
    def __init__(self):
        self.session = get_session()
    
    def __del__(self):
        close_session(self.session)
    
    def fetch_stock_basic(self, exchange='', list_status='L', market=''):
        """
        获取股票基本信息

        参数:
            exchange: 交易所 SSE上交所 SZSE深交所 BSE北交所，默认为空（全部）
            list_status: 上市状态 L上市 D退市 P暂停上市，默认为L（上市）
            market: 市场类别 主板/创业板/科创板/CDR/北交所，默认为空（全部）
        """
        try:
            logger.info(f"开始获取股票基本信息... (exchange={exchange}, list_status={list_status}, market={market})")

            # 调用 Tushare API 获取股票基本信息（获取所有字段）
            df = pro.stock_basic(
                exchange=exchange,
                list_status=list_status,
                market=market
            )

            if df.empty:
                logger.warning("未获取到任何股票数据")
                return df

            # 批量插入或更新数据
            for _, row in df.iterrows():
                stock = StockBasic(
                    ts_code=row['ts_code'],
                    symbol=row['symbol'],
                    name=row['name'],
                    area=row.get('area', ''),
                    industry=row.get('industry', ''),
                    fullname=row.get('fullname', None),
                    enname=row.get('enname', None),
                    cnspell=row.get('cnspell', None),
                    market=row.get('market', ''),
                    exchange=row.get('exchange', None),
                    curr_type=row.get('curr_type', None),
                    list_status=row.get('list_status', None),
                    list_date=row.get('list_date', ''),
                    delist_date=row.get('delist_date', None),
                    is_hs=row.get('is_hs', None),
                    act_name=row.get('act_name', None),
                    act_ent_type=row.get('act_ent_type', None)
                )
                self.session.merge(stock)

            self.session.commit()
            logger.info(f"成功获取 {len(df)} 只股票基本信息")
            return df
        except Exception as e:
            logger.error(f"获取股票基本信息失败: {e}")
            self.session.rollback()
            raise
    
    def count_trading_days(self, start_date, end_date, exchange='SSE'):
        """计算日期范围内的交易日数量"""
        try:
            count = self.session.query(TradeCal).filter(
                TradeCal.exchange == exchange,
                TradeCal.cal_date >= start_date,
                TradeCal.cal_date <= end_date,
                TradeCal.is_open == '1'
            ).count()
            return count
        except Exception as e:
            logger.error(f"计算交易日数量失败: {e}")
            raise

    def fetch_stock_daily(self, ts_code, start_date=None, end_date=None):
        """
        获取单只股票的日线数据

        参数:
            ts_code: 股票代码
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
        """
        try:
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')

            logger.info(f"获取 {ts_code} 日线数据: {start_date} - {end_date}")
            df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)

            if df.empty:
                logger.warning(f"{ts_code} 未获取到日线数据")
                return df

            for _, row in df.iterrows():
                daily = StockDailyData(
                    ts_code=row['ts_code'],
                    trade_date=row['trade_date'],
                    open=row['open'],
                    high=row['high'],
                    low=row['low'],
                    close=row['close'],
                    pre_close=row.get('pre_close', None),
                    change=row.get('change', None),
                    pct_chg=row.get('pct_chg', None),
                    vol=row['vol'],
                    amount=row['amount']
                )
                self.session.merge(daily)

            self.session.commit()
            logger.info(f"成功获取 {ts_code} 的 {len(df)} 条日线数据")
            return df
        except Exception as e:
            logger.error(f"获取 {ts_code} 日线数据失败: {e}")
            self.session.rollback()
            raise

    def fetch_stock_daily_batch(self, ts_codes, start_date=None, end_date=None, exchange='SSE'):
        """
        批量获取多只股票的日线数据

        根据交易日期个数和 API 限制（6000条数据），自动分批请求

        参数:
            ts_codes: 股票代码列表或逗号分隔的字符串
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            exchange: 交易所 (SSE/SZSE)，用于计算交易日数量
        """
        try:
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')

            # 转换为列表
            if isinstance(ts_codes, str):
                ts_codes = [code.strip() for code in ts_codes.split(',')]

            logger.info(f"批量获取 {len(ts_codes)} 只股票的日线数据: {start_date} - {end_date}")

            # 检查开始日期和结束日期是否都有股票数据
            start_date_has_data = self.session.query(StockDailyData).filter(
                StockDailyData.trade_date == start_date
            ).first() is not None

            end_date_has_data = self.session.query(StockDailyData).filter(
                StockDailyData.trade_date == end_date
            ).first() is not None

            if start_date_has_data and end_date_has_data:
                logger.info(f"开始日期 {start_date} 和结束日期 {end_date} 都有股票数据，跳过获取")
                return None

            # 根据缺失的数据情况分别处理
            if not end_date_has_data:
                # 缺少 end_date 的数据，从最新交易日期的下一个交易日开始获取
                latest_daily = self.session.query(StockDailyData).order_by(
                    StockDailyData.trade_date.desc()
                ).first()

                if latest_daily:
                    latest_trade_date = latest_daily.trade_date
                    logger.info(f"缺少结束日期数据，数据库中最新交易日期: {latest_trade_date}")

                    # 获取最新交易日期的下一个交易日
                    next_trade_date = self.session.query(TradeCal).filter(
                        TradeCal.exchange == exchange,
                        TradeCal.cal_date > latest_trade_date,
                        TradeCal.is_open == '1'
                    ).order_by(TradeCal.cal_date.asc()).first()

                    if next_trade_date:
                        start_date = next_trade_date.cal_date
                        logger.info(f"更新开始日期为最新交易日期的下一个交易日: {start_date}")
                    else:
                        logger.warning(f"未找到 {latest_trade_date} 之后的交易日，使用原始开始日期: {start_date}")
                else:
                    logger.info("数据库中无股票数据，使用原始开始日期")

            elif not start_date_has_data:
                # 缺少 start_date 的数据，从最前面的交易日的上一个交易日结束获取
                earliest_daily = self.session.query(StockDailyData).order_by(
                    StockDailyData.trade_date.asc()
                ).first()

                if earliest_daily:
                    earliest_trade_date = earliest_daily.trade_date
                    logger.info(f"缺少开始日期数据，数据库中最早交易日期: {earliest_trade_date}")

                    # 获取最早交易日期的上一个交易日
                    prev_trade_date = self.session.query(TradeCal).filter(
                        TradeCal.exchange == exchange,
                        TradeCal.cal_date < earliest_trade_date,
                        TradeCal.is_open == '1'
                    ).order_by(TradeCal.cal_date.desc()).first()

                    if prev_trade_date:
                        end_date = prev_trade_date.cal_date
                        logger.info(f"更新结束日期为最早交易日期的上一个交易日: {end_date}")
                    else:
                        logger.warning(f"未找到 {earliest_trade_date} 之前的交易日，使用原始结束日期: {end_date}")
                else:
                    logger.info("数据库中无股票数据，使用原始结束日期")

            # 计算交易日数量
            trading_days_count = self.count_trading_days(start_date, end_date, exchange)
            logger.info(f"日期范围内交易日数量: {trading_days_count}")

            # API 限制：
            # 1. 每次请求最多 6000 条数据
            # 2. 每次请求最多 1000 只股票
            max_data_per_request = 6000
            max_stocks_by_data = max(1, max_data_per_request // trading_days_count)
            max_stocks_per_request = min(1000, max_stocks_by_data)

            logger.info(f"每次请求最多包含 {max_stocks_per_request} 只股票")

            # 计算总批次
            total_batches = (len(ts_codes) + max_stocks_per_request - 1) // max_stocks_per_request
            logger.info(f"总共需要请求 {total_batches} 批")

            # 分批请求
            all_data = []
            with tqdm(total=len(ts_codes), desc="获取股票日线数据", unit="只") as pbar:
                for i in range(0, len(ts_codes), max_stocks_per_request):
                    batch_codes = ts_codes[i:i + max_stocks_per_request]
                    batch_str = ','.join(batch_codes)
                    batch_num = i // max_stocks_per_request + 1

                    try:
                        df = pro.daily(
                            ts_code=batch_str,
                            start_date=start_date,
                            end_date=end_date
                        )

                        if df.empty:
                            logger.warning(f"批次 {batch_num}/{total_batches} 未获取到数据")
                            pbar.update(len(batch_codes))
                            continue

                        # 保存数据
                        for _, row in df.iterrows():
                            daily = StockDailyData(
                                ts_code=row['ts_code'],
                                trade_date=row['trade_date'],
                                open=row['open'],
                                high=row['high'],
                                low=row['low'],
                                close=row['close'],
                                pre_close=row.get('pre_close', None),
                                change=row.get('change', None),
                                pct_chg=row.get('pct_chg', None),
                                vol=row['vol'],
                                amount=row['amount']
                            )
                            self.session.merge(daily)

                        all_data.append(df)
                        # logger.info(f"批次 {batch_num}/{total_batches} 成功获取 {len(df)} 条数据")
                        pbar.update(len(batch_codes))

                    except Exception as batch_error:
                        logger.error(f"批次 {batch_num}/{total_batches} 请求失败: {batch_error}")
                        pbar.update(len(batch_codes))
                        continue

            self.session.commit()

            if all_data:
                total_rows = sum(len(df) for df in all_data)
                logger.info(f"批量获取完成，共获取 {total_rows} 条日线数据")
                import pandas as pd
                return pd.concat(all_data, ignore_index=True)
            else:
                logger.warning("未获取到任何日线数据")
                return None

        except Exception as e:
            logger.error(f"批量获取日线数据失败: {e}")
            self.session.rollback()
            raise
    
    def fetch_index_daily(self, ts_code, start_date=None, end_date=None):
        """获取指数日线数据"""
        try:
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')

            logger.info(f"获取 {ts_code} 指数数据: {start_date} - {end_date}")
            df = pro.index_daily(ts_code=ts_code, start_date=start_date, end_date=end_date)

            if df.empty:
                logger.warning(f"{ts_code} 未获取到指数数据")
                return df

            for _, row in df.iterrows():
                daily = IndexDailyData(
                    ts_code=ts_code,
                    trade_date=row['trade_date'],
                    open=row['open'],
                    high=row['high'],
                    low=row['low'],
                    close=row['close'],
                    pre_close=row.get('pre_close', None),
                    change=row.get('change', None),
                    pct_chg=row.get('pct_chg', None),
                    vol=row['vol'],
                    amount=row['amount']
                )
                self.session.merge(daily)

            self.session.commit()
            logger.info(f"成功获取 {ts_code} 的 {len(df)} 条指数数据")
            return df
        except Exception as e:
            logger.error(f"获取 {ts_code} 指数数据失败: {e}")
            self.session.rollback()
            raise

    def fetch_index_daily_batch(self, ts_codes, start_date=None, end_date=None, exchange='SSE'):
        """
        批量获取多个指数的日线数据（逐个处理）

        由于指数接口不支持批量请求，需要逐个获取每个指数的数据

        参数:
            ts_codes: 指数代码列表或逗号分隔的字符串
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            exchange: 交易所 (SSE/SZSE)，用于查询下一个交易日
        """
        try:
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')

            # 转换为列表
            if isinstance(ts_codes, str):
                ts_codes = [code.strip() for code in ts_codes.split(',')]

            logger.info(f"批量获取 {len(ts_codes)} 个指数的日线数据: {start_date} - {end_date}")

            # 检查开始日期和结束日期是否都有指数数据
            start_date_has_data = self.session.query(IndexDailyData).filter(
                IndexDailyData.trade_date == start_date
            ).first() is not None

            end_date_has_data = self.session.query(IndexDailyData).filter(
                IndexDailyData.trade_date == end_date
            ).first() is not None

            if start_date_has_data and end_date_has_data:
                logger.info(f"开始日期 {start_date} 和结束日期 {end_date} 都有指数数据，跳过获取")
                return None

            # 根据缺失的数据情况分别处理
            if not end_date_has_data:
                # 缺少 end_date 的数据，从最新交易日期的下一个交易日开始获取
                latest_daily = self.session.query(IndexDailyData).order_by(
                    IndexDailyData.trade_date.desc()
                ).first()

                if latest_daily:
                    latest_trade_date = latest_daily.trade_date
                    logger.info(f"缺少结束日期数据，数据库中最新交易日期: {latest_trade_date}")

                    # 获取最新交易日期的下一个交易日
                    next_trade_date = self.session.query(TradeCal).filter(
                        TradeCal.exchange == exchange,
                        TradeCal.cal_date > latest_trade_date,
                        TradeCal.is_open == '1'
                    ).order_by(TradeCal.cal_date.asc()).first()

                    if next_trade_date:
                        start_date = next_trade_date.cal_date
                        logger.info(f"更新开始日期为最新交易日期的下一个交易日: {start_date}")
                    else:
                        logger.warning(f"未找到 {latest_trade_date} 之后的交易日，使用原始开始日期: {start_date}")
                else:
                    logger.info("数据库中无指数数据，使用原始开始日期")

            elif not start_date_has_data:
                # 缺少 start_date 的数据，从最前面的交易日的上一个交易日结束获取
                earliest_daily = self.session.query(IndexDailyData).order_by(
                    IndexDailyData.trade_date.asc()
                ).first()

                if earliest_daily:
                    earliest_trade_date = earliest_daily.trade_date
                    logger.info(f"缺少开始日期数据，数据库中最早交易日期: {earliest_trade_date}")

                    # 获取最早交易日期的上一个交易日
                    prev_trade_date = self.session.query(TradeCal).filter(
                        TradeCal.exchange == exchange,
                        TradeCal.cal_date < earliest_trade_date,
                        TradeCal.is_open == '1'
                    ).order_by(TradeCal.cal_date.desc()).first()

                    if prev_trade_date:
                        end_date = prev_trade_date.cal_date
                        logger.info(f"更新结束日期为最早交易日期的上一个交易日: {end_date}")
                    else:
                        logger.warning(f"未找到 {earliest_trade_date} 之前的交易日，使用原始结束日期: {end_date}")
                else:
                    logger.info("数据库中无指数数据，使用原始结束日期")

            # 逐个获取每个指数的数据
            all_data = []
            with tqdm(total=len(ts_codes), desc="获取指数日线数据", unit="个") as pbar:
                for ts_code in ts_codes:
                    try:
                        logger.info(f"获取指数 {ts_code} 的日线数据: {start_date} - {end_date}")
                        df = pro.index_daily(
                            ts_code=ts_code,
                            start_date=start_date,
                            end_date=end_date
                        )

                        if df.empty:
                            logger.warning(f"指数 {ts_code} 未获取到数据")
                            pbar.update(1)
                            continue

                        # 保存数据
                        for _, row in df.iterrows():
                            daily = IndexDailyData(
                                ts_code=row['ts_code'],
                                trade_date=row['trade_date'],
                                open=row['open'],
                                high=row['high'],
                                low=row['low'],
                                close=row['close'],
                                pre_close=row.get('pre_close', None),
                                change=row.get('change', None),
                                pct_chg=row.get('pct_chg', None),
                                vol=row['vol'],
                                amount=row['amount']
                            )
                            self.session.merge(daily)

                        all_data.append(df)
                        logger.info(f"成功获取指数 {ts_code} 的 {len(df)} 条数据")
                        pbar.update(1)

                    except Exception as index_error:
                        logger.error(f"获取指数 {ts_code} 失败: {index_error}")
                        pbar.update(1)
                        continue

            self.session.commit()

            if all_data:
                total_rows = sum(len(df) for df in all_data)
                logger.info(f"批量获取完成，共获取 {total_rows} 条指数日线数据")
                import pandas as pd
                return pd.concat(all_data, ignore_index=True)
            else:
                logger.warning("未获取到任何指数日线数据")
                return None

        except Exception as e:
            logger.error(f"批量获取指数日线数据失败: {e}")
            self.session.rollback()
            raise

    def refresh_index_daily(self, ts_codes, days=40, exchange='SSE'):
        """
        刷新指数日线数据（最近40天）

        参数:
            ts_codes: 指数代码列表或逗号分隔的字符串
            days: 刷新天数，默认40天
            exchange: 交易所 (SSE/SZSE)
        """
        try:
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')

            logger.info(f"刷新指数日线数据，时间范围: {start_date} - {end_date}")
            return self.fetch_index_daily_batch(ts_codes, start_date, end_date, exchange)
        except Exception as e:
            logger.error(f"刷新指数日线数据失败: {e}")
            raise
    
    def get_stock_list(self):
        """获取所有股票列表"""
        try:
            stocks = self.session.query(StockBasic).all()
            return stocks
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            raise

    def get_latest_trade_cal(self, exchange='SSE'):
        """获取最后一条交易日历记录"""
        try:
            latest = self.session.query(TradeCal).filter(
                TradeCal.exchange == exchange
            ).order_by(TradeCal.cal_date.desc()).first()
            return latest
        except Exception as e:
            logger.error(f"获取最后交易日历失败: {e}")
            raise

    def need_update_trade_cal(self, exchange='SSE', days_threshold=180):
        """检查是否需要更新交易日历"""
        try:
            latest = self.get_latest_trade_cal(exchange)
            if not latest:
                logger.info(f"{exchange} 交易日历为空，需要更新")
                return True

            latest_date = datetime.strptime(latest.cal_date, '%Y%m%d')
            days_diff = (datetime.now() - latest_date).days

            if days_diff >= days_threshold:
                logger.info(f"{exchange} 最后交易日期为 {latest.cal_date}，距今 {days_diff} 天，需要更新")
                return True

            logger.info(f"{exchange} 交易日历无需更新，最后日期为 {latest.cal_date}")
            return False
        except Exception as e:
            logger.error(f"检查交易日历更新状态失败: {e}")
            raise

    def fetch_trade_cal(self, exchange='SSE', start_date=None, end_date=None):
        """获取交易日历数据"""
        try:
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            if not end_date:
                end_date = (datetime.now() + timedelta(days=365)).strftime('%Y%m%d')

            logger.info(f"获取 {exchange} 交易日历: {start_date} - {end_date}")
            df = pro.trade_cal(exchange=exchange, start_date=start_date, end_date=end_date)

            for _, row in df.iterrows():
                trade_cal = TradeCal(
                    exchange=row['exchange'],
                    cal_date=row['cal_date'],
                    is_open=row['is_open'],
                    pretrade_date=row.get('pretrade_date', None)
                )
                self.session.merge(trade_cal)

            self.session.commit()
            logger.info(f"成功获取 {exchange} 的 {len(df)} 条交易日历数据")
            return df
        except Exception as e:
            logger.error(f"获取 {exchange} 交易日历失败: {e}")
            self.session.rollback()
            raise

    def update_trade_cal_if_needed(self, exchange='SSE', days_threshold=180):
        """如果需要则更新交易日历"""
        try:
            if self.need_update_trade_cal(exchange, days_threshold):
                self.fetch_trade_cal(exchange)
                logger.info(f"{exchange} 交易日历更新完成")
                return True
            return False
        except Exception as e:
            logger.error(f"更新交易日历失败: {e}")
            raise

