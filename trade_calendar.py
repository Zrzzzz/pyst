"""
交易日历管理模块
提供交易日期相关的工具函数
"""
from datetime import datetime, timedelta
import logger_config  # 必须在导入 logger 之前
from loguru import logger
from database import get_session, close_session, TradeCal


class TradeCalendarManager:
    """交易日历管理类"""
    
    def __init__(self):
        self.session = get_session()
    
    def __del__(self):
        close_session(self.session)
    
    def is_trading_day(self, date_str, exchange='SSE'):
        """检查指定日期是否为交易日"""
        try:
            trade_cal = self.session.query(TradeCal).filter(
                TradeCal.exchange == exchange,
                TradeCal.cal_date == date_str
            ).first()
            
            if not trade_cal:
                logger.warning(f"未找到 {date_str} 的交易日历数据")
                return None
            
            return trade_cal.is_open == '1'
        except Exception as e:
            logger.error(f"检查交易日失败: {e}")
            raise
    
    def get_next_trading_day(self, date_str, exchange='SSE'):
        """获取下一个交易日"""
        try:
            next_day = self.session.query(TradeCal).filter(
                TradeCal.exchange == exchange,
                TradeCal.cal_date > date_str,
                TradeCal.is_open == '1'
            ).order_by(TradeCal.cal_date).first()
            
            return next_day.cal_date if next_day else None
        except Exception as e:
            logger.error(f"获取下一个交易日失败: {e}")
            raise
    
    def get_prev_trading_day(self, date_str, exchange='SSE'):
        """获取上一个交易日"""
        try:
            prev_day = self.session.query(TradeCal).filter(
                TradeCal.exchange == exchange,
                TradeCal.cal_date < date_str,
                TradeCal.is_open == '1'
            ).order_by(TradeCal.cal_date.desc()).first()
            
            return prev_day.cal_date if prev_day else None
        except Exception as e:
            logger.error(f"获取上一个交易日失败: {e}")
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
    
    def get_trading_days_list(self, start_date, end_date, exchange='SSE'):
        """获取日期范围内的所有交易日列表"""
        try:
            trading_days = self.session.query(TradeCal).filter(
                TradeCal.exchange == exchange,
                TradeCal.cal_date >= start_date,
                TradeCal.cal_date <= end_date,
                TradeCal.is_open == '1'
            ).order_by(TradeCal.cal_date).all()
            
            return [day.cal_date for day in trading_days]
        except Exception as e:
            logger.error(f"获取交易日列表失败: {e}")
            raise
    
    def get_nth_trading_day_before(self, date_str, n, exchange='SSE'):
        """获取指定日期前第N个交易日"""
        try:
            trading_days = self.session.query(TradeCal).filter(
                TradeCal.exchange == exchange,
                TradeCal.cal_date < date_str,
                TradeCal.is_open == '1'
            ).order_by(TradeCal.cal_date.desc()).limit(n).all()
            
            if len(trading_days) < n:
                logger.warning(f"找不到 {n} 个交易日")
                return None
            
            return trading_days[-1].cal_date
        except Exception as e:
            logger.error(f"获取第 {n} 个交易日失败: {e}")
            raise
    
    def get_nth_trading_day_after(self, date_str, n, exchange='SSE'):
        """获取指定日期后第N个交易日"""
        try:
            trading_days = self.session.query(TradeCal).filter(
                TradeCal.exchange == exchange,
                TradeCal.cal_date > date_str,
                TradeCal.is_open == '1'
            ).order_by(TradeCal.cal_date).limit(n).all()

            if len(trading_days) < n:
                logger.warning(f"找不到 {n} 个交易日")
                return None

            return trading_days[-1].cal_date
        except Exception as e:
            logger.error(f"获取第 {n} 个交易日失败: {e}")
            raise

    def get_last_n_trading_days(self, n, end_date=None, exchange='SSE'):
        """
        获取截至指定日期的最后N个交易日列表

        参数:
            n: 交易日数量
            end_date: 结束日期 (YYYYMMDD)，默认为今天
            exchange: 交易所代码

        返回:
            交易日列表，按时间升序排列
        """
        try:
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')

            trading_days = self.session.query(TradeCal).filter(
                TradeCal.exchange == exchange,
                TradeCal.cal_date <= end_date,
                TradeCal.is_open == '1'
            ).order_by(TradeCal.cal_date.desc()).limit(n).all()

            if not trading_days:
                logger.warning(f"未找到任何交易日")
                return []

            # 反转列表使其按时间升序排列
            result = [day.cal_date for day in reversed(trading_days)]
            logger.info(f"获取最后 {len(result)} 个交易日: {result[0]} - {result[-1]}")
            return result
        except Exception as e:
            logger.error(f"获取最后 {n} 个交易日失败: {e}")
            raise

