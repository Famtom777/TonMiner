import os, sqlite3, time, json
from flask import Flask, request, jsonify, send_from_directory, abort
from dotenv import load_dotenv
from db import init_db, db
from security import check_init_data

load_dotenv()
WEB_DIR = os.path.join(os.path.dirname(__file__), "web")
from flask import Flask, send_from_directory
import os

app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(__file__), "web"),
    static_url_path="/"
)


# ======= STATIC =======
@app.get("/")
def index():
    return send_from_directory(WEB_DIR, "index.html")
@app.get("/app.js")
def app_js():
    return send_from_directory(WEB_DIR, "app.js")
@app.get("/style.css")
def style_css():
    return send_from_directory(WEB_DIR, "style.css")

# ======= HELPERS =======
def user_from_initdata_or_401():
    init_data = request.headers.get("X-TG-INIT-DATA", "")
    data = check_init_data(init_data)
    if not data:
        abort(401)
    user = json.loads(data.get("user","{}"))
    return user   # {id, first_name, …}

# ======= API =======
@app.post("/api/state")
def api_state():
    user = user_from_initdata_or_401()
    uid = user["id"]; name = user.get("first_name","player")
    ref = request.args.get("ref")
    with db() as conn:
        row = conn.execute("SELECT * FROM users WHERE uid=?", (uid,)).fetchone()
        if not row:
            # простая генерация реф-кода
            ref_code = f"{uid:x}"[-6:]
            conn.execute(
                "INSERT INTO users(uid,name,coins,energy,click_power,miner_hashrate,ref_code) VALUES(?,?,?,?,?,?,?)",
                (uid, name, 0, 0, 1, 0, ref_code)
            )
            # зафиксировать рефера если ref предоставлен и валидный
            if ref and ref.isdigit() and int(ref) != uid:
                # parent = ref (uid пригласившего)
                # добавим уровень 1
                conn.execute("INSERT OR IGNORE INTO referrals(child_uid,parent_uid,level) VALUES(?,?,?)",
                             (uid, int(ref), 1))
                # уровень 2: родитель родителя
                p2 = conn.execute("SELECT parent_uid FROM referrals WHERE child_uid=?", (int(ref),)).fetchone()
                if p2:
                    conn.execute("INSERT OR IGNORE INTO referrals(child_uid,parent_uid,level) VALUES(?,?,?)",
                                 (uid, p2["parent_uid"], 2))
            conn.commit()
            row = conn.execute("SELECT * FROM users WHERE uid=?", (uid,)).fetchone()
        return jsonify(dict(row))

# клик Energizer (анти-спам: не чаще N раз в секунду на сервере — см. задачу)
_LAST = {}
MAX_CPS = 8  # кликов в секунду

@app.post("/api/energize")
def api_energize():
    user = user_from_initdata_or_401()
    uid = user["id"]
    now = time.time()
    if now - _LAST.get(uid, 0) < 1.0/MAX_CPS:
        # слишком часто — игнор
        return jsonify({"ok": False, "reason": "rate"}), 200
    _LAST[uid] = now
    with db() as conn:
        row = conn.execute("SELECT energy, click_power FROM users WHERE uid=?", (uid,)).fetchone()
        energy = row["energy"] + row["click_power"]
        conn.execute("UPDATE users SET energy=? WHERE uid=?", (energy, uid))
        conn.commit()
    return jsonify({"ok": True, "energy": energy})

# конверт энергии в «добычу» (Miner): упростим — 1 EE -> +hashrate или немедленная добыча
@app.post("/api/mine_tick")
def api_mine_tick():
    user = user_from_initdata_or_401()
    uid = user["id"]
    use = int((request.get_json() or {}).get("use", 0))  # сколько EE применить
    if use <= 0: abort(400)
    with db() as conn:
        row = conn.execute("SELECT energy, coins, miner_hashrate FROM users WHERE uid=?", (uid,)).fetchone()
        if row["energy"] < use:
            return jsonify({"ok": False, "error": "Недостаточно энергии"}), 200
        # модель простая: каждые 10 EE -> +1 коин (пример)
        gained = use // 10
        energy_left = row["energy"] - use
        coins = row["coins"] + gained
        conn.execute("UPDATE users SET energy=?, coins=? WHERE uid=?", (energy_left, coins, uid))
        conn.commit()
    return jsonify({"ok": True, "coins": coins, "energy": energy_left, "gained": gained})

# магазин апгрейдов (повышаем click_power)
@app.post("/api/upgrade_click")
def api_upgrade_click():
    user = user_from_initdata_or_401()
    uid = user["id"]
    COST = 50   # монет
    INC  = 1
    with db() as conn:
        row = conn.execute("SELECT coins, click_power FROM users WHERE uid=?", (uid,)).fetchone()
        if row["coins"] < COST:
            return jsonify({"ok": False, "error": "Нужно 50 коинов"}), 200
        coins = row["coins"] - COST
        power = row["click_power"] + INC
        conn.execute("UPDATE users SET coins=?, click_power=? WHERE uid=?", (coins, power, uid))
        conn.commit()
    return jsonify({"ok": True, "coins": coins, "click_power": power})

# рынок энергии (упрощённо: листинг ордера)
@app.post("/api/order_energy")
def api_order_energy():
    user = user_from_initdata_or_401()
    uid = user["id"]
    j = request.get_json() or {}
    side = j.get("side")         # 'sell' / 'buy'
    amount = int(j.get("amount", 0))
    price = float(j.get("price_ton", 0))
    if side not in ("sell","buy") or amount<=0 or price<=0:
        abort(400)
    with db() as conn:
        if side == "sell":
            row = conn.execute("SELECT energy FROM users WHERE uid=?", (uid,)).fetchone()
            if row["energy"] < amount:
                return jsonify({"ok": False, "error": "Недостаточно EE"}), 200
            conn.execute("UPDATE users SET energy=energy-? WHERE uid=?", (amount, uid))
        conn.execute("INSERT INTO orders_energy(uid,side,amount,price_ton,status) VALUES(?,?,?,?,?)",
                     (uid, side, amount, price, 'open'))
        conn.commit()
    return jsonify({"ok": True})

# топ-100
@app.get("/api/leaderboard")
def api_leaderboard():
    with db() as conn:
        rows = conn.execute("SELECT uid,name,coins,energy FROM users ORDER BY coins DESC LIMIT 100").fetchall()
        return jsonify([dict(r) for r in rows])

if __name__ == "__main__":
    init_db()
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
