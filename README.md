# 重构后的 Flask 用户管理应用  

这是一个**简单用户管理应用**的重构版本，最初以**单文件 Flask 应用**形式开发。新结构采用 **应用工厂模式** 和 **蓝图（Blueprints）** 设计，大幅提升代码的 **组织性、可扩展性和可维护性**。  


## 项目结构  

```  
项目根目录/  
├── config.py          # 应用配置类（开发/生产环境等）  
├── run.py             # 应用启动入口  
├── requirements.txt   # 依赖清单  
└── project/           # 主应用包（Python Package）  
    ├── __init__.py    # 应用工厂：定义 create_app() 函数  
    ├── extensions.py  # 初始化 Flask 扩展（如 SQLAlchemy、JWT 等）  
    ├── models.py      # 数据库模型（User、LoginLog 等）  
    ├── auth/          # 认证蓝图（处理登录、注册、登出）  
    │   ├── __init__.py # 蓝图实例化（auth_bp）  
    │   └── routes.py   # 认证路由和视图函数  
    ├── main/          # 核心功能蓝图（仪表盘、个人资料）  
    │   ├── __init__.py # 蓝图实例化（main_bp）  
    │   └── routes.py   # 核心路由和视图函数  
    └── templates/     # Jinja2 模板文件（按蓝图模块分类存放）  
```  


## 运行指南  

### 1. 创建虚拟环境（推荐）  
```bash  
python -m venv venv  
source venv/bin/activate  # Windows 系统请执行：venv\Scripts\activate  
```  


### 2. 安装依赖  
```bash  
pip install -r requirements.txt  
```  


### 3. 启动应用  
```bash  
python run.py  
```  

- 应用将以 **调试模式** 启动，访问地址：`http://localhost:5001`。  
- 首次运行时，SQLite 数据库文件 `users.db` 会自动在 `project/` 目录下创建。  


通过这种结构，后续新增功能（如权限管理、日志模块）可通过 **新增蓝图** 实现，无需修改核心逻辑，真正做到“模块化开发”。