from project import create_app, db
from project.models import User, LoginLog # 确保模型被导入

# 使用工厂函数创建应用实例
app = create_app()

@app.shell_context_processor
def make_shell_context():
    """为 flask shell 命令添加上下文"""
    return {'db': db, 'User': User, 'LoginLog': LoginLog}

if __name__ == '__main__':
    # 确保在运行应用前创建所有数据库表
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)