from app import create_app, db
from config import Config

# 初始化数据库
Config.init_db()

# 创建应用
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()       # 创建所有表
        Config.import_sql_files() # 导入 SQL 文件
    app.run(host='0.0.0.0', port=5001, debug=True)