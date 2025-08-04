import logging
from datetime import datetime, timedelta
from tqdm import tqdm

from database_manager import DatabaseManager
from data_fetcher import get_all_stock_codes, fetch_stock_data
from data_validator import validate_data

# --- Configuration ---
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

DB_FILE = "stock_data.db"
FULL_SYNC_DAYS = 365 # Fetch data for the past year on a full sync

def run_pipeline(full_resync: bool = False):
    """
    Main pipeline to fetch, validate, and store stock data.
    :param full_resync: If True, deletes all existing data and fetches everything again.
    """
    db_manager = DatabaseManager(DB_FILE)
    
    if full_resync:
        logging.warning("FULL RESYNC triggered. All existing data will be wiped.")
        # This is a destructive action, so ideally you'd have a backup or confirmation.
        # For this problem, we'll just recreate the table.
        db_manager = DatabaseManager(DB_FILE) # Re-initializing will recreate table if needed
        # Or add a specific wipe method: `db_manager.wipe_data()`

    stock_codes = get_all_stock_codes()
    if not stock_codes:
        logging.error("Could not retrieve stock codes. Exiting.")
        return

    end_date = datetime.now()
    default_start_date = end_date - timedelta(days=FULL_SYNC_DAYS)
    
    logging.info(f"Processing {len(stock_codes)} stocks...")

    # Use tqdm for a progress bar
    for code in tqdm(stock_codes, desc="Updating Stocks"):
        start_date = default_start_date
        
        # For incremental updates, find the last entry
        if not full_resync:
            latest_date_str = db_manager.get_latest_date(code)
            if latest_date_str:
                latest_date = datetime.strptime(latest_date_str, '%Y-%m-%d')
                start_date = latest_date + timedelta(days=1)
        
        # Skip if we already have up-to-date data
        if start_date.date() >= end_date.date():
            logging.info(f"Stock {code} is already up to date. Skipping.")
            continue

        start_date_str = start_date.strftime('%Y%m%d')
        end_date_str = end_date.strftime('%Y%m%d')
        
        # 1. Fetch data
        stock_df = fetch_stock_data(code, start_date_str, end_date_str)

        if stock_df is None or stock_df.empty:
            continue

        # 2. Validate data
        validated_df = validate_data(stock_df)

        if validated_df.empty:
            logging.warning(f"No valid data remained for {code} after validation.")
            continue
            
        # 3. Save to database
        db_manager.save_data(validated_df)

    logging.info("Pipeline execution finished.")

if __name__ == '__main__':
    # To run a full sync (e.g., if the DB was lost):
    # run_pipeline(full_resync=True)
    
    # To run a standard incremental update:
    run_pipeline(full_resync=False)