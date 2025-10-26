from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler
import os, asyncio

# Загружаем токен и адрес
TOKEN = os.getenv("TOKEN")
BASE_URL = os.getenv("BASE_URL")  # ссылка на твой webapp (https://tonminer-web.onrender.com)
SELF_URL = os.getenv("SELF_URL")  # ссылка на этого бота на Render

WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{SELF_URL}{WEBHOOK_PATH}"

# Flask-приложение
app = Flask(__name__)

# Telegram-приложение
application = Application.builder().token(TOKEN).build()

# Команда /start
async def start(update: Update, context):
    kb = [
        [InlineKeyboardButton("🎮 Играть в TON Miner", web_app={"url": f"{BASE_URL}/?ref={update.effective_user.id}"})]
    ]
    await update.message.reply_text("Запускай игру 👇", reply_markup=InlineKeyboardMarkup(kb))

application.add_handler(CommandHandler("start", start))


# === Flask маршруты ===
@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok", 200


@app.route("/set_webhook")
async def set_webhook():
    await application.bot.set_webhook(WEBHOOK_URL)
    return f"Webhook установлен на {WEBHOOK_URL}", 200


@app.route("/")
def index():
    return "TON Miner Bot работает ✅", 200


# === Запуск ===
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(application.initialize())
    loop.create_task(application.start())
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "10000")))

