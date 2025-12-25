"""
Flask 应用主程序
提供 Web 界面和 API 接口
前后端分离架构
"""
import os
from datetime import datetime
from dotenv import load_dotenv

# 必须在导入其他模块之前加载环境变量
load_dotenv()

from flask import Flask, render_template, jsonify
from flask_cors import CORS
import logger_config  # 必须在导入 logger 之前
from loguru import logger
from database import init_db
from data_manager import DataManager
from trade_calendar import TradeCalendarManager
from monitor import INDEX_CODES
from cache_manager import CacheManager
from apscheduler.schedulers.background import BackgroundScheduler
from config import COPYRIGHT, WATERMARK, CHANGELOG

# 初始化 Flask 应用
app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['JSON_AS_ASCII'] = False

# 启用 CORS
CORS(app)

# 初始化数据库
try:
    init_db()
    logger.info("数据库初始化成功")
except Exception as e:
    logger.error(f"数据库初始化失败: {e}")

# 初始化定时任务
scheduler = BackgroundScheduler()


def refresh_data():
    """定期刷新数据的任务"""
    try:
        logger.info("开始刷新股票和指数数据...")
        dm = DataManager()
        tcm = TradeCalendarManager()
        cache_mgr = CacheManager()

        # 更新交易日历
        logger.info("更新交易日历...")
        dm.update_trade_cal_if_needed('SSE', days_threshold=180)
        dm.update_trade_cal_if_needed('SZSE', days_threshold=180)

        # 更新股票基本信息
        logger.info("更新股票基本信息...")
        dm.fetch_stock_basic()

        # 获取过去40个交易日的数据
        logger.info("获取过去40个交易日的股票数据...")
        try:
            # 判断今天是否为交易日且在17:00之后
            today = datetime.now().strftime('%Y%m%d')
            current_hour = datetime.now().hour

            # 如果今天是交易日且在17:00之后，则包括今天；否则从上一个交易日开始
            if tcm.is_trading_day(today, 'SSE') and current_hour >= 17:
                end_date = today
                logger.info(f"今天 {today} 是交易日且已过17:00，包括今天")
            else:
                end_date = tcm.get_prev_trading_day(today, 'SSE')
                logger.info(f"使用上一个交易日 {end_date} 作为结束日期")

            # 获取最后40个交易日
            trading_days = tcm.get_last_n_trading_days(40, end_date, 'SSE')

            if trading_days:
                start_date = trading_days[0]
                end_date = trading_days[-1]
                logger.info(f"获取 {start_date} 到 {end_date} 的股票数据")

                # 获取所有上市股票列表
                stocks = dm.get_stock_list()
                if stocks:
                    ts_codes = [stock.ts_code for stock in stocks]
                    logger.info(f"准备获取 {len(ts_codes)} 只股票的数据")

                    # 批量获取日线数据
                    dm.fetch_stock_daily_batch(
                        ts_codes,
                        start_date=start_date,
                        end_date=end_date,
                        exchange='SSE'
                    )
                    logger.info("股票日线数据获取完成")
                else:
                    logger.warning("未找到任何股票")
            else:
                logger.warning("未获取到交易日数据")
        except Exception as e:
            logger.error(f"获取股票日线数据失败: {e}")

        # 刷新指数日线数据（最近40个交易日）
        logger.info("刷新指数日线数据...")
        try:
            logger.info(f"准备刷新 {len(INDEX_CODES)} 个指数的数据")

            # 使用与股票相同的日期范围（过去40个交易日）
            if trading_days:
                start_date = trading_days[0]
                end_date = trading_days[-1]
                logger.info(f"获取 {start_date} 到 {end_date} 的指数数据")

                dm.fetch_index_daily_batch(
                    INDEX_CODES,
                    start_date=start_date,
                    end_date=end_date,
                    exchange='SSE'
                )
                logger.info("指数日线数据刷新完成")
            else:
                logger.warning("未获取到交易日数据，跳过指数数据刷新")
        except Exception as e:
            logger.error(f"刷新指数日线数据失败: {e}")

        # 数据刷新完成后，填充缓存
        logger.info("填充双榜缓存...")
        try:
            from monitor import StockMonitor
            monitor = StockMonitor()

            # 获取10日数据
            logger.info("获取10日榜数据...")
            results_10 = monitor.query_stocks(n=10, threshold=100)
            results_10.sort(key=lambda x: x['deviation'], reverse=True)
            results_10 = results_10[:30]

            # 获取30日数据
            logger.info("获取30日榜数据...")
            results_30 = monitor.query_stocks(n=30, threshold=200)
            results_30.sort(key=lambda x: x['deviation'], reverse=True)
            results_30 = results_30[:30]

            # 缓存数据
            cache_data = {
                'stocks_10': results_10,
                'stocks_30': results_30
            }

            # 同时填充当天缓存和上一天缓存
            cache_mgr.set('stocks_both', cache_data, ttl_hours=24)
            cache_mgr.set('stocks_both_prev', cache_data, ttl_hours=24)

            logger.info(f"双榜缓存填充完成，10日榜 {len(results_10)} 只，30日榜 {len(results_30)} 只")
        except Exception as e:
            logger.error(f"填充双榜缓存失败: {e}")

        logger.info("股票和指数数据刷新完成")
    except Exception as e:
        logger.error(f"数据刷新失败: {e}")


# ============ 静态页面路由 ============

@app.route('/')
def index():
    """首页 - 返回静态 HTML"""
    return render_template('index.html',
                         copyright=COPYRIGHT,
                         watermark=WATERMARK,
                         changelog=CHANGELOG)


# ============ API 路由 ============

@app.route('/api/stocks/both')
def api_stocks_both():
    """API: 同时获取10日和30日偏离值榜数据（智能缓存策略）"""
    try:
        cache_mgr = CacheManager()
        current_hour = datetime.now().hour

        # 确定要查询的缓存 key
        # 如果在 17 点之前，查询上一天的数据；否则查询当天的数据
        if current_hour < 17:
            cache_key = 'stocks_both_prev'
            logger.info(f"当前时间 {current_hour}:00，查询上一天的缓存数据")
        else:
            cache_key = 'stocks_both'
            logger.info(f"当前时间 {current_hour}:00，查询当天的缓存数据")

        # 尝试从缓存获取数据
        cached_data = cache_mgr.get(cache_key)

        if cached_data:
            logger.info(f"API 从缓存获取双榜数据 (key: {cache_key})")
            return jsonify({
                'code': 0,
                'message': 'success',
                'data': cached_data,
                'count': {
                    '10': len(cached_data.get('stocks_10', [])),
                    '30': len(cached_data.get('stocks_30', []))
                },
                'from_cache': True
            })

        # 缓存未命中，执行 refresh_data 填充缓存
        logger.warning(f"API 缓存未命中 (key: {cache_key})，执行 refresh_data 填充缓存")
        refresh_data()

        # 再次尝试从缓存获取数据
        cached_data = cache_mgr.get(cache_key)
        if cached_data:
            logger.info(f"API 从新填充的缓存获取双榜数据 (key: {cache_key})")
            return jsonify({
                'code': 0,
                'message': 'success',
                'data': cached_data,
                'count': {
                    '10': len(cached_data.get('stocks_10', [])),
                    '30': len(cached_data.get('stocks_30', []))
                },
                'from_cache': True
            })

        # 缓存仍未命中，返回空数据
        logger.warning("API 缓存仍未命中，返回空数据")
        return jsonify({
            'code': 0,
            'message': 'no cache',
            'data': {'stocks_10': [], 'stocks_30': []},
            'count': {
                '10': 0,
                '30': 0
            },
            'from_cache': False
        })
    except Exception as e:
        logger.error(f"API 获取双榜数据失败: {e}")
        return jsonify({
            'code': 500,
            'message': str(e),
            'data': {'stocks_10': [], 'stocks_30': []}
        }), 500


# 启动定时任务（无论用什么方式启动都会执行）
scheduler.add_job(refresh_data, 'cron', hour=17, minute=0)
scheduler.start()

# 应用启动时立即刷新一次数据
# refresh_data()
logger.info("定时任务已启动，每天 17:00 自动刷新数据")


if __name__ == '__main__':
    logger.info("Flask 应用启动")
    app.run(debug=True, host='127.0.0.1', port=5000)

