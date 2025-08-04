# src/main.py
import argparse
import time
from data_fetcher import DataFetcher
from database_manager import DatabaseManager
from data_validator import DataValidator

def run_full_refresh(db_manager, fetcher):
    """
    执行全量刷新。会删除旧表，获取所有A股近一年的数据并存入。
    这是容错机制的核心：当数据库丢失或损坏时，运行此模式可完全恢复。
    """
    print("--- 开始全量刷新模式 ---")
    db_manager.create_table_if_not_exists() # 确保表存在
    
    stock_codes = fetcher.get_all_a_stock_codes()
    total = len(stock_codes)
    
    for i, code in enumerate(stock_codes):
        print(f"\n--- 处理进度: {i+1}/{total} (股票代码: {code}) ---")
        df = fetcher.fetch_full_history(code)
        if not df.empty:
            db_manager.save_data(df)
        time.sleep(0.5) # 控制请求频率，防止IP被封

def run_incremental_update(db_manager, fetcher):
    """
    执行增量更新。对每只股票，检查数据库中的最新日期，并只拉取此后的数据。
    """
    print("--- 开始增量更新模式 ---")
    db_manager.create_table_if_not_exists()
    
    stock_codes = fetcher.get_all_a_stock_codes()
    total = len(stock_codes)

    for i, code in enumerate(stock_codes):
        print(f"\n--- 处理进度: {i+1}/{total} (股票代码: {code}) ---")
        latest_date = db_manager.get_latest_date_for_stock(code)
        df = fetcher.fetch_increment_data(code, latest_date)
        if not df.empty:
            db_manager.save_data(df)
        time.sleep(0.5)

def run_validation(db_manager):
    """
    执行数据校验。
    """
    print("--- 开始数据校验模式 ---")
    all_data = db_manager.get_all_data()
    if all_data.empty:
        print("数据库为空，无法校验。")
        return
        
    validator = DataValidator(all_data)
    validator.run_all_validations()

def main():
    parser = argparse.ArgumentParser(description="A股日频行情数据处理工具")
    parser.add_argument(
        '--mode', 
        type=str, 
        required=True, 
        choices=['full', 'increment', 'validate'],
        help="运行模式: 'full' (全量刷新), 'increment' (增量更新), 'validate' (数据校验)"
    )
    args = parser.parse_args()

    db_manager = DatabaseManager()
    fetcher = DataFetcher()

    if args.mode == 'full':
        run_full_refresh(db_manager, fetcher)
    elif args.mode == 'increment':
        run_incremental_update(db_manager, fetcher)
    elif args.mode == 'validate':
        run_validation(db_manager)

if __name__ == '__main__':
    main()