import pandas as pd
from sqlalchemy import create_engine, text, inspect
import logging

class DatabaseManager:
    """Handles all interactions with the SQL database."""

    def __init__(self, db_path: str = "stock_data.db"):
        """
        Initializes the database connection.
        :param db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}')
        self.table_name = "daily_prices"
        self._create_table()

    def _create_table(self):
        """Creates the daily_prices table if it does not exist."""
        try:
            with self.engine.connect() as connection:
                connection.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    date DATE NOT NULL,
                    code VARCHAR(10) NOT NULL,
                    open FLOAT,
                    high FLOAT,
                    low FLOAT,
                    close FLOAT,
                    volume BIGINT,
                    PRIMARY KEY (date, code)
                );
                """))
            logging.info(f"Table '{self.table_name}' is ready.")
        except Exception as e:
            logging.error(f"Error creating table: {e}")
            raise

    def save_data(self, df: pd.DataFrame):
        """
        Saves a DataFrame to the database, appending new data.
        Handles potential conflicts with existing primary keys.
        :param df: DataFrame with stock data.
        """
        if df.empty:
            return

        try:
            # 'append' will add new rows. 'if_exists' is for the table itself.
            # Using a temporary table and INSERT OR IGNORE for better conflict handling
            # However, for simplicity with pandas, we'll rely on primary key constraints
            # and catch the integrity error, which is slower but simpler to implement.
            # A more performant way is to filter out existing keys before inserting.
            df.to_sql(self.table_name, self.engine, if_exists='append', index=False)
            logging.info(f"Saved {len(df)} rows to the database.")
        except Exception as e:
            # This will catch IntegrityError for duplicates, but also other errors.
            logging.warning(f"Could not save all rows, likely due to duplicates or other DB error: {e}")

    def get_latest_date(self, stock_code: str) -> str | None:
        """
        Gets the latest date for a given stock code from the database.
        :param stock_code: The stock code to check.
        :return: The latest date as a 'YYYY-MM-DD' string, or None if no data exists.
        """
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(
                    f"SELECT MAX(date) FROM {self.table_name} WHERE code = :code"
                ), {"code": stock_code}).scalar_one_or_none()
            return result
        except Exception as e:
            logging.error(f"Error getting latest date for {stock_code}: {e}")
            return None

    def is_db_empty(self) -> bool:
        """Checks if the main data table is empty."""
        inspector = inspect(self.engine)
        if not inspector.has_table(self.table_name):
            return True
        try:
            with self.engine.connect() as connection:
                count = connection.execute(text(f"SELECT COUNT(1) FROM {self.table_name}")).scalar()
            return count == 0
        except Exception as e:
            logging.error(f"Could not check if DB is empty, assuming it is. Error: {e}")
            return True