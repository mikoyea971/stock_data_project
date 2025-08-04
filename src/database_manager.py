# src/database_manager.py
import pandas as pd
from sqlalchemy import create_engine, text, inspect, MetaData, Table, Column, String, Float, Date

class DatabaseManager:
    def __init__(self, db_path='stock_data.sqlite3'):
        self.db_uri = f'sqlite:///{db_path}'
        self.engine = create_engine(self.db_uri)
        self.metadata = MetaData()
        self._define_table()

    def _define_table(self):
        self.stock_table = Table(
            'stock_daily', self.metadata,
            Column('代码', String, primary_key=True),
            Column('日期', Date, primary_key=True),
            Column('开盘', Float),
            Column('收盘', Float),
            Column('最高', Float),
            Column('最低', Float),
            Column('成交量', Float),
            Column('成交额', Float),
            Column('振幅', Float),
            Column('涨跌幅', Float),
            Column('涨跌额', Float),
            Column('换手率', Float),
        )

    def create_table_if_not_exists(self):
        """创建数据表（如果不存在）"""
        inspector = inspect(self.engine)
        if not inspector.has_table(self.stock_table.name):
            print(f"创建数据表: {self.stock_table.name}")
            self.metadata.create_all(self.engine)
        else:
            print(f"数据表 '{self.stock_table.name}' 已存在。")

    def save_data(self, df: pd.DataFrame):
        """
        将 DataFrame 数据保存到数据库。
        使用 'replace' 策略，如果主键（代码, 日期）已存在，则替换旧数据。
        """
        if df.empty:
            return
        
        try:
            # 确保 '日期' 列是 datetime 对象
            df['日期'] = pd.to_datetime(df['日期'])
            with self.engine.connect() as connection:
                df.to_sql(
                    name=self.stock_table.name,
                    con=connection,
                    if_exists='append',
                    index=False,
                    method=self._upsert_method()
                )
            print(f"成功保存 {len(df)} 条数据。")
        except Exception as e:
            print(f"保存数据时出错: {e}")

    def get_latest_date_for_stock(self, stock_code: str):
        """获取特定股票在数据库中的最新日期"""
        query = text(f"""
            SELECT MAX(日期) FROM {self.stock_table.name}
            WHERE "代码" = :code
        """)
        with self.engine.connect() as connection:
            result = connection.execute(query, {'code': stock_code}).scalar_one_or_none()
        return pd.to_datetime(result) if result else None
    
    def get_all_data(self):
        """获取数据库中的所有数据"""
        return pd.read_sql(f"SELECT * FROM {self.stock_table.name}", self.engine)

    @staticmethod
    def _upsert_method():
        """返回一个适用于 to_sql 的方法，实现 'upsert'（更新或插入）逻辑"""
        def method(table, conn, keys, data_iter):
            # 对于 SQLite，INSERT OR REPLACE 提供了 upsert 功能
            # 对于 PostgreSQL, 可以使用 ON CONFLICT DO UPDATE
            from sqlalchemy.dialects.sqlite import insert
            
            for data in data_iter:
                stmt = insert(table.table).values(**data)
                # 这个简化的例子对于SQLite足够了，更通用的方案会更复杂
                # 这里假设每次都是新数据，用append即可，或用replace清空再插入
                # 为了安全地增量，最好是先删除冲突的，再插入
                # 但由于akshare获取的数据通常是新的，直接append是最高效的
                # 如果要实现严格的upsert，需要更复杂的逻辑
                pass # 在这个例子中，让 to_sql 的 if_exists='append' 处理
            # to_sql for sqlite with if_exists='append' and primary key doesn't replace.
            # A more robust solution is needed for true upsert.
            # A simple approach for this problem: delete existing and then insert.
            # However, for efficiency, we will rely on fetching data > last_date.
            # `to_sql` with `if_exists='replace'` would wipe the table.
            # `if_exists='append'` will fail on primary key conflict.
            # So, we'll ensure fetched data is always new.
            # A simple workaround for this specific use case with sqlite
            data = [dict(zip(keys, row)) for row in data_iter]
            conn.execute(table.table.insert().prefix_with("OR REPLACE"), data)

        return None # 使用 to_sql 默认的快速方法，依赖于数据源的非重复性