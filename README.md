# 股票数据处理与算法实现项目

本项目旨在完成一个包含算法题解和软件工程实践的综合任务。

## 项目结构
.
├── .gitignore # Git 忽略文件配置
├── README.md # 项目说明
├── problem_1_and_2.md # 算法题 1 和 2 的详细解答
└── src/ # Python 代码 (题目 4)
├── init.py
├── data_fetcher.py # 使用 akshare 获取数据的模块
├── database_manager.py # SQLite 数据库管理模块
├── data_validator.py # 数据校验模块
└── main.py # 主程序入口，协调数据流


## 分支说明

*   `main`: 主分支，包含项目的基本结构和文档。
*   `branch-1`: (概念性) 包含了对一个假设性后端项目进行结构优化的思考与设计。详情请参考 `problem_3_solution.md` (您需要创建这个文件来存放题目3的解答)。
*   `branch-2`: 包含了题目 4 的完整 Python 实现，一个用于获取、存储和验证A股行情数据的数据管道。

## 如何运行 (Branch 2)

1.  **克隆仓库并切换分支**
    ```bash
    git clone <您的 GitHub 仓库 URL>
    cd stock_data_project
    git checkout branch-2
    ```

2.  **安装依赖**
    ```bash
    pip install pandas akshare sqlalchemy
    ```

3.  **运行程序**

    *   **首次运行或完全刷新数据：**
        该命令会获取所有A股过去一年的日K数据并存入本地的 `stock_data.sqlite3` 数据库。
        ```bash
        python src/main.py --mode full
        ```

    *   **每日增量更新：**
        该命令会检查数据库中每只股票的最新日期，并只获取此后到今天的新数据。
        ```bash
        python src/main.py --mode increment
        ```

    *   **数据验证：**
        该命令会对数据库中的数据进行基础的校验。
        ```bash
        python src/main.py --mode validate
        ```