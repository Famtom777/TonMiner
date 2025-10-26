import sqlite3, os

DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), "db.sqlite3"))

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")

    # Проверяем, существует ли файл схемы
    if not os.path.exists(schema_path):
        print("⚠ schema.sql не найден — создаю пустую базу данных")
        return

    # Открываем schema.sql в режиме чтения (!!!)
    with open(schema_path, "r", encoding="utf-8") as f:
        sql_script = f.read()

    # Выполняем SQL-скрипт
    with db() as conn:
        conn.executescript(sql_script)
        conn.commit()

    print("✅ База данных успешно инициализирована.")

