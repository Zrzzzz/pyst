"""
数据管理模块
负责从 AKShare 获取股票数据并存储到 SQLite 数据库
"""
import multiprocessing as mp
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from tqdm import tqdm
import logger_config  # 必须在导入 logger 之前
from loguru import logger
from database import get_session, close_session, StockBasic, StockDailyData, IndexDailyData, TradeCal


# ---------- baostock 多进程 worker（必须 top-level 才能被 spawn 子进程 pickle）----------

def _bs_worker_init():
    """每个子进程启动时 login 一次，复用 socket。"""
    import baostock as bs
    bs.login()


def _bs_worker_fetch(args):
    """
    子进程内执行：用 baostock 拉一只股票的 K 线，返回标准化字段 DataFrame。

    返回 (ts_code, df_or_None, err_str_or_None)
    """
    ts_code, start_date, end_date = args
    try:
        import baostock as bs
        import pandas as _pd

        parts = ts_code.split('.')
        if len(parts) != 2:
            return ts_code, None, f"invalid ts_code: {ts_code}"
        code, suffix = parts[0], parts[1].lower()
        if suffix == 'bj':
            return ts_code, None, 'SKIP_BJ'  # 主进程会用新浪兜底
        bs_code = f"{suffix}.{code}"

        sd = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:8]}"
        ed = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:8]}"
        rs = bs.query_history_k_data_plus(
            bs_code,
            "date,code,open,high,low,close,preclose,volume,amount,pctChg",
            start_date=sd, end_date=ed, frequency="d", adjustflag="3",
        )
        rows = []
        while (rs.error_code == "0") and rs.next():
            rows.append(rs.get_row_data())
        if rs.error_code != "0":
            return ts_code, None, f"err={rs.error_code} {rs.error_msg[:80]}"
        if not rows:
            return ts_code, None, None

        df = _pd.DataFrame(rows, columns=rs.fields)
        for col in ['open', 'high', 'low', 'close', 'preclose', 'volume', 'amount', 'pctChg']:
            df[col] = _pd.to_numeric(df[col], errors='coerce')
        df['ts_code'] = ts_code
        df['trade_date'] = df['date'].astype(str).str.replace('-', '', regex=False)
        df['pre_close'] = df['preclose']
        df['change'] = df['close'] - df['preclose']
        df['pct_chg'] = df['pctChg']
        df['vol'] = df['volume'] / 100.0  # 股 -> 手
        df['amount'] = df['amount'] / 1000.0  # 元 -> 千元

        out = df[[
            'ts_code', 'trade_date', 'open', 'high', 'low', 'close',
            'pre_close', 'change', 'pct_chg', 'vol', 'amount',
        ]]
        return ts_code, out, None
    except Exception as e:
        return ts_code, None, str(e)


# ---------- 工具函数 ----------

def _symbol_to_ts_code(symbol: str) -> str:
    """根据 6 位代码推断交易所后缀，返回 ts_code 形式 (例如 000001.SZ)"""
    code = str(symbol).zfill(6)
    if code.startswith(('60', '68', '900')):
        return f"{code}.SH"
    if code.startswith(('00', '30', '20')):
        return f"{code}.SZ"
    if code.startswith(('43', '83', '87', '88', '92')):
        return f"{code}.BJ"
    # 其他情况下，以 8 开头一般归到北交所
    if code.startswith('8'):
        return f"{code}.BJ"
    return f"{code}.SZ"


def _ts_code_to_sina_symbol(ts_code: str) -> str:
    """ts_code (000001.SZ) -> 新浪/腾讯格式 (sz000001)"""
    parts = str(ts_code).split('.')
    code = parts[0]
    suffix = parts[1].lower() if len(parts) > 1 else 'sz'
    return f"{suffix}{code}"


def _normalize_date(value) -> str:
    """统一日期为 YYYYMMDD 字符串"""
    if value is None:
        return ''
    if isinstance(value, (datetime, pd.Timestamp)):
        return value.strftime('%Y%m%d')
    s = str(value)
    if not s:
        return ''
    # 处理 2024-01-01 这种
    if '-' in s:
        try:
            return datetime.strptime(s[:10], '%Y-%m-%d').strftime('%Y%m%d')
        except ValueError:
            pass
    return s.replace('-', '').replace('/', '')[:8]


# ---------- DataManager ----------

class DataManager:
    """数据管理类"""

    def __init__(self):
        self.session = get_session()

    def __del__(self):
        close_session(self.session)

    # ---------- 股票基本信息 ----------

    def fetch_stock_basic(self, exchange='', list_status='L', market=''):
        """
        获取股票基本信息（沪深京 A 股，已上市）

        参数 exchange/list_status/market 保留以兼容旧调用，但 akshare 接口仅返回当前在市的 A 股。
        """
        try:
            logger.info(
                f"开始获取股票基本信息... (exchange={exchange}, list_status={list_status}, market={market})"
            )

            df = self._fetch_stock_basic_dataframe()
            if df.empty:
                logger.warning("未获取到任何股票数据")
                return df

            # 按 exchange 参数过滤
            if exchange:
                target_exchange = {'SSE': 'SSE', 'SZSE': 'SZSE', 'BSE': 'BSE'}.get(exchange.upper())
                if target_exchange:
                    df = df[df['exchange'] == target_exchange].reset_index(drop=True)

            # 按 market 参数过滤
            if market:
                df = df[df['market'] == market].reset_index(drop=True)

            for _, row in df.iterrows():
                stock = StockBasic(
                    ts_code=row['ts_code'],
                    symbol=row['symbol'],
                    name=row['name'],
                    area=row.get('area', '') or '',
                    industry=row.get('industry', '') or '',
                    fullname=row.get('fullname') or None,
                    enname=None,
                    cnspell=None,
                    market=row.get('market', '') or '',
                    exchange=row.get('exchange') or None,
                    curr_type='CNY',
                    list_status='L',
                    list_date=row.get('list_date', '') or '',
                    delist_date=None,
                    is_hs=None,
                    act_name=None,
                    act_ent_type=None,
                )
                self.session.merge(stock)

            self.session.commit()
            logger.info(f"成功获取 {len(df)} 只股票基本信息")
            return df
        except Exception as e:
            logger.error(f"获取股票基本信息失败: {e}")
            self.session.rollback()
            raise

    def _fetch_stock_basic_dataframe(self) -> pd.DataFrame:
        """整合沪深京三大交易所的股票列表，返回统一字段的 DataFrame"""
        frames = []

        # 上交所 - 主板A股
        try:
            sh_main = ak.stock_info_sh_name_code(symbol="主板A股")
            sh_main['market'] = '主板'
            sh_main['exchange'] = 'SSE'
            frames.append(sh_main)
        except Exception as e:
            logger.warning(f"获取上交所主板A股列表失败: {e}")

        # 上交所 - 科创板
        try:
            sh_kcb = ak.stock_info_sh_name_code(symbol="科创板")
            sh_kcb['market'] = '科创板'
            sh_kcb['exchange'] = 'SSE'
            frames.append(sh_kcb)
        except Exception as e:
            logger.warning(f"获取上交所科创板列表失败: {e}")

        sh_normalized = []
        for df in frames:
            if df is None or df.empty:
                continue
            tmp = pd.DataFrame({
                'symbol': df['证券代码'].astype(str).str.zfill(6),
                'name': df['证券简称'],
                'fullname': df.get('证券全称'),
                'list_date': df['上市日期'].apply(_normalize_date),
                'market': df['market'],
                'exchange': df['exchange'],
                'industry': '',
                'area': '',
            })
            sh_normalized.append(tmp)

        # 深交所
        sz_normalized = []
        try:
            sz_df = ak.stock_info_sz_name_code(symbol="A股列表")
            if sz_df is not None and not sz_df.empty:
                board_map = {
                    '主板': '主板',
                    '中小企业板': '中小板',
                    '创业板': '创业板',
                }
                tmp = pd.DataFrame({
                    'symbol': sz_df['A股代码'].astype(str).str.zfill(6),
                    'name': sz_df['A股简称'],
                    'fullname': None,
                    'list_date': sz_df['A股上市日期'].apply(_normalize_date),
                    'market': sz_df['板块'].map(board_map).fillna(sz_df['板块']),
                    'exchange': 'SZSE',
                    'industry': sz_df.get('所属行业', '').fillna('') if '所属行业' in sz_df.columns else '',
                    'area': '',
                })
                sz_normalized.append(tmp)
        except Exception as e:
            logger.warning(f"获取深交所A股列表失败: {e}")

        # 北交所
        bj_normalized = []
        try:
            bj_df = ak.stock_info_bj_name_code()
            if bj_df is not None and not bj_df.empty:
                tmp = pd.DataFrame({
                    'symbol': bj_df['证券代码'].astype(str).str.zfill(6),
                    'name': bj_df['证券简称'],
                    'fullname': None,
                    'list_date': bj_df['上市日期'].apply(_normalize_date),
                    'market': '北交所',
                    'exchange': 'BSE',
                    'industry': bj_df.get('所属行业', '').fillna('') if '所属行业' in bj_df.columns else '',
                    'area': bj_df.get('地区', '').fillna('') if '地区' in bj_df.columns else '',
                })
                bj_normalized.append(tmp)
        except Exception as e:
            logger.warning(f"获取北交所股票列表失败: {e}")

        all_frames = sh_normalized + sz_normalized + bj_normalized
        if not all_frames:
            return pd.DataFrame()

        merged = pd.concat(all_frames, ignore_index=True)
        merged['ts_code'] = merged['symbol'].apply(_symbol_to_ts_code)
        merged = merged.drop_duplicates(subset=['ts_code']).reset_index(drop=True)
        return merged

    # ---------- 交易日历 ----------

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

    def fetch_trade_cal(self, exchange='SSE', start_date=None, end_date=None):
        """获取交易日历数据（基于 akshare 的 A 股交易日历）"""
        try:
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            if not end_date:
                end_date = (datetime.now() + timedelta(days=365)).strftime('%Y%m%d')

            logger.info(f"获取 {exchange} 交易日历: {start_date} - {end_date}")

            # akshare 返回的是所有 A 股交易日，沪深京通用
            trade_dates = ak.tool_trade_date_hist_sina()
            trading_set = {
                _normalize_date(d) for d in trade_dates['trade_date'].tolist()
            }

            start_dt = datetime.strptime(start_date, '%Y%m%d')
            end_dt = datetime.strptime(end_date, '%Y%m%d')

            rows = []
            cur = start_dt
            pretrade_date = None
            while cur <= end_dt:
                date_str = cur.strftime('%Y%m%d')
                is_open = '1' if date_str in trading_set else '0'
                rows.append({
                    'exchange': exchange,
                    'cal_date': date_str,
                    'is_open': is_open,
                    'pretrade_date': pretrade_date,
                })
                if is_open == '1':
                    pretrade_date = date_str
                cur += timedelta(days=1)

            df = pd.DataFrame(rows)
            for row in rows:
                trade_cal = TradeCal(
                    exchange=row['exchange'],
                    cal_date=row['cal_date'],
                    is_open=row['is_open'],
                    pretrade_date=row['pretrade_date'],
                )
                self.session.merge(trade_cal)

            self.session.commit()
            logger.info(f"成功获取 {exchange} 的 {len(df)} 条交易日历数据")
            return df
        except Exception as e:
            logger.error(f"获取 {exchange} 交易日历失败: {e}")
            self.session.rollback()
            raise

    # ---------- 股票日线 ----------

    def fetch_stock_daily(self, ts_code, start_date=None, end_date=None):
        """获取单只股票的日线数据"""
        try:
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')

            logger.info(f"获取 {ts_code} 日线数据: {start_date} - {end_date}")
            df = self._fetch_one_stock_daily(ts_code, start_date, end_date)

            if df is None or df.empty:
                logger.warning(f"{ts_code} 未获取到日线数据")
                return df if df is not None else pd.DataFrame()

            for _, row in df.iterrows():
                daily = StockDailyData(
                    ts_code=row['ts_code'],
                    trade_date=row['trade_date'],
                    open=row['open'],
                    high=row['high'],
                    low=row['low'],
                    close=row['close'],
                    pre_close=row.get('pre_close'),
                    change=row.get('change'),
                    pct_chg=row.get('pct_chg'),
                    vol=row['vol'],
                    amount=row['amount'],
                )
                self.session.merge(daily)

            self.session.commit()
            logger.info(f"成功获取 {ts_code} 的 {len(df)} 条日线数据")
            return df
        except Exception as e:
            logger.error(f"获取 {ts_code} 日线数据失败: {e}")
            self.session.rollback()
            raise

    def _fetch_one_stock_daily(self, ts_code, start_date, end_date) -> pd.DataFrame:
        """获取单只股票日线，返回标准化字段的 DataFrame（不写库）

        改用新浪 ak.stock_zh_a_daily：东财 push2his.eastmoney.com 在部分网络环境
        （服务器 Clash/mihomo 透明代理）会被 path 级阻断；新浪走 finance.sina.com.cn
        在同环境可用。
        """
        symbol = _ts_code_to_sina_symbol(ts_code)
        raw = ak.stock_zh_a_daily(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            adjust='',
        )
        if raw is None or raw.empty:
            return pd.DataFrame()
        return _normalize_sina_daily_df(raw, ts_code)

    def fetch_stock_daily_batch(self, ts_codes, start_date=None, end_date=None, exchange='SSE'):
        """
        批量获取多只股票的日线数据（逐只调用 akshare）

        akshare 不支持批量请求，这里在内部循环逐只获取，
        但保留了与原接口相同的入参/出参以兼容上层调用。
        """
        try:
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')

            if isinstance(ts_codes, str):
                ts_codes = [code.strip() for code in ts_codes.split(',')]

            logger.info(f"批量获取 {len(ts_codes)} 只股票的日线数据: {start_date} - {end_date}")

            # 检查日期边界是否已有数据，决定是否缩窄区间
            start_date_has_data = self.session.query(StockDailyData).filter(
                StockDailyData.trade_date == start_date
            ).first() is not None

            end_date_has_data = self.session.query(StockDailyData).filter(
                StockDailyData.trade_date == end_date
            ).first() is not None

            if start_date_has_data and end_date_has_data:
                logger.info(f"开始日期 {start_date} 和结束日期 {end_date} 都有股票数据，跳过获取")
                return None

            if not end_date_has_data:
                latest_daily = self.session.query(StockDailyData).order_by(
                    StockDailyData.trade_date.desc()
                ).first()

                if latest_daily:
                    latest_trade_date = latest_daily.trade_date
                    logger.info(f"缺少结束日期数据，数据库中最新交易日期: {latest_trade_date}")

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
                earliest_daily = self.session.query(StockDailyData).order_by(
                    StockDailyData.trade_date.asc()
                ).first()

                if earliest_daily:
                    earliest_trade_date = earliest_daily.trade_date
                    logger.info(f"缺少开始日期数据，数据库中最早交易日期: {earliest_trade_date}")

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

            trading_days_count = self.count_trading_days(start_date, end_date, exchange)
            logger.info(f"日期范围内交易日数量: {trading_days_count}")

            # baostock 多进程拉沪深股票（库本身是全局 socket，不能多线程，需要多进程隔离）
            # 北交所 baostock 不支持，单独走新浪
            n_proc = 16
            all_data = []
            err_count = 0
            bj_codes = [c for c in ts_codes if c.split('.')[-1].upper() == 'BJ']
            other_codes = [c for c in ts_codes if c.split('.')[-1].upper() != 'BJ']
            logger.info(f"baostock 多进程拉取 {len(other_codes)} 只沪深股票（{n_proc} 进程），北交所 {len(bj_codes)} 只走新浪")

            def _write_df(df):
                """主线程写库：把单只 DataFrame 写入数据库"""
                for _, row in df.iterrows():
                    daily = StockDailyData(
                        ts_code=row['ts_code'],
                        trade_date=row['trade_date'],
                        open=row['open'],
                        high=row['high'],
                        low=row['low'],
                        close=row['close'],
                        pre_close=row.get('pre_close'),
                        change=row.get('change'),
                        pct_chg=row.get('pct_chg'),
                        vol=row['vol'],
                        amount=row['amount'],
                    )
                    self.session.merge(daily)

            with tqdm(total=len(ts_codes), desc="获取股票日线数据", unit="只") as pbar:
                if other_codes:
                    ctx = mp.get_context('spawn')
                    args_iter = [(c, start_date, end_date) for c in other_codes]
                    with ctx.Pool(processes=n_proc, initializer=_bs_worker_init) as pool:
                        for ts_code, df, err in pool.imap_unordered(_bs_worker_fetch, args_iter, chunksize=8):
                            if err is not None and err != 'SKIP_BJ':
                                err_count += 1
                                logger.error(f"获取 {ts_code} (baostock) 失败: {err}")
                                pbar.update(1)
                                continue
                            if df is None or df.empty:
                                pbar.update(1)
                                continue
                            _write_df(df)
                            all_data.append(df)
                            pbar.update(1)
                            if len(all_data) % 200 == 0:
                                self.session.commit()

                # 北交所主进程兜底（数量少，串行新浪即可）
                for ts_code in bj_codes:
                    try:
                        df = self._fetch_one_stock_daily(ts_code, start_date, end_date)
                        if df is None or df.empty:
                            pbar.update(1)
                            continue
                        _write_df(df)
                        all_data.append(df)
                    except Exception as one_err:
                        err_count += 1
                        logger.error(f"获取 {ts_code} (新浪) 失败: {one_err}")
                    pbar.update(1)

            self.session.commit()
            if err_count:
                logger.warning(f"批量抓取共有 {err_count} 只失败")

            if all_data:
                total_rows = sum(len(df) for df in all_data)
                logger.info(f"批量获取完成，共获取 {total_rows} 条日线数据")
                return pd.concat(all_data, ignore_index=True)

            logger.warning("未获取到任何日线数据")
            return None
        except Exception as e:
            logger.error(f"批量获取日线数据失败: {e}")
            self.session.rollback()
            raise

    # ---------- 指数日线 ----------

    def fetch_index_daily(self, ts_code, start_date=None, end_date=None):
        """获取指数日线数据"""
        try:
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')

            logger.info(f"获取 {ts_code} 指数数据: {start_date} - {end_date}")
            df = self._fetch_one_index_daily(ts_code, start_date, end_date)

            if df is None or df.empty:
                logger.warning(f"{ts_code} 未获取到指数数据")
                return df if df is not None else pd.DataFrame()

            for _, row in df.iterrows():
                daily = IndexDailyData(
                    ts_code=ts_code,
                    trade_date=row['trade_date'],
                    open=row['open'],
                    high=row['high'],
                    low=row['low'],
                    close=row['close'],
                    pre_close=row.get('pre_close'),
                    change=row.get('change'),
                    pct_chg=row.get('pct_chg'),
                    vol=row['vol'],
                    amount=row['amount'],
                )
                self.session.merge(daily)

            self.session.commit()
            logger.info(f"成功获取 {ts_code} 的 {len(df)} 条指数数据")
            return df
        except Exception as e:
            logger.error(f"获取 {ts_code} 指数数据失败: {e}")
            self.session.rollback()
            raise

    def _fetch_one_index_daily(self, ts_code, start_date, end_date) -> pd.DataFrame:
        """获取单个指数的日线数据，返回标准化字段 DataFrame（不写库）

        改用新浪 ak.stock_zh_index_daily（理由同 _fetch_one_stock_daily）。
        该接口不接受日期范围，会返回全量历史，这里在客户端按区间过滤。
        """
        symbol = _ts_code_to_sina_symbol(ts_code)
        raw = ak.stock_zh_index_daily(symbol=symbol)
        if raw is None or raw.empty:
            return pd.DataFrame()
        df = _normalize_sina_daily_df(raw, ts_code)
        return df[(df['trade_date'] >= start_date) & (df['trade_date'] <= end_date)].reset_index(drop=True)

    def fetch_index_daily_batch(self, ts_codes, start_date=None, end_date=None, exchange='SSE'):
        """批量获取多个指数的日线数据（逐个处理）"""
        try:
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')

            if isinstance(ts_codes, str):
                ts_codes = [code.strip() for code in ts_codes.split(',')]

            logger.info(f"批量获取 {len(ts_codes)} 个指数的日线数据: {start_date} - {end_date}")

            start_date_has_data = self.session.query(IndexDailyData).filter(
                IndexDailyData.trade_date == start_date
            ).first() is not None

            end_date_has_data = self.session.query(IndexDailyData).filter(
                IndexDailyData.trade_date == end_date
            ).first() is not None

            if start_date_has_data and end_date_has_data:
                logger.info(f"开始日期 {start_date} 和结束日期 {end_date} 都有指数数据，跳过获取")
                return None

            if not end_date_has_data:
                latest_daily = self.session.query(IndexDailyData).order_by(
                    IndexDailyData.trade_date.desc()
                ).first()

                if latest_daily:
                    latest_trade_date = latest_daily.trade_date
                    logger.info(f"缺少结束日期数据，数据库中最新交易日期: {latest_trade_date}")

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
                earliest_daily = self.session.query(IndexDailyData).order_by(
                    IndexDailyData.trade_date.asc()
                ).first()

                if earliest_daily:
                    earliest_trade_date = earliest_daily.trade_date
                    logger.info(f"缺少开始日期数据，数据库中最早交易日期: {earliest_trade_date}")

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

            all_data = []
            with tqdm(total=len(ts_codes), desc="获取指数日线数据", unit="个") as pbar:
                for ts_code in ts_codes:
                    try:
                        logger.info(f"获取指数 {ts_code} 的日线数据: {start_date} - {end_date}")
                        df = self._fetch_one_index_daily(ts_code, start_date, end_date)

                        if df is None or df.empty:
                            logger.warning(f"指数 {ts_code} 未获取到数据")
                            pbar.update(1)
                            continue

                        for _, row in df.iterrows():
                            daily = IndexDailyData(
                                ts_code=ts_code,
                                trade_date=row['trade_date'],
                                open=row['open'],
                                high=row['high'],
                                low=row['low'],
                                close=row['close'],
                                pre_close=row.get('pre_close'),
                                change=row.get('change'),
                                pct_chg=row.get('pct_chg'),
                                vol=row['vol'],
                                amount=row['amount'],
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
                return pd.concat(all_data, ignore_index=True)

            logger.warning("未获取到任何指数日线数据")
            return None
        except Exception as e:
            logger.error(f"批量获取指数日线数据失败: {e}")
            self.session.rollback()
            raise

    def refresh_index_daily(self, ts_codes, days=40, exchange='SSE'):
        """刷新指数日线数据（最近 N 天）"""
        try:
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')

            logger.info(f"刷新指数日线数据，时间范围: {start_date} - {end_date}")
            return self.fetch_index_daily_batch(ts_codes, start_date, end_date, exchange)
        except Exception as e:
            logger.error(f"刷新指数日线数据失败: {e}")
            raise

    # ---------- 其他工具 ----------

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


def _normalize_sina_daily_df(raw: pd.DataFrame, ts_code: str) -> pd.DataFrame:
    """
    新浪 ak.stock_zh_a_daily / ak.stock_zh_index_daily 返回字段标准化。

    新浪原始字段：date, open, high, low, close, volume(股), amount(元),
                  outstanding_share, turnover  （指数没有 amount）
    转换后字段对齐数据库 / 原 tushare：
    - vol 单位手 = volume / 100（个股）；指数直接用 volume（原始单位）
    - amount 单位千元 = amount / 1000（个股）；指数 amount 缺失 → 0
    - pre_close / change / pct_chg 由相邻收盘价计算
    """
    df = raw.copy()
    df['trade_date'] = df['date'].apply(_normalize_date)
    df = df.sort_values('trade_date').reset_index(drop=True)
    df['ts_code'] = ts_code

    df['open'] = pd.to_numeric(df['open'], errors='coerce')
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    df['high'] = pd.to_numeric(df['high'], errors='coerce')
    df['low'] = pd.to_numeric(df['low'], errors='coerce')

    vol_raw = pd.to_numeric(df.get('volume'), errors='coerce')
    if 'amount' in df.columns:
        amount_raw = pd.to_numeric(df['amount'], errors='coerce')
        df['vol'] = vol_raw / 100.0
        df['amount'] = amount_raw / 1000.0
    else:
        df['vol'] = vol_raw
        df['amount'] = 0.0

    df['pre_close'] = df['close'].shift(1)
    df['change'] = df['close'] - df['pre_close']
    df['pct_chg'] = (df['change'] / df['pre_close']) * 100.0

    return df[[
        'ts_code', 'trade_date', 'open', 'high', 'low', 'close',
        'pre_close', 'change', 'pct_chg', 'vol', 'amount',
    ]]
