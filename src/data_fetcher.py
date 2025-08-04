import akshare as ak
import pandas as pd
import logging
from typing import List

def get_all_stock_codes() -> List[str]:
    """
    Fetches all A-share stock codes.
    :return: A list of stock codes.
    """
    try:
        stock_spot_df = ak.stock_zh_a_spot_em()
        logging.info(f"Fetched {len(stock_spot_df)} stock codes.")
        return stock_spot_df['代码'].tolist()
    except Exception as e:
        logging.error(f"Failed to fetch stock codes: {e}")
        return []

def fetch_stock_data(stock_code: str, start_date: str, end_date: str) -> pd.DataFrame | None:
    """
    Fetches daily historical data for a single stock.
    :param stock_code: The stock code (e.g., '600519').
    :param start_date: Start date in 'YYYYMMDD' format.
    :param end_date: End date in 'YYYYMMDD' format.
    :return: A DataFrame with the data, or None if it fails.
    """
    try:
        df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date=start_date, end_date=end_date, adjust="")
        if df.empty:
            logging.warning(f"No data returned for {stock_code} from {start_date} to {end_date}.")
            return None
        
        # Rename columns to match database schema
        df.rename(columns={
            '日期': 'date',
            '开盘': 'open',
            '最高': 'high',
            '最低': 'low',
            '收盘': 'close',
            '成交量': 'volume'
        }, inplace=True)
        
        df['code'] = stock_code
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        
        # Select only the columns we need
        required_columns = ['date', 'code', 'open', 'high', 'low', 'close', 'volume']
        return df[required_columns]

    except Exception as e:
        logging.error(f"Failed to fetch data for {stock_code}: {e}")
        return None