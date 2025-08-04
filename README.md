### 股票数据管道项目  

本项目实现了一套 Python 数据管道，用于获取 A 股每日行情数据、校验数据质量，并将其存储到本地 SQLite 数据库。  


## 核心功能  
- **数据来源**：依托 `akshare` 库拉取 A 股市场数据。  
- **数据库存储**：采用 SQLite 数据库本地化存储数据。  
- **增量更新**：重复运行时，仅抓取上次更新后的新增数据。  
- **容错机制**：若数据库文件丢失或损坏，支持全量重刷数据恢复完整内容。  
- **数据校验**：入库前执行基础校验（如格式、完整性），保障数据质量。  


## 项目结构  
- `src/`：核心代码目录  
  - `main.py`：数据管道的启动入口。  
  - `data_fetcher.py`：封装 `akshare` 的数据获取逻辑。  
  - `database_manager.py`：处理数据库的建表、增删查改等操作。  
  - `data_validator.py`：实现数据校验规则（如字段合法性检查）。  
- `requirements.txt`：项目依赖的 Python 包清单（需安装）。  
- `stock_data.db`：SQLite 数据库文件（首次运行自动生成）。  


## 运行指南  

### 1. 配置虚拟环境（推荐）  
```bash  
python -m venv venv  
source venv/bin/activate  # Windows 系统请用 `venv\Scripts\activate`  
```  


### 2. 安装依赖包  
```bash  
pip install -r requirements.txt  
```  


### 3. 启动数据管道  
进入 `src` 目录，执行主脚本：  

```bash  
cd src  
python main.py  
```  

- **首次运行**：全量拉取近一年的 A 股数据，耗时较长（因数据量较大）。  
- **后续运行**：仅同步新增数据，执行速度更快。  


### 故障恢复 / 全量同步  
若 `stock_data.db` 文件丢失，或需要重新全量同步数据，可修改 `src/main.py` 的最后一行：  

将：  
```python  
run_pipeline(full_resync=False)  
```  
改为：  
```python  
run_pipeline(full_resync=True)  
```  
重新运行 `main.py` 即可触发全量同步，重建完整数据库。