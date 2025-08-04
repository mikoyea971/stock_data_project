import pandas as pd
import logging

def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Performs basic validation on the stock data DataFrame.
    :param df: The input DataFrame.
    :return: A cleaned DataFrame.
    """
    if df.empty:
        return df

    # 1. Check for missing values in critical columns
    initial_rows = len(df)
    df.dropna(subset=['date', 'code', 'open', 'high', 'low', 'close', 'volume'], inplace=True)
    if len(df) < initial_rows:
        logging.warning(f"Dropped {initial_rows - len(df)} rows due to missing values.")

    # 2. Check for logical inconsistencies (high >= low, etc.)
    # Note: In some rare cases (e.g., stock suspension), open/high/low/close can be equal.
    invalid_rows = df[(df['high'] < df['low']) | (df['high'] < df['open']) | (df['high'] < df['close']) | \
                      (df['low'] > df['open']) | (df['low'] > df['close']) | (df['volume'] < 0)]

    if not invalid_rows.empty:
        logging.warning(f"Found {len(invalid_rows)} rows with inconsistent values. Dropping them.")
        # Drop invalid rows by index
        df.drop(invalid_rows.index, inplace=True)
    
    # 3. Ensure data types are correct
    df['open'] = pd.to_numeric(df['open'])
    df['high'] = pd.to_numeric(df['high'])
    df['low'] = pd.to_numeric(df['low'])
    df['close'] = pd.to_numeric(df['close'])
    df['volume'] = pd.to_numeric(df['volume']).astype('int64')

    return df