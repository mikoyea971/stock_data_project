from flask import Flask
from config import Config
from .extensions import db
from .models import User, LoginLog # 导入模型以确保它们被SQLAlchemy识别

def create_app(config_class=Config):
    """应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化扩展
    db.init_app(app)

    # 注册蓝图
    from .auth.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from .main.routes import main_bp
    app.register_blueprint(main_bp, url_prefix='/')

    return app