import logger_config
from loguru import logger
from monitor import StockMonitor

def test_query_stocks():
    """测试 query_stocks 方法"""
    try:
        monitor = StockMonitor()
        
        # 测试获取过去30个交易日的股票数据
        logger.info("开始测试 query_stocks 方法...")
        results = monitor.query_stocks(
            n=30,
            top_n=20,
            threshold=200,
            include_cyb=True,
            include_kcb=False,
            include_bj=False,
            is_sg=False
        )
        
        if not results:
            logger.warning("未获取到任何数据")
            return False
        
        logger.info(f"获取到 {len(results)} 只股票的数据")
        

        # 显示前3只股票的关键信息
        logger.info("\n前3只股票的关键信息:")
        for i, stock in enumerate(results[:20]):
            logger.info(f"\n{i+1}. {stock['ts_code']} - {stock['name']}")
            logger.info(f"   市场: {stock['market']}")
            logger.info(f"   开始价格: {stock['start_price']}")
            logger.info(f"   结束价格: {stock['end_price']}")
            logger.info(f"   涨幅: {stock['price_change_pct']}%")
            logger.info(f"   指数涨幅: {stock['index_change_pct']}%")
            logger.info(f"   偏离值: {stock['deviation']}%")
            logger.info(f"   ---")
            logger.info(f"   最低价格: {stock['low_price']}")
            logger.info(f"   最低价格日期: {stock['low_date']}")
            logger.info(f"   从最低价到结束价的涨幅: {stock['price_change_low_pct']}%")
            logger.info(f"   指数从最低价日期到结束日期的涨幅: {stock['index_change_low_pct']}%")
            logger.info(f"   基于最低价的偏离值: {stock['deviation_low']}%")
            logger.info(f"   从最低价到结束价的交易日周期: {stock['deviation_date_range']}")

            # 显示 t+i 数据
            logger.info(f"   --- t+i 数据 ---")
            for j in range(1, 7):
                ti_key = f't+{j}'
                if ti_key in stock:
                    ti_data = stock[ti_key]
                    logger.info(f"   {ti_key}: 日期={ti_data['low_date']}, 涨停价={ti_data['end_zhangting_price']}, 涨幅={ti_data['price_change_pct']}%, 偏离值={ti_data['deviation']}%, 异动={ti_data['is_abnormal']}")

        logger.info("\n✓ 测试通过！")
        return True
        
    except Exception as e:
        logger.error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_query_stocks()
    exit(0 if success else 1)