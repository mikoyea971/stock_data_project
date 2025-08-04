# src/data_fetcher.py
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import time

class DataFetcher:
    def __init__(self):
        pass

    def get_all_a_stock_codes(self) -> list:
        """获取所有A股的股票代码列表"""
        try:
            stock_df = ak.stock_zh_a_spot_em()
            # 筛选出沪市（sh）和深市（sz）的股票
            codes = stock_df[stock_df['代码'].str.match(r'^(60|00|30|68)')]['代码'].tolist()
            print(f"成功获取 {len(codes)} 只 A 股代码。")
            return codes
        except Exception as e:
            print(f"获取股票列表失败: {e}")
            return []

    def get_stock_data(self, stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取单只股票指定时间段的日频数据"""
        for attempt in range(3): # 重试机制
            try:
                # 使用后复权数据
                df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date=start_date, end_date=end_date, adjust="hfq")
                if df.empty:
                    return pd.DataFrame()
                # 选择并重命名列以匹配数据库
                df = df[['日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率']]
                df['代码'] = stock_code
                return df
            except Exception as e:
                print(f"获取 {stock_code} 数据失败 (尝试 {attempt+1}/3): {e}")
                time.sleep(5) # 等待5秒后重试
        print(f"获取 {stock_code} 数据彻底失败。")
        return pd.DataFrame()

    def fetch_full_history(self, stock_code: str) -> pd.DataFrame:
        """获取单只股票近一年的完整历史数据"""
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
        print(f"正在获取 {stock_code} 从 {start_date} 到 {end_date} 的数据...")
        return self.get_stock_data(stock_code, start_date, end_date)

    def fetch_increment_data(self, stock_code: str, last_date_in_db: datetime) -> pd.DataFrame:
        """从上次记录的日期之后获取增量数据"""
        if last_date_in_db is None:
            return self.fetch_full_history(stock_code)
            
        start_date = (last_date_in_db + timedelta(days=1)).strftime('%Y%m%d')
        end_date = datetime.now().strftime('%Y%m%d')
        
        if start_date > end_date:
            print(f"{stock_code} 数据已是最新，无需更新。")
            return pd.DataFrame()
            
        print(f"正在获取 {stock_code} 从 {start_date} 到 {end_date} 的增量数据...")
        return self.get_stock_data(stock_code, start_date, end_date)