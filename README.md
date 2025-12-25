# 股票异动监控系统 (Tushare + SQLite 版本)

一个用于监控热门股票距离触发证监会异动规则的剩余上涨空间的网页应用。

**核心特性**：
- ✅ 使用 **Tushare** 作为数据源（专业的股票数据 API）
- ✅ 使用 **SQLite** 本地数据库存储历史数据
- ✅ **Flask** 前后端框架
- ✅ **UV** 作为 Python 包管理工具
- ✅ 支持数据初始化和定期刷新
- ✅ 实时监控股票异动指标

## 项目概述

该系统通过 Tushare API 获取股票数据，存储到本地 SQLite 数据库，然后监控股票的异动规则，帮助投资者识别哪些股票即将触发证监会的异动规则。

### 监控规则

#### 异常波动规则
1. **3日异常波动**
   - 连续3个交易日内日收盘价格涨跌幅偏离值累计达到 ±20%
   - 公式：偏离值累计 = (期末收盘价/期初前收盘价 - 1) × 100% - (对应指数期末收盘点数/期初前收盘点数 - 1) × 100%

2. **3日换手率异常**
   - 连续3个交易日内日均换手率与前5个交易日的日均换手率比值达到30倍
   - 且累计换手率达到20%

#### 严重异常波动规则
1. **10日严重异常波动**
   - 连续10个交易日内涨幅达到 +100%（价格翻倍）或 -50%
   - 计算公式：剩余空间 = (10天前价格 × 2 - 当前价格) / 当前价格 × 100%

2. **30日严重异常波动**
   - 连续30个交易日内涨幅达到 +200%（价格涨3倍）或 -70%
   - 计算公式：剩余空间 = (30天前价格 × 3 - 当前价格) / 当前价格 × 100%

## 项目结构

```
pyst/
├── README.md                 # 项目说明文档
├── pyproject.toml           # 项目配置文件
├── uv.lock                  # UV 依赖锁定文件
├── Dockerfile               # Docker 容器配置
├── database.py              # 数据库模型定义
├── data_manager.py          # 数据获取和存储管理
├── monitor.py               # 股票异动监控计算
├── app.py                   # Flask 应用主程序
└── templates/               # HTML 模板目录
    └── index.html           # 前端页面
```

## 快速开始

### 环境要求
- Python >= 3.12
- UV 包管理工具

### 安装依赖
```bash
uv sync
```

### 配置 Tushare Token
编辑 `.env` 文件，添加你的 Tushare Token：
```
TUSHARE_TOKEN=your_token_here
```

获取 Token：https://tushare.pro

### 初始化项目
运行初始化脚本，自动完成数据库初始化和基础数据获取：
```bash
python init.py
```

或手动初始化：
```bash
# 初始化数据库
python -c "from database import init_db; init_db()"

# 获取股票基本信息
python -c "from data_manager import DataManager; DataManager().fetch_stock_basic()"
```

### 运行应用
```bash
python app.py
```

访问 `http://localhost:5000` 查看应用。

## 主要模块说明

### database.py
- 定义数据库模型：StockBasic、StockDailyData、IndexDailyData、TradeCal
- 提供数据库初始化和会话管理

### data_manager.py
- 从 Tushare 获取股票基本信息
- 获取股票和指数的日线数据
- 获取和管理交易日历数据
- 自动检测并更新交易日历（当最后交易日距离现在 > 180 天时）
- 存储数据到 SQLite 数据库
- 支持数据更新和刷新

### monitor.py
- 计算股票的异动指标
- 监控异常波动规则
- 计算剩余上涨空间
- 获取交易日期相关信息
- 生成监控报告

### trade_calendar.py
- 交易日历管理工具类
- 提供交易日期查询功能
- 支持计算交易日数量
- 获取指定日期前后的交易日

### app.py
- Flask 应用主程序
- 定义 API 路由
- 提供前端数据接口
- 支持定期数据刷新
- 提供交易日历状态查询和更新接口

## API 接口文档

### 股票相关接口

#### 获取股票列表
```
GET /api/stocks
```
返回所有上市股票的基本信息

#### 监控单只股票
```
GET /api/monitor/<ts_code>?index=000001.SH
```
获取指定股票的异动监控数据

### 交易日历接口

#### 获取交易日历状态
```
GET /api/trade-cal/status
```
返回上交所和深交所的交易日历状态，包括最后更新日期和是否需要更新

#### 手动更新交易日历
```
POST /api/trade-cal/update?exchange=SSE
```
手动更新指定交易所的交易日历数据

### 数据管理接口

#### 手动刷新数据
```
POST /api/refresh
```
手动刷新所有数据（股票信息、交易日历等）

#### 健康检查
```
GET /api/health
```
检查应用是否正常运行

## 交易日历自动更新机制

系统会自动检测交易日历的更新状态：

1. **初始化时**：`init.py` 会获取一年前到一年后的交易日历
2. **定期更新**：每天 16:00（交易结束后）自动检查并更新
3. **自动触发条件**：当最后交易日距离现在 ≥ 180 天时自动更新
4. **手动更新**：可通过 `/api/trade-cal/update` 接口手动更新

## 许可证

MIT
