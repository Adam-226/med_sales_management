import os
from sqlalchemy import create_engine, text

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+pymysql://root:********@localhost/med_sales_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_db():
        engine = create_engine('mysql+pymysql://root:********@localhost/')
        conn = engine.connect()
        conn.execute(text("CREATE DATABASE IF NOT EXISTS med_sales_db"))
        conn.close()

    @staticmethod
    def import_sql_files():
        engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        conn = engine.connect()
        sql_files_path = 'Dump-med_sales_db'
        for filename in os.listdir(sql_files_path):
            if filename.endswith('.sql'):
                file_path = os.path.join(sql_files_path, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    sql = file.read()
                    # 分割 SQL 语句
                    statements = sql.split(';')
                    for statement in statements:
                        statement = statement.strip()
                        if statement:
                            try:
                                conn.execute(text(statement))
                            except Exception as e:
                                print(f"Error executing statement: {statement}\n{e}")
        conn.close()


