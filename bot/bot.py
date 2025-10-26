import os
import threading
import asyncio
from flask import Flask
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

# === Загрузка переменных окружения ===
load_dotenv()
TOKEN = os.getenv("TOKEN")
BASE_URL = os.getenv("BASE_URL", "https://tonminer-2ybq.onrender.com")

if not TOKEN:
    raise ValueError("❌ Ошибка: TOKEN не найден. Укажи его в файле .env или переменных окружения.")

# === Инициализация Telegram-бота ===
bot_app = Application.builder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ответ на команду /start"""
    kb = [[
        InlineKeyboardButton(
            "🎮 Играть в TON Miner",
            web_app=WebAppInfo(url=f"{BASE_URL}/?ref={update.effective_user.id}")
        )
    ]]
    await update.message.reply_text(
        "Запускай игру 👇",
        reply_markup=InlineKeyboardMarkup(kb)
    )

bot_app.add_handler(CommandHandler("start", start))

# === Асинхронный запуск бота ===
async def run_bot():
    print("🤖 Бот запущен...")
    await bot_app.initialize()
    await bot_app.start()
    await bot_app.updater.start_polling()
    await asyncio.Event().wait()  # держит бота активным

def bot_thread():
    asyncio.run(run_bot())

# === Flask Keep-alive сервер ===
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "ok", 200

# === Точка входа ===
if __name__ == "__main__":
    # Запускаем Telegram-бота в отдельном потоке
    threading.Thread(target=bot_thread, daemon=True).start()

    # Запускаем Flask-сервер
    port = int(os.getenv("PORT", "10000"))
    print(f"🌐 Flask сервер запущен на порту {port}")
    flask_app.run(host="0.0.0.0", port=port)

