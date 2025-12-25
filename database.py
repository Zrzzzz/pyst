"""
数据库模型和初始化模块
使用 SQLAlchemy ORM 定义数据库模型
"""
from sqlalchemy import create_engine, Column, String, Float, Date, DateTime, Integer, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logger_config  # 必须在导入 logger 之前
from loguru import logger

# 数据库配置
DATABASE_URL = "sqlite:///stock_data.db"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class StockBasic(Base):
    """股票基本信息表"""
    __tablename__ = "stock_basic"

    ts_code = Column(String(10), primary_key=True, comment="TS代码")
    symbol = Column(String(10), comment="股票代码")
    name = Column(String(50), comment="股票名称")
    area = Column(String(50), comment="地域")
    industry = Column(String(50), comment="所属行业")
    fullname = Column(String(100), nullable=True, comment="股票全称")
    enname = Column(String(100), nullable=True, comment="英文全称")
    cnspell = Column(String(50), nullable=True, comment="拼音缩写")
    market = Column(String(20), comment="市场类型（主板/创业板/科创板/CDR）")
    exchange = Column(String(10), nullable=True, comment="交易所代码")
    curr_type = Column(String(10), nullable=True, comment="交易货币")
    list_status = Column(String(1), nullable=True, comment="上市状态 L上市 D退市 P暂停上市")
    list_date = Column(String(10), comment="上市日期")
    delist_date = Column(String(10), nullable=True, comment="退市日期")
    is_hs = Column(String(1), nullable=True, comment="是否沪深港通标的，N否 H沪股通 S深股通")
    act_name = Column(String(100), nullable=True, comment="实控人名称")
    act_ent_type = Column(String(50), nullable=True, comment="实控人企业性质")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class StockDailyData(Base):
    """股票日线数据表"""
    __tablename__ = "stock_daily_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String(10), comment="股票代码")
    trade_date = Column(String(10), comment="交易日期")
    open = Column(Float, comment="开盘价")
    high = Column(Float, comment="最高价")
    low = Column(Float, comment="最低价")
    close = Column(Float, comment="收盘价")
    pre_close = Column(Float, nullable=True, comment="昨收价【除权价，前复权】")
    change = Column(Float, nullable=True, comment="涨跌额")
    pct_chg = Column(Float, nullable=True, comment="涨跌幅")
    vol = Column(Float, comment="成交量（手）")
    amount = Column(Float, comment="成交额（千元）")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    __table_args__ = (
        UniqueConstraint('ts_code', 'trade_date', name='uq_ts_code_trade_date'),
    )


class IndexDailyData(Base):
    """指数日线数据表"""
    __tablename__ = "index_daily_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String(10), comment="指数代码")
    trade_date = Column(String(10), comment="交易日期")
    open = Column(Float, comment="开盘点数")
    high = Column(Float, comment="最高点数")
    low = Column(Float, comment="最低点数")
    close = Column(Float, comment="收盘点数")
    pre_close = Column(Float, nullable=True, comment="昨日收盘点")
    change = Column(Float, nullable=True, comment="涨跌点")
    pct_chg = Column(Float, nullable=True, comment="涨跌幅（%）")
    vol = Column(Float, comment="成交量")
    amount = Column(Float, comment="成交额")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    __table_args__ = (
        UniqueConstraint('ts_code', 'trade_date', name='uq_index_ts_code_trade_date'),
    )


class TradeCal(Base):
    """交易日历表"""
    __tablename__ = "trade_cal"

    id = Column(Integer, primary_key=True, autoincrement=True)
    exchange = Column(String(10), comment="交易所代码 SSE上交所 SZSE深交所")
    cal_date = Column(String(10), comment="日历日期")
    is_open = Column(String(1), comment="是否交易 0休市 1交易")
    pretrade_date = Column(String(10), nullable=True, comment="上一个交易日")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    __table_args__ = (
        UniqueConstraint('exchange', 'cal_date', name='uq_exchange_cal_date'),
    )


class QueryCache(Base):
    """查询缓存表 - 模拟 Redis 缓存"""
    __tablename__ = "query_cache"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cache_key = Column(String(255), unique=True, index=True, comment="缓存键")
    cache_value = Column(String(65535), comment="缓存值（JSON 格式）")
    cache_date = Column(String(10), comment="缓存日期")
    expire_at = Column(DateTime, comment="过期时间")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    __table_args__ = (
        UniqueConstraint('cache_key', 'cache_date', name='uq_cache_key_date'),
    )


def init_db():
    """初始化数据库，创建所有表"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("数据库初始化成功")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise


def get_session():
    """获取数据库会话"""
    return SessionLocal()


def close_session(session):
    """关闭数据库会话"""
    if session:
        session.close()

