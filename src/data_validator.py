# src/data_validator.py
import pandas as pd

class DataValidator:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.errors = []

    def run_all_validations(self):
        """执行所有校验"""
        self.validate_ohlc()
        self.validate_positive_values()
        self.validate_missing_values()
        
        if self.errors:
            print("数据校验发现以下问题:")
            for error in self.errors:
                print(f"- {error}")
        else:
            print("数据校验通过，未发现明显问题。")
        return not self.errors

    def validate_ohlc(self):
        """校验开盘/最高/最低/收盘价的逻辑关系"""
        invalid_ohlc = self.df[
            (self.df['最低'] > self.df['开盘']) |
            (self.df['最低'] > self.df['收盘']) |
            (self.df['最高'] < self.df['开盘']) |
            (self.df['最高'] < self.df['收盘'])
        ]
        if not invalid_ohlc.empty:
            self.errors.append(f"发现 {len(invalid_ohlc)} 条 OHLC 逻辑错误的数据。")

    def validate_positive_values(self):
        """校验价格和成交量是否为正"""
        cols_to_check = ['开盘', '收盘', '最高', '最低', '成交量']
        for col in cols_to_check:
            if (self.df[col] < 0).any():
                self.errors.append(f"列 '{col}' 中发现负值。")

    def validate_missing_values(self):
        """检查是否存在空值"""
        if self.df.isnull().values.any():
            self.errors.append("数据中包含空值 (NaN)。")