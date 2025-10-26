import os
import sqlite3
from flask import Flask, render_template, jsonify, g

# === Настройки Flask ===
app = Flask(__name__, static_folder="static", template_folder="templates")

# === Настройки базы данных ===
DATABASE = os.path.join(os.path.dirname(__file__), "miner.db")

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    """Создать таблицы, если их нет"""
    conn = sqlite3.connect(DATABASE)
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        energy INTEGER DEFAULT 0
    );
    """)
    conn.commit()
    conn.close()

# === Главная страница ===
@app.route("/")
def index():
    return render_template("index.html")

# === API: Майнить энергию ===
@app.route("/api/mine", methods=["POST"])
def mine():
    conn = get_db()
    cur = conn.cursor()

    # Для теста: используем одного игрока (id=1)
    cur.execute("INSERT OR IGNORE INTO users (id, energy) VALUES (1, 0)")
    cur.execute("UPDATE users SET energy = energy + 1 WHERE id = 1")
    conn.commit()

    cur.execute("SELECT energy FROM users WHERE id = 1")
    energy = cur.fetchone()["energy"]
    return jsonify({"energy": energy})

# === Точка входа ===
if __name__ == "__main__":
    # создаём базу в контексте приложения
    with app.app_context():
        init_db()

    port = int(os.getenv("PORT", "10000"))
    print(f"🌐 TON Miner сервер запущен: http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port)



