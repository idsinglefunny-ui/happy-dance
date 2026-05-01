import pymysql
import os

DB_CONFIG = {
    'host': '117.72.76.53',
    'port': 63306,
    'user': 'king_dancer_go',
    'password': 'KingDance_._334456',
    'database': 'king_dance',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def init_db():
    connection = pymysql.connect(**DB_CONFIG)
    try:
        with connection.cursor() as cursor:
            # 读取 schema.sql 文件
            schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
            with open(schema_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()

            # 去掉 CREATE DATABASE 和 USE dance_king，因为用户给的 DB 是 king_dance 且已存在
            statements = sql_script.split(';')
            
            for statement in statements:
                stmt = statement.strip()
                if stmt and not stmt.lower().startswith('create database') and not stmt.lower().startswith('use '):
                    print(f"Executing: {stmt[:50]}...")
                    cursor.execute(stmt)
            
        connection.commit()
        print("Database schema initialized successfully!")
    except Exception as e:
        print(f"Error initializing DB: {e}")
    finally:
        connection.close()

if __name__ == '__main__':
    init_db()
