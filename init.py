#!/usr/bin/env python3
"""
项目初始化脚本
用于初始化数据库和获取基础数据
"""
import os
import sys
from dotenv import load_dotenv
import logger_config  # 必须在导入 logger 之前
from loguru import logger
from database import init_db
from data_manager import DataManager

# 加载环境变量
load_dotenv()


def main():
    """主函数"""
    print("=" * 50)
    print("股票异动监控系统 - 项目初始化")
    print("=" * 50)
    
    # 检查 Tushare Token
    token = os.getenv("TUSHARE_TOKEN", "").strip()
    if not token:
        print("\n❌ 错误：未设置 TUSHARE_TOKEN")
        print("请在 .env 文件中配置你的 Tushare Token")
        print("获取 Token: https://tushare.pro")
        return False
    
    print("\n✅ Tushare Token 已配置")
    
    # 初始化数据库
    print("\n📦 初始化数据库...")
    try:
        init_db()
        print("✅ 数据库初始化成功")
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return False
    
    # 获取股票基本信息
    print("\n📥 获取股票基本信息...")
    try:
        dm = DataManager()
        df = dm.fetch_stock_basic()
        print(f"✅ 成功获取 {len(df)} 只股票基本信息")
    except Exception as e:
        print(f"❌ 获取股票基本信息失败: {e}")
        return False
    
    # 获取交易日历
    print("\n📅 获取交易日历...")
    try:
        dm = DataManager()
        # 获取上交所交易日历
        dm.fetch_trade_cal('SSE')
        print("✅ 成功获取上交所交易日历")

        # 获取深交所交易日历
        dm.fetch_trade_cal('SZSE')
        print("✅ 成功获取深交所交易日历")
    except Exception as e:
        print(f"⚠️  获取交易日历失败: {e}")

    # 获取指数数据
    print("\n📥 获取指数数据...")
    try:
        dm = DataManager()
        # 获取上证指数数据
        dm.fetch_index_daily('000001.SH')
        print("✅ 成功获取上证指数数据")
    except Exception as e:
        print(f"⚠️  获取指数数据失败: {e}")
    
    print("\n" + "=" * 50)
    print("✅ 初始化完成！")
    print("=" * 50)
    print("\n下一步：")
    print("1. 运行应用: python app.py")
    print("2. 访问: http://localhost:5000")
    print("\n提示：")
    print("- 首次运行可能需要获取更多股票数据")
    print("- 建议在交易时间后运行，以获取最新数据")
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

